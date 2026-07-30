# Calibration-certificate governance

## Purpose

Future laboratory and flight observations may enter L1 calibration only through a versioned calibration certificate. A certificate binds the sensor identity, measurand, input/output units, scale, standard uncertainty, validity interval, traceability record, evidence references, and lifecycle status.

## Enforced controls

The calibration adapter rejects a certificate that is revoked or superseded, belongs to another sensor, or is outside its validity interval. A successful L1 record preserves the original L0 digest and carries the certificate ID, scale, uncertainty, and `certificate_traceable` quality flag.

Certificate references are required to resolve inside the independent Heimdall repository. The initial registry is intentionally empty: no laboratory or flight certificate has been admitted.

## Scientific boundary

The synthetic fixture’s calibration is a test parameter, not a traceable laboratory or flight calibration. A traceable certificate establishes only the documented measurement-chain transformation and uncertainty; it does not validate the plasma model, identify debris, or establish operational fitness.

## Next laboratory evidence

An actual certificate must be accompanied by controlled test procedures, reference-signal records, instrument configuration/serial evidence, uncertainty analysis, reviewer approval, and a revocation/supersession policy. These records should be stored through the evidence-ingestion and audit-bundle controls before the certificate is activated.
