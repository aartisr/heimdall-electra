# Detection governance

## Raw score is not a detection

The detector produces a raw, reproducible matched-filter score. It becomes a candidate detection only when the score crosses its threshold and every configured candidate gate passes. A gate must never alter or erase the raw score.

## Plug-in gate contract

Candidate gates implement a narrow Strategy port: they receive a detector context and return a gate ID, pass/fail result, human-readable reason, and numeric metrics. Gates can be composed without changing detector code. This is a Pipeline plus Strategy design: detector scoring, acceptance policy, and final product construction remain separate.

## Current synthetic gate

PeakContrastGate rejects a fixture whose matched-filter response remains nearly constant over time, such as a same-frequency continuous-tone interference case. Its current 1.75 peak-to-mean threshold was chosen only to demonstrate a transparent interface against synthetic fixtures.

It is not calibrated for plasma data, hardware data, or flight telemetry. It must be tuned only through a pre-registered experiment using a fresh locked validation corpus and must report false rejection and false acceptance by environment/stratum.

## Required release behavior

- Preserve raw score, threshold, every gate ID, every metric, and rejection reason.
- Treat a rejected high-score item as a false-positive-risk investigation, not deleted noise.
- Version and sign all gate configurations.
- Keep gate evaluation independent from labels in locked or blind datasets.
- Do not add a learned gate until this transparent baseline is independently evaluated.
