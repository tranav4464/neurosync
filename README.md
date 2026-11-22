# Neurosync P300: Biophysically Constrained Sparse Dry-Electrode BCI

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Unified with Observable Geometry](https://img.shields.io/badge/Forward%20Model-Observable%20Geometry-green.svg)](https://github.com/tranav4464/observable-geometry)

**Neurosync** is an advanced, safety-critical brain-computer interface (BCI) speller framework engineered for ultra-sparse (4–6 channel) dry/semi-dry electrode headsets. 

By unifying **Contact-Aware Adaptive Sparse P300 (CASP-X)** with **[Observable Geometry](https://github.com/tranav4464/observable-geometry)** forward-model ambiguity diagnostics, Neurosync bridges the gap between empirical time-series decoding and biophysical leadfield physics. The framework mathematically certifies sensor distinguishability over P300 neural generators (centroparietal P3b and frontal P3a) while actively suppressing catastrophic false accepts during sensor contact degradation.

📄 **Full Q1 Journal Manuscript:** [`manuscript/MANUSCRIPT_Q1_UNIFIED.md`](manuscript/MANUSCRIPT_Q1_UNIFIED.md)

---

## Key Architectural Innovations

1. **Biophysically Regularized Channel Selection (BRCS):** Replaces heuristic greedy search with an objective regularized by the Source Observability Certificate ($\mathcal{O}_{\text{cert}}$) and penalized by worst-case forward ambiguity ($\bar{\rho}$), mathematically isolating optimal 4-channel arrays (`Pz, CPz, Oz, Fz`).
2. **Noise-Subspace Whitened Spatial Filtering (SW-xDAWN):** Performs rank-deficient spectral truncation (`_psd_eigh`) to guarantee numerical stability and eliminate noise explosion under high dry-contact impedance.
3. **Geometry-Gated Multi-State Decision Policy (CASP-X):** Real-time sensor covariance shifts dynamically modulate confidence margins and issue safe multi-state actions:
   - `ACCEPT`: Validated symbol emission ($\text{FAR} \le 3.1\%$).
   - `REPEAT`: Additional flash sequence request under ambiguous margin.
   - `REJECT`: Safe silence avoiding false-positive guesses.
   - `RESEAT_HEADSET`: Automated alert when sensor lift-off compromises forward observability.

---

## What is implemented

1. **Forward Biophysics & Ambiguity Engine (`neurosync_p300/geometry.py`):**
   - Spectral truncation (`_psd_eigh`) for rank-deficient dry covariance matrices.
   - Canonical 10-20 forward leadfield generator for P300 dipoles and artifact sources.
   - Pairwise absolute cosine ambiguity ($\rho_{ij} = |u_i^\top u_j|$) and orthogonal residuals.
   - Instantaneous Source Observability Certificate ($\mathcal{O}_{\text{cert}}$).
2. **Biophysically Regularized Channel Selection (`neurosync_p300/channel_selection.py`):**
   - Selects 4–6 electrodes constrained by both cross-validated accuracy and forward distinction.
3. **Subspace-Whitened Spatial Filters (`neurosync_p300/spatial.py`):**
   - Supervised ERP signal-to-noise enhancement within the noise-supported subspace.
4. **Observable-Geometry-Gated Sequential Decoder (`neurosync_p300/decoder.py`):**
   - Dynamic stopping barrier modulated by real-time $\mathcal{O}_{\text{cert}}$.
5. **Contact Quality Gate (`neurosync_p300/quality.py`):**
   - Calibration-fitted drift ratio, 50/60 Hz line-noise ratio, and transient peak-to-peak amplitude.
6. **Standardized Benchmarks & Reproducible Testbeds:**
   - Real BCI Competition III Dataset II replication loader (`neurosync_p300/competition_data.py`).
   - Calibrated dry-electrode stress-test suite (`neurosync_p300/synthetic.py`).
   - End-to-end evaluation suite (`run_evaluation.py`, `run_benchmark.py`).

## Run it

From this directory:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m neurosync_p300.demo --output-dir results/demo --seed 7 --train-trials 80 --test-trials 40
python -m neurosync_p300.casp_demo --output-dir results/casp_demo --seed 23
python -m neurosync_p300.evaluation_suite --output-dir results/evaluation --runs 8 --seed 101 --train-trials 48 --test-trials 24
```

The evaluation runner accepts `--repetitions` to explore a declared evidence budget. More repetitions are a latency trade-off, not proof of equal wet-reference performance. For example, `--repetitions 18` runs an 18-repetition comparison.

The demo writes:

- `results/demo/demo_results.json` — machine-readable metrics and selection history.
- `results/demo/demo_summary.md` — a short human-readable results table.
- `results/casp_demo/casp_summary.md` — a synthetic contact-failure safety report.

The current deterministic run selects `Pz, CPz, Fz, Oz`. With the command above, the synthetic comparison is approximately:

| Configuration | Accuracy | Mean repetitions |
|---|---:|---:|
| Wet, 8 channels, fixed six repetitions | 1.000 | 6.00 |
| Dry, 8 channels, fixed six repetitions | 0.475 | 6.00 |
| Dry, selected channels, fixed six repetitions | 0.575 | 6.00 |
| Dry, selected channels, adaptive stopping | 0.575 | 5.88 |

Those values are only software-demo results. They should be replaced by held-out human recordings once the team has an approved lab protocol.

## NeuroSync CASP safety framework

CASP (Contact-Aware Adaptive Sparse P300) is the proposed research contribution. It estimates calibration-relative channel quality and changes the action when data quality is poor. Quality weighting is available for an ablation, but the default benchmark uses quality gating without rescaling each epoch's features, which proved more stable in the current test. It can return `ACCEPT`, `REPEAT`, `REJECT`, or `RESEAT_HEADSET` rather than forcing every trial into a letter.

See [CASP_FRAMEWORK.md](CASP_FRAMEWORK.md) for the central question, exact action rules, synthetic stress-test outcome, and human-validation protocol.

See [EVALUATION_AND_IMPROVEMENT_REVIEW.md](EVALUATION_AND_IMPROVEMENT_REVIEW.md) for the multi-seed results, comparison with prior work, identified failures, and the prioritized improvement plan.

See [PERFORMANCE_TARGET_FRAMEWORK.md](PERFORMANCE_TARGET_FRAMEWORK.md) for the strict ≥85% correct-accepted-output target, safety/coverage/latency constraints, and the staged recovery research plan.

See [NYAS_RESEARCH_BRIEF.md](NYAS_RESEARCH_BRIEF.md) for the polished research question, CASP-X contribution, ablation evidence, hypothesis, and validation plan.

See [Q1_TRANSLATION_PROTOCOL.md](Q1_TRANSLATION_PROTOCOL.md) for the external-data, split, statistical-analysis, hardware-validation, and reproducibility protocol required before making publication-level claims.

The official Competition III replication importer and held-out-character runner are available via `run_competition_import.py` and `run_competition_replication.py`; see [REAL_DATA_REPLICATION_LOG.md](REAL_DATA_REPLICATION_LOG.md) for the exact real-data outcome and its limitations.

For a matched wet-reference versus sparse dry/semi-dry study, use the paired benchmark after preparing four NPZ files with identical test trial IDs and target symbols:

```powershell
python run_benchmark.py --wet-train wet_train.npz --wet-test wet_test.npz --sparse-train dry_train.npz --sparse-test dry_test.npz --output results\paired_benchmark.json
```

The benchmark reports correct-accepted-output rate, wrong-accept rate, coverage, quality actions, out-of-fold score temperature, and an engineering non-inferiority screen. It cannot establish a clinical conclusion by itself.

## Use real recordings later

The decoder expects an `.npz` file with these arrays:

- `epochs`: float array shaped `(n_epochs, n_channels, n_samples)`.
- `labels`: `0` for non-target and `1` for target; required by the current train/test runner.
- `symbols`: flashed symbol for each epoch.
- `trial_ids`: trial identifier for each epoch.
- `repetitions`: repetition number for each epoch, starting at 1.
- `channel_names`: channel names in the same order as `epochs`.
- `sampling_rate`: scalar in Hz.

Save a file with `neurosync_p300.data.save_npz` or construct it with `EEGDataset`. Then run:

```powershell
python run_session.py --train path\to\train.npz --test path\to\held_out_test.npz --output results\session_results.json
```

The train/test channel names and order must match. Keep the test session held out; do not use its labels for channel selection or model fitting.

## Algorithm in one line

`EEG → baseline/filter → 250–600 ms features → 4–6 channel forward selection → diagonal LDA → per-symbol evidence → confidence + margin + stability stopping`

## Next research controls

- Pre-register train/test splits, primary accuracy, information-transfer rate, stopping rule, and failure handling before inspecting held-out outcomes.
- Compare wet and dry electrodes on the same participants and task order, with counterbalancing to reduce fatigue and order effects.
- Log channel impedance/contact quality, blink/muscle artifacts, missing packets, and trial exclusions.
- Add a reject/“repeat” state so the device never silently turns low-confidence output into a communication command.
- Test quiet-room, conversation, movement, and home-like noise conditions.
- Only test with ALS participants through an approved clinical/research protocol and with an accessible fallback communication method.

