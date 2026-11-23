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

## External context and limitation

The same fixed classifier was tested on held-out characters from BCI Competition III Dataset II:

| Dataset | 6 channels | 8 channels |
|---|---:|---:|
| Subject A | 36% | 60% |
| Subject B | 76% | 88% |

This transfer result prevents an overbroad claim: the six-channel result is excellent on BNCI 2014-008 but does not yet generalize to every P300 acquisition. The datasets differ in hardware, montage candidates, epoch duration, protocol, and signal distribution.

## Exact reproducibility

```powershell
python -m scripts.run_bnci_008_benchmark `
  --directory data/external/bnci_008_2014 `
  --output results/bnci_008_cohort.json
```

The compact, version-controlled result is stored in [`evidence/public_benchmark_summary.json`](../evidence/public_benchmark_summary.json). Raw public files remain excluded from Git because of size and source licensing.

## Claim boundary

BNCI 2014-008 used active Ag/AgCl electrodes, not the proposed dry headset. The result answers the electrode-count portion of the central question: six channels can retain near-eight-channel accuracy under this protocol. It does not yet answer dry-versus-wet equivalence, setup cost, comfort, contact degradation, or home use.
