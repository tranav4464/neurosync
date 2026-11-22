# NeuroSync CASP — Evaluation, Prior-Work Comparison, and Improvement Review

**Evaluation date:** 22 November 2026  
**Scope:** software tests and multi-seed synthetic EEG only  
**Not evidence for:** a real headset, human users, ALS participants, clinical safety, cost, or wet/dry equivalence.

## 1. What was tested

### Software integrity

The project ran ten automated tests covering:

- preprocessing shape and baseline behavior;
- LDA learning on a controlled separable signal;
- 4–6 channel selection;
- ordinary symbol evidence accumulation;
- contact-quality decline after injected artifacts;
- `RESEAT_HEADSET` on repeated low-quality repetitions;
- out-of-fold score temperature calibration;
- out-of-fold symbol-level decision calibration;
- accepted-output non-inferiority logic;
- paired wet-reference versus sparse benchmark execution.

Compilation of every Python entry point also passed.

### Multi-seed stress evaluation

The reproducible command was:

```powershell
python -m neurosync_p300.evaluation_suite --output-dir results/evaluation --runs 8 --seed 101 --train-trials 48 --test-trials 24
```

Each of the eight runs used:

- 48 synthetic training trials and 24 matched test trials;
- an 8-channel synthetic wet reference;
- a 4–6 channel synthetic dry CASP condition;
- training-only channel selection and out-of-fold decision calibration;
- a fixed six-repetition comparison for the wet/sparse non-inferiority screen;
- a separate whole-cap contact-failure stress condition on 25% of dry test trials.

## 2. Results

| Scenario | Correct-accept rate | Wrong-accept rate | Coverage | Re-seat rate |
|---|---:|---:|---:|---:|
| Wet reference | 1.000 | 0.000 | 1.000 | 0.000 |
| Sparse CASP, clean synthetic dry | 0.193 | 0.099 | 0.292 | 0.000 |
| Ordinary decoder, corrupted synthetic dry | 0.159 | 0.284 | 0.443 | 0.000 |
| CASP, corrupted synthetic dry | 0.185 | 0.102 | 0.286 | 0.250 |

The paired non-inferiority result was **0 / 8 runs**. Mean sparse-minus-wet correct-accept-rate difference was **−0.807**.

### Interpretation

1. The wet reference is intentionally easy in the current synthetic generator and should not be treated as a realistic clinical baseline.
2. The current dry generator represents a difficult low-SNR condition. Under it, the sparse CASP system is too conservative and does not meet the non-inferiority target.
3. Adding fixed early/peak/late P300 pooled features to the sampled waveform increased clean-sparse correct accepted outputs from 0.167 to **0.193** in this same protocol, but also increased wrong accepted outputs. It is retained as an interpretable feature improvement, not treated as a target match.
4. On corrupted dry data, CASP cuts wrong accepted outputs from **0.284** to **0.102**, and requests a re-seat on **25%** of trials. That is the expected safety behavior.
5. The cost is coverage: CASP accepts only **28.6%** of corrupted trials. This is not acceptable as a finished communication device.

**Bottom line:** CASP's safety gate works as a software mechanism, but the full communication system is not yet good enough. The correct conclusion is “reject/revise,” not “same accuracy as a wet headset.”

The exact per-run outputs are saved in [evaluation_results.json](results/evaluation/evaluation_results.json) and summarized in [evaluation_summary.md](results/evaluation/evaluation_summary.md).

## 3. Comparison with prior work

| Prior work | What it found | Relation to current result |
|---|---|---|
| [Throckmorton et al. — electrode-number optimization](https://pubmed.ncbi.nlm.nih.gov/25316166/) | A four-electrode posterior configuration performed without a significant prospective loss in its tested healthy cohort. | Our result does **not** refute this. The current dry synthetic model, classifier, quality gate, and test protocol are different. It shows that four channels cannot be assumed sufficient under low-SNR/contact-failure conditions. |
| [Colwell et al. — channel-selection methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC4106671/) | Channel selection can help, but poor channel sets can make the speller unusable. | Matches our finding: selection is necessary but not sufficient; selection stability and session transfer must be tested. |
| [Clements et al. — dry/wet P300 with dynamic collection](https://pmc.ncbi.nlm.nih.gov/articles/PMC6378883/) | Dynamic data collection improved dry performance but did not fully remove the dry-system gap; slow-band and transient artifacts were important. | Strong qualitative agreement. CASP detects/rejects poor-quality data, but that alone does not restore dry communication throughput. |
| [Bayesian dynamic stopping](https://pmc.ncbi.nlm.nih.gov/articles/PMC3798004/) | Sequential probability-based stopping can improve the speed/accuracy trade-off. | Our implementation needs better joint calibration of evidence, quality, and coverage; dynamic stopping cannot compensate for weak signal evidence alone. |
| [P300 speller design/evaluation review](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2022.1077717/full) | Performance depends on paradigm, stimulus design, algorithm, and evaluation metric. | Confirms that the current direct-flash synthetic task is inadequate as a final evaluation; row/column/checkerboard and user burden must be tested. |

## 4. Code and framework review

### Strengths

- Training-only forward channel selection avoids direct test-session channel leakage.
- Quality scoring is transparent: low-frequency ratio, line-noise ratio, and peak-to-peak transients are saved conceptually and can be inspected.
- The sequential decoder can abstain rather than silently forcing an output.
- The benchmark uses correct accepted outputs, not only accepted-output accuracy, so it cannot claim success by rejecting every hard trial.
- The framework separates wet-reference, sparse, ordinary-decoder, and corrupted-contact scenarios.
- The synthetic data path is deterministic through declared seeds.

### Current weaknesses

1. **Synthetic realism:** the noise/contact model is a stress generator, not a physical electrode–skin or ALS EEG model.
2. **Weak dry evidence remains:** pooled P300 features improve correct acceptance but do not close the wet-reference gap, and the accept/reject policy still needs calibration to a task-specific utility target.
3. **No true no-intent model:** `REJECT` is currently a low-confidence rule, not a validated asynchronous/no-intent classifier.
4. **No real impedance/contact sensor:** the gate infers quality from EEG; it does not replace amplifier impedance measurement or a physical pressure/contact sensor.
5. **Classifier scope:** diagonal LDA is a strong transparent baseline, but xDAWN+LDA, SWLDA, Riemannian, and compact neural baselines have not yet been compared on the same data.
6. **Stimulus scope:** the synthetic task directly flashes six symbols; it is not yet a hardware-timed row/column or checkerboard speller.
7. **No hardware truth:** there are no measured event markers, packet-loss logs, electrode positions, costed bill of materials, or comfort data.

## 5. Priority improvement plan

### P0 — required before claiming a better algorithm

1. Add a real public P300 dataset loader with verified event codes and trial/session splits.
2. Reproduce a standard fixed-repetition SWLDA/LDA baseline exactly.
3. Add xDAWN+LDA and at least one compact modern comparator.
4. Test 4, 5, 6, and 8 channels under identical splits.
5. Run calibration curves, selective-risk curves, and wrong-accept versus coverage curves.

### P1 — improve CASP without hiding the failure

1. Replace the single aggregate quality threshold with channel-specific reliability and minimum-good-channel rules.
2. Compare feature down-weighting, epoch rejection, and robust spatial filtering separately.
3. Calibrate the quality/acceptance decision to a pre-declared utility function that includes communication burden.
4. Make `REPEAT` a clear user-interface flow and measure how many repeats are tolerable.
5. Add a true no-intent dataset/condition before treating `REJECT` as a real safety control.

### P2 — hardware and human factors

1. Define an 8-channel wet reference and the exact candidate 4–6 electrode dry/semi-dry layout.
2. Record impedance, contact pressure, cap size, hair/scalp notes, setup time, and cleaning time.
3. Prototype flexible/spring-loaded or semi-dry contact options; do not pick a material solely on cost.
4. Test comfort and channel stability over long sessions, posture changes, and mild movement.
5. Publish a bill of materials, repairability plan, and per-session consumable cost before calling the design low cost.

### P3 — clinical translation

1. Co-design the task with AAC/ALS clinicians and users.
2. Pre-register the non-inferiority margin, false-accept constraint, stopping policy, and failure protocol.
3. Run a counterbalanced, held-out-session wet/dry or wet/semi-dry study.
4. Maintain a fallback communication method; never make an uncertain BCI selection the only path to communicate.

## 6. Central-question answer after evaluation

**Can the current low-channel CASP system match a normal wet system?**

**No evidence yet.** In the current hard synthetic benchmark, it did not match the wet reference (even after adding fixed pooled P300 features). It did show a useful safety behavior—fewer wrong accepted outputs and more re-seat requests during injected contact-failure stress—but its coverage was too low.

The next scientifically valid target is therefore narrower:

> Improve the correct-accept versus wrong-accept/coverage trade-off on public and then real EEG, while preserving the quality-triggered re-seat behavior.

If that target fails on held-out data, Neurosync should report the failure and consider a semi-dry, hybrid eye/EEG, or conventional wet solution instead of forcing a sparse dry-headset claim.

