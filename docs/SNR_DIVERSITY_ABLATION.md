# ERP signal and diversity selection ablation

This exploratory method combines two established P300 selection concepts:
target response energy relative to residual noise, and a penalty for selecting
electrodes with nearly identical target-minus-nontarget waveforms. It selects
six channels using only the `Train02` recording, then fits the same shrinkage
LDA decoder and evaluates the later `Test06` file.

| bigP3BCI Study A RD event AUC | One-shot forward selection | ERP SNR + diversity | All 32 channels |
|---|---:|---:|---:|
| A01–A07 development, n=7 | 0.746 | 0.772 | — |
| A09/A14–A19 confirmation, n=6 | 0.698 | 0.695 | 0.728 |
| All 13, descriptive | 0.724 | 0.736 | 0.773 |

The all-participant paired difference for ERP SNR + diversity versus the
original selector is +0.0126 AUC (participant bootstrap 95% interval -0.0116
to +0.0380; six of 13 participants improved). Its confirmation mean was 0.0033
lower than the original selector. This does not establish a new state of the
art, nor does it close the full-montage gap. The method is retained as a
reproducible ablation and should be tested on a new untouched cohort if revised.

This tests a methodological hypothesis from [Colwell et al.'s channel selection
study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4106671/) and prior work on
redundant P300 electrodes. The particular score and penalty are our
integration; the underlying signal and redundancy concepts are established.

Reproduce with `python -m scripts.run_bigp3bci_benchmark --selection-method
snr_diverse --pair TRAIN TEST` repeated for the 13 pairs in the data manifest.
