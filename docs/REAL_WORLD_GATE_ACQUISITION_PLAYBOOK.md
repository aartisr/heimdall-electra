# HEIMDALL ELECTRA real-world gate-acquisition playbook

## Purpose and truth boundary

This is the practical route from the present software foundation to a
reviewable research mission. It explains how to **obtain evidence**, approvals,
partners, and independent review for each remaining gate. It is not a promise
of scientific success, launch selection, spectrum authorization, funding,
regulatory approval, or an award. A negative result, redesign, or stop decision
is a successful outcome when it is supported by preserved evidence.

The project currently has research-only software and contract foundations. It
has no admitted physical wake model, calibrated hardware result, observed
HEIMDALL ELECTRA measurement, debris track, flight authorization, or operational
traffic product. Do not present any repository output as one.

This playbook complements the [stage delivery ledger](STAGE_DELIVERY_LEDGER.md).
It is deliberately jurisdiction-aware rather than claiming a universal legal
checklist. Engage qualified legal, spectrum, export-control, safety, launch,
and institutional-review authorities for every jurisdiction and partner.

## The operating model: evidence before assertion

For every gate, create one controlled evidence package with these fields:

1. **Claim and decision:** exact hypothesis or capability boundary; explicit
   advance, narrow, redesign, and stop criteria.
2. **Authority:** accountable owner, independent reviewer, approval role, and
   conflict-of-interest disclosure.
3. **Inputs:** source agreement or artifact digest, calibration/configuration,
   model/build/environment identity, and evidence class.
4. **Method:** pre-registered protocol, quality controls, statistical plan,
   uncertainty treatment, and fault handling.
5. **Results:** complete positive, negative, excluded, failed, and missing
   results; raw evidence location and its integrity record.
6. **Limitations:** what was not tested, known confounders, validity range, and
   prohibited interpretations.
7. **Review outcome:** dated decision, reviewer identity/role, dissent, and
   the precise gate state affected.

Use the repository’s sealed plans, content digests, audit bundles, HIL plans,
convergence studies, relation suites, comparison suites, and stage ledger as
the internal records. For real-world evidence, add an independently governed
archive, signing/key management, access controls, retention policy, and a
reviewer who is not accountable for the result.

## Build the team and governance first

Establish a host institution or legal entity able to sign agreements, hold
insurance where needed, manage grants/contracts, accept controlled data, and
be the accountable mission operator. Appoint these distinct roles; one person
may hold more than one only with documented conflict controls:

| Role | Accountability | Independence rule |
| --- | --- | --- |
| Principal investigator | Scientific question and public claims | Cannot be sole final reviewer of their own result |
| Systems engineer | Requirements, interfaces, verification matrix, configuration control | Does not approve scientific interpretation alone |
| Science lead | Physical model, analysis protocol, uncertainty and null-result reporting | Maintains a declared conflict register |
| Instrument lead | Sensor chain, calibration, environmental test evidence | Separate acceptance witness for critical tests |
| Data steward | Source agreements, custody, access, retention, retraction handling | Cannot silently alter scientific evidence |
| Security/mission assurance lead | Threat model, key management, safe modes, incident response | May block release or test readiness |
| Independent review chair | Gate evidence and dissent record | No incentive tied to a positive result |
| Regulatory/launch counsel | Jurisdictional assessment and submissions | Gives written applicability advice, not assumptions |

Create a small external science advisory board with relevant plasma physics,
radio instrumentation, orbital debris, statistics, and mission-assurance
expertise. Publish its charter, meeting cadence, recusal process, and how
minority opinions are retained. Pay reviewers for time if needed, but never
condition compensation on a favorable conclusion.

## Gate 0 — obtain an approvable research program

### Acquire

- A host institution, accountable PI, mission assurance lead, and independent
  review charter.
- A pre-registered claims/evidence matrix: variables, confounders, sample
  sizes/power where applicable, thresholds, and stop rules.
- A requirements baseline with L0–L5 product boundaries, time/frame/unit
  conventions, security classification, retention, and release policy.
- Initial safety, cybersecurity, export-control, spectrum, privacy, and
  orbital-debris applicability assessments from the responsible authorities.
- Funding that covers negative-result publication, independent review,
  calibration, archive retention, and decommissioning—not only hardware.

### How to get it

1. Start with a 4–8 page mission concept that states the narrow, falsifiable
   measurement question and explicitly excludes maneuver authority.
2. Hold a requirements/claims workshop led by someone other than the principal
   model author. Convert every attractive statement into a measurable claim or
   remove it.
3. Ask the host’s research office, export-control office, safety office, and
   counsel for written applicability determinations. Record unknowns as risks;
   do not treat silence as approval.
4. Commission an external pre-Phase-A review. The acceptable outcome may be
   “narrow,” “redesign,” or “stop.”

### Gate-close package

Signed governance charter, requirements and traceability matrix, risk/threat
register, claim registry, data-management plan, independent-review report,
and a configuration baseline. Gate 0 remains open until an independent review
accepts the falsifiability and boundaries.

## Gate 1 — obtain defensible physics and synthetic-truth evidence

### Acquire

- A named model owner and a physical hypothesis with derivation, initial and
  boundary conditions, validity range, and explicit excluded regimes.
- At least two separately identified numerical implementations or an otherwise
  defensible independent reference method.
- Reproducible execution environments, source/binary digests, raw outputs,
  convergence studies, limiting cases/invariants, benchmark suites, and
  cross-implementation comparisons.
- Independent expert review of equations, numerics, assumptions, and results.

### How to get it

1. Partner with plasma-physics and computational-science researchers; do not
   relabel the illustrative repository forward model as a physical model.
2. Write the governing equations and nondimensional/limiting cases before
   coding. Predeclare which conservation/error checks must hold and what
   numerical change is tolerable under refinement.
3. Implement behind the existing `PhysicsModel` port, submit a model-admission
   record, and keep its card at `analytic_unvalidated` until review accepts the
   evidence.
4. Have an unaffiliated group reproduce selected cases from the published
   specification or compare against a separately governed implementation.
   Record the actual independence basis; differing IDs alone are not proof.
5. Generate L0-like synthetic outputs including timing error, gaps, saturation,
   quantization, and self-noise. Preserve simulation inputs and seeds.

### Gate-close package

Model admission, model card, derivation, validity statement, source/build and
environment attestations, sealed benchmark/convergence/relation/comparison
results, raw outputs, uncertainty budget, and independent review. The result
must show a predeclared distinguishable region **and** the limitations of that
region. Otherwise narrow or stop.

## Gate 1A — obtain an independent locked synthetic corpus

### Acquire

A corpus custodian independent of detector tuning, a sealed corpus manifest,
hidden labels, scenario/seed separation, and one-time evaluation controls.

### How to get it

1. Contract a separate laboratory, university group, or internal team with a
   reporting line independent of the detector developers.
2. Give it the pre-registered scenario distribution and constraints, not the
   desired labels or a tuning target. It generates and locks data, labels, and
   manifests in access-controlled storage.
3. The detector team receives development/training material only. The custodian
   releases the validation material once under the locked-corpus process.
4. Evaluate sensitivity, false alarms, confidence intervals, completeness, and
   failure cases by declared strata. Any threshold/model change requires a new
   corpus and a new plan.

### Gate-close package

Custodian independence statement, corpus/consumption manifests, access log,
sealed plan, stratified performance report with intervals, all exclusions, and
review decision. A strong aggregate score without strata is insufficient.

## Gate 1B — obtain authentic external context and future observed sources

### Context sources

Use an authoritative provider directly, preserve raw bytes, terms, retrieval
metadata, release/version, cryptographic transport/signature evidence where
available, and a provider correction/retraction path. NOAA SWPC publishes a
data-service endpoint and identifies NCEI as the long-term archive for SWPC
products; it is useful contextual information, not debris ground truth.
[NOAA SWPC data access](https://www.swpc.noaa.gov/content/data-access)

The existing NOAA connector remains context-only until its time contract and
source approval are formally reviewed.

### Observed HEIMDALL ELECTRA sources

There is no public shortcut to authentic HEIMDALL ELECTRA observations before hardware
exists. Obtain them through an approved instrument campaign or written data
agreement. Require, at minimum:

- provider identity, legal authority, allowed purpose, classification, retention,
  redistribution, and retraction terms;
- traceable acquisition clock/timescale, sensor identity, calibration, health,
  location/attitude or their documented absence, and uncertainty;
- source-specific authentication/verification—not a checksum alone;
- preserved raw artifact and acquisition manifest, both carried into observed
  provenance; and
- an independent quality/source review before acceptance into observed class.

For any provider, begin with a non-binding technical/data questionnaire, then
negotiate a data-use agreement, security assessment, pilot transfer, byte and
time validation campaign, and acceptance review. If any link is missing, keep
the data as unapproved or context-only; never call it observed debris evidence.

## Gate 2 — obtain detector and edge-prototype evidence

### Acquire

Representative target proxies or injected signals, representative background
libraries, an emulated or candidate flight-compute platform, a measured power/
memory/latency setup, and adversarial interference tests.

### How to get it

1. Define the false-alarm budget and minimum strata before selecting a detector
   threshold. Lock both in a plan.
2. Procure or access a representative processor/emulator only after the Stage
   1 model provides justified signal and rate envelopes; otherwise label every
   result illustrative.
3. Run controlled replay and fault scenarios: overload, malformed inputs,
   missing time, storage pressure, packet duplication/loss, configuration
   mismatch, and key rotation.
4. Measure distributions, not only means: p50/p95/p99 latency, peak memory,
   energy, temperature, dropped/retained evidence, numerical differences, and
   recovery time.

### Gate-close package

Locked corpus outcome, threshold rationale, model/detector cards, raw benchmark
measurements, adversarial/fault report, resource report, and independent review
of sensitivity, false alarms, and limitations.

## Gate 3 — obtain timing, association, and localization evidence

### Acquire

At least three synchronized measurement nodes or a defensible geometry for the
specific inference question, traceable timing equipment, surveyed geometry,
attitude/ephemeris inputs where applicable, controlled truth injections, and a
blind-analysis team.

### How to get it

1. Write the time-reference design and error budget first: timescale,
   distribution, holdover, timestamp point, calibration interval, telemetry,
   and failure behavior.
2. Calibrate each node against a traceable reference and retain certificates,
   raw residuals, environmental conditions, and uncertainty.
3. Perform controlled multi-node injections across geometry, clock offsets,
   missing nodes, dispersion/environment regimes, and interference. Seal the
   association and solver policy before labels are revealed.
4. Report ambiguity sets, covariance coverage, residuals, false associations,
   rejected/retracted inferences, and all geometry strata. Association is not
   object identity.

### Gate-close package

Timing architecture, calibration evidence, geometry/ephemeris provenance,
sealed association/inference plan, raw trials, coverage and false-association
assessment, and independent review of confidence calibration.

## Gate 4 — obtain a credible demonstrator design

### Acquire

A mission concept and trade team, candidate orbit/baseline/contact assumptions,
instrument and link budgets, reliability/fault-tree analysis, cost/schedule
estimate, and a launch/operations partner dialogue.

### How to get it

1. Feed only Stage 1–3 evidence into coverage and transport models; label any
   remaining inputs as assumptions with sensitivity ranges.
2. Separate a minimum evidence demonstrator from a hypothetical operational
   constellation. Neither becomes a capability claim without validation.
3. Hold system requirements, preliminary design, and mission assurance reviews.
   Trace every mass, power, thermal, EMC, timing, downlink, and risk allocation
   to a requirement and a verification method.
4. Include end-of-life/disposal, collision avoidance, ground-station, and
   contingency concepts early; do not defer them to launch integration.

NASA’s CubeSat resources link to CubeSat design, dispenser/interface, mission
success, systems-engineering, risk-management, and orbital-debris materials.
They are useful starting references, while the mission-specific interface
control document remains controlling once a launch opportunity exists.
[NASA CSLI resources](https://www.nasa.gov/kennedy/launch-services-program/cubesat-launch-initiative/cubesat-launch-initiative-resources/)

### Gate-close package

Reviewed trade study, requirements allocation, demonstrator concept, risk-
retirement plan, verified margins, lifecycle/disposal concept, and a decision
that the evidentiary mission is feasible within stated resources.

## Gate 5 — obtain hardware-in-the-loop and laboratory evidence

### Acquire

Calibrated engineering models, traceable signal and time references, suitable
test facilities, witnessable procedures, configuration control, and raw
instrument outputs.

### How to get it

1. Freeze the measurement-chain architecture and write acceptance procedures
   before running tests. Use the repository HIL plan/result contract, but keep
   actual laboratory records in the controlled test system.
2. Select laboratories for the needed ranges and accreditation/traceability
   requirements. Obtain written capability statements, schedules, safety rules,
   calibration status, and data-delivery terms.
3. Run characterization first: transfer function, amplitude/phase, cross-axis
   coupling, dynamic range, self-noise, timing/latency, power, and storage.
4. Progress to environmental and fault campaigns only under an approved test
   readiness review: thermal-vacuum, vibration/shock, radiation as applicable,
   EMI/EMC, magnetic cleanliness, safe-mode recovery, malformed data, time loss,
   and key rotation.
5. Replay untouched raw outputs through the production-intended edge/ground
   path. Record discrepancies and bounded uncertainty; never tune away an
   inconvenient discrepancy without a new configuration and review.

NASA’s CubeSat guidance explains that launch/interface requirements ultimately
drive environmental verification and that mission integrators supply the
mission-specific rule set. [CubeSat 101](https://www.nasa.gov/wp-content/uploads/2017/03/nasa_csli_cubesat_101_508.pdf)

### Gate-close package

Approved procedures, test-readiness review, certificates, raw outputs,
environmental/fault reports, nonconformance dispositions, calibration and
acceptance records, replay comparison, margins, and independent review.

## Gate 6 — obtain authorization and independent flight validation

### Acquire

A selected launch/mission partner, mission-specific interface requirements,
appropriate spectrum and operational authorizations, ground operations,
in-orbit calibration plan, independent reference-data agreements, and a blind
science campaign.

### How to get it

1. Choose the path that fits the accountable organization and mission. In the
   United States, NASA’s CubeSat Launch Initiative offers opportunities to U.S.
   educational institutions and nonprofits and issues detailed instructions in
   its annual opportunity announcement; selection is competitive and not an
   entitlement. [NASA CSLI introduction](https://www.nasa.gov/cubesat-launch-initiative-introduction/)
2. In parallel, engage a launch integrator or other lawful launch path early.
   Obtain the actual mission ICD, schedule, environmental levels, deliverable
   list, safety reviews, and operations interfaces; generic standards do not
   replace them.
3. Obtain written spectrum/regulatory applicability advice for every ground and
   space transmitter/receiver, frequency, jurisdiction, and test location.
   For U.S. Experimental Radio Service operations, station authorization is
   required where the rules apply; orbital-debris or proprietary conditions can
   require a conventional rather than program authorization. Consult the FCC
   and qualified counsel rather than assuming an exemption.
   [FCC Experimental Radio Service rules](https://docs.fcc.gov/public/attachments/FCC-13-15A1_Rcd.pdf)
4. Establish independent reference-data and red-team agreements before launch.
   Pre-register exclusions, discovery/confirmation split, candidate matching,
   alternative explanations, and publication/null-result commitments.
5. Commission slowly: health, time, calibration, interference, and completeness
   first; science claims only after campaign evidence passes the sealed protocol.

### Gate-close package

Authorized mission and operations records, regulatory decisions, launch
integration evidence, in-orbit calibration/health records, preserved L0 data,
blind campaign report, independent-reference/red-team findings, retractions,
and independent scientific review. The evidence may support only the precise
claim earned in its tested conditions.

## Gate 7 — obtain a governed research/traffic platform

Do not build an operational advisory service merely because a web console
exists. First obtain validated L3/L4 evidence and an explicit safety-authority
decision about permitted outputs.

Then acquire a mission-grade security and operations environment: independently
scalable services, immutable or object-lock evidence storage, managed keys,
strong identity/authorization, backup/restore testing, incident response,
capacity/load tests, consumer contracts, standards/partner agreements, and
release/retraction governance. Every product must remain traceable to raw
evidence, model/configuration, uncertainty, reviewer decision, and validity
period. No product path may issue spacecraft commands.

## Gate 8 — obtain validated analyst/operator experience

Use the current TanStack console as a read-only research prototype only. To
advance, obtain an authenticated server-side API; role definitions; privacy/
data classification review; accessibility assessment; representative user
studies; and load/security testing with realistic catalogs and failure modes.

Test whether users accurately distinguish signal, candidate, association,
inference, independently validated conclusion, and released advisory. Measure
task error, time, stale-data comprehension, accessibility, keyboard operation,
and performance. Treat misunderstanding of uncertainty as a release-blocking
defect, not a training inconvenience.

## Gate 9 — obtain continuous-assurance evidence

Before any sustained operation, establish a signed and rollback-tested release
process; SBOM and dependency/vulnerability handling; monitoring for timing,
calibration, interference, model/data drift, security, latency, completeness,
and false alarms; access reviews; key rotation; backup/restore and disaster
recovery exercises; incident postmortems; and periodic independent science,
security, and safety reviews.

Each incident must create a tracked corrective action with owner, due date,
verification, and closure review. Reprocessing must create versioned products
and supersession/retraction records rather than overwrite history.

## Acquisition sequence and funding strategy

Pursue evidence in dependency order, not in the order that looks most
impressive publicly:

1. Governance and funded Phase-A/Stage-1 modeling work.
2. Independent model review and locked synthetic corpus.
3. Detector/edge and timing/association evidence.
4. Demonstrator trade, laboratory/HIL evidence, and mission authorization.
5. Flight demonstration and independent science validation.
6. Only then governed product, analyst experience, and continuous operations.

Fund each phase with a separately costed evidence package. A credible proposal
budgets independent review, calibration, test facilities, raw-data retention,
security, negative-result dissemination, and decommissioning. It does not use
an award aspiration as a requirement or a success metric.

Potential routes include university research programs, national-laboratory or
space-agency collaborations, mission/technology demonstration opportunities,
competitive grants, and contracted laboratories. Evaluate every prospective
partner for complementary expertise, data/measurement authority, conflict
controls, security maturity, and willingness to publish null results.

## Review cadence and stop rules

Hold a formal gate review after every material evidence package. The review
must choose one: `advance`, `narrow`, `redesign`, `repeat with a new plan`, or
`stop`. Stop or narrow when the signal is not distinguishable in the declared
region, false associations exceed budget, uncertainty coverage fails, model-to-
hardware differences remain unexplained, source authenticity/time provenance is
incomplete, margins are not credible, or independent reviewers identify a more
plausible explanation.

Scientific credibility comes from making these outcomes visible—not from
declaring a project infallible or award-worthy.
