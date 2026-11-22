# NeuroSync CASP-X — Q1-Style Translation and Validation Protocol

## Status statement

This is a **protocol and reproducibility package**, not a Q1 publication claim. A Q1-level result requires actual external EEG evaluation, human-factors evidence, ethics approval where people are enrolled, and peer review. The purpose of this document is to make the next study capable of supporting a rigorous manuscript rather than another synthetic-only demo.

## Research contribution to test

CASP-X combines sparse channel selection, contact-aware safety actions, P300 feature selection/spatial-filter ablations, and bounded sequential evidence collection. The central test is whether this integrated policy improves **correct usable communication** without hiding errors through abstention.

## Dataset sequence

| Stage | Resource | Role | Split rule |
|---|---|---|---|
| Development | One public P300 dataset | Freeze preprocessing and candidate grid | Participant/session-disjoint folds; no test labels in any fit step |
| External validation | A different public P300 dataset | Evaluate generalization | No hyperparameter change after development freeze |
| Translation | Counterbalanced wet versus candidate semi-dry study | Evaluate hardware/contact hypothesis | Held-out sessions and participants; pre-registered analysis |

Recommended public data sources:

- The [BNCI 2014-008 P300 dataset](https://www.nemar.org/discover?q=P3) is compact and directly relevant: eight ALS participants and eight 10–10 electrodes, including Fz, Cz, Pz, Oz, P3, and P4.
- The [bigP3BCI dataset](https://www.physionet.org/content/bigp3bci/1.0.0/bigP3BCI-data/) provides open EDF+ recordings, event markers, multi-session structure, and where available ALS-associated metadata. Start with a small selected study/file subset rather than downloading the whole archive.
- The [BCI Competition III Dataset II description](https://www.bbci.de/competition/iii/desc_II.pdf) is a classic 6×6 P300 benchmark for reproduction only; it must not be merged blindly with another dataset because paradigm, montage, and timing differ.

## Locked comparators

Every comparator receives the same training examples, channel budget, preprocessing range, and symbol-decoding rule where technically possible.

1. **Baseline:** waveform + pooled features + regularized LDA.
2. **Sparse-feature ablation:** SWLDA-inspired training-only channel–time feature selection + LDA.
3. **Spatial-filter ablation:** xDAWN-inspired template spatial filter + LDA.
4. **CASP-X policy:** best frozen signal model + contact/reliability action policy.
5. **Wet reference:** all prespecified wet channels, same task and counterbalanced order.

No deep model is added unless it beats these baselines on the development dataset and then survives the untouched external dataset. This avoids “larger model = better paper” bias.

## Data partition and leakage controls

- Split by **participant first** for cross-participant claims; use session-held-out testing for personalization claims.
- Fit filtering references, channel selection, spatial filters, feature selection, classifier, temperature, accept threshold, and repetition budget inside each training fold only.
- Select one final configuration using development folds; lock it before external validation.
- Keep raw files immutable; save a machine-readable manifest with file checksum, participant/session ID, channels, sampling rate, event mapping, exclusions, and software commit identifier.
- Never normalize or average across a test epoch using information estimated from training-plus-test data.

## Primary and secondary endpoints

### Primary endpoint

**Correct accepted-output rate**: correct `ACCEPT` selections divided by all intended selections.

### Co-primary safety constraint

**Wrong accepted-output rate ≤5%**. A system cannot pass by becoming fast but unsafe.

### Secondary endpoints

- coverage, accepted-output accuracy, repetition count, time per selection, and information-transfer rate;
- `REPEAT`, `REJECT`, and `RESEAT_HEADSET` action rates;
- calibration reliability and selective-risk curves;
- setup time, contact/impedance stability, comfort, and cleaning burden in a hardware study;
- performance degradation under session transfer, mild movement, and home-like noise.

## Statistical analysis plan

1. Report participant-level points and aggregate median/IQR; do not present only pooled epochs.
2. Use paired, participant-stratified bootstrap confidence intervals for wet–candidate differences in correct accepted-output rate.
3. Pre-register a non-inferiority margin and false-accept constraint before viewing external/test results.
4. Report effect sizes and confidence intervals for every primary/secondary endpoint, not just p-values.
5. Report all participants, sessions, exclusions, missing recordings, failed runs, and aborted selections.
6. Conduct an error taxonomy: low confidence, bad contact, artifact, latency/marker failure, and confidently wrong output.

## Minimum reproducibility release

- anonymized configuration manifest and exact split files;
- code/environment lockfile plus deterministic run command;
- per-participant predictions and actions, not only averages;
- figure-generation script for accuracy/coverage/risk/latency curves;
- a limitations statement that distinguishes offline replay, closed-loop use, and clinical evidence.

## Hardware-study protocol sketch

Use a within-participant counterbalanced crossover: wet reference and sparse candidate completed in randomized order, with matched copy-spelling phrases and rest. Record electrode type/layout, event-marker timing, sampling rate, impedance/contact proxy, fit pressure notes, setup/removal time, and a comfort score. The candidate setup must have a fallback AAC route throughout.

## Go/no-go ladder

| Gate | Decision |
|---|---|
| Public-data implementation fails leakage audit | Fix pipeline; do not optimize models yet |
| Candidate loses to basic LDA on internal development folds | Drop that component |
| Best frozen method fails external data | Report failed generalization; revise hypothesis |
| Candidate has >5% wrong accepted outputs | Safety fail; do not proceed to communication claim |
| Candidate meets endpoint on external public data | Proceed to hardware/contact pilot |
| Hardware pilot meets pre-registered endpoint | Prepare manuscript; seek independent replication |

## Why this is materially stronger

The protocol addresses the common weaknesses of BCI papers: epoch leakage, selective reporting, accuracy without communication safety, and no session-transfer test. It also treats the low-electrode hardware question as a separate causal hypothesis rather than claiming an algorithm trained on synthetic noise proves a headset works.
