# NeuroSync — Milestone 3 Submission Snapshot

## Project vision

NeuroSync is developing a safer, more accessible P300 brain–computer-interface research framework for people with severe motor impairment, including potential future AAC applications for ALS. Our long-term goal is a comfortable, low-cost 4–6 electrode dry or semi-dry headset that approaches a conventional wet-EEG reference without forcing unreliable communication outputs.

## Central research question

> Can a custom-fit 4–6 electrode P300 headset achieve at least 85% correct usable selections while maintaining low wrong-output risk, reasonable setup burden, and transparent recovery when electrode contact is poor?

## Our proposed solution: CASP-X

**CASP-X** (*Contact-Aware Sparse P300 with eXplainable recovery*) combines:

- data-driven selection of 4–6 informative posterior/central electrodes;
- P300 waveform and pooled temporal features;
- sparse channel–time feature and spatial-filter ablations;
- confidence-calibrated evidence accumulation;
- explicit `ACCEPT`, `REPEAT`, `REJECT`, and `RESEAT_HEADSET` outcomes; and
- a fallback communication path when confidence or contact quality is insufficient.

The key idea is that a communication BCI should not merely produce a predicted letter. It must decide whether the data are reliable enough for a user-facing action.

## What we built and tested

The repository includes a runnable research prototype with preprocessing, compact-channel selection, regularized LDA, P300 feature extraction, decision calibration, contact-quality checks, synthetic dry/wet stress testing, and an official P300 Competition data importer.

We also built a matched wet-reference evaluation framework that measures:

- correct accepted-output rate;
- wrong accepted-output rate;
- coverage and repeats;
- headset re-seat actions; and
- repetitions/latency burden.

## Honest results and lessons

Our synthetic stress tests show that safety gating can reduce unsafe accepted outputs during simulated bad contact, but the current sparse dry algorithm does **not** yet meet wet-reference performance. A real-data replication on a public P300 benchmark similarly shows that the lightweight baseline needs improvement before any strong performance claim.

This is an important result: reliability and contact quality are the central engineering gap, not just the number of electrodes. We are therefore treating the current prototype as a testable research platform—not a medical device or finished communication system.

## Next steps

1. Reproduce validated SWLDA and xDAWN+LDA baselines on public P300 data.
2. Compare 4, 5, 6, and 8 channels with held-out participant/session splits.
3. Test semi-dry/custom-fit contact designs with impedance/contact-quality logging.
4. Pre-register the ≥85% correct-output, ≤5% wrong-output, coverage, and latency criteria.
5. Conduct a counterbalanced wet-versus-candidate study with appropriate ethical approval and accessible fallback communication.

## Why it matters

A lower-burden BCI could reduce setup and comfort barriers for people who need assistive communication. Equally, low accuracy can create fatigue, confusion, and unsafe communication. NeuroSync’s contribution is to make that trade-off visible and measurable, so comfort never comes at the cost of silently wrong output.

## Evidence boundary

This is engineering and research software. It is not clinical evidence, a medical device, or evidence of performance in ALS users. The project’s strength is a transparent, reproducible path to test the idea responsibly.
