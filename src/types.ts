export type TabType = 'overview' | 'conjunction' | 'tdoa' | 'radar' | 'evidence' | 'tests' | 'evaluation';

export interface ConjunctionEvent {
  id: string;
  primaryObject: string;
  secondaryObject: string;
  noradPrimary: number;
  noradSecondary: number;
  tca: string; // Time of Closest Approach
  missDistanceKm: number;
  collisionProbability: number;
  relativeVelocityKms: number;
  riskLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  evidenceClass: 'synthetic' | 'laboratory' | 'observed';
}

export interface GroundStation {
  id: string;
  name: string;
  lat: number;
  lng: number;
  elevationM: number;
  frequencyGHz: number;
  snrDb: number;
  status: 'ACTIVE' | 'CALIBRATING' | 'OFFLINE';
  delayNs: number;
}

export interface AuditLedgerEntry {
  id: string;
  timestamp: string;
  artifactHash: string;
  evidenceClass: 'synthetic' | 'laboratory' | 'observed';
  gateDecision: 'ADMITTED' | 'REJECTED' | 'QUARANTINED';
  author: string;
  summary: string;
  falsifierChecked: boolean;
}

export interface TestSuiteResult {
  name: string;
  module: string;
  numTests: number;
  passed: number;
  failed: number;
  durationMs: number;
  status: 'PASSED' | 'FAILED' | 'RUNNING' | 'PENDING';
}
