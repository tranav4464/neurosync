# NeuroSync CASP — Deep Prior-Work Matrix

**Companion to:** [Research Gap Review](RESEARCH_GAP_REVIEW.md)  
**Scope:** 91 sources, indexed as `S01`–`S91` in that review  
**Purpose:** turn literature into design decisions, replication tasks, and explicit claim boundaries.

## How to read this matrix

“Deep review” has different evidence levels. A paper can be relevant without being strong evidence for a final product claim.

- **Anchor:** accessible full text or extended result record was checked for methods, population, outcome, and limitation. These papers drive the proposed experiment.
- **Structured:** title, abstract, study record, and/or review context were checked. These papers identify prior art and comparators; read the full protocol before copying a threshold or a hardware specification.
- **Context:** review, dataset, tool, or enabling technology. Useful for scope and implementation, but not direct proof that NeuroSync will work.

The paper numbers below resolve to full links in `RESEARCH_GAP_REVIEW.md`. “Action” means what NeuroSync should do with the paper, not what the paper proves.

## A. Deep anchor findings

| Anchor | What was tested | What it establishes | Boundary / limitation | NeuroSync action |
|---|---|---|---|---|
| S01 Farwell & Donchin (1988) | Rare attended flashes in a spelling matrix | The P300 can support character selection without muscle output | Foundational controlled paradigm, not a home/ALS product validation | Reproduce a standard P300 baseline before claiming any improvement |
| S04 Krusienski et al. (2006) | Multiple P300 classifier families | A standard classifier comparison is mandatory; classifier choice changes apparent performance | Older datasets and protocol do not answer dry-headset performance | Keep SWLDA/LDA as baselines beside any new model |
| S06 Nijboer et al. (2008) | Repeated P300 use by people with advanced ALS | P300 communication can be feasible, but person/day variation matters | Clinical feasibility does not imply universal access or comfort | Evaluate participant and session, not pooled epochs |
| S07 Krusienski et al. (2008) | Channel/reference/decimation/feature choices | Small preprocessing choices can alter P300 results materially | Offline optimization can overfit if test data influence choices | Freeze preprocessing and nest all selection inside training folds |
| S13 Townsend et al. (2010) | Checkerboard versus row/column stimulus structure | The flash paradigm itself is an important design variable | Better paradigm scores may not transfer across users or hardware | Compare a standard checkerboard/reference paradigm before inventing a new display |
| S17 Pan et al. (2022 review) | P300 paradigms, algorithms, and evaluation practices | There is no single universal P300 design; paradigm choice affects usability and ITR | Review aggregates heterogeneous populations and protocols | State the exact paradigm, timing, user group, and metric in every claim |
| S36 Guger et al. (2012) | Dry versus gel P300 spelling in controlled use | Dry electrodes can be usable and comfortable in some conditions | A positive controlled result does not remove contact/movement/home variability | Include dry electrodes as a candidate, not a presumed equal replacement |
| S53 Colwell et al. (2014) | Competing channel-selection methods | Selection can improve a P300 system; poor subsets can make it unusable | The best method/set is data- and user-dependent | Compare fixed standard sets and multiple selectors, with nested evaluation |
| S54 Throckmorton et al. (2015) | Electrode-number/configuration optimization and prospective test | A four-electrode posterior configuration can be sufficient in its tested setting | Population-specific result; not proof that one four-channel set works for all | Treat 4–6 channels as an empirical design constraint, not a fixed montage claim |
| S66 Throckmorton et al. (2013) | Bayesian dynamic stopping across 26 users | Probability-based stopping can improve accuracy/rate compared with static collection | Posterior quality depends on classifier likelihood calibration and task assumptions | Reproduce fixed versus dynamic stopping; audit calibration and false confidence |
| S67 Mainsah et al. (2015) | Dynamic stopping with ALS participants | Dynamic stopping is relevant in the target population, not only healthy cohorts | It does not establish dry-electrode performance or safe abstention | Use it as the clinical dynamic-stopping comparator |
| S91 Clements et al. (2016) | Wet/dry P300 comparison; healthy and ALS/PLS groups; dynamic data collection | Dry systems can have poorer SNR, lower accuracy/bit rate, higher slow-band power, and more artifact sensitivity; additional flashes help but do not fully close the wet/dry gap | Specific hardware, montage, and sample; results should not be generalized to every dry electrode | This is the key problem statement: model contact/artifact quality, not just stopping thresholds |
| S40 Mikkelsen et al. (2020) | Wireless dry versus conventional wet EEG for clinical applications | Hardware and electrode type must be evaluated at signal and application levels | Non-P300 clinical paradigms do not automatically predict speller accuracy | Log device, reference, channel reliability, latency, and packet loss |
| S49 Hinrichs et al. (2021) | Dry-electrode mechanical design and wearing comfort | Pressure, pin geometry, and scalp coupling are engineering variables—not cosmetic details | Comfort/electrical studies are not communication-outcome studies | Build comfort/contact measures into the headset requirements |
| S52 Fiedler et al. (2022) | Multi-center gel/dry cap evaluation | Operator skill, cap fit, impedance, and channel reliability can dominate dry-cap results | Broad EEG measures are not direct P300 utility results | Counterbalance operators and record preparation quality in every session |
| S56 Zhang et al. (2015) | Grouped automatic relevance determination for P300 channels | Structured sparsity is a credible low-channel baseline | Computational selection can be unstable with limited calibration data | Benchmark against forward selection rather than assuming one selector wins |
| S62 Zhang et al. (2022) | Regional smoothing block-sparse Bayesian selection | Anatomical/channel-neighborhood structure can improve sparse selection | Requires careful validation and may be harder to deploy online | Use as an offline benchmark; retain simpler online selector first |
| S68 Kindermans et al. (2014) | Dynamic stopping + transfer learning + language model | A combined adaptive pipeline is prior art | Combining components alone is not novel and language priors can mask EEG mistakes | Separate raw EEG, adaptive, and language-assisted results |
| S79 Spüler et al. (2016) | Error-related activity for correction | Error signals may add a correction path after a bad selection | Error detection itself can fail; it adds time and cognitive demand | Evaluate correction benefit and burden, not only final corrected accuracy |
| S87 Meng et al. (2021) | Tiny adversarial perturbations in BCI spellers | Small perturbations can cause consequential speller errors | Adversarial threat model is not identical to ordinary EEG artifact | Treat robustness, false confidence, and reject behavior as core safety outcomes |

## B. Source-by-source design matrix

### B1. Foundations, paradigms, reviews, and public resources

| Sources | Finding for this project | Gap or caution | Replicate / use / enhance |
|---|---|---|---|
| S01 | The basic oddball-P300 spelling mechanism is viable. | It is a research paradigm, not a modern home-use system. | Replicate standard matrix timing and event labels. |
| S02 | Communication rate is a joint function of speed and accuracy. | A higher raw accuracy can still be a slower or more tiring system. | Report characters/minute, ITR, repetitions, and error cost. |
| S03 | BCI communication must be framed around user control and practical constraints. | Broad review, not evidence that one montage is clinically best. | Use its communication/control boundary in all public claims. |
| S04 | SWLDA/LDA-style classifiers are legitimate P300 benchmarks. | A new neural model must beat these under the same split, not a weaker baseline. | Keep LDA/SWLDA and publish feature settings. |
| S07 | Reference, spatial layout, decimation, and feature count affect performance. | Tuning every setting on the test set produces optimistic results. | Pre-register preprocessing; tune only in training. |
| S08 | A public competition dataset supports reproducible baseline work. | Competition-style data may not represent dry, home, or ALS use. | Use as Phase 0 algorithm verification only. |
| S09 | xDAWN enhances ERP components and is established prior art. | Spatial filtering may be sensitive to montage shifts. | Compare raw and xDAWN features in the benchmark. |
| S13 | Checkerboard designs address row/column adjacency and double-flash issues. | Paradigm changes can alter fatigue and visual demands. | Implement a checkerboard baseline before a custom display. |
| S15–S18 | Reviews show many visual, auditory, tactile, hybrid, and language-assisted variants. | Review averages hide heterogeneous participants and evaluation splits. | Use reviews to identify baselines; cite primary evidence for claims. |
| S19 | Public RSVP/P300 data support reproducible evaluation. | Dataset task and event codes must be verified before reuse. | Version-pin loaders and preserve trial/session grouping. |
| S20 | ERP command-decoding tools exist. | Reusing a toolbox is not an original method. | Compare outputs or reuse for validation where licensing permits. |

### B2. ALS, severe motor disability, and assistive use

| Sources | Finding for this project | Gap or caution | Replicate / use / enhance |
|---|---|---|---|
| S05 | Initial ALS tests support feasibility of P300-based communication. | Very small clinical samples cannot define universal performance. | Use as historical feasibility, not an accuracy target. |
| S06 | Repeated ALS sessions show learning and variability need to be modeled. | Advanced ALS cohorts differ in vision, fatigue, medication, and support. | Include repeated sessions and report per-user trajectories. |
| S10 | Follow-up work matters because one successful session is not deployment. | Follow-up is still not a full home/noise evaluation. | Plan session-transfer and retention tests. |
| S12 | Psychological state and motivation influence BCI performance. | Self-report is imperfect and may be unavailable for some users. | Log fatigue, attention, comfort, and task burden. |
| S21 | Attention correlates with P300 BCI performance in ALS. | Correlation does not specify a decoder fix. | Treat attention as a measured covariate and design shorter/rejectable runs. |
| S22 | Motor impairment groups can show different P300 accuracy. | “Motor impaired” is not one homogeneous population. | Stratify rather than pooling diagnoses. |
| S23 | P300 can contribute to cognitive assessment in ALS. | Cognitive assessment and communication decoding are distinct endpoints. | Do not turn ERP presence into a communication claim. |
| S24–S25 | Latency jitter in ALS can affect performance and correlates. | Fixed 250–600 ms windows may miss user-specific timing. | Compare fixed windows with latency-aware features without test leakage. |
| S26 | Visual paradigms can have different ALS usability/performance. | A higher score may come with greater visual strain. | Include display size, contrast, and visual screening. |
| S27 | Complete immobility research shows the difficulty of interpreting non-response. | Cognitive detection is not proof of reliable spelling. | Keep assessment and communication outcomes separate. |
| S28 | Auditory/visuo-auditory alternatives may help when vision is constrained. | Single/rare cases cannot define a default interface. | Offer auditory/tactile alternatives only after a separate validation path. |
| S29 | Remote training/monitoring is possible. | Telehealth infrastructure and caregiver support may be decisive. | Design logs, remote support, and a minimal troubleshooting flow. |
| S30 | Multilingual language assistance can extend access. | Language priors may correct text without improving EEG evidence. | Evaluate raw decoder and language layer separately. |
| S31 | Embedded hardware can support autonomy. | Embedded proof-of-concept is not a comfort or clinical outcome study. | Keep hardware latency/power as secondary engineering requirements. |
| S32–S35 | Related clinical BCI work broadens the communication context. | Stroke, consciousness disorders, and ALS have different mechanisms and needs. | Use as design/safety context; do not merge efficacy estimates. |

### B3. Dry, semi-dry, wet, and wearable electrode systems

| Sources | Finding for this project | Gap or caution | Replicate / use / enhance |
|---|---|---|---|
| S11 | Dry recording requires careful impedance/noise management. | Hardware results do not guarantee ERP classification. | Add per-channel quality features and amplifier metadata. |
| S36 | Controlled dry P300 may approach gel performance. | Results depend on electrode type, cap, task, and operator. | Treat it as a best-case comparator, not a guarantee. |
| S37 | Solid-gel is a middle ground between wet and dry. | Material convenience alone does not solve fit/cleaning. | Consider semi-dry as a fallback design branch. |
| S38 | Semi-dry designs can support multiple BCI paradigms. | Multi-paradigm feasibility does not prove long-term ALS comfort. | Compare dry and semi-dry before committing to one electrode class. |
| S39 | Different acquisition systems vary in BCI suitability. | A hardware purchase decision cannot be made from headline accuracy alone. | Benchmark latency, noise, reference, API access, and markers. |
| S40 | Wireless dry versus wet comparisons reveal modality-specific trade-offs. | Clinical EEG tasks may differ from P300 timing requirements. | Validate directly with the intended speller task. |
| S41 | Bristle/semi-dry geometries target hair and contact impedance. | Physical contact can raise pressure/discomfort. | Measure pressure points and channel reliability concurrently. |
| S42 | Large dry arrays are technically possible. | More dry channels do not solve low-cost sparse-montage use. | Use as evidence that dry instrumentation is maturing, not as the target design. |
| S43 | Novel comfort-oriented geometries address dry-electrode wearability. | Comfort ratings can be device- and duration-specific. | Add repeated-use comfort, not just immediate post-test comfort. |
| S44 | Hair-adaptive materials can improve coupling. | Manufacturing complexity may conflict with low cost. | Evaluate cost, durability, cleaning, and fit together. |
| S45 | Advanced electrode review maps material options. | Review evidence is heterogeneous and often non-P300. | Use it to define material-selection criteria, not performance promises. |
| S46 | Low-cost mobile BCI systems are feasible in principle. | “Low cost” varies by country, amplifier, and laptop inclusion. | Publish a transparent bill of materials and operating cost. |
| S47 | Consumer systems need task-specific BCI benchmarking. | Consumer claims can hide data-access and marker-timing limitations. | Require raw data, stable sampling, and event-marker verification. |
| S48 | Home monitoring research highlights patient-controlled deployment. | Monitoring success is not communication success. | Borrow usability, training, and support measures. |
| S49–S51 | Electrode geometry/material affects impedance, motion, and comfort. | Better impedance is not sufficient without robust decoding. | Co-design mechanics with signal-quality thresholds. |
| S52 | Multi-center evidence shows operator/fit effects are large. | Multi-center EEG metrics are not a direct P300 comparison. | Randomize operator/order and log preparation experience. |
| S91 | The most direct dry/wet P300 evidence indicates a remaining SNR gap. | Specific g.Sahara system and study protocol may not represent new electrode designs. | Make this the reference failure mode: slow drift + transient artifacts + low SNR. |

### B4. Sparse montages and channel selection

| Sources | Finding for this project | Gap or caution | Replicate / use / enhance |
|---|---|---|---|
| S14 | Sparse spatial filtering can select informative sensors. | Selection can be sensitive to calibration quality. | Compare a sparse filter to direct subset selection. |
| S53 | Sequential selection can outperform poor fixed channel sets. | A selector may overfit an individual session. | Use nested CV and report selection stability. |
| S54 | Four posterior channels can be sufficient in one prospective setting. | It is not evidence that `PO7/PO8/POz/CPz` is universal. | Test 4–6 channels versus the reference in each new cohort. |
| S55 | Exhaustive, forward, and backward selection can differ. | Exhaustive search may be infeasible online and unstable with few trials. | Use simple forward/backward methods as transparent baselines. |
| S56 | Grouped relevance can encode channel structure. | More complex models need enough calibration data. | Add only after simple selectors are reproduced. |
| S57 | Phase information can be useful for selection. | P300 phase features may be sensitive to filtering/timing. | Include as an ablation, not a default. |
| S58 | Mobile P300 configurations depend on classifier and montage together. | Mobility conditions can introduce confounds. | Evaluate classifier × montage interactions. |
| S59 | Subject-specific and subject-independent selection differ. | A subject-independent set may sacrifice individual performance. | Report both a fixed deployable set and individualized selection. |
| S60 | Joint spatiotemporal selection can reduce features. | Semi-supervision assumptions may fail on noisy clinical data. | Use only with declared labels/adaptation data. |
| S61 | Wavelet/PSO approaches broaden the baseline family. | Heuristic optimizers can be hard to reproduce and may overfit. | Keep only if they beat transparent baselines on held-out sessions. |
| S62 | Block-sparse Bayesian methods exploit spatial neighborhood. | Computational and calibration burden may be high. | Offline benchmark first; do not call it a real-time default. |
| S63 | Source-informed selection is reviewed across BCI paradigms. | Source localization adds model assumptions and may not help a low-cost headset. | Treat source guidance as exploratory, not an input requirement. |
| S64–S65 | System-design and Bayesian LDA work show selection/input design interact. | Distinct languages and interfaces change prior probabilities. | Specify alphabet, language, and symbol layout in every benchmark. |

### B5. Adaptive stopping, asynchronous operation, language, and correction

| Sources | Finding for this project | Gap or caution | Replicate / use / enhance |
|---|---|---|---|
| S66 | Bayesian stopping updates candidate probability per flash. | Miscalibrated likelihoods cause confident wrong stops. | Calibrate on validation data; plot reliability and selective risk. |
| S67 | ALS dynamic stopping can improve communication rate. | Clinical samples are small and protocol-specific. | Use a fixed-versus-adaptive ALS-relevant benchmark. |
| S68 | Transfer, dynamic stopping, and language models have already been combined. | A component bundle is not original. | Novelty must come from contact-aware safety and held-out validation. |
| S69–S70 | Language priors/HMMs can improve online communication. | Text priors can obscure neural evidence and disadvantage nonstandard language. | Make language optional; report raw and assisted accuracy separately. |
| S71 | Self-calibration can reduce labelled training. | Unsupervised adaptation may drift or leak target-session information. | Compare it with no adaptation and supervised recalibration. |
| S72 | New early-stopping methods remain an active area. | “Earlier” can simply mean more wrong selections. | Report accuracy, coverage, error cost, and burden jointly. |
| S73 | Subject-independent ERP BCI is possible. | Cross-user methods often underperform user-specific calibration. | Present zero-calibration as a baseline, not the only product mode. |
| S74 | Active-inference framing formalizes adaptive decisions. | More elaborate theory does not replace empirical calibration. | Compare against Bayesian stopping with equal information. |
| S75 | Stimulus timing can be tuned online. | Faster timing can harm weaker users or increase fatigue. | Use bounded personalized SOA trials and safety limits. |
| S76 | Asynchronous P300 control addresses no-intent operation. | Asynchronous errors are more safety-critical than copy-spelling errors. | Include no-intent blocks and false-activation metrics. |
| S77 | Utility metrics address more than accuracy. | Utility definitions embed assumptions about cost. | State the cost of wrong, rejected, and slow selections. |
| S78 | Detectability may predict P300 performance. | Predictor thresholds may not transport to another electrode type. | Evaluate contact/quality signals prospectively. |
| S79 | Error-related signals can auto-correct some selections. | Correction may be unavailable in fatigued or low-SNR users. | Use as optional confirmation, not sole safety layer. |
| S80 | Auditory dynamic spelling gives an accessibility alternative. | Auditory rate and cognitive load often differ from visual P300. | Keep as a separate accessibility branch. |
| S81 | Flashing paradigm and language model choices remain active research. | Newer online typing studies can still be narrow/healthy cohorts. | Use as an up-to-date comparator after reproducing classical baselines. |
| S82 | Practitioners identify device/service needs beyond decoding. | Opinion studies do not establish technical efficacy. | Convert needs into requirements: setup, cleaning, support, repair, fallback. |

### B6. Modern processing, latency, and robustness

| Sources | Finding for this project | Gap or caution | Replicate / use / enhance |
|---|---|---|---|
| S83 | CNN P300 detection is established prior art. | Deep models can overfit small P300 data and obscure failure causes. | Use a compact CNN only after LDA/xDAWN baselines. |
| S84 | Semi-supervised online learning may reduce labels. | Training dynamics can confuse adaptation with leakage. | Isolate adaptation data and test it on later sessions only. |
| S85 | Latency-aware estimation helps assess P300 performance. | Latency estimates can be noisy and user/task-specific. | Add latency as a diagnostic and optional feature. |
| S86 | Wearable subject-independent P300 learning is an active benchmark. | Wearability claim needs hardware-specific validation. | Use as a modern ML comparator, not a direct performance target. |
| S87 | Small perturbations can cause speller errors. | Controlled adversarial noise differs from everyday artifacts. | Stress-test confidence under slow drift, transient peaks, motion, and packet loss. |
| S88 | Audio-visual P300 can broaden access. | Multimodal stimuli add timing and attentional complexity. | Evaluate only if visual screening reveals need. |
| S89 | Weak/hidden target conditions test low-SNR target detection. | RSVP task results may not transfer directly to matrix spelling. | Use as a low-SNR methodological control. |
| S90 | Environment and electrode configuration jointly affect P300 quality. | Conference-scale study may need independent replication. | Directly test environment × montage in the planned protocol. |

## C. Decision synthesis: what we can do now

### C1. Replicate now with public data and the existing code

1. **Standard P300 baseline:** matrix/checkerboard task, fixed repetitions, LDA/SWLDA, and documented event markers (S01, S04, S07, S13).
2. **Spatial-filter baseline:** raw versus xDAWN plus the same classifier (S09).
3. **Montage curve:** full reference, 6, 5, and 4 channels; fixed standard set, forward/backward, and sparse selector (S14, S53–S62).
4. **Sequential baseline:** fixed versus Bayesian dynamic stopping, with a maximum-repetition limit and calibration analysis (S66–S78).
5. **Low-SNR diagnostics:** slow-band power, transient peaks, channel reliability, and performance versus quality (S78, S89–S91).

### C2. Integrate in the first actual headset prototype

- A 4–6 channel posterior/parietal candidate layout plus reference/ground, but do not freeze placement before data.
- Dry and semi-dry electrode branches; evaluate cost, setup, comfort, and signal quality together.
- Per-channel contact-quality status based on impedance when available and signal-derived quality measures when not.
- Artifact-aware epoch flags; do not feed flagged flashes into confident evidence accumulation without an explicit policy.
- A calibrated sequential decoder with `ACCEPT`, `REPEAT`, `REJECT`, and `RE-SEAT HEADSET` outcomes.
- A transparent, versioned output file containing raw scores, quality flags, selected channels, and final decision.

### C3. Enhance only after baselines pass

- User-specific latency alignment.
- Structured sparse/Bayesian selection.
- Cross-session transfer or limited calibration.
- Error-related correction.
- Optional language model, separately audited.
- Auditory/multimodal interface for users for whom the visual task is inaccessible.

### C4. Do not claim before evidence exists

- Same accuracy as wet electrodes for every user.
- Clinical benefit for ALS participants.
- Lower cost without a published bill of materials and maintenance cost.
- Safety because the model is confident.
- Generalization to home, noise, movement, or different devices from one lab session.
- Novelty merely from combining old components.

## D. The experiment that can close the gap

**Hypothesis:** A contact-aware 4–6 electrode dry/semi-dry P300 headset with calibrated adaptive abstention can achieve pre-specified non-inferior *accepted-output* accuracy to a conventional 8-channel wet reference on held-out sessions, while reducing setup burden and preserving acceptable comfort.

**Critical design:** within-participant, counterbalanced wet/dry(or semi-dry) sessions; same visual paradigm; frozen primary metric; training-only channel/threshold selection; held-out session; no-intent blocks; and separate raw-versus-language-assisted reporting.

**Primary metric:** accepted-output character accuracy and selective risk on the held-out session.

**Required co-outcomes:** setup time, comfort, false activation, rejection rate, repetitions/character, contact failure rate, slow-band/transient-artifact burden, and user/session variability.

**Success:** the sparse system meets the pre-registered margin without unacceptable false activations or burden.

**Useful failure:** it identifies whether the limiting factor is contact mechanics, low-frequency drift, transient artifact, classifier calibration, visual task accessibility, or a genuinely insufficient sparse montage. That diagnosis is already a reusable research result.

