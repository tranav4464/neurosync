# NeuroSync P300

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**NeuroSync** is a reproducible research framework for studying a difficult
question in P300 brain--computer interfaces (BCIs):

> Can a 4--6-channel dry or semi-dry P300 system approach an 8-channel wet
> reference **without increasing wrong outputs or hiding failures through
> excessive abstention**?

It is not a headset, a medical device, or a clinical decision aid. Its central
scientific contribution is an evidence hierarchy: it distinguishes results
that are confirmed, externally bounded, and still only proposed. The framework
makes the target measurable through correct outputs, wrong outputs, coverage,
repetitions, contact-quality actions, and held-out-session performance.

## What the evidence says now

| Status | Finding | What it does **not** show |
|---|---|---|
| Confirmed active-EEG feasibility | Six selected active channels achieved 92.9% mean held-out character accuracy on BNCI ALS participants A02–A08, versus 93.6% with eight. | Dry-electrode equivalence, home use, or clinical benefit. |
| External boundary result | Across 13 bigP3BCI Study A participants, six channels averaged event AUC 0.724 versus 0.773 with 32 channels. | A universal compact-montage claim or a 6×6 character-accuracy result. |
| Testable mechanism | NeuroSync-OG provides contact/geometry-aware selective actions. | That geometry or contact gating improves real EEG performance; this requires a measured-forward-model ablation. |

Read the concise [flagship research narrative](docs/FLAGSHIP_RESEARCH_NARRATIVE.md)
or the traceable [flagship manuscript](manuscript/FLAGSHIP_MANUSCRIPT.md).

## NeuroSync-OG: the testable mechanism layer

NeuroSync-OG combines Observable Geometry with Contact-Aware Adaptive Sparse
P300 decoding. Conventional systems ask whether a classifier is confident;
NeuroSync-OG also asks whether the signal is trustworthy and whether the
remaining electrode configuration can still distinguish target and nuisance
source signatures. It is an implemented, falsifiable mechanism layer, not a
claimed source of the current benchmark gain. It combines:

1. training-only 4--6-channel selection jointly regularized by fold stability,
   contact reliability, forward observability, and target–artifact ambiguity;
2. transparent P300 features and a regularized-LDA baseline;
3. out-of-fold calibration of evidence, confidence, and stopping thresholds;
4. geometry- and quality-weighted sequential evidence;
5. an explicit `ACCEPT`, `REPEAT`, `REJECT`, or `RESEAT_HEADSET` action rather
   than forcing every uncertain trial into a character.

The repository also contains linear-algebra tools for inspecting a **supplied,
measured** forward model. Its bundled 10--20 coefficient table is only an
illustrative montage proxy. It is not an anatomical BEM/FEM model and cannot
certify source separation, electrode contact, false-accept probability, or
clinical safety.

## Public-data result

On the locked A02–A08 confirmation cohort of BNCI 2014-008, containing
participants with ALS, the six-channel spatiotemporal shrinkage-LDA system
achieved **92.9% mean held-out character accuracy** at ten repetitions versus
**93.6% with eight channels**. All seven confirmation participants reached at
least 85% with six channels. The paired six-minus-eight difference was −0.7
percentage points (participant-bootstrap 95% interval: −2.86 to +1.43 points),
passing the declared −5-point engineering non-inferiority margin.

This result used active Ag/AgCl electrodes—not dry electrodes—and therefore
supports low-channel feasibility, not dry/wet equivalence. See the
[public-data benchmark](docs/PUBLIC_DATA_BENCHMARK.md).

The full external bigP3BCI Study A benchmark is equally important: across 13
file-disjoint participant recordings, six channels averaged 0.724 target-event
AUC versus 0.773 with 32 channels. This prevents a misleading universal
compact-montage claim and defines the next technical target. See the
[external cohort evidence](evidence/bigp3bci_studyA_rd_13cohort.json).

In a controlled software contact-failure stress evaluation, CASP reduced wrong
accepted outputs relative to an ordinary decoder, but coverage remained too
low for communication use. The sparse system was non-inferior to its easy wet
reference in **0/8** runs. See the
[evaluation review](docs/EVALUATION_AND_IMPROVEMENT_REVIEW.md).

NeuroSync has demonstrated the **six-channel accuracy target on one public ALS
cohort**. It has not yet demonstrated dry-electrode performance, prospective
wet-reference equivalence, low cost, home use, or clinical benefit.

## Performance target

The intended deployment gate is stricter than a single "85% accuracy" number:

| Outcome on a pre-registered, held-out session | Target |
|---|---:|
| Correct accepted-output rate | >= 0.85 |
| Wrong accepted-output rate | <= 0.05 |
| Coverage | >= 0.90 |
| Accepted-output accuracy | >= 0.90 |
| Wet-reference comparison | Lower 95% CI meets a pre-registered non-inferiority margin |

Details, including why acceptance accuracy alone is insufficient, are in
[the performance-target framework](docs/PERFORMANCE_TARGET_FRAMEWORK.md).

## Repository map

```
neurosync_p300/   core preprocessing, quality, selection, calibration, decoding
scripts/          reproducible command-line runners
tests/            unit and integration tests
docs/             protocol, literature synthesis, evidence boundaries
manuscript/       traceable manuscript source and figure-generation tools
```

Key documents:

- [Research brief](docs/RESEARCH_BRIEF.md): question, hypothesis, and outcomes.
- [Research gap review](docs/RESEARCH_GAP_REVIEW.md): 50+ source literature map.
- [Real-data replication log](docs/REAL_DATA_REPLICATION_LOG.md): verified public-data baseline.
- [Evaluation review](docs/EVALUATION_AND_IMPROVEMENT_REVIEW.md): controlled stress-test results and failure analysis.
- [Clinical translation protocol](docs/CLINICAL_TRANSLATION_PROTOCOL.md): future validation plan, not a clinical claim.
- [NeuroSync-OG method](docs/NEUROSYNC_OG_METHOD.md): equations, forward-model interface, and required ablations.
- [Public-data benchmark](docs/PUBLIC_DATA_BENCHMARK.md): locked ALS confirmation results and external transfer limits.
- [Flagship research narrative](docs/FLAGSHIP_RESEARCH_NARRATIVE.md): strongest defensible framing, contribution, and claim boundaries.
- [Prior-work and NYAS comparison](docs/PRIOR_WORK_AND_NYAS_COMPARISON.md): field positioning, judging alignment, and presentation narrative.
- [Data manifest](docs/DATA_MANIFEST.md): public-source provenance, licenses, and exact checksums.

## Run the software

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v

python scripts/run_demo.py
python scripts/run_casp_demo.py
python scripts/run_evaluation.py
python -m scripts.run_bnci_008_benchmark --directory data/external/bnci_008_2014
python scripts/run_session.py --train train.npz --test held_out.npz --forward-model forward_model.npz
```

For BCI Competition III Dataset II, follow the file-layout instructions in
`scripts/run_competition_import.py` and then run
`scripts/run_competition_replication.py`. Keep the held-out characters locked
until the complete pipeline is fixed.

## Reproducibility and responsible use

- Freeze splits, stopping rules, and success criteria before checking held-out results.
- Compare 4, 5, 6, and 8 channels under identical subject/session splits.
- Report correct outputs, wrong outputs, coverage, repetitions, calibration,
  setup time, contact stability, comfort, and failure recovery together.
- Use a measured, participant-specific forward model only if geometry is used
  as a decoding input; otherwise report proxy diagnostics as exploratory.
- Do not test with clinical populations outside an approved protocol, and keep
  an accessible fallback communication method available.

## License

No license has been selected yet. Until a license file is added by the
copyright holders, reuse is not granted.
