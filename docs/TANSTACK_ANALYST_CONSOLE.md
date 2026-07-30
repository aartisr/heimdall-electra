# TanStack Research Evidence Console

## Purpose

The analyst console is a read-only transparency surface for research status, evidence classes, source limits, and stage-gate state. It is intentionally not an orbital-traffic display, candidate tracker, command console, or system of record.

## TanStack architecture

- TanStack Router provides typed route composition and is ready for future role-scoped routes.
- TanStack Query manages the read-only research-status resource and its freshness/retry policy.
- TanStack Table renders source metadata from declared columns rather than ad hoc table markup.
- Future TanStack Form workflows must be limited to governed review/approval proposals; the server repeats authorization and validation.
- Future live updates must invalidate narrowly scoped query keys and display stale/disconnected state.

## Current data boundary

The UI reads a static fixture in public/research-status.json. It is explicit about this limitation. A future read-only API must derive its response from the experiment ledger, source registry, model registry, and evidence catalog; it must not treat the browser snapshot as authoritative.

## Security boundary

No secret, command path, privileged calculation, detector logic, or model decision runs in the browser. Before a server API is added, require route-level authorization, short-lived credentials, strict CSP, safe rendering, rate limiting, audit events, and server-side policy enforcement.

