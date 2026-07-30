# Locked-corpus custody

## Current status

The current synthetic registry 0.2.0 is **consumed demonstration data**. Its scenarios and expected outcomes live in the project repository and have already informed development. It cannot honestly be called a fresh locked corpus or independent validation evidence.

## Future corpus requirements

A valid locked corpus must be:

1. created by or delivered to an independent custodian;
2. withheld from detector/model/gate developers until a plan is sealed;
3. versioned with scenario-manifest digests, registry version, and custody reference;
4. marked fresh and independently held;
5. consumed exactly once by the corpus-consumption ledger;
6. followed by a new corpus before any post-result tuning.

The code enforces the final two requirements for a declared fresh independent corpus. It cannot prove the human/organizational independence assertion; that requires documented custody and review.

## Prohibited practice

Do not reuse the current repository fixtures as locked validation, change a threshold after seeing a locked result, or re-run a consumed corpus until a preferred score appears.

