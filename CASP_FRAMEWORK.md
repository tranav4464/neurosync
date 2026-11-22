# NeuroSync CASP Framework

**CASP = Contact-Aware Adaptive Sparse P300**

## Central question

> Can a low-cost, custom-fit 4–6 electrode dry or semi-dry P300 headset maintain pre-specified non-inferior accepted-output performance versus a conventional 8-channel wet reference, while reducing setup burden and safely refusing poor-quality selections?

The answer is **not known yet**. It needs a pre-registered, held-out human study. The current implementation answers the smaller engineering question: *does the decoder change its action when contact-quality metrics signal an artifact-heavy recording?*

## Why this is potentially novel

P300 spelling, sparse electrode selection, dry electrodes, and dynamic stopping are established prior art. CASP's proposed contribution is their safety-aware integration:

1. It estimates per-channel signal quality from calibration-relative low-frequency power, line-noise ratio, and transient amplitude.
2. It down-weights degraded channels instead of assuming every channel is equally useful.
3. It prevents poor-quality repetitions from accumulating evidence.
4. It uses confidence, top-two margin, symbol stability, maximum burden, and quality together.
5. It produces an explicit action, not merely a predicted character.

The novelty claim is falsifiable: contact-aware adaptation must preserve or improve **accepted-output** accuracy and reduce unsafe outputs on held-out data without an unacceptable loss of coverage or user burden.

## Architecture

```text
EEG + synchronized flash markers
  ├─ channel/contact-quality metrics
  │    ├─ low-frequency drift ratio
  │    ├─ line-noise ratio
  │    └─ transient peak-to-peak amplitude
  ├─ baseline correction + 0.5–20 Hz band-limit
  ├─ 250–600 ms P300 features
  ├─ training-only 4–6 channel selection
  ├─ channel-quality feature weighting
  ├─ target/non-target diagonal LDA baseline
  ├─ sequential per-symbol evidence
  └─ safety decision
       ├─ ACCEPT
       ├─ REPEAT
       ├─ REJECT
       └─ RESEAT_HEADSET
```

## Decision policy

| Action | Meaning | Current rule |
|---|---|---|
| `ACCEPT` | Output the highest-evidence character | Quality is adequate; confidence, top-two margin, and stability all pass. |
| `REPEAT` | Collect a fresh attempt | Quality is acceptable but evidence is insufficient by the repetition limit. |
| `REJECT` | Do not infer an intended character | Quality is acceptable but confidence is near chance. This requires a future true no-intent calibration study. |
| `RESEAT_HEADSET` | Pause and fix the headset/contact | Multiple repetitions have low aggregate channel quality. |

The current `REJECT` rule is an engineering placeholder. A real no-intent classifier must be trained and evaluated before it becomes a clinical control.

## What the code implements

| Component | File | Current capability |
|---|---|---|
| Signal-quality gate | `neurosync_p300/quality.py` | Learns calibration-relative quality and provides per-channel weights. |
| Sparse selection | `neurosync_p300/channel_selection.py` | Trial-level cross-validated 4–6 channel forward selection. |
| Baseline decoder | `neurosync_p300/model.py` | Interpretable regularized diagonal LDA. |
| Safe sequential decoder | `neurosync_p300/decoder.py` | Evidence accumulation plus action state. |
| End-to-end session path | `neurosync_p300/session.py` | Training-only selection, quality fitting, held-out decoding. |
| Stress test | `neurosync_p300/casp_demo.py` | Synthetic cap-failure simulation and action metrics. |

## Reproducible engineering result

Run:

```powershell
python -m unittest discover -s tests -v
python -m neurosync_p300.casp_demo --output-dir results/casp_demo --seed 23
```

The current deterministic synthetic stress test injects whole-cap artifacts into approximately 22% of dry-electrode trials. It reports:

| Configuration | Overall accuracy | Accepted-output accuracy | Coverage | Re-seat rate |
|---|---:|---:|---:|---:|
| Ordinary sparse decoder on corrupted dry data | 0.450 | 0.333 | 0.450 | 0.000 |
| CASP on corrupted dry data | 0.450 | 1.000 | 0.125 | 0.225 |
| CASP on clean dry data | 0.500 | 0.857 | 0.175 | 0.000 |

This result shows a **safety–coverage trade-off**: CASP is more selective, so its accepted outputs are more accurate in this synthetic test, but it accepts fewer trials. It does **not** show that CASP is better overall, that it is ready for ALS users, or that it matches a wet system.

## Experiment that can answer the central question

1. Use a conventional 8-channel wet P300 system as the reference.
2. Test the same participants with wet and 4–6 channel dry/semi-dry conditions in counterbalanced order.
3. Freeze the visual paradigm, classifier family, quality thresholds, and non-inferiority margin before test outcomes are viewed.
4. Select channels and tune thresholds using training data only; test on a later session.
5. Include quiet, mild-noise, movement, long-session, and no-intent conditions.
6. Report accuracy, selective risk, coverage, false activation, repetitions, setup time, comfort, fatigue, contact stability, and cost.
7. Only then conduct an approved ALS/clinical collaboration with a fallback communication method.

## Claim boundary

NeuroSync may currently claim a reproducible research framework and synthetic safety stress test. It may not claim equal wet/dry accuracy, low-cost hardware performance, clinical benefit, or ALS usability until those outcomes are measured.

