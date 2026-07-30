# Source registry governance

## Purpose

The source registry is the data-driven approval boundary for all external integrations. It records the exact approved source, owner, terms reference, evidence class, verification scheme, endpoint/host allowlist, byte limit, permitted use, review record, and time-contract status.

A connector must resolve a source from the registry before it can fetch. Application code must not enable a new source, host, evidence class, or purpose by itself.

## Current record

The registry contains one source: NOAA SWPC planetary K-index. It is approved only for external environmental context and HTTPS transport-authenticated retrieval. It is not approved for debris prior, independent validation, primary measurement, observed evidence, or automated time alignment.

## Review flow

1. Propose source and intended purpose.
2. Review ownership, terms, classification, data level, caveats, retention, and access restrictions.
3. Review endpoint, host allowlist, size/rate limits, authentication, and integrity-verification method.
4. Define time basis, time uncertainty, coordinate/unit conventions, and source-specific parser.
5. Obtain independent science, security, and data-governance approval.
6. Add a versioned registry record and test the connector against it.
7. Re-review on source/API/schema/terms change or expiry.

## Current time-contract decision

The current official-feed search verified that NOAA publishes the planetary K-index endpoint but did not yield an authoritative statement for the semantics and uncertainty of the returned time_tag field. The registry therefore preserves an unapproved time-contract status, and the alignment engine continues to refuse automatic joins. No inference is made from field formatting.

