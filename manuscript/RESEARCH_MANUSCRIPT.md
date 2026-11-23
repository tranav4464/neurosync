# NeuroSync-OG: Geometry-Constrained Contact-Adaptive Selective Decoding for Sparse P300 BCIs

> Historical working draft. The current submission narrative is [FLAGSHIP_MANUSCRIPT.md](FLAGSHIP_MANUSCRIPT.md). This draft predates the complete 13-person external analysis.

## Abstract

Low-channel EEG could reduce P300 BCI setup burden, but sensor reduction and variable contact can increase wrong outputs. NeuroSync-OG combines training-only montage selection, full-covariance spatiotemporal decoding, forward-model observability, contact-quality weighting, and selective `ACCEPT`, `REPEAT`, `REJECT`, and `RESEAT_HEADSET` actions. We evaluated the electrode-count hypothesis on BNCI 2014-008, comprising eight participants with ALS and an eight-channel active-electrode P300 speller. Subject A01 was used to freeze the 100--800 ms feature interval, temporal downsampling, and covariance shrinkage; A02--A08 formed a locked confirmation cohort using the official first-15-character calibration and final-20-character feedback split. At ten repetitions, six training-selected channels achieved 92.9% mean held-out character accuracy versus 93.6% for eight channels. All seven confirmation participants reached at least 85% with six channels. The paired six-minus-eight difference was -0.7 percentage points (participant-bootstrap 95% interval -2.86 to +1.43), meeting a -5-point engineering non-inferiority margin. External evaluation on BCI Competition III produced lower and heterogeneous results, preventing a universal-performance claim. The findings support sparse active-electrode feasibility in the ALS cohort; dry-electrode equivalence, contact-robust safety, and prospective clinical utility remain untested.

**Keywords:** P300 BCI; selective prediction; EEG quality; channel selection; reproducible evaluation.

## 1. Central question and contribution

P300 spellers identify an attended rare stimulus in an oddball sequence [1--3]. Wet electrodes and larger montages can yield useful signals, but gel, preparation time, cleanup, and assistance can impede repeated use. Dry sensors may reduce setup burden; direct comparisons also show reduced signal-to-noise ratio, slow-band drift, and contact instability [4]. A compact design is not useful merely because it uses fewer electrodes: it must avoid turning uncertainty into wrong communication.

> Can a 4--6-channel dry or semi-dry P300 system attain pre-specified non-inferior correct accepted-output performance relative to an 8-channel wet reference, while constraining wrong outputs and user burden?

NeuroSync-OG provides a testable integration: training-only selection, inspectable decoding, calibration-aware sequential evidence, measured forward-model geometry, and explicit recovery states. Its distinctive contribution is to treat spatial distinguishability as a time-varying reliability input rather than a static montage assumption. It requires a study to report the full trade-off: correct and wrong outputs, abstention, repetitions, contact failure, comfort, setup time, and cost.

## 2. Gap and framework

P300 BCI literature covers stimulus presentation, classifiers, and communication metrics [1--3,5]. Small posterior/central montages can work in some cohorts, but channel identity and session transfer need prospective verification [6,7]. Dynamic stopping improves speed only when evidence is calibrated [8]. Wet/dry comparisons show that extra flashes may not fully compensate for poor contact or slow-band noise [4]. The unfilled gap is an evaluation that treats wrong emitted characters, abstention, recovery, and setup burden as co-primary outcomes. Accepted-output accuracy alone can be inflated by refusing difficult trials; coverage alone can hide unsafe wrong outputs.

Each epoch is baseline corrected and band-limited. Interpretable waveform and pooled P300-window features are scored by a regularized diagonal LDA. Channels are selected with training-character folds only. The proposed montage objective combines cross-validated balanced accuracy, fold stability, median contact reliability, forward observability, and target–artifact ambiguity. Calibration-relative features quantify slow-band energy, line-noise energy, and transient amplitude. Symbol evidence is multiplied by quality and observability reliability before accumulation. `ACCEPT` requires training-calibrated confidence, margin, stability, quality, and observability. Poor quality can yield `REPEAT` or `RESEAT_HEADSET`; exhausted weak evidence yields `REJECT` and fallback communication. These are engineering actions, not validated clinical controls or a substitute for impedance measurement.

For an externally supplied measured leadfield and matched noise covariance, the code computes a whitened topographic-ambiguity diagnostic. The included 10--20 coefficient table is a pedagogical proxy, not a participant-specific BEM/FEM model. It cannot establish source localisation, predict electrode detachment, or prove a false-accept bound.

## 3. Outcomes and evidence to date

The primary development outcome is correct accepted-output rate (CAOR): `correct ACCEPT decisions / intended selections`. It is reported with wrong accepted-output rate (WAOR), coverage, accepted-output accuracy, median repetitions, setup time, and recovery actions. For forced-choice public data, coverage is one and character accuracy is the corresponding endpoint. A candidate deployment gate is CAOR >= 0.85, WAOR <= 0.05, coverage >= 0.90, and accepted-output accuracy >= 0.90 on a pre-registered held-out session. A hardware wet-reference comparison must use a pre-registered non-inferiority margin and the lower confidence bound of the paired difference.

BNCI 2014-008 contains 35 copy-spelled characters from each of eight people with ALS, recorded from `Fz, Cz, Pz, Oz, P3, P4, PO7, PO8` at 256 Hz [10]. The first 15 characters were originally used for calibration and the final 20 for feedback; we retained this temporal split. A01 was explicitly designated for method development. After its held-out feedback block was inspected, the feature interval (100--800 ms), downsampling factor (eight), and full-covariance diagonal shrinkage (0.10) were frozen. A02--A08 were then processed without further adjustment.

At ten repetitions, confirmation means were 87.1%, 92.9%, and 93.6% for four, six, and eight channels, respectively. Six-channel participant accuracies were 90%, 90%, 95%, 85%, 95%, 95%, and 100%; therefore, 7/7 confirmation participants met the 85% character target. Eight-channel accuracies were 95%, 90%, 95%, 85%, 90%, 100%, and 100%. The paired mean difference was -0.7 points. Resampling the seven participant differences 10,000 times produced a 95% interval of -2.86 to +1.43 points; its lower bound exceeded the declared -5-point engineering margin. At six channels, spatiotemporal shrinkage LDA improved the confirmation mean from 60.7% for diagonal LDA to 92.9%.

![Locked public-data confirmation](figures/public_benchmark_confirmation.png)

*Figure 1. Character-level confirmation on BNCI 2014-008 A02--A08. Thin lines show participant trajectories across channel counts; paired points compare six and eight channels. The dashed line is the pre-specified 85% character target.*

The fixed method was also applied to held-out characters from BCI Competition III Dataset II [9]. Subject A achieved 36% and 60% with six and eight channels, while Subject B achieved 76% and 88%. These outcomes show that the sparse result depends on acquisition and participant characteristics and does not transfer uniformly across datasets.

Across eight seeded controlled software stress runs, sparse CASP produced CAOR 0.193, WAOR 0.099, and coverage 0.292. Under injected contact failure, WAOR was 0.102 versus 0.284 for the ordinary decoder; coverage was only 0.286 and re-seat rate was 0.250. The wet-reference non-inferiority screen passed in 0/8 runs. The narrow observation is that selective gating can trade coverage for fewer wrong outputs under defined stress assumptions. It does not demonstrate a viable communication system.

## 4. Threats to validity and next experiments

The confirmation cohort contains seven participants and 140 held-out character decisions; the participant-level confidence interval is therefore imprecise. BNCI 2014-008 used active Ag/AgCl electrodes, not dry electrodes, and all recordings came from one study. Channel selection and classification were participant-specific. The public files represent an existing protocol rather than a prospective preregistration. The stress suite remains a regression test rather than a physical electrode--skin model, and no measured forward model or impedance stream accompanies the public cohort. These limitations rule out dry/wet equivalence, setup-cost, home-use, clinical-safety, and prospective-efficacy claims.

Next, add an independent multi-session cohort, reproduce SWLDA and xDAWN+LDA comparators, and evaluate whether one shared six-channel montage can replace participant-specific selection. Then run a counterbalanced wet versus candidate dry/semi-dry protocol. Record electrode type, montage, cap size, impedance/contact, event timing, packet loss, setup/cleanup time, comfort, fatigue, and recovery actions. Any clinical phase needs ethics approval, AAC/ALS co-design, preregistration, and an independent fallback communication method.

## 5. Conclusion

NeuroSync-OG provides evidence that six participant-selected channels can retain near-eight-channel P300 character accuracy in a locked confirmation cohort of people with ALS. The result meets the 85% character target and a declared five-point engineering non-inferiority margin on that active-electrode dataset. Cross-dataset variability and the absence of dry hardware prevent broader equivalence or clinical claims. The next decisive experiment is therefore not another offline optimization, but a prospective counterbalanced wet-versus-dry/semi-dry study with contact, burden, and selective-safety outcomes.

## References

1. Farwell LA, Donchin E. Talking off the top of your head. *Electroencephalogr Clin Neurophysiol*. 1988;70:510--523.
2. Donchin E, Spencer KM, Wijesinghe R. The mental prosthesis. *IEEE Trans Rehabil Eng*. 2000;8:174--179.
3. Wolpaw JR, et al. Brain-computer interfaces for communication and control. *Clin Neurophysiol*. 2002;113:767--791.
4. Clements JM, et al. Applying dynamic data collection to improve dry electrode system performance for a P300-based brain-computer interface. *J Neural Eng*. 2016;13:066018. doi:10.1088/1741-2560/13/6/066018.
5. Rezeika A, et al. A review of P300-based BCI applications. *J Clin Med*. 2018;7:419.
6. Throckmorton CS, et al. Performance of a P300-based BCI using four electrodes. *Clin Neurophysiol*. 2013;124:2300--2307.
7. Colwell KA, et al. A comparison of online electrode selection methods for P300 BCI. *J Neural Eng*. 2014;11:066012.
8. Throckmorton CS, et al. Bayesian approach to dynamically stopping P300 speller stimulation. *J Neural Eng*. 2013;10:036004.
9. Blankertz B, et al. BCI Competition III: dataset II description. 2004. https://www.bbci.de/competition/iii/desc_II.pdf
10. Riccio A, et al. Attention and P300-based BCI performance in people with amyotrophic lateral sclerosis. *Front Hum Neurosci*. 2013;7:732.
