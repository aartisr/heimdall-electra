# Signed instrument-frame ingestion

## Purpose

Observed Heimdall evidence must enter through a fail-closed signed-frame boundary. A frame declares its source, node, instrument serial, acquisition time, payload, signer key ID, and detached signature. A deployment-specific verifier port must confirm the exact frame payload against approved key material before the bytes are stored as observed evidence.

## Enforced controls

The ingestion path rejects a non-instrument source, a source/frame identity mismatch, an unapproved schema/media type/byte limit, a source not approved for observed evidence, a failed signature check, a signer-key mismatch, a replayed/out-of-order frame, an excessive sequence gap, implausible future skew, stale transport delay, or a source policy that does not explicitly permit detached-signature verification. It preserves the payload hash, signature hash, signer key ID, verifier ID, acquisition time, receive time, transport delay, schema/payload policy, node, instrument serial, sequence number, and sequence gap in content-addressed manifest lineage.

Any future decoder that turns an admitted frame into an observed L0 waveform must carry both the preserved raw-artifact digest and the acquisition-manifest digest in its provenance. The domain contract rejects an observed L0 provenance record without both links, so decoded samples cannot be presented without their immutable source-byte lineage.

The decoder is a Strategy port. It must verify that the acquisition manifest has the exact payload digest, media type, source, detached-signature scheme, node, instrument serial, signer key, signature digest, schema ID, and sequence number of the raw frame before producing L0. No decoder implementation or observed waveform format is bundled with this repository.

## Deliberate limitation

There is no bundled crypto verifier and no registered observed Heimdall source. A test double only proves that the fail-closed integration contract behaves correctly; it does not authenticate any instrument. A real deployment must provide a reviewed verifier adapter with hardware-backed or otherwise governed key management, certificate/revocation handling, hardware-counter/replay protection, time-quality checks, and an approved instrument source record.
