"""Controlled conversion of admitted signed frames into observed L0 waveforms."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from .domain import EvidenceClass, ObservationL0, Provenance, waveform_digest
from .ingestion import AcquisitionManifest
from .instrument_ingestion import SignedInstrumentFrame


@dataclass(frozen=True)
class DecodedWaveform:
    samples: tuple[float, ...]
    sample_rate_hz: int
    sensor_id: str
    clock_uncertainty_ns: float
    calibration_id: str

    def __post_init__(self) -> None:
        if not self.samples or self.sample_rate_hz <= 0 or not self.sensor_id or not self.calibration_id:
            raise ValueError("decoded waveform fields are incomplete")
        if self.clock_uncertainty_ns < 0:
            raise ValueError("decoded waveform clock uncertainty is invalid")


class InstrumentFrameDecoder(Protocol):
    decoder_id: str
    decoder_version: str

    def decode(self, frame: SignedInstrumentFrame) -> DecodedWaveform:
        """Decode the approved signed payload format without mutating raw bytes."""


def decode_verified_instrument_frame(
    frame: SignedInstrumentFrame,
    manifest: AcquisitionManifest,
    decoder: InstrumentFrameDecoder,
    decoder_configuration_digest: str,
) -> ObservationL0:
    """Create observed L0 only from a matching signed-frame acquisition record."""
    if not decoder_configuration_digest:
        raise ValueError("decoder configuration digest is required")
    if manifest.source_id != frame.source_id or manifest.evidence_class is not EvidenceClass.OBSERVED:
        raise ValueError("acquisition manifest is not observed evidence for this frame source")
    if manifest.artifact_digest != frame.payload_digest or manifest.media_type != frame.media_type:
        raise ValueError("acquisition manifest does not match raw frame bytes")
    if manifest.verification.scheme != "detached_signature":
        raise ValueError("observed frame manifest lacks required detached-signature verification")
    metadata = manifest.transport_metadata
    expected_metadata = {
        "node_id": frame.node_id,
        "instrument_serial": frame.instrument_serial,
        "signer_key_id": frame.signer_key_id,
        "signature_digest": frame.signature_digest,
        "schema_id": frame.schema_id,
        "sequence_number": str(frame.sequence_number),
    }
    if any(metadata.get(key) != value for key, value in expected_metadata.items()):
        raise ValueError("acquisition manifest security metadata does not match frame")

    decoded = decoder.decode(frame)
    configuration_digest = sha256(
        f"{decoder_configuration_digest}:{decoder.decoder_id}:{decoder.decoder_version}:{manifest.digest}".encode()
    ).hexdigest()
    provenance = Provenance(
        evidence_class=EvidenceClass.OBSERVED,
        scenario_id=f"observed:{manifest.artifact_digest}",
        generator_version=f"{decoder.decoder_id}/{decoder.decoder_version}",
        configuration_digest=configuration_digest,
        model_card_digest=sha256(b"not-applicable:instrument-decoder").hexdigest(),
        created_at=frame.acquired_at,
        source_artifact_digest=manifest.artifact_digest,
        source_manifest_digest=manifest.digest,
    )
    return ObservationL0(
        observation_id=f"l0-{manifest.artifact_digest[:12]}-{configuration_digest[:12]}",
        samples=decoded.samples,
        sample_rate_hz=decoded.sample_rate_hz,
        started_at=frame.acquired_at,
        sensor_id=decoded.sensor_id,
        sequence_number=frame.sequence_number,
        clock_uncertainty_ns=decoded.clock_uncertainty_ns,
        calibration_id=decoded.calibration_id,
        provenance=provenance,
        payload_digest=waveform_digest(decoded.samples),
    )
