# HEIMDALL stage delivery ledger

## Authority and counting rule

This is the current implementation tracker for the ten primary stages in the
[implementation plan](HEIMDALL_IMPLEMENTATION_PLAN.md). It reconciles the
plan with the gate registry and codebase as of 2026-07-30.

A stage is **gate-complete** only when its stated exit evidence has been
independently reviewed and accepted. A repository contract, test fixture, or
synthetic demonstration is valuable implementation progress, but it is not
gate completion. This avoids turning software work into an unsupported
scientific or operational claim.

## Current ledger

| Plan stage | Foundation status | Gate status | Implemented and tracked | Still required for closure |
| --- | --- | --- | --- | --- |
| 0. Proof obligations and governance | Partial | Not gate-complete | Claim registry, provenance/evidence classes, gate review, uncertainty, source governance, audit/custody, durable local storage, and independent-project verification | Approved ConOps/requirements/risk and formal independent review of falsifiable thresholds |
| 1. Physics and synthetic-truth foundation | Partial | In progress | Synthetic L0–L2 vertical slice, scenario registry, forward-model/model-card admission boundaries, input contract, conformance, sealed benchmarks, and numerical-convergence contract | An admitted physical model with real governing equations, verification/convergence evidence, independent code comparison, and independent review |
| 2. Detection science and edge prototype | Partial | Not gate-complete | Deterministic baseline detector, sealed threshold/gate policy, stratified assessment, sensitivity controls, and edge-resource budget contracts | Realistic, independently held synthetic corpus; leakage-resistant evaluation; calibrated false-alarm/sensitivity evidence; representative compute measurements |
| 3. Timing, association, and kinematic inference | Partial | Not gate-complete | Time-quality and calibration contracts, replay defense, multi-node association foundation, false-coincidence assessment, covariance checks, solver-neutral TDOA contract, and inference lifecycle | Implemented/reviewed solver, geometry/ephemeris/attitude evidence, blind truth-matched campaigns, confidence-coverage and false-association results |
| 4. Constellation, instrument, and communications trade | Partial | Not gate-complete | Explicit coverage, instrument, and transport-budget contracts | Credible scenario inputs, actual trades, fault/reliability/cost analyses, and reviewed demonstrator concept |
| 5. Hardware-in-the-loop and laboratory validation | Partial | Not gate-complete | Sealed HIL test-plan/result contract and ingestion/calibration boundaries | Authorized calibrated test articles, traceable measurements, fault/environmental campaigns, raw results, acceptance evidence, and independent review |
| 6. Flight demonstration and independent science validation | Not started | Blocked on prior gates and external authority | Claim boundaries and source-alignment controls only | Authorized flight campaign, in-orbit calibration, blind analysis, independent references/red team, raw evidence, and scientific review |
| 7. Governed traffic-data platform | Partial | Not gate-complete | Content-addressed ingestion, manifests, durable local storage, audit bundles, lifecycle/retraction concepts, and explicit product boundaries | Validated L3/L4 evidence, independently scalable services, authorization, recovery evidence, external adapters, SLOs, and safety authority |
| 8. Analyst/operator experience (TanStack) | Partial | Not gate-complete | Read-only TanStack Router/Query/Table research-status console with explicit research-only status | Authenticated server API, role-specific workflows, live/catalog performance and accessibility evidence, security review, and validated products |
| 9. Operations and continuous assurance | Partial | Not gate-complete | Local integrity/replay/durability primitives, tests, and audit contracts | Signed release pipeline, monitoring, recovery drills, access reviews, SBOM/vulnerability practice, independent exercises, and operational governance |

## Remaining-stage count

There are **10 primary-stage gate closures remaining**. None may honestly be
marked complete today because no primary-stage exit gate has the independently
reviewed evidence it requires. The repository contains partial foundations for
nine stages; Stage 6 has not begun because it properly depends on external
scientific, hardware, and flight evidence.

The already complete `synthetic-vertical-slice` entry in
`config/research/gates.json` is a **narrow internal software milestone**, not
completion of Plan Stage 1 or any physical claim.

## Dependency-safe order from here

1. Finish the Stage 1 physics-model evidence package: model admission,
   sealed benchmark/convergence outputs, and independent review. Do not admit
   a fixture as physics-capable.
2. Build a genuinely independent, locked synthetic validation corpus and run
   the pre-registered detector assessment once.
3. Use those results to perform the Stage 2 detector/edge evidence work, then
   complete timing/association studies in Stage 3.
4. Ground Stage 4 trades in the resulting evidence. Only then pursue Stage 5
   HIL, Stage 6 flight validation, and the gated product/operations work.

Every update must identify artifact references, the evidence class, known
limitations, review authority, and the precise gate it can or cannot advance.
