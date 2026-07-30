# Detector performance assessment

## Purpose

Detector performance must be assessed separately for each predeclared stratum—not with aggregate accuracy. The assessment contract calculates Wilson confidence intervals for detection probability on positive cases and false-alarm probability on negative cases. A criterion specifies minimum positive/negative trial counts, the minimum lower bound for detection probability, and the maximum upper bound for false-alarm probability.

## Evidence boundary

Every assessment records the workload digest, detector configuration digest, criterion digest, and stratum. It fails when the sample counts are insufficient, even if the observed point estimate appears favorable. Passing only means the supplied labeled workload meets the declared statistical criterion; it does not establish physical validity, independence of the corpus, laboratory performance, or flight sensitivity.

## Required use

Future Stage 2 criteria must be sealed before evaluation and paired with an independently held corpus where a result will affect a scientific claim. Use the locked-corpus custody and audit-bundle controls to preserve the complete basis for review.
