# Neurosync P300 Speller Prototype

This folder is a runnable research prototype for Team Neurosync's Milestone 3 concept: a low-channel P300 speller designed around a comfortable headset, noise-aware preprocessing, data-driven electrode selection, and adaptive stopping.

It is an engineering prototype, not a medical device and not evidence of performance in ALS participants. The included demo uses synthetic EEG with a known target so the full software path can be tested before lab access.

## What is implemented

1. Baseline correction followed by a 0.5–20 Hz frequency-domain filter.
2. A 250–600 ms P300 feature window with configurable downsampling.
3. Forward channel selection with trial-level cross-validation, constrained to 4–6 electrodes.
4. Regularized diagonal LDA for target versus non-target flashes.
5. Symbol-level evidence accumulation across repetitions.
6. Conservative adaptive stopping using confidence, top-two margin, and consecutive-symbol stability.
7. A synthetic wet/dry electrode simulator and a reproducible comparison report.
8. An NPZ interchange format and an end-to-end held-out-session runner for future EEG recordings.
9. NeuroSync CASP: contact-quality gating (with optional quality weighting) and safe `ACCEPT` / `REPEAT` / `REJECT` / `RESEAT_HEADSET` decisions.

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
- `results/casp_demo/casp_summary.md` — a simulated contact-failure safety report.

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

