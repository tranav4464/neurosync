# NeuroSync P300

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**NeuroSync** is a reproducible research framework for studying a difficult
question in P300 brain--computer interfaces (BCIs):

> Can a 4--6-channel dry or semi-dry P300 system approach an 8-channel wet
> reference **without increasing wrong outputs or hiding failures through
> excessive abstention**?

It is not a headset, a medical device, a clinical decision aid, or evidence of
performance for people with ALS. The framework makes the target measurable:
correct accepted outputs, wrong accepted outputs, coverage, repetitions,
contact-quality actions, and held-out-session performance.

## NeuroSync-OG: the research innovation

NeuroSync-OG combines Observable Geometry with Contact-Aware Adaptive Sparse
P300 decoding. Conventional systems ask whether a classifier is confident;
NeuroSync-OG also asks whether the signal is trustworthy and whether the
remaining electrode configuration can still distinguish target and nuisance
source signatures. It combines:

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

## Current evidence

The current real-data result establishes a transparent improvement benchmark.
On a within-subject held-out-character split
of the labelled BCI Competition III Dataset II Subject A training recording,
the compact 4-channel LDA baseline achieved **16.0% character accuracy**.
The eight-channel sparse-feature ablation also achieved **16.0%**. See the
[replication log](docs/REAL_DATA_REPLICATION_LOG.md) for the exact import,
split, and limitations.

In a controlled software contact-failure stress evaluation, CASP reduced wrong
accepted outputs relative to an ordinary decoder, but coverage remained too
low for communication use. The sparse system was non-inferior to its easy wet
reference in **0/8** runs. See the
[evaluation review](docs/EVALUATION_AND_IMPROVEMENT_REVIEW.md).

Therefore, NeuroSync has **not** demonstrated 85% correct accepted outputs,
wet-reference equivalence, dry-electrode performance, low cost, home use, or
clinical benefit. Those are pre-specified objectives for later experiments,
not current results.

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

## Run the software

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v

python scripts/run_demo.py
python scripts/run_casp_demo.py
python scripts/run_evaluation.py
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
