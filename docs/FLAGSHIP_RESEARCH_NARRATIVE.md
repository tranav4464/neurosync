# NeuroSync flagship research narrative

## One-sentence positioning

**NeuroSync is a reproducible boundary study of sparse P300 decoding: it shows
where personalised six-channel active EEG can match a fuller montage, where it
does not, and what a dry-headset claim must prove next.**

## Central question

Can a personalised 4--6-channel P300 communication system preserve useful,
safe performance relative to a fuller montage while reducing practical burden?

## What is genuinely established

| Evidence level | Finding | Exact boundary |
|---|---|---|
| Confirmed | Six active channels reached 92.9% held-out character accuracy on BNCI 2014-008 A02--A08, versus 93.6% with eight. | Eight active Ag/AgCl channels; ALS cohort; ten repetitions; participant-specific selection. |
| Externally tested | Six channels averaged AUC 0.724 versus 0.773 with 32 channels across all 13 bigP3BCI Study A participants. | 9x8 RD paradigm; file-disjoint recordings; event detection, not character accuracy. |
| Falsified mechanism | Leave-one-trial stability voting did not remove the external gap. | Negative control, not a final method. |
| Implemented hypothesis | Contact-aware, geometry-aware selective actions can make compact BCI safer. | Requires a measured forward model and physical dry-electrode data before any performance claim. |

## Why this is a strong research contribution

Many compact-BCI projects stop at a favourable within-dataset accuracy.
NeuroSync makes its headline claim survive a locked ALS split, then deliberately
tries to break it on a protocol-incompatible external cohort. It preserves the
failure instead of discarding it. That turns the project into a scientific map:

```text
Sparse montage works in one locked active-electrode ALS cohort
                         ↓
Sparse montage loses average AUC in an external 32-channel 9x8 paradigm
                         ↓
Simple stability voting does not recover the loss
                         ↓
Next falsifiable mechanism: measured geometry/contact or added calibration
```

## Research contribution statement

> We built NeuroSync, a reproducible sparse-P300 evaluation framework that
> separates feasibility from deployment claims. In a locked ALS cohort, six
> personalised active channels retained 92.9% held-out character accuracy,
> close to eight channels. In a complete 13-person external cohort with a
> different P300 paradigm, the same sparse policy lost 4.9 AUC points against
> 32 channels. We report that limitation, test and reject a simple
> stability-selection remedy, and provide a preregisterable path for testing
> whether measured electrode contact and forward-model geometry can close the
> gap.

## Novelty that can be defended

- **Evidence architecture:** explicit separation between demonstrated,
  externally bounded, and proposed claims.
- **Protocol-respecting transfer evaluation:** no unsupported conversion of a
  9x8 event paradigm into 6x6 spelling accuracy.
- **Failure-aware compact BCI objective:** wrong outputs, coverage, recovery,
  and burden are first-class outcomes rather than hidden beneath accuracy.
- **Mechanism discipline:** geometry/contact code is clearly labelled as a
  hypothesis until it beats strong empirical selection under ablation.

## Claims to avoid

- “Dry electrodes match wet electrodes.”
- “The system is clinically ready” or “safe for ALS communication.”
- “Six channels work universally.”
- “Geometry improved decoding,” until a measured-forward-model ablation proves it.
- “Best in the world” or “nothing better exists.”

## The next paper-quality experiment

Freeze the primary endpoint and compare, under matched held-out sessions:

1. empirical six-channel selection;
2. measured-geometry-constrained six-channel selection;
3. geometry plus measured contact-quality gate; and
4. eight-channel wet reference.

The experiment succeeds only if geometry/contact improves a predeclared
user-facing outcome (correct accepted output, wrong accepted output, coverage,
or repetitions) and shuffled-geometry controls remove that gain.
