# NeuroSync: a preregisterable framework for safe sparse P300 BCI evaluation

## Abstract

Low-channel dry and semi-dry EEG could reduce P300 BCI setup burden, but fewer sensors and variable contact can increase wrong outputs. NeuroSync is an open framework for evaluating—not assuming—whether a 4--6-channel candidate can approach an 8-channel wet reference. It combines training-only selection, transparent regularized-LDA decoding, out-of-fold decision calibration, contact-quality features, and `ACCEPT`, `REPEAT`, `REJECT`, and `RESEAT_HEADSET` actions. The primary outcome is correct accepted-output rate, reported with wrong accepted-output rate, coverage, and repetitions. On a held-out-character split of BCI Competition III Dataset II Subject A, the current 4-channel baseline reached 16.0% character accuracy; an eight-channel sparse-feature ablation also reached 16.0%. In controlled software contact-failure stress testing, the selective policy reduced wrong accepted outputs relative to an ordinary decoder, but had inadequate coverage and was non-inferior to the wet reference in 0/8 runs. This is an honest baseline and a falsifiable protocol—not evidence of wet-reference equivalence, dry-electrode performance, clinical benefit, or home use.

**Keywords:** P300 BCI; selective prediction; EEG quality; channel selection; reproducible evaluation.

## 1. Central question and contribution

P300 spellers identify an attended rare stimulus in an oddball sequence [1--3]. Wet electrodes and larger montages can yield useful signals, but gel, preparation time, cleanup, and assistance can impede repeated use. Dry sensors may reduce setup burden; direct comparisons also show reduced signal-to-noise ratio, slow-band drift, and contact instability [4]. A compact design is not useful merely because it uses fewer electrodes: it must avoid turning uncertainty into wrong communication.

> Can a 4--6-channel dry or semi-dry P300 system attain pre-specified non-inferior correct accepted-output performance relative to an 8-channel wet reference, while constraining wrong outputs and user burden?

NeuroSync provides a testable integration: training-only selection, inspectable decoding, calibration-aware sequential evidence, and explicit recovery states. It requires a study to report the full trade-off: correct and wrong outputs, abstention, repetitions, contact failure, comfort, setup time, and cost.

## 2. Gap and framework

P300 BCI literature covers stimulus presentation, classifiers, and communication metrics [1--3,5]. Small posterior/central montages can work in some cohorts, but channel identity and session transfer need prospective verification [6,7]. Dynamic stopping improves speed only when evidence is calibrated [8]. Wet/dry comparisons show that extra flashes may not fully compensate for poor contact or slow-band noise [4]. The unfilled gap is an evaluation that treats wrong emitted characters, abstention, recovery, and setup burden as co-primary outcomes. Accepted-output accuracy alone can be inflated by refusing difficult trials; coverage alone can hide unsafe wrong outputs.

Each epoch is baseline corrected and band-limited. Interpretable waveform and pooled P300-window features are scored by a regularized diagonal LDA. Channels are selected with training-character folds only. Calibration-relative features quantify slow-band energy, line-noise energy, and transient amplitude. Evidence is accumulated by symbol for a limited number of repetitions. `ACCEPT` requires training-calibrated confidence, margin, and stability. Poor quality can yield `REPEAT` or `RESEAT_HEADSET`; exhausted weak evidence yields `REJECT` and fallback communication. These are engineering actions, not validated clinical controls or a substitute for impedance measurement.

For an externally supplied measured leadfield and matched noise covariance, the code computes a whitened topographic-ambiguity diagnostic. The included 10--20 coefficient table is a pedagogical proxy, not a participant-specific BEM/FEM model. It cannot establish source localisation, predict electrode detachment, or prove a false-accept bound.

## 3. Outcomes and evidence to date

The primary outcome is correct accepted-output rate (CAOR): `correct ACCEPT decisions / intended selections`. It is reported with wrong accepted-output rate (WAOR), coverage, accepted-output accuracy, median repetitions, setup time, and recovery actions. A candidate deployment gate is CAOR >= 0.85, WAOR <= 0.05, coverage >= 0.90, and accepted-output accuracy >= 0.90 on a pre-registered held-out session. A wet-reference comparison must use a pre-registered non-inferiority margin and the lower confidence bound of the paired difference. These are proposed criteria, not established properties of this code.

The current real-data check uses the labelled training recording of BCI Competition III Dataset II, Subject A [9]. It imports 15,130 valid flash epochs from 85 character selections, uses 60 training and 25 held-out characters (`seed=7`), and aggregates row/column evidence into the official 6x6 matrix. The 4-channel LDA baseline obtained 54.3% held-out flash balanced accuracy and 16.0% character accuracy. An eight-channel 60-feature ablation obtained 55.7% flash balanced accuracy and 16.0% character accuracy. Exact configuration and predictions are in the [replication log](../docs/REAL_DATA_REPLICATION_LOG.md). This is a baseline failure: the pipeline does not reproduce high-performing published decoders and cannot support a low-channel conclusion yet.

Across eight seeded controlled software stress runs, sparse CASP produced CAOR 0.193, WAOR 0.099, and coverage 0.292. Under injected contact failure, WAOR was 0.102 versus 0.284 for the ordinary decoder; coverage was only 0.286 and re-seat rate was 0.250. The wet-reference non-inferiority screen passed in 0/8 runs. The narrow observation is that selective gating can trade coverage for fewer wrong outputs under defined stress assumptions. It does not demonstrate a viable communication system.

## 4. Threats to validity and next experiments

The public replication is one subject, one labelled file, and one split. It is not dry-electrode data, an ALS cohort, or an independent test-set evaluation. The stress suite is useful for regression testing but is not a physical electrode--skin model. The quality gate does not measure impedance, cap pressure, motion, timing, or packet loss. The geometry proxy has no anatomical or individual calibration. These limitations rule out wet/dry equivalence, cost, home-use, clinical-safety, and efficacy claims.

Next, verify event alignment and reproduce documented full-montage SWLDA and xDAWN+LDA baselines across both Competition III subjects and an external set. Freeze all choices, then compare 4, 5, 6, and 8 channels with subject- and session-held-out splits. Publish calibration and selective-risk curves. Only after a credible public benchmark, run a counterbalanced wet versus candidate dry/semi-dry protocol. Record electrode type, montage, cap size, impedance/contact, event timing, packet loss, setup/cleanup time, comfort, fatigue, and recovery actions. Any clinical phase needs ethics approval, AAC/ALS co-design, preregistration, and an independent fallback communication method.

## 5. Conclusion

NeuroSync is a transparent route to test a promising low-burden BCI hypothesis, not proof that it works. Its present value is methodological: it makes the accuracy--safety--coverage trade-off explicit and exposes a public-data baseline failure rather than converting an aspiration into a result. Meeting the 85% target remains an empirical question for held-out public, hardware, and human evaluations.

## References

1. Farwell LA, Donchin E. Talking off the top of your head. *Electroencephalogr Clin Neurophysiol*. 1988;70:510--523.
2. Donchin E, Spencer KM, Wijesinghe R. The mental prosthesis. *IEEE Trans Rehabil Eng*. 2000;8:174--179.
3. Wolpaw JR, et al. Brain-computer interfaces for communication and control. *Clin Neurophysiol*. 2002;113:767--791.
4. Clements JM, et al. Comparison of dry and gel based electrodes for P300 BCI. *J Neural Eng*. 2016;13:066020.
5. Rezeika A, et al. A review of P300-based BCI applications. *J Clin Med*. 2018;7:419.
6. Throckmorton CS, et al. Performance of a P300-based BCI using four electrodes. *Clin Neurophysiol*. 2013;124:2300--2307.
7. Colwell KA, et al. A comparison of online electrode selection methods for P300 BCI. *J Neural Eng*. 2014;11:066012.
8. Throckmorton CS, et al. Bayesian approach to dynamically stopping P300 speller stimulation. *J Neural Eng*. 2013;10:036004.
9. Blankertz B, et al. BCI Competition III: dataset II description. 2004. https://www.bbci.de/competition/iii/desc_II.pdf
