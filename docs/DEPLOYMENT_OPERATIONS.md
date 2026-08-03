# Heimdall Electra — Deployment & Operations Guide

Production deployment and operational excellence guide for Heimdall research system.

## Deployment Architecture

### Development Environment
```
Local Development
├── Python 3.11+ environment
├── Local file-based storage
├── SQLite audit trails
├── Console on localhost:5173
└── No external services required
```

### Staging Environment
```
Staging Deployment
├── Containerized detector service
├── Object storage (S3-like interface)
├── PostgreSQL audit logs
├── TLS/mTLS for internal services
├── Rate limiting and backpressure
└── Distributed tracing (Jaeger)
```

### Production Environment
```
Production Deployment
├── Kubernetes-managed services
├── Multi-zone object storage
├── Replicated database with failover
├── End-to-end encryption
├── SLA-backed service levels
├── Comprehensive monitoring
├── Automated incident response
└── Audit trail with external archive
```

## Docker Containerization

### Dockerfile Example
```dockerfile
FROM python:3.11-slim

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source
COPY src/ ./src/
COPY pyproject.toml ./

# Install package
RUN pip install --no-deps .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import heimdall; print('OK')"

# Run detector service
CMD ["python", "-m", "heimdall.detector_service"]
```

### Image Security
- Scan for CVEs: `trivy image heimdall:latest`
- Use specific base image versions
- No root user in container
- Read-only filesystem where possible
- No secrets in images

## Configuration Management

### Environment Variables
```bash
# Detector configuration
HEIMDALL_DETECTOR_THRESHOLD=0.65
HEIMDALL_DETECTOR_FREQUENCY_HZ=64.0
HEIMDALL_DETECTOR_WINDOW_DURATION_S=0.25

# Gate configuration
HEIMDALL_GATE_PEAK_CONTRAST_RATIO=1.75
HEIMDALL_GATE_CLOCK_UNCERTAINTY_NS=1000

# Service configuration
HEIMDALL_PORT=8080
HEIMDALL_WORKERS=4
HEIMDALL_LOG_LEVEL=INFO

# Storage configuration
HEIMDALL_STORAGE_TYPE=s3
HEIMDALL_STORAGE_BUCKET=heimdall-evidence
HEIMDALL_STORAGE_REGION=us-east-1

# Audit configuration
HEIMDALL_AUDIT_TRAIL_PATH=/var/log/heimdall/audit.jsonl
HEIMDALL_AUDIT_REMOTE_URL=https://audit-archive.example.com
```

### Configuration Validation
```python
from heimdall import ConfigurationManager, ConfigurationSchema, ConfigField, ConfigValueType

# Define schema
schema = ConfigurationSchema("detector")
schema.add_field(ConfigField(
    name="threshold",
    value_type=ConfigValueType.FLOAT,
    constraints=[
        ConfigConstraint("min", 0.0),
        ConfigConstraint("max", 1.0),
    ],
    required=True,
))

# Load from environment
manager = ConfigurationManager()
manager.register_schema(schema)
config = manager.load_from_env("detector", prefix="HEIMDALL_DETECTOR")

# Access with type safety
threshold = config.get_float("threshold")
```

## Monitoring & Observability

### Key Metrics

#### Detector Metrics
- `detector_latency_ms`: Detector execution time (p50, p95, p99)
- `detector_score_distribution`: Score value distribution
- `detector_throughput_ops_sec`: Operations per second
- `detector_memory_mb`: Memory usage per operation

#### Quality Metrics
- `detection_rate`: True positive rate on validation corpus
- `false_alarm_rate`: False positive rate on noise corpus
- `gate_rejection_rate`: Percentage of observations rejected by gates

#### Service Metrics
- `http_request_latency_ms`: API request latency
- `audit_trail_write_latency_ms`: Audit trail performance
- `storage_operation_latency_ms`: Storage adapter latency
- `service_errors_total`: Total error count by error type

#### Operational Metrics
- `uptime_hours`: Service uptime
- `active_connections`: Current connection count
- `disk_usage_gb`: Disk space used
- `cpu_utilization_percent`: CPU usage

### Logging

#### Log Levels
```
ERROR  - Failures requiring intervention
WARN   - Degraded behavior or anomalies
INFO   - Significant events and decisions
DEBUG  - Detailed diagnostic information
TRACE  - Very detailed debugging
```

#### Structured Logging Format
```json
{
  "timestamp": "2026-08-03T12:34:56.789Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": "INFO",
  "logger": "detector",
  "event_kind": "operation_complete",
  "component": "BaselineMatchedFilter",
  "operation": "detect",
  "duration_ms": 42,
  "status": "success",
  "details": {
    "observation_id": "obs-001",
    "candidate_id": "cand-001",
    "detected": true,
    "score": 0.78
  }
}
```

### Alerting Rules

#### Critical Alerts
```
- Detector latency > 1 second (p99)
- Error rate > 1%
- Audit trail write failure
- Service unavailable
```

#### Warning Alerts
```
- Detector latency > 500ms (p95)
- Error rate > 0.1%
- Disk usage > 80%
- Memory usage > 90%
```

## High Availability

### Redundancy
- **Multi-zone deployment**: Run in at least 3 availability zones
- **Database replication**: Master-slave with automatic failover
- **Load balancing**: Distribute traffic across multiple instances
- **Circuit breaker**: Fail fast on cascading failures

### Fault Tolerance
```python
from heimdall.factories import DependencyContainer

# Configure with fallbacks
container = get_container()

# Primary storage
primary_storage = FileEvidenceStore(Path("/var/lib/heimdall/storage"))
# Fallback storage
fallback_storage = FileEvidenceStore(Path("/backup/heimdall/storage"))

# Decorator to add retry logic
class RetryableAdapter:
    def __init__(self, primary, fallback, max_retries=3):
        self.primary = primary
        self.fallback = fallback
        self.max_retries = max_retries
    
    def put(self, payload: bytes) -> str:
        for attempt in range(self.max_retries):
            try:
                return self.primary.put(payload)
            except StorageError as e:
                if attempt == self.max_retries - 1:
                    logger.warning(f"Primary failed, using fallback: {e}")
                    return self.fallback.put(payload)
                time.sleep(2 ** attempt)  # Exponential backoff
```

## Disaster Recovery

### Backup Strategy
- **RPO (Recovery Point Objective)**: 1 hour
- **RTO (Recovery Time Objective)**: 15 minutes
- **Backup frequency**: Continuous with hourly snapshots
- **Backup location**: Geographically separate region

### Recovery Procedures
```bash
# Full recovery from backup
heimdall-restore --backup-date 2026-08-03T12:00:00Z --target /var/lib/heimdall

# Partial recovery (specific evidence class)
heimdall-restore --backup-date 2026-08-03T12:00:00Z \
                 --evidence-class observed \
                 --target /var/lib/heimdall

# Verify restored data
heimdall-verify-integrity --root /var/lib/heimdall/restored
```

## Security Operations

### Access Control
- **RBAC**: Role-based access to evidence classes
- **Service accounts**: Short-lived tokens for service-to-service
- **Audit**: All access logged with actor, resource, action

### Secret Management
- **Secrets store**: Vault or AWS Secrets Manager
- **Rotation**: Automatic rotation every 90 days
- **Encryption**: Secrets encrypted in transit and at rest
- **Never log**: Secrets never appear in logs or error messages

### Compliance

#### Data Protection
- **Encryption at rest**: AES-256
- **Encryption in transit**: TLS 1.3
- **Data classification**: Mark by evidence class
- **Retention**: Policy-based with automatic archival

#### Audit & Accountability
- **Immutable audit trail**: Append-only logs with checksums
- **Tamper detection**: Regular integrity checks
- **External archive**: Send audit logs to certified archive
- **Regulatory reporting**: Automated compliance reports

## Performance Tuning

### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_observation_timestamp ON observations(timestamp);
CREATE INDEX idx_candidate_scenario ON candidates(scenario_id);
CREATE INDEX idx_audit_correlation ON audit_events(correlation_id);

-- Analyze query plans
EXPLAIN ANALYZE SELECT * FROM candidates WHERE scenario_id = 'scenario-001';
```

### Caching Strategy
```python
from functools import lru_cache
from heimdall import ModelRegistry

class CachedModelRegistry(ModelRegistry):
    @lru_cache(maxsize=128)
    def resolve(self, model_id: str, version: str):
        """Cache model cards to avoid repeated lookups."""
        return super().resolve(model_id, version)
```

### Resource Limits
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Incident Response

### Incident Severity Levels
- **CRITICAL**: Service unavailable, data loss risk, security breach
- **HIGH**: Degraded performance, significant error rate
- **MEDIUM**: Minor functionality impaired, single-user impact
- **LOW**: Cosmetic issues, no functional impact

### Response Procedures

#### Critical Incident
```
1. Page on-call engineer
2. Declare incident (war room)
3. Gather stakeholders
4. Implement immediate mitigation
5. Document timeline
6. Post-incident review within 24h
```

#### Incident Log Example
```
Incident ID: INC-2026-0103
Severity: HIGH
Detected: 2026-08-03T14:23:15Z
Root Cause: Storage adapter timeout under load
Timeline:
  14:23:15 - Alerts triggered (error rate > 1%)
  14:24:00 - On-call paged
  14:26:00 - Incident war room opened
  14:28:00 - Mitigation: Scaled detector service
  14:35:00 - Error rate normalized
  14:45:00 - Root cause identified
  15:00:00 - Permanent fix deployed
Resolution: Increased storage connection pool
Impact: 15 min, ~500 requests affected
```

## Release Management

### Versioning
- Semantic versioning: MAJOR.MINOR.PATCH
- Alpha/Beta releases: Suffix with -alpha or -beta
- Long-term support: Mark critical versions as LTS

### Release Checklist
- [ ] All tests passing
- [ ] Code review completed
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] CHANGELOG entry
- [ ] Deployment runbook reviewed
- [ ] Rollback plan documented
- [ ] Stakeholder communication sent

### Deployment Strategy
```bash
# Blue-green deployment
# 1. Deploy to green environment
docker pull heimdall:1.2.3
docker run -d --name heimdall-green heimdall:1.2.3

# 2. Run smoke tests on green
./smoke-tests.sh heimdall-green

# 3. Switch traffic
load_balancer.route_to("green")

# 4. Monitor for errors
monitor.alert_on_error_rate_spike()

# 5. Keep blue for quick rollback
# If issues: load_balancer.route_to("blue")
```

## Maintenance Windows

### Planned Maintenance
- **Frequency**: Monthly second Tuesday, 02:00-04:00 UTC
- **Notification**: 1 week advance notice
- **Duration**: 2 hours maximum
- **Impact**: Brief service interruption expected

### Emergency Maintenance
- **Triggers**: Critical security patches, data corruption, system failure
- **Notification**: Best effort (may be immediate)
- **Duration**: As long as needed
- **Approval**: On-call + manager authorization

## Operational Runbooks

### Scaling Detector Service
```bash
# Increase replicas
kubectl scale deployment heimdall-detector --replicas=10

# Monitor scaling
watch kubectl get pods -l app=heimdall-detector

# Verify health
curl http://heimdall-detector:8080/health
```

### Recovering Corrupted Audit Trail
```bash
# Verify integrity
heimdall-audit-verify --path /var/log/heimdall/audit.jsonl

# Restore from backup
heimdall-audit-restore --backup-date 2026-08-03 --output audit.jsonl

# Validate restored data
heimdall-audit-verify --path audit.jsonl
```

### Clearing Old Evidence
```bash
# List eligible for deletion
heimdall-evidence-cleanup --policy "delete-after-90-days" --dry-run

# Execute cleanup with confirmation
heimdall-evidence-cleanup --policy "delete-after-90-days" --confirm

# Verify
heimdall-audit-events --event-type "evidence_deleted" --limit=100
```

## Operational Metrics

### SLO (Service Level Objectives)
- **Availability**: 99.9% uptime (43 minutes downtime/month)
- **Latency**: p99 < 500ms
- **Throughput**: 1000 ops/second
- **Error Rate**: < 0.1%

### Error Budget
- Monthly error budget: 100 errors (0.1%)
- When exhausted: Feature freeze until reset
- Burn rate monitoring: Alert if 2x budget use in 1 week
