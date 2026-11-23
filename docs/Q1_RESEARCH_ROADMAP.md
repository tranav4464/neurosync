# NeuroSync research audit and route to a strong journal submission

> Historical audit snapshot dated 23 November 2026. The full 13-person
> bigP3BCI Study A external benchmark and subsequent ablations are documented
> in [PUBLIC_DATA_BENCHMARK.md](PUBLIC_DATA_BENCHMARK.md) and
> [SNR_DIVERSITY_ABLATION.md](SNR_DIVERSITY_ABLATION.md).

**Audit date:** 23 November 2026. This is an execution plan and evidence audit, not a claim of journal acceptance.

## Research question and claim ladder

**Primary question:** Can a compact P300 montage preserve reliable character communication across users, sessions, and electrode conditions while reducing preparation burden?

The project currently has three distinct claims. They must be tested separately:

1. **Electrode count:** Six selected channels can approach eight active channels in one ALS cohort. Supported by the retrospective BNCI 2014-008 analysis, subject to independent event and result replication.
2. **Geometry/contact method:** Forward-model distinguishability and measured contact state improve robustness, selective risk, or calibration. Implemented in code, not yet demonstrated in the main human-data benchmark.
3. **Low-cost dry headset:** A 4–6-electrode dry or semi-dry device matches a wet reference while reducing setup burden. No paired hardware evidence exists.

The proposed paper contribution is **reliability-aware sparse P300 decoding**: a channel set is useful only if neural evidence, sensor quality, and forward-model distinguishability remain jointly adequate. Geometry must demonstrate incremental value over strong empirical selection. A fallback outcome is still publishable: a well powered boundary study showing when geometry helps and when empirical selection is sufficient.

## Audit of the current repository

| Component | Existing evidence | Weakness that reviewers will notice | Required correction |
|---|---|---|---|
| BNCI 2014-008 | A01 development, A02–A08 confirmation, 20 held-out characters each; six channels 92.9%, eight 93.6% at ten repetitions | One retrospective study, seven confirmation users, method settings inspected on A01's feedback set | Independent event parser, character-level outputs, uncertainty and sensitivity analysis |
| Electrode selection | Training-fold forward selection | Selected channels vary by participant; full-montage and fixed-set comparisons incomplete | Fixed posterior montage, backward selection, SSNR selection, stability-aware selection; compare equal channel budgets |
| Classifier | Full-covariance shrinkage LDA substantially improves on diagonal LDA | Diagonal LDA is a weak principal comparator; xDAWN and SWLDA absent | Faithful SWLDA and xDAWN+LDA baselines with frozen training-only tuning |
| NeuroSync-OG | Optional forward-model interface and geometry-weighted evidence | No anatomical model or prospective geometry ablation on the reported ALS cohort | MNE BEM or measured head-model import, source/ROI definitions, negative-control leadfields, ablation |
| Contact policy | EEG-derived quality and selective actions | No measured impedance, pressure or dry contact; coverage is poor under controlled stress | Calibrate risk–coverage policy, then validate with hardware logs |
| External data | Competition III A/B: six channels 36%/76%, eight 60%/88% | Poor transfer; datasets differ in protocol and montage | Study-aware bigP3BCI validation and documented domain-shift analysis |
| Statistics | Seven-participant paired bootstrap | Five-point margin was declared retrospectively; precision is limited | Prespecify margin and sample size for a future evaluation; participant-level hierarchical intervals |
| Manuscript | Short Markdown feasibility narrative | Method detail, baselines, limitations, related-work comparison and supplementary evidence are insufficient for a full journal article | Full methods, flow diagram, tables, ablations, error analysis, data/code availability |

## Prior-work cross-pollination: specific mechanisms to reuse and test

| Prior work | What it contributes | What NeuroSync must test beyond it |
|---|---|---|
| Farwell & Donchin (1988), Donchin et al. (2000) | Oddball row/column spelling and communication-rate framing | Character-level evaluation and actual time/recovery cost |
| Krusienski et al. (2006, 2008) | Conventional classifiers and the sensitivity to reference, decimation and channel choice | Match preprocessing and training budget before claiming model gains |
| Rivet et al. (2009), xDAWN | ERP spatial filtering | Full xDAWN implementation, including equal-dimensional fair comparison with shrinkage LDA |
| Colwell et al. (2014) | Channel selection can dominate P300 performance | Compare selection algorithms, fixed sets and stability across calibration folds |
| Throckmorton et al. (2015) | Four-electrode performance in a tested setting | Identify the user/channel conditions under which four channels fail and six remain viable |
| Throckmorton et al. (2013), Mainsah et al. (2015) | Calibrated dynamic stopping, including ALS use | Optimize wrong outputs, coverage, repetitions and time jointly |
| Guger et al. (2012) | Dry P300 feasibility in controlled use | Test actual candidate dry electrode and fit, not transfer an active-electrode score |
| Clements et al. (2016) | Dry–wet comparison and incomplete recovery from more flashes | Test whether quality and geometry reduce the dry gap at a matched flash/time budget |
| Tangent-space alignment (2022) | Cross-user/session transfer for ERP BCIs | Compare transfer with participant calibration, quantify adaptation data and leakage |
| bigP3BCI (2025) | Diverse studies, multi-session and ALS metadata | Use study-level holdout and report heterogeneity, not one pooled score |

These are integrations of established components. A novel contribution requires a measured gain from the **joint reliability decision** and a falsifiable mechanism analysis, not a new name for an ensemble.

## New data reconnaissance completed

A single 8,057,142-byte bigP3BCI EDF file was downloaded locally from `StudyA/A_01/SE001/Train/RD/A_01_SE001_RD_Train02.edf` (SHA-256 `59226E70E588DF2CC28DAFFEA47580F759A6454BF01C61624B0378F0B24056C1`). It remains outside Git. Inspection found 32 channels labelled `EEG_*` at approximately 256 Hz, many character-grid and state channels, a 9×8 interface, `StimulusBegin`, `StimulusCode`, `StimulusType`, `CurrentTarget`, and `SelectedTarget` sampled signals. The EDF annotation track contains only `Begin recording`; an adapter must decode the sampled marker channels. The header identifies this file as `NonALS`. One recording is an adapter feasibility sample, not an external benchmark cohort.

Next inventory bigP3BCI by study and condition: electrode type, common channels, grid, target encoding, train/test structure, session count, participant population and size. Select at least two compatible development studies and one untouched external study before model tuning. Keep the entire 44.6-GB uncompressed collection optional; download only selected files and retain checksums.

## Execution phases and gates

### Phase 0 — independent audit (1–2 weeks)

- Implement a second BNCI 2014-008 event parser using onset transitions and verify 35 targets, 4,200 flashes, row/column counts and character labels per subject.
- Publish test-character predictions and exact code/data hashes for each subject and montage.
- Audit Competition III channel mapping and trial-major ASCII interpretation against the official examples.
- Repeat all results from a clean environment. Add a no-information label permutation check.

**Gate:** two pipelines agree on every trial target and event, and the headline tables regenerate from raw files.

### Phase 1 — credible baselines and operating point (2–4 weeks)

- Reproduce SWLDA, xDAWN+shrinkage LDA, current shrinkage LDA and a covariance/tangent-space baseline.
- Compare fixed posterior, empirical forward/backward and geometry-aware montages at 4, 6, 8 and full available channels.
- Use nested participant-calibration folds for all hyperparameters. Freeze repetition choices before confirmation.
- Report 1–10 repetition curves, characters/minute, balanced flash accuracy and character errors.

**Gate:** a named baseline is reproduced under identical splits; the proposed method's contribution survives the strongest fair comparator.

### Phase 2 — geometry mechanism (3–6 weeks)

- Generate a documented template BEM forward model using real electrode coordinates, reference, conductivity and source-orientation conventions. Add subject models where scans exist.
- Define target and nuisance ROIs before fitting. Audit reference rank and covariance regularization.
- Run identical-split ablations: empirical only; +contact; +geometry selection; +geometry evidence gate; full method.
- Run negative controls: shuffled channel/leadfield mapping, unrelated ROI, and constant observability.
- Evaluate single-channel loss, posterior loss and artifact episodes. Report false accepts, coverage and geometry-score calibration.

**Gate:** geometry changes a prespecified user-facing endpoint with a confidence interval and the negative controls remove that gain. If it fails, use geometry only as an exploratory diagnostic.

### Phase 3 — independent external validation (4–8 weeks)

- Build a bigP3BCI EDF adapter from sampled marker channels with a protocol-specific row/column or grid mapping. Confirm event timelines manually on several files.
- Split by subject and study, never by flash. Freeze one common montage policy and a participant-specific policy; report both.
- Leave one study out, evaluate session transfer, and estimate calibration needs at 5, 10 and 15 characters.
- Stratify by ALS status and study when metadata are available; never merge incompatible grids into a single character metric without a common decoder.

**Gate:** frozen settings retain benefit on at least one untouched compatible study and failures are fully documented.

### Phase 4 — headset and paired study (requires lab, hardware and ethics)

- Prototype six-channel dry/semi-dry placement with a costed bill of materials; measure pressure, impedance/contact, setup and cleaning time.
- Counterbalance wet and candidate sessions on the same task and participants. Record event latency, dropouts, fatigue, comfort and caregiver effort.
- Prespecify non-inferiority margin from a clinically meaningful communication loss, sample size, primary endpoint and stopping policy before enrollment.
- Keep an accessible fallback communication method. Use repeated sessions and a held-out final assessment.

**Gate:** correct accepted-output rate ≥85%, wrong accepted-output rate ≤5%, coverage ≥90%, and a participant-level lower confidence bound above the justified wet-reference margin, with measured setup/comfort advantage. Missing any gate narrows the claim.

## Statistical and reporting rules

- Participant or study is the independent unit for population inference; flashes within a character are correlated.
- Character accuracy on a forced-choice public recording is not a measurement of selective safety or no-intent performance.
- The current five-point BNCI margin is a retrospective **engineering screen**; do not describe it as prospectively preregistered clinical non-inferiority.
- Report paired differences, participant-level intervals, effect sizes and all individual outcomes, including the worst participant and external failures.
- Predefine primary and secondary outcomes, exclusions, missing data, adaptive stopping, multiplicity handling and permitted model-selection data.
- For an observational secondary-data paper, complete the STROBE reporting checklist; for a prospective intervention, use the appropriate trial protocol/reporting guidance.

## Manuscript package required for a 9/10 submission

1. Precise abstract and contribution claims aligned to the tested method.
2. Reproducible data flow and protocol table per study.
3. Baseline table and training-budget parity.
4. Full geometry and decision equations with explicit assumptions.
5. Ablation and negative-control figure.
6. Cross-study and per-user results, risk–coverage and calibration curves.
7. Robustness, runtime, cost and user-burden figures where measured.
8. Limitations, failure cases, ethics, license and data/code availability.
9. Supplementary event validation, hyperparameters, seeds, hashes and regeneration commands.

## Selected primary sources

- [Farwell & Donchin 1988](https://doi.org/10.1016/0013-4694(88)90149-6)
- [Rivet et al. xDAWN 2009](https://doi.org/10.1109/TBME.2009.2012869)
- [Colwell et al. channel selection 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4106671/)
- [Throckmorton et al. four-channel study](https://pubmed.ncbi.nlm.nih.gov/25316166/)
- [Throckmorton et al. Bayesian stopping 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3798004/)
- [Mainsah et al. ALS dynamic stopping](https://doi.org/10.1088/1741-2560/12/1/016013)
- [Guger et al. dry/gel P300 comparison](https://pubmed.ncbi.nlm.nih.gov/22586362/)
- [Clements et al. wet/dry P300 comparison](https://pmc.ncbi.nlm.nih.gov/articles/PMC6378883/)
- [Tangent-space alignment 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9755175/)
- [bigP3BCI dataset](https://www.physionet.org/content/bigp3bci/1.0.0/)
- [STROBE checklist](https://equator-network.org/reporting-guidelines/strobe/)
