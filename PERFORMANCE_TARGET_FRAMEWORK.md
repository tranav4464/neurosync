# NeuroSync 85% Performance-Target Framework

## Purpose

The project target is **not** “make one reported accuracy number exceed 85%.” A BCI can manufacture a high accepted-output accuracy by refusing almost every difficult trial. It can also create high coverage by accepting unsafe letters. NeuroSync must pass every gate below on a pre-registered, held-out session.

## Primary deployment gate

For the candidate 4–6-channel dry or semi-dry system, measured per participant and then summarized across participants:

| Gate | Required value | Why it exists |
|---|---:|---|
| Correct accepted-output rate | **≥ 0.85** | At least 85 of 100 intended selections become correct usable outputs. This is the primary 85% target. |
| Wrong accepted-output rate | **≤ 0.05** | Wrong communication is more harmful than a request to repeat. |
| Coverage | **≥ 0.90** | Prevents passing by abstaining on difficult trials. |
| Accepted-output accuracy | **≥ 0.90** | Ensures the accepted outputs themselves are highly reliable. |
| Median repetitions | **≤ pre-specified budget** | Makes the speed burden visible; proposed starting budget: 12 repetitions. |
| Wet-reference comparison | Lower 95% CI of dry-minus-wet correct-accept difference ≥ pre-registered margin | Tests the headline “near wet performance” claim fairly. |
| Safety | No forced output after `RESEAT_HEADSET`; measured error/recovery logs retained | Protects users during contact failure. |

The 0.85 correct-accepted-output gate is deliberately stricter than “85% accuracy among accepted trials.”

## The adaptive recovery framework

```text
Calibrate → choose 4–6 stable posterior/central channels → collect flashes
     │
     ├─ Contact bad for two repetitions → RESEAT_HEADSET; do not classify
     │
     ├─ Good contact + confident/stable evidence → ACCEPT
     │
     ├─ Good contact + weak evidence at the initial budget → collect a
     │  limited extra block; re-evaluate
     │
     └─ Evidence still weak at the maximum budget → REPEAT / fallback AAC
```

The initial and maximum repetition budgets must be selected **from training-only cross-validation**. Test-session labels may never be used to choose them.

## Algorithm work packages

### A. Signal and hardware quality (highest priority)

1. Use a comfortable custom-fit **semi-dry or actively stabilized dry** candidate; do not assume a passive dry electrode can meet the target.
2. Log impedance/contact pressure and amplifier saturation, then use those physical measurements with the EEG quality gate.
3. Optimize the 4–6 locations per session from a posterior/central candidate pool, while evaluating stability across sessions.
4. Improve timing: hardware event markers, packet-loss logging, and verified stimulus-to-EEG latency.

### B. Signal extraction comparison (no winner declared in advance)

Evaluate each method on identical participant/session splits:

1. Current transparent baseline: filtered waveform + pooled early/peak/late P300 features + regularized LDA.
2. SWLDA baseline.
3. xDAWN spatial filtering + LDA.
4. Riemannian covariance/tangent-space classifier.
5. A compact ensemble only if it improves held-out correct acceptance without violating false-accept or latency gates.

### C. Evidence and safety policy

1. Calibrate confidence/margin/repeat thresholds using out-of-fold training data.
2. Use sequential evidence only up to a pre-specified maximum budget.
3. Report a selective-risk curve: correct accepted outputs, wrong accepted outputs, coverage, and repetitions at every operating point.
4. Require an explicit fallback communication path after `REPEAT` or `RESEAT_HEADSET`.

## Current evidence against the target

All values below are synthetic software stress-test results, not human evidence.

| Protocol | Accepted-output accuracy | Correct accepted-output rate | Wrong accepted-output rate | Result |
|---|---:|---:|---:|---|
| Six repetitions, eight seeds | 64.7% | 19.3% | 9.9% | Fails every deployment gate |
| Eighteen repetitions, preliminary two seeds | 83.3% | 60.4% | 14.6% | Near 85% accepted accuracy, but not the primary 85% target and unsafe |
| Twenty-four repetitions, preliminary two seeds | 78.0% | 75.0% | 20.8% | More coverage, unacceptable wrong-output rate |

**Conclusion:** evidence accumulation helps, but repetition alone cannot meet the target. The bottleneck is low-SNR/contact quality plus classifier transfer. The next valid work is to test the signal/hardware and comparator work packages on public recordings, then on a properly approved wet-versus-candidate study.

## Claim language for Milestone 3

> NeuroSync's target is a 4–6-channel comfortable dry/semi-dry P300 system with at least 85% correct accepted outputs, at least 90% coverage, and no more than 5% wrong accepted outputs. The current prototype has not met this target. CASP provides a testable recovery-and-safety framework; the next phase will determine whether a semi-dry/custom-contact design plus better spatial decoding can meet the target on held-out human data.
