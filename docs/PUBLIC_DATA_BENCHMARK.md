# NeuroSync Public-Data Benchmark

**Analysis date:** 23 November 2026  
**Primary public dataset:** BNCI 2014-008  
**Confirmation design:** A01 development; A02–A08 locked confirmation

## Why this dataset matters

BNCI 2014-008 contains eight participants with ALS performing a 6×6 P300 copy-spelling task using eight active EEG electrodes (`Fz, Cz, Pz, Oz, P3, P4, PO7, PO8`) at 256 Hz. Each participant attempted 35 characters. The original protocol used the first 15 characters for calibration and the final 20 with online feedback. NeuroSync preserves this split rather than randomly mixing flashes or characters.

Source: [BNCI Horizon 008-2014](https://bnci-horizon-2020.eu/database/data-sets), [Riccio et al. 2013](https://doi.org/10.3389/fnhum.2013.00732).

## Locked method

Subject A01 was used to choose one fixed improvement over the original diagonal-LDA baseline:

- 100–800 ms post-stimulus spatiotemporal waveform;
- temporal downsampling by eight;
- full pooled covariance with 0.10 diagonal shrinkage;
- training-only forward channel selection;
- row and column evidence summed over ten repetitions.

No method setting was changed after viewing A02–A08. The final 20 characters of every participant remained outside channel selection and model fitting.

Before each model was fit, the imported event table was audited against the
published protocol: 35 character trials, 120 flashes per trial, ten
presentations of every row/column code, and exactly one target row plus one
target column. All eight source files passed this audit.

## Confirmation result

| Participant | 4 channels | 6 channels | 8 channels |
|---|---:|---:|---:|
| A02 | 90% | 90% | 95% |
| A03 | 95% | 90% | 90% |
| A04 | 80% | 95% | 95% |
| A05 | 80% | 85% | 85% |
| A06 | 75% | 95% | 90% |
| A07 | 90% | 95% | 100% |
| A08 | 100% | 100% | 100% |
| **Mean** | **87.1%** | **92.9%** | **93.6%** |

All seven confirmation participants reached at least 85% character accuracy with six selected channels. The paired six-minus-eight-channel mean difference was **−0.7 percentage points**. A 10,000-resample participant bootstrap gave a 95% interval of **−2.86 to +1.43 percentage points**. The lower limit exceeds the declared −5-point engineering margin.

This is strong evidence that six carefully selected channels can preserve eight-channel performance in this dataset. It is not a prospective clinical non-inferiority trial.

## Baseline improvement

At six channels and ten repetitions, the original diagonal-LDA confirmation mean was 60.7%; the locked spatiotemporal shrinkage-LDA mean was 92.9%. This 32.2-point absolute improvement comes from modelling correlated spatiotemporal ERP structure instead of treating every feature as independent.

| Six-channel comparator | A02–A08 mean at 10 repetitions | Interpretation |
|---|---:|---|
| Diagonal LDA | 60.7% | Deliberately simple baseline |
| Spatiotemporal shrinkage LDA | **92.9%** | Locked primary method |
| Training-only template spatial filter + shrinkage LDA | 91.4% | Did not improve the primary method |

The spatial projection was included as a fair, training-only ablation. It is
not labelled xDAWN and is not carried forward as a claimed improvement because
it reduced the six-channel confirmation mean by 1.4 points. Reporting this
negative comparator is important: NeuroSync's current evidence supports a
simple sparse spatiotemporal decoder, not an unverified stack of extra modules.

## External context and limitation

The same fixed classifier was tested on held-out characters from BCI Competition III Dataset II:

| Dataset | 6 channels | 8 channels |
|---|---:|---:|
| Subject A | 36% | 60% |
| Subject B | 76% | 88% |

This transfer result prevents an overbroad claim: the six-channel result is excellent on BNCI 2014-008 but does not yet generalize to every P300 acquisition. The datasets differ in hardware, montage candidates, epoch duration, protocol, and signal distribution.

### bigP3BCI readiness check

NeuroSync now includes a conservative EDF adapter and a file-disjoint
event-detection benchmark for the large public bigP3BCI resource. Study A uses
a 9×8 random paradigm, so its 120 unique stimulus codes per trial cannot be
silently converted into the 6×6 character decoder used above. Instead, the
external endpoint is target-versus-nontarget event ROC AUC, trained on one
`Train02` file and evaluated on the later `Test06` file for the same person.
Every one of the six EDF inputs passed the event audit: seven target blocks,
120 events per block, and ten labelled target events per block.

| Study A participant | Six selected channels: held-out AUC | All 32 channels: held-out AUC |
|---|---:|---:|
| A01 | 0.764 | 0.895 |
| A02 | 0.844 | 0.841 |
| A03 | 0.703 | 0.690 |
| **Mean** | **0.771** | **0.809** |

The corresponding held-out balanced-accuracy means were 70.2% (six) and
71.2% (32). This three-participant pilot does **not** establish non-inferiority
or a character-accuracy result. Its value is methodological: it shows that a
sparse montage can be evaluated honestly on a second, protocol-incompatible
resource; it also exposes participant-dependent performance and makes robust
montage selection the priority rather than claiming generalisation too early.

## Exact reproducibility

```powershell
python -m scripts.run_bnci_008_benchmark `
  --directory data/external/bnci_008_2014 `
  --output results/bnci_008_cohort.json
```

The compact, version-controlled result is stored in [`evidence/public_benchmark_summary.json`](../evidence/public_benchmark_summary.json). Raw public files remain excluded from Git because of size and source licensing.

For the bigP3BCI pilot:

```powershell
python -m scripts.run_bigp3bci_benchmark `
  --train data/external/bigp3bci_sample_A01_train02.edf `
  --test data/external/bigp3bci_studyA_rd/A_01_SE001_RD_Test06.edf
```

## Claim boundary

BNCI 2014-008 used active Ag/AgCl electrodes, not the proposed dry headset. The result answers the electrode-count portion of the central question: six channels can retain near-eight-channel accuracy under this protocol. It does not yet answer dry-versus-wet equivalence, setup cost, comfort, contact degradation, or home use.
