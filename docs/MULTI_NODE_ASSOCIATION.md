# Multi-node candidate association

## Purpose

The first Stage 3 contract forms a transparent association of time-stamped candidates from distinct nodes. It uses explicit integer nanosecond time tags with a declared time scale—not a microsecond-resolution datetime. It requires a predeclared minimum node count, candidate-score floor, evidence-class consistency, time-scale consistency, and uncertainty-expanded timing bound. The association preserves candidate IDs, node IDs, evidence class, and the observed timing/uncertainty envelope.

## Deliberate limit

An association is not a TDOA/FDOA inversion, position estimate, velocity estimate, object identity, debris track, or collision assessment. It contains no propagation model, ephemeris, attitude, baseline geometry, dispersion model, covariance inference, or false-coincidence model. Those capabilities require separately reviewed scientific and timing evidence.

## Progression

Before a localization solver is admitted, the project needs a time-reference architecture, verified cross-node timing calibration, a pre-registered association false-coincidence study, and an uncertainty-aware solver validation plan. The timing-certificate contract applies an integer nanosecond offset only when its node, time scale, and validity interval match, then combines reported and certificate standard uncertainties. The association assessment requires separately stratified true- and false-association cases and applies conservative confidence bounds to both recall and false coincidence. Mixed synthetic/observed evidence is rejected so development fixtures cannot silently support an observed association.
