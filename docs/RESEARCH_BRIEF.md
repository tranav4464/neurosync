# NeuroSync CASP-X: Research Brief for NYAS Junior Work

## Project question

**Can a custom-fit, low-cost 4–6-electrode dry/semi-dry P300 headset provide safe, high-quality communication that approaches an 8-channel wet reference, while explicitly detecting poor contact rather than forcing incorrect outputs?**

## Why this is worth studying

Conventional wet EEG is a strong reference but involves gel, setup time, cleaning, and expert assistance. A dry system could lower those burdens, yet weak or unstable contact can cause a communication device to output a wrong letter. That makes “accuracy” alone an inadequate goal.

Prior studies show that dry P300 systems can be practical in some settings, while other work shows that low-quality contact and slow artifacts can create persistent dry-versus-wet gaps. xDAWN-style spatial filters, sparse SWLDA-like feature selection, and sequential evidence accumulation are established ideas; the research opportunity is to join them with explicit contact-aware safe actions and evaluate the complete system fairly. [Dry-vs-gel P300 study](https://pubmed.ncbi.nlm.nih.gov/22586362/), [dry/wet P300 and dynamic collection](https://pmc.ncbi.nlm.nih.gov/articles/PMC6378883/), [xDAWN P300 pipeline example](https://pmc.ncbi.nlm.nih.gov/articles/PMC3710229/), [P300 speller review](https://pmc.ncbi.nlm.nih.gov/articles/PMC9810759/).

## Proposed contribution: CASP-X

**CASP-X** means *Contact-Aware Sparse P300 with eXplainable recovery*. It is an integration contribution, not a claim that every component is new.

```text
Custom fit + 4–6 selected electrodes
        ↓
Contact quality / artifact signals
        ↓
P300 preprocessing → sparse channel–time features / spatial-filter ablation
        ↓
Calibrated evidence accumulation
        ↓
ACCEPT | COLLECT EXTRA EVIDENCE | REPEAT | RESEAT HEADSET | fallback AAC
```

### Novel, testable part

The system does not just predict a symbol. It jointly decides whether the signal is good enough to communicate, whether to collect a limited extra evidence block, or whether physical contact should be fixed. Every decision is evaluated by correct usable output, wrong usable output, coverage, and burden.

## Falsifiable hypothesis

With participant-specific channel selection, reliable semi-dry/custom contact, and a training-only calibrated CASP-X policy, the candidate system will attain:

- at least 85% correct accepted outputs;
- at most 5% wrong accepted outputs;
- at least 90% coverage; and
- no more than a pre-registered loss from a counterbalanced wet reference.

The hypothesis is **not currently supported**. It is deliberately falsifiable.

## What has been implemented

1. Baseline correction and band-limited P300 preprocessing.
2. Training-only 4–6 channel forward selection.
3. Sampled waveform plus early/peak/late pooled P300 features.
4. Interpretable regularized LDA baseline.
5. Training-only sparse channel–time feature selector, inspired by the sparsity goal of SWLDA.
6. A supervised, regularized spatial-filter ablation inspired by xDAWN-family ERP enhancement.
7. Symbol evidence accumulation and out-of-fold decision calibration.
8. Contact-quality gating and `ACCEPT`, `REPEAT`, `REJECT`, and `RESEAT_HEADSET` actions.
9. Matched wet-reference benchmark and explicit non-inferiority screen.
10. Deterministic synthetic stress tests plus automated software tests (currently 26).

## Algorithm ablation record

All results below are synthetic engineering screens. They are not results from people, patients, or a headset.

| Candidate at 6 repetitions | Seeds | Correct accepted outputs | Wrong accepted outputs | Interpretation |
|---|---:|---:|---:|---|
| CASP pooled-feature baseline | 8 | 19.3% | 9.9% | Too weak for target; establishes baseline. |
| CASP + spatial-filter ablation | 4 | 20.8% | 8.3% | Small safety/correctness gain. |
| CASP + sparse 48-feature ablation | 4 | 22.9% | 9.4% | Best six-repetition algorithm screen so far; still fails target. |

At 18 repetitions, both baseline and sparse-feature preliminary two-seed screens produced 83.3% accepted-output accuracy, but only 58–60% correct accepted outputs and 14.6% wrong accepted outputs. This fails the safety/coverage target. More repetitions alone are therefore not the answer.

## Research plan that can genuinely change the result

### Phase 1 — public data reproduction

Reproduce LDA/SWLDA/xDAWN+LDA/geometry-based baselines on one public P300 dataset with subject-wise and session-wise held-out splits. Select the method by correct accepted outputs and safety, not flash-level accuracy.

### Phase 2 — hardware-contact study

Build one candidate 4–6 electrode posterior/central layout and one 8-channel wet reference. For each participant, counterbalance wet/candidate order and record contact impedance, pressure/fit notes, setup time, marker latency, packet loss, and comfort.

### Phase 3 — closed-loop evaluation

Pre-register the primary gate, false-accept limit, repetition budget, fallback procedure, and wet-reference margin. Test quiet, mild movement, and home-like noise conditions. Use a fallback AAC path for every low-confidence decision.

### Phase 4 — ALS co-design only with appropriate approval

Work with an AAC/ALS clinician, approved protocol, and participant-accessible consent materials. Never make the prototype the only communication channel.

## What success would mean

Success is not “the model printed 85%.” It is a held-out, reproducible result showing that a comfortable sparse headset can deliver ≥85 correct usable selections per 100 intended selections with low wrong-output risk and tolerable communication burden.

## Current conclusion

CASP-X is a strong, testable research framework with a real safety contribution. The current software evidence does **not** show wet-equivalent performance. The next credible lever is improved signal acquisition and evaluation on public/real EEG—not more hidden tuning of the synthetic benchmark.
