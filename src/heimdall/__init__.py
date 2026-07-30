"""Project Heimdall research reference implementation."""

from .calibration import calibrate
from .audit_bundle import AuditBundle, build_audit_bundle, verify_audit_bundle, write_audit_bundle
from .domain import CalibratedObservationL1, CandidateL2, DatasetSplit, EvidenceClass, ObservationL0, Provenance
from .evaluation import DetectionReport, EvaluationRow, evaluate, evaluate_by_stratum
from .forward_models import ForwardModel, IllustrativeBurstSineModel, NullSignalModel
from .governance import (
    ExperimentPlan,
    ExperimentResult,
    JsonlExperimentLedger,
    PlanStatus,
    ThresholdPolicy,
    execute_pre_registered_experiment,
    sealed_now,
)
from .pipeline import BaselineMatchedFilter, CandidateGate, ClockQualityGate, GateDecision, PeakContrastGate, detect
from .official_sources import NOAA_SWPC_PLANETARY_K_INDEX, NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT
from .remote_context import HttpsContextConnector, OfficialEndpoint, ingest_external_context
from .registry import RegisteredScenario, reference_registry
from .simulation import SyntheticScenario, generate_observation

__all__ = [
    "BaselineMatchedFilter",
    "AuditBundle",
    "CandidateGate",
    "CalibratedObservationL1",
    "CandidateL2",
    "ClockQualityGate",
    "DatasetSplit",
    "DetectionReport",
    "EvidenceClass",
    "ExperimentPlan",
    "ExperimentResult",
    "EvaluationRow",
    "ForwardModel",
    "GateDecision",
    "HttpsContextConnector",
    "IllustrativeBurstSineModel",
    "JsonlExperimentLedger",
    "ObservationL0",
    "OfficialEndpoint",
    "NOAA_SWPC_PLANETARY_K_INDEX",
    "NOAA_SWPC_PLANETARY_K_INDEX_ENDPOINT",
    "NullSignalModel",
    "Provenance",
    "PeakContrastGate",
    "PlanStatus",
    "RegisteredScenario",
    "SyntheticScenario",
    "ThresholdPolicy",
    "calibrate",
    "build_audit_bundle",
    "detect",
    "evaluate",
    "evaluate_by_stratum",
    "execute_pre_registered_experiment",
    "generate_observation",
    "ingest_external_context",
    "reference_registry",
    "sealed_now",
    "verify_audit_bundle",
    "write_audit_bundle",
]
