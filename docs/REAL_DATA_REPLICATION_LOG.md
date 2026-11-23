# BCI Competition III Dataset II Replication Log

> Historical baseline log. The later spatiotemporal shrinkage-LDA benchmark improved the same held-out Subject A split to 36% with six channels and 60% with eight channels, and obtained 76%/88% on Subject B. The primary locked confirmation result is now the multi-participant [BNCI 2014-008 benchmark](PUBLIC_DATA_BENCHMARK.md). This file is retained to document the algorithmic progression rather than silently replacing the earlier result.

## Purpose

This log moves NeuroSync beyond synthetic EEG. It records a reproducible, within-subject held-out-character replication on the official BCI Competition III Dataset II ASCII files. It is **not** a dry-electrode, ALS, clinical, or wet-reference result.

## Source and protocol

- Dataset: [BCI Competition III Dataset II — Wadsworth P300](https://www.bbci.de/competition/iii/desc_II.pdf).
- Subject: A, labelled official training file only.
- Original acquisition: 64 channels, 240 Hz, 6×6 row/column P300 task, 15 intensifications per row/column.
- Sparse replication montage: `Fz, Cz, CPz, Pz, POz, Oz, P3, P4` (eight available posterior/central channels).
- Import result: 15,130 valid flash epochs from 85 character selections. Boundary flashes without a complete pre/post epoch were excluded deterministically.
- Evaluation: 60 training character epochs and 25 randomly selected held-out character epochs (`seed=7`). Every learned operation uses training characters only.
- Decoder: row/column evidence is aggregated separately, then intersected in the official 6×6 symbol matrix.

## Results

| Configuration | Channels | Feature policy | Held-out flash balanced accuracy | Held-out character accuracy |
|---|---:|---|---:|---:|
| Compact LDA baseline | 4 data-selected | waveform + pooled P300 features | 54.3% | 16.0% |
| Sparse-feature ablation | 8 | 60 training-selected channel–time features | 55.7% | 16.0% |

Exact reports:

- [Compact baseline JSON](results/competition_iii_replication_subject_a.json)
- [8-channel sparse-feature JSON](results/competition_iii_subject_a_8ch_sparse60.json)

## Interpretation

This lightweight implementation does not yet reproduce the high-performance published P300 pipelines. The difference is expected: published systems commonly use the full competition montage, task-specific SWLDA/xDAWN implementations, carefully tuned epoch representation, and different validation protocols. A 16% character result should be treated as an **honest baseline failure**, not evidence against P300 BCIs or a sparse headset.

## What this adds to the project

1. The project now imports and processes real, event-coded P300 EEG with only the intended sparse candidate channels loaded into memory.
2. It evaluates full spelled characters on held-out trials rather than reporting only flash-level classification.
3. It exposes an algorithmic gap that can be addressed openly: exact SWLDA reproduction, full xDAWN+LDA reproduction, and an independent public-data test must be added before any performance claim.
4. The original files, converter, random seed, channel list, trial split, and output predictions are recorded, making failure analysis reproducible.

## Next replication milestones

1. Reproduce an exact published SWLDA baseline using a validated implementation and state its feature-entry/removal policy.
2. Reproduce xDAWN+LDA with the documented full-montage protocol before constraining to 4–6 channels.
3. Verify the imported epoch/event alignment against the official MATLAB example output.
4. Repeat across Subject B and an external P300 dataset, locking all settings before external evaluation.
5. Only then test whether a 4–6 channel selection retains the best full-montage system's character accuracy.
