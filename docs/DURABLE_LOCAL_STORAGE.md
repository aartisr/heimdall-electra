# Durable local storage controls

The local JSONL ledgers, corpus-consumption ledger, content-addressed evidence store, and audit-bundle writer use POSIX advisory sidecar locks. Appends are flushed with `fsync`; audit-bundle replacements are written to a temporary file, flushed, and atomically renamed.

These measures prevent cooperating local processes from interleaving an append or observing a partially replaced audit bundle. They also make reuse of a corrupted content-addressed object fail closed.

## Boundary

This is local process-safety, not non-repudiation or immutable retention. An actor with filesystem write access can still alter files, locks, and history. Any material scientific or operational evidence must be moved to an externally administered, access-controlled, versioned, object-locked store with managed signing keys and independent review.

The adapter intentionally requires POSIX locking. A deployment on a different platform must provide and test an equivalent storage adapter rather than silently weakening the guarantee.
