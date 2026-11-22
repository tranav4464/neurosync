# Neurosync P300 — Research, Gap, Replication, and Outcome Review

**Prepared:** 22 November 2026  
**Team:** Neurosync · Team 7601  
**Review type:** Targeted scoping review and engineering audit  
**Corpus:** 91 research papers, reviews, datasets, and enabling EEG studies listed in the source register below

> This is a research-planning document, not a clinical recommendation. It distinguishes established prior art, a proposed integration gap, synthetic software evidence, and human/ALS validation that has not yet been performed by Neurosync.

## 1. What we actually want

Neurosync should build a **safe, low-channel, non-invasive P300 communication aid** for people with severe motor impairment, including people with ALS who can still reliably attend the visual task. The system should let a user select letters or commands by attending to rare target flashes. It should not be described as unrestricted thought reading, diagnosis, or complete reconstruction of brain activity.

The project has four linked requirements:

1. **Communication function:** select a character or command and display the confidence of that selection.
2. **Practical form:** use a comfortable 4–6 electrode headset target, with dry or semi-dry electrodes considered for faster setup and home use.
3. **Signal robustness:** handle slow baseline drift, contact-quality changes, movement/eye/muscle artifacts, and different users and sessions.
4. **Safety and honesty:** support a visible `repeat/reject` state, calibrated uncertainty, held-out evaluation, and a fallback communication method.

### The primary outcome

The primary outcome should be:

> **On held-out participants or held-out sessions, can a 4–6 electrode system select characters with a pre-specified non-inferiority margin versus a conventional reference montage while reducing setup burden, and can it refuse uncertain selections instead of silently producing a wrong command?**

This outcome is more meaningful than a high synthetic accuracy number. It tests the complete user-facing trade-off: accuracy, speed, setup time, comfort, contact stability, false activation, and safe refusal.

### Secondary outcomes

- Character accuracy and balanced target/non-target performance.
- Selective risk: error rate among accepted outputs at a stated coverage level.
- False activation rate when the user is not intentionally selecting.
- Characters per minute, information-transfer rate, flashes per character, and average repetitions.
- Calibration time, setup time, channel failure rate, and operator assistance.
- Comfort, pressure, skin/hair tolerance, fatigue, and willingness to reuse the headset.
- Low-frequency power, artifact rate, impedance/contact stability, and performance drift over a session.
- Transfer from one day, operator, device, or electrode type to another.

The exact non-inferiority margin and safety thresholds should be fixed with a research mentor and clinical/communication partner before the human test. They should not be chosen after seeing the held-out results.

### Candidate project framing: NeuroSync CASP

**NeuroSync CASP** stands for **Contact-Aware Adaptive Sparse P300**. It frames the work as a headset-and-algorithm co-design project:

> Can a low-cost, custom-fit 4–6 electrode dry or semi-dry headset use real-time contact-quality and artifact information to adapt its channel weighting and stopping decision, while remaining non-inferior to a conventional 8-channel wet P300 reference on held-out communication sessions?

The proposed innovation is not the use of P300, dry electrodes, a small montage, or adaptive stopping in isolation. The testable contribution is the **closed loop between headset contact quality and decoder behavior**:

1. The headset reports a contact-quality estimate for every electrode.
2. The decoder detects slow drift, transient artifacts, line noise, and implausible amplitude changes.
3. Channel weights or the selected subset are updated only under a pre-declared adaptation rule.
4. The sequential decoder either accepts the character, collects another repetition, asks the user to re-seat the headset, or rejects the selection.
5. The complete system is evaluated against an 8-channel wet reference for accuracy, setup time, comfort, cost, and false activation.

This gives the project a falsifiable innovation claim: **contact-aware adaptation should preserve accepted-output performance while reducing electrode count and setup burden.** If it does not, the contribution is still a useful negative result showing where the low-cost design fails.

## 2. What the prior work says

### 2.1 P300 spelling is established, not a new invention

The P300 speller has been studied since the original mental-prosthesis work and is supported by a mature body of work on oddball ERPs, row/column and alternative visual paradigms, classification, language assistance, and clinical use. Foundational studies established the paradigm, the speed/accuracy trade-off, and feasibility for people with ALS or severe motor impairment. Reviews describe a large design space rather than a single best speller.

**Implication for Neurosync:** the novelty cannot be “we use a P300 speller.” The contribution must be a specific, measurable improvement in deployment robustness or validation quality.

### 2.2 ALS use is feasible but highly variable

Studies with ALS and other severely motor-disabled participants show that P300-based communication can work, but performance varies with attention, motivation, fatigue, visual function, disease stage, setup, and individual neural/behavioral timing. Home and remote training are possible, but a lab result does not automatically establish home reliability.

**Implication:** the test unit must be the participant and session, not thousands of correlated epochs. The protocol must log visual ability, fatigue, operator help, session time, and failed/repeated trials. A participant who cannot use the visual task should not be counted as a decoder failure without reporting the accessibility issue separately.

### 2.3 Four-to-six channel selection is already prior art

Reduced electrode configurations, active channel selection, sparse spatial filtering, grouped relevance methods, phase-based selection, and block-sparse Bayesian selection have all been proposed. One influential optimization study reported a four-posterior-electrode configuration and prospective testing without a significant loss relative to a full configuration. Other work shows that the best subset is participant- and method-dependent; poor channel sets can make an otherwise usable speller fail.

**Implication:** “4–6 electrodes” is a design constraint and a replication target, not by itself a novel algorithm. Neurosync must use nested or trial-level selection, compare against standard montages, and test whether the chosen subset remains useful on a later session or a new participant.

### 2.4 Dry electrodes create a real but conditional trade-off

Dry electrodes can reduce gel application, cleaning, and setup time. Some P300 studies reported performance comparable to gel electrodes under controlled conditions. Other direct comparisons—including healthy participants and participants with ALS/PLS—reported lower dry-system SNR, lower accuracy/bit rate, increased slow-frequency power, transient artifacts, and greater sensitivity to contact and movement. Multi-center dry-cap work shows that operator skill, channel reliability, pressure, hair, fit, and device design materially affect the outcome.

**Implication:** “dry electrodes are better” and “dry electrodes are unusable” are both too broad. The design target is a particular electrode/headset geometry plus measured contact quality and artifact handling. A dry-vs-wet test must compare the same users, task, montage, order, and session schedule.

### 2.5 Adaptive stopping is established, but it does not magically recover SNR

Bayesian and probabilistic dynamic stopping methods update character probabilities after each flash and stop when confidence passes a threshold. They can improve communication rate and may partly compensate for low SNR by collecting more flashes. The dry-electrode P300 comparison found that dynamic collection improved dry performance but did not fully reach wet-system performance; its authors identified slow-wave and transient artifacts as unresolved causes.

**Implication:** adding another stopping threshold is not a sufficient research gap. Neurosync needs calibrated probabilities, temporal/stability checks, a reject/repeat state, a maximum-burden rule, and tests that separate “more data helped” from “the classifier became confidently wrong.”

### 2.6 Language models and error correction are also established

Language models, hidden Markov models, multilingual assistance, self-calibration, online learning, subject-independent models, and error-related potentials have all been used to improve speed, correction, or calibration. They can be useful in Neurosync, but they can also hide the underlying EEG error by making text look fluent.

**Implication:** language assistance should be a downstream, optional layer. Report raw EEG selection, language-corrected selection, and rejected/ambiguous outputs separately. The system must not use a language model to claim that a wrong EEG selection was neurally correct.

## 3. The defensible gap

The gap is **not** an absent component. The field already contains papers on sparse montages, dry electrodes, P300 classifiers, dynamic stopping, language models, and ALS communication.

The defensible gap is an **under-validated intersection**:

> A patient-centered, 4–6 electrode P300 communication pipeline that combines electrode/contact quality, low-frequency and transient artifact handling, individualized channel selection, calibrated adaptive stopping, and safe abstention, then evaluates the full system under held-out sessions, dry/wet comparison, realistic noise, and user burden.

The gap has four parts:

| Gap | What exists | What remains to solve | Neurosync contribution |
|---|---|---|---|
| Sparse montage under deployment variation | Four-channel and channel-selection studies | Stability across users, sessions, operators, hair/fit, and dry-electrode noise | Nested selection plus held-out-session benchmark |
| Dry-electrode signal quality | Dry/wet comparisons and improved electrode materials | Contact drift, slow-wave/transient artifacts, movement, and user-specific fit | Contact-quality features, artifact/reject model, and custom-fit design requirements |
| Adaptive stopping | Bayesian posterior thresholds and dynamic collection | Calibration, temporal dependence, false confidence, fatigue burden, and safe refusal | Calibrated sequential decision rule with stability and abstention |
| Evidence of real usefulness | Many offline or controlled online accuracy results | Setup time, comfort, repeated use, noisy/home conditions, and participant-level outcomes | A complete outcome protocol and reproducible report |

This is a credible research contribution only if the improvement is demonstrated on data not used to choose channels, thresholds, or the final algorithm. If a standard method performs equally well, the correct conclusion is that Neurosync produced a useful replication/benchmark, not a new algorithm.

## 4. Audit of the work already in this workspace

### What is already implemented

The existing `Neurotech/Create/Neurosync P300` prototype contains:

- Baseline correction and a 0.5–20 Hz frequency-domain filter.
- A 250–600 ms feature window.
- Forward selection constrained to 4–6 channels.
- Regularized diagonal LDA.
- Per-symbol evidence accumulation.
- Confidence, margin, and consecutive-symbol stability for adaptive stopping.
- Synthetic wet/dry data with slow drift and higher dry noise.
- NPZ data loading and a held-out train/test runner.
- Unit tests and reproducible JSON/Markdown demo output.

### What the current prototype can legitimately claim

- The software path is executable and reproducible.
- The code can demonstrate an engineering trade-off under a controlled synthetic signal model.
- The components correspond to established P300 methods and can serve as a baseline.
- The prototype exposes where channel selection and adaptive stopping decisions are made.

### What it cannot claim yet

- Human or ALS performance.
- A clinically useful headset.
- A validated dry-electrode noise model.
- Generalization across people, days, operators, rooms, or devices.
- Clinical safety, communication benefit, or superiority over eye tracking/other AAC.
- A novel algorithm solely because the implementation combines familiar components.

The current demo uses six directly flashed symbols. A full row/column or checkerboard keyboard with synchronized hardware markers, realistic timing, accessible visual presentation, and a no-intent/reject state is still required before human testing.

## 5. What to replicate, integrate, and enhance

### Replicate first

| Prior method | Replication target | Why it matters |
|---|---|---|
| Foundational row/column P300 spelling | Standard target/non-target paradigm and SWLDA/LDA baseline | Establish a trusted reference before changing the hardware |
| xDAWN/spatial filtering | Compare spatial enhancement against raw-channel baselines | Prevent a channel-selector result from being mistaken for a better classifier |
| Four-channel electrode optimization | Reproduce the published reduced montage on a public dataset | Check whether the claimed reduction transfers to a different split/device |
| Channel-selection families | Compare forward, backward, SSNR, sparse, grouped-relevance, and fixed standard sets | Quantify selection stability and avoid cherry-picking one selector |
| Bayesian dynamic stopping | Reproduce fixed versus dynamic accuracy, rate, and repetitions | Verify calibration and subject-specific behavior |
| Dry/wet P300 comparison | Match montage, flash timing, repetitions, and order | Connect the new test directly to the strongest prior dry-electrode evidence |
| Language-model assistance | Compare raw EEG output with corrected output and a text-only baseline | Keep linguistic prior knowledge from hiding EEG errors |
| Error-related correction | Test whether error signals reduce false activation without increasing fatigue | Add a safe correction path, not just a higher headline accuracy |

### Integrate

1. **Montage selection + contact quality:** choose among 4–6 channels using training data while logging impedance, packet loss, variance, low-frequency power, and transient peaks.
2. **Artifact-aware decoding:** classify or down-weight epochs with blink, muscle, motion, contact, or amplifier artifacts instead of treating every large waveform as P300 evidence.
3. **Calibrated sequential decisions:** accumulate evidence using a participant-calibrated likelihood or conformal/selective rule, require top-symbol stability, cap repetitions, and allow reject.
4. **User and session adaptation:** adapt only with explicitly declared calibration data; compare no-adaptation, unsupervised-adaptation, and supervised-recalibration conditions.
5. **Accessible communication layer:** expose confidence and repeat options, provide large/high-contrast stimuli, allow auditory or alternative paradigms where vision is limited, and preserve an independent fallback.

### Enhance, where the evidence supports it

- Replace the synthetic direct-flash task with a timed row/column or checkerboard paradigm.
- Add a full hardware timestamp path using LSL/BrainFlow or a validated amplifier SDK.
- Add nested channel selection so the test session cannot influence the montage.
- Add probability calibration plots, Brier score, expected calibration error, and selective-risk curves.
- Add a separate false-activation/no-intent condition.
- Add online contact-quality alarms and a visible “re-seat headset” instruction.
- Test 4, 5, 6, and standard-montage cost curves instead of assuming that fewer is better.
- Report participant/session-level confidence intervals, not only epoch counts.
- Compare 0.5–4 Hz and 4–8 Hz power, transient peak rates, and baseline drift explicitly because the dry-electrode P300 evidence implicates slow and transient artifacts.
- Treat language modeling as a separate ablation with a text-only prior and a no-language baseline.

## 6. Proposed Neurosync algorithm

```text
EEG + flash markers
  → channel/contact quality check
  → robust reference and baseline estimation
  → artifact flags and low-frequency/transient-noise features
  → 250–600 ms ERP feature extraction
  → nested 4–6 channel selection on training data only
  → calibrated target/non-target classifier
  → symbol-level sequential evidence update
  → stability + confidence + margin + burden rule
  → ACCEPT character / REPEAT / REJECT / RE-SEAT HEADSET
```

### Candidate decision rule

At repetition (r), maintain a posterior or calibrated score (P(c mid x_{1:r})) for each candidate character (c). Stop only when all conditions hold:

1. The best character exceeds a pre-registered confidence threshold.
2. Its margin over the runner-up exceeds a pre-registered threshold.
3. The same character remains best for a stability window.
4. Contact quality and artifact flags are acceptable.
5. The number of repetitions is within a user-specific burden limit.

If the quality or uncertainty checks fail, return `REPEAT` or `RE-SEAT`, not a guessed letter. This is a proposed design; it is not yet validated.

## 7. Minimal experiments that can answer the gap

### Phase 0 — public-data reproduction

Use a version-pinned public P300 dataset and reproduce one standard baseline before fitting the Neurosync model. Keep all epochs from a trial together. If multiple sessions exist, split by session. If only one session exists, use blocked evaluation and label the limitation.

Compare:

- Standard montage + SWLDA/LDA.
- Fixed 4, 5, and 6-channel sets.
- Forward/backward/SSNR/sparse channel selection.
- Raw features versus xDAWN or another established spatial filter.
- Fixed repetitions versus Bayesian dynamic stopping.
- With and without language modeling.

**Decision gate:** if the baseline cannot be reproduced, stop model development and fix data/event/provenance issues first.

### Phase 1 — controlled healthy-participant test

Use the same participants, same task, same stimulus timing, and counterbalanced wet/dry or wet/semi-dry sessions. Record a conventional reference montage at the same time if hardware allows. Freeze the analysis plan before inspecting held-out performance.

Log:

- Electrode type, position, fit, pressure, impedance/contact quality, hair/skin notes.
- Flash timestamps, amplifier timestamps, packet loss, reference/ground, and sampling rate.
- Blinks, eye movement, facial/muscle events, movement, room noise, and operator intervention.
- Setup time, cleaning time, comfort, pressure points, fatigue, and session abandonment.

### Phase 2 — realistic robustness test

Test quiet, conversation, small head movement, naturalistic posture, and longer sessions. Include a no-intent condition. Test transfer across day and operator. The primary analysis must remain participant/session held out.

### Phase 3 — ALS/clinical collaboration

Only after the pipeline is technically characterized, conduct an approved study with a hospital or ALS research group. Include visual, cognitive, motor, communication, and fatigue screening. Use consent, an independent fallback communication method, and a protocol for stopping if the headset causes pressure, discomfort, confusion, or distress.

## 8. Evaluation plan and failure criteria

### Primary analyses

- Character accuracy per participant and per session.
- Selective risk versus coverage for accepted outputs.
- False activation rate in no-intent blocks.
- Held-out-session or held-out-participant performance.
- Accuracy/setup-time/comfort trade-off for each montage.

### Secondary analyses

- Information-transfer rate and characters per minute.
- Repetitions per character and adaptive stopping savings.
- Channel-selection stability across bootstrap samples and sessions.
- Calibration error and reliability diagrams.
- Relationship between contact quality, low-frequency power, artifact burden, and errors.
- User-reported comfort, fatigue, and willingness to repeat the session.

### Stop/revise conditions

- Performance is explained by flash timing, block position, cue leakage, or eye/muscle signals.
- Selection works within-session but fails on the next session.
- Confidence is high on incorrect or no-intent trials.
- Dry electrodes save setup time but create unacceptable pressure, fatigue, or false activations.
- The language model improves text fluency while raw EEG accuracy worsens or errors become less visible.
- Four to six electrodes do not meet the pre-registered margin; keep the conventional montage or revise the hardware rather than forcing the claim.

## 9. What other researchers could reuse

A successful Neurosync release should contain:

- Version-pinned dataset adapters and event-code documentation.
- A standard P300 baseline and all reduced-montage baselines.
- Nested channel selection and fixed evaluation splits.
- Contact-quality and artifact logs.
- Calibrated sequential decoding with accept/repeat/reject outputs.
- Subject/session/device transfer tests.
- Raw, corrected, and rejected outputs separated in the report.
- Failure examples and negative results.
- A runnable command that recreates every table and figure.

The reusable contribution would therefore be a **benchmarkable, safety-aware low-channel deployment framework**, not merely another classifier name.

## 10. Strongest argument against the recommendation

The strongest argument against this project is that P300 spelling, electrode reduction, dry EEG, dynamic stopping, language models, and ALS use are all crowded fields. The integrated system may produce no meaningful advantage over a well-tuned conventional headset or over eye tracking for users who can control their eyes. A four-channel headset could also reduce contact quality so much that the lower setup burden is not worth the communication errors. If held-out data show this, the evidence should move the team toward a different AAC interface, hybrid eye/EEG system, or a research tool for understanding contact-quality failure rather than claiming a universal low-cost solution.

The project should continue only if the controlled experiment shows a concrete benefit at the level of the primary outcome: comparable accepted-output performance, fewer setup resources, acceptable comfort, and safer uncertainty handling under conditions where the baseline and closest prior methods are fairly compared.

## 11. Source register — 91 sources screened and annotated

The register is a targeted evidence map, not a claim that every paper in the entire BCI field has been exhaustively reviewed. Abstracts and metadata were screened across PubMed/PMC and DOI records; the key dry-electrode, channel-selection, dynamic-stopping, and P300-review sources were checked in full text where accessible. Preprints and reviews are labelled by their role.

### Foundations, paradigms, reviews, and data

| ID | Source | Use in this project |
|---|---|---|
| S01 | [Farwell & Donchin 1988 — Talking off the top of your head](https://pubmed.ncbi.nlm.nih.gov/2461285/) | Original P300 mental-prosthesis paradigm. |
| S02 | [Donchin, Spencer & Wijesinghe 2000 — The mental prosthesis](https://pubmed.ncbi.nlm.nih.gov/10896179/) | Speed/accuracy and communication-rate framing. |
| S03 | [Wolpaw et al. 2002 — Brain-computer interfaces for communication and control](https://pubmed.ncbi.nlm.nih.gov/12048038/) | BCI scope and clinical context review. |
| S04 | [Krusienski et al. 2006 — Comparison of classification techniques for the P300 Speller](https://pubmed.ncbi.nlm.nih.gov/17124334/) | Standard classifier baseline. |
| S05 | [Sellers & Donchin 2006 — Initial tests by ALS patients](https://pubmed.ncbi.nlm.nih.gov/16461003/) | Early ALS feasibility evidence. |
| S06 | [Nijboer et al. 2008 — P300 BCI for people with ALS](https://pubmed.ncbi.nlm.nih.gov/18571984/) | Clinical population and variability. |
| S07 | [Krusienski et al. 2008 — Toward enhanced P300 speller performance](https://pubmed.ncbi.nlm.nih.gov/17822777/) | Reference, spatial, decimation, and feature choices. |
| S08 | [Rakotomamonjy & Guigue 2008 — BCI Competition III dataset II](https://pubmed.ncbi.nlm.nih.gov/18334407/) | Public benchmark and strict split baseline. |
| S09 | [Rivet et al. 2009 — xDAWN algorithm](https://pubmed.ncbi.nlm.nih.gov/19174332/) | Established spatial enhancement baseline. |
| S10 | [Kübler et al. 2009 — P300 communication follow-up in ALS](https://pubmed.ncbi.nlm.nih.gov/20582284/) | Longer-term/clinical follow-up context. |
| S11 | [Liao et al. 2010 — Dry electrode bio-potential recordings](https://pubmed.ncbi.nlm.nih.gov/21096726/) | Dry-electrode acquisition constraints. |
| S12 | [Kübler et al. 2010 — Psychological state and ALS BCI performance](https://pubmed.ncbi.nlm.nih.gov/20700521/) | Motivation and state as performance covariates. |
| S13 | [Townsend et al. 2010 — Moving beyond rows and columns](https://pubmed.ncbi.nlm.nih.gov/20347387/) | Alternative stimulus design. |
| S14 | [Zhang et al. 2011 — EEG sensor selection by sparse spatial filtering](https://pubmed.ncbi.nlm.nih.gov/21096264/) | Sparse spatial/channel selection. |
| S15 | [A comprehensive review of EEG-based BCI paradigms 2019](https://doi.org/10.1088/1741-2552/aaf12e) | Broader BCI evaluation context. |
| S16 | [Brain-Computer Interface Spellers: A Review 2018](https://pubmed.ncbi.nlm.nih.gov/29601538/) | Speller paradigm and evaluation review. |
| S17 | [Advances in P300 spellers 2022](https://doi.org/10.3389/fnhum.2022.1077717) | Paradigm and performance review. |
| S18 | [Non-invasive EEG-based BCI spellers from the beginning to today 2023](https://doi.org/10.3389/fnhum.2023.1216648) | Recent mini-review and gap framing. |
| S19 | [EEG dataset for RSVP and P300 spellers 2022](https://pubmed.ncbi.nlm.nih.gov/35803976/) | Public data and reproducibility resource. |
| S20 | [A toolbox for decoding BCI commands based on ERPs 2024](https://pubmed.ncbi.nlm.nih.gov/38505100/) | Software/reproducibility comparator. |

### ALS, severe motor disability, and assistive communication

| ID | Source | Use in this project |
|---|---|---|
| S21 | [Attention and P300 BCI performance in ALS 2013](https://pubmed.ncbi.nlm.nih.gov/24282396/) | Attention/performance variability. |
| S22 | [Accuracy of a P300 speller for people with motor impairments 2011](https://pubmed.ncbi.nlm.nih.gov/22208117/) | Motor-disability comparison. |
| S23 | [Cognitive assessment in ALS by P300 BCI 2016](https://pubmed.ncbi.nlm.nih.gov/27169693/) | ALS cognitive/ERP considerations. |
| S24 | [P300 jitter latency and its correlates in ALS 2021](https://pubmed.ncbi.nlm.nih.gov/33279436/) | Participant-specific timing and jitter. |
| S25 | [P300 jitter, BCI, and ALS 2021](https://pubmed.ncbi.nlm.nih.gov/33339727/) | Timing relevance to decoding. |
| S26 | [Evaluating BCI performance in an ALS population 2018](https://pubmed.ncbi.nlm.nih.gov/29076357/) | Paradigm comparison in ALS. |
| S27 | [Screening cognitive function in complete immobility 2018](https://pubmed.ncbi.nlm.nih.gov/30158845/) | Accessibility and severe impairment context. |
| S28 | [Visuo-auditory P300 BCI with an ALS CLIS participant 2022](https://pubmed.ncbi.nlm.nih.gov/35817307/) | Alternative modality and CLIS boundary. |
| S29 | [TeleBCI remote training and monitoring 2020](https://pubmed.ncbi.nlm.nih.gov/33763499/) | Remote/home deployment considerations. |
| S30 | [Extending BCI access with a multilingual language model 2022](https://pubmed.ncbi.nlm.nih.gov/35574291/) | Language assistance and accessibility. |
| S31 | [FPGA-embedded BCI for locked-in individuals 2022](https://pubmed.ncbi.nlm.nih.gov/35009860/) | Embedded implementation and autonomy. |
| S32 | [Noninvasive BCI communication after brainstem stroke 2014](https://pubmed.ncbi.nlm.nih.gov/25298323/) | Related clinical communication evidence. |
| S33 | [Rapid P300 BCI communication with a head-mounted display 2015](https://pubmed.ncbi.nlm.nih.gov/26097447/) | Display and speed design. |
| S34 | [Cognitive processing in non-communicative patients 2016](https://pubmed.ncbi.nlm.nih.gov/27895567/) | ERP interpretation in non-communicative users. |
| S35 | [BCIs for consciousness assessment and communication 2020](https://pubmed.ncbi.nlm.nih.gov/32164848/) | Consciousness/communication boundary. |

### Electrode technology, dry/wet comparisons, and wearability

| ID | Source | Use in this project |
|---|---|---|
| S36 | [Comparison of dry and gel-based electrodes for P300 BCI 2012](https://pubmed.ncbi.nlm.nih.gov/22586362/) | Controlled dry/wet P300 comparison. |
| S91 | [Clements et al. 2016 — Dynamic data collection for dry-electrode P300 BCI](https://pubmed.ncbi.nlm.nih.gov/27819250/) | Key healthy and ALS/PLS dry-versus-wet comparison; dynamic stopping improved but did not fully eliminate the dry-system gap. |
| S37 | [A non-adhesive solid-gel electrode 2012](https://pubmed.ncbi.nlm.nih.gov/22826701/) | Gel-free/semi-dry design option. |
| S38 | [Novel semi-dry electrodes for BCI 2016](https://pubmed.ncbi.nlm.nih.gov/27378253/) | Semi-dry design and multi-paradigm testing. |
| S39 | [Evaluation of different EEG acquisition systems 2016](https://pubmed.ncbi.nlm.nih.gov/27746714/) | Device/system comparison. |
| S40 | [Wireless dry versus wired wet EEG for clinical applications 2020](https://pubmed.ncbi.nlm.nih.gov/32251333/) | Portable versus conventional recording. |
| S41 | [Bristle-shaped semi-dry electrode 2020](https://pubmed.ncbi.nlm.nih.gov/31170063/) | Hair/scalp coupling design. |
| S42 | [High-density 256-channel dry EEG cap 2022](https://pubmed.ncbi.nlm.nih.gov/34796574/) | Dry cap scalability and reliability. |
| S43 | [Novel flower electrodes for comfortable dry EEG 2023](https://pubmed.ncbi.nlm.nih.gov/37789022/) | Comfort/contact trade-off. |
| S44 | [Hairy-skin-adaptive viscoelastic dry electrodes 2023](https://pubmed.ncbi.nlm.nih.gov/37072159/) | Fit and hair adaptation. |
| S45 | [Advanced electrode technologies for noninvasive BCI 2023](https://pubmed.ncbi.nlm.nih.gov/38064282/) | Electrode technology review. |
| S46 | [Design and validation of a low-cost mobile EEG BCI 2023](https://pubmed.ncbi.nlm.nih.gov/37447780/) | Low-cost/mobile system constraints. |
| S47 | [Consumer-grade wireless EEG for BCI 2024](https://pubmed.ncbi.nlm.nih.gov/39465107/) | Hardware and signal-quality evaluation. |
| S48 | [Patient-controlled EEG home-monitoring feasibility 2022](https://pubmed.ncbi.nlm.nih.gov/35653930/) | Home usability and longitudinal burden. |
| S49 | [The arch electrode for wearing comfort 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8558300/) | Mechanical comfort versus coupling. |
| S50 | [Dry EEG electrodes review 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4168519/) | Dry-electrode methods and limitations. |
| S51 | [The feature, performance, and prospect of advanced EEG electrodes 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9855417/) | Material and signal-quality review. |
| S52 | [Multi-center evaluation of gel and dry multipin caps 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9612204/) | Operator, center, reliability, and prep-time evidence. |

### Channel selection and low-channel decoding

| ID | Source | Use in this project |
|---|---|---|
| S53 | [Channel selection methods for the P300 Speller 2014](https://pubmed.ncbi.nlm.nih.gov/24797224/) | Sequential/SSNR selection comparison. |
| S54 | [Method for optimizing electrode number/configuration 2015](https://pubmed.ncbi.nlm.nih.gov/25316166/) | Four-electrode replication target. |
| S55 | [Electrode subset selection methods 2015](https://pubmed.ncbi.nlm.nih.gov/24506528/) | Subset selection baseline. |
| S56 | [Grouped automatic relevance determination 2015](https://pubmed.ncbi.nlm.nih.gov/25794393/) | Sparse Bayesian channel selection. |
| S57 | [Channel selection based on phase measurement 2013](https://pubmed.ncbi.nlm.nih.gov/23593261/) | Non-amplitude selection criterion. |
| S58 | [Mobile P300 classifier and channel configurations 2017](https://pubmed.ncbi.nlm.nih.gov/28553694/) | Mobile low-channel comparison. |
| S59 | [Subject-dependent versus subject-independent channel selection 2019](https://pubmed.ncbi.nlm.nih.gov/31728934/) | Generalization and selection leakage. |
| S60 | [Semi-supervised joint spatio-temporal feature selection 2011](https://pubmed.ncbi.nlm.nih.gov/23115595/) | Feature/channel joint selection. |
| S61 | [Wavelet features and IBPSO channel selection 2012](https://pubmed.ncbi.nlm.nih.gov/23717804/) | Alternative optimization baseline. |
| S62 | [Regional smoothing block sparse Bayesian channel selection 2022](https://pubmed.ncbi.nlm.nih.gov/35754766/) | Recent structured sparse method. |
| S63 | [EEG channel selection from source localization review 2023](https://pubmed.ncbi.nlm.nih.gov/35794417/) | Selection review and broader context. |
| S64 | [Brain-computer speller design with channel selection algorithms 2020](https://pubmed.ncbi.nlm.nih.gov/32278892/) | System-design comparison. |
| S65 | [P300 Chinese input system based on Bayesian LDA 2010](https://pubmed.ncbi.nlm.nih.gov/20128741/) | Bayesian LDA and language/input design. |

### Adaptive stopping, calibration, language, and error handling

| ID | Source | Use in this project |
|---|---|---|
| S66 | [Bayesian approach to dynamically controlling data collection 2013](https://pubmed.ncbi.nlm.nih.gov/23529202/) | Participant-independent posterior stopping. |
| S67 | [Increasing rates with dynamic stopping in an ALS study 2015](https://pubmed.ncbi.nlm.nih.gov/25588137/) | Clinical dynamic-stopping evidence. |
| S68 | [Integrating dynamic stopping, transfer learning, and language models 2014](https://pubmed.ncbi.nlm.nih.gov/24834896/) | Combined adaptive pipeline prior art. |
| S69 | [Language model for online dynamic data collection 2014](https://pubmed.ncbi.nlm.nih.gov/24808413/) | Language-assisted stopping. |
| S70 | [HMM language information for P300 communication 2014](https://pubmed.ncbi.nlm.nih.gov/24760927/) | Sequence-level correction. |
| S71 | [Self-calibration in an asynchronous P300 BCI 2014](https://pubmed.ncbi.nlm.nih.gov/24838347/) | Calibration burden and online adaptation. |
| S72 | [A new early stopping method for P300 spellers 2019](https://pubmed.ncbi.nlm.nih.gov/31226078/) | Direct early-stopping comparator. |
| S73 | [Subject-independent ERP-based BCI 2018](https://pubmed.ncbi.nlm.nih.gov/29641376/) | Cross-user generalization. |
| S74 | [Active inference as an adaptive P300 BCI 2020](https://pubmed.ncbi.nlm.nih.gov/31783392/) | Adaptive decision framework. |
| S75 | [Online SOA tuning for P300-speller performance 2021](https://pubmed.ncbi.nlm.nih.gov/34638106/) | Stimulus timing as an adaptive variable. |
| S76 | [Asynchronous P300 BCI for environmental control 2018](https://pubmed.ncbi.nlm.nih.gov/28391211/) | No-intent/asynchronous control. |
| S77 | [BCI-Utility metric for asynchronous P300 systems 2023](https://pubmed.ncbi.nlm.nih.gov/37792654/) | Utility beyond accuracy alone. |
| S78 | [Using detectability index to predict P300 performance 2016](https://pubmed.ncbi.nlm.nih.gov/27705956/) | Signal-quality/performance link. |
| S79 | [Error-related potentials for auto-correction 2016](https://pubmed.ncbi.nlm.nih.gov/26302518/) | Error recovery and false activation. |
| S80 | [Listen, you are writing — dynamic auditory BCI 2011](https://pubmed.ncbi.nlm.nih.gov/22016719/) | Auditory accessibility alternative. |
| S81 | [Comparing P300 flashing paradigms with language models 2025](https://pubmed.ncbi.nlm.nih.gov/39899514/) | Current paradigm/language comparison. |
| S82 | [Practitioner opinions for an AAC BCI device 2021](https://pubmed.ncbi.nlm.nih.gov/33236859/) | User, clinician, and service requirements. |

### Processing, robustness, and modern baselines

| ID | Source | Use in this project |
|---|---|---|
| S83 | [Convolutional neural networks for P300 detection 2011](https://pubmed.ncbi.nlm.nih.gov/20567055/) | Deep-learning baseline. |
| S84 | [Online semi-supervised BCI 2013](https://pubmed.ncbi.nlm.nih.gov/23674410/) | Label-efficient adaptation. |
| S85 | [P300 performance estimation with classifier-based latency 2023](https://pubmed.ncbi.nlm.nih.gov/37747230/) | Latency-aware evaluation. |
| S86 | [Subject-independent wearable P300 CNN and metric learning 2024](https://pubmed.ncbi.nlm.nih.gov/39255188/) | Modern wearable/generalization baseline. |
| S87 | [Tiny noise, big mistakes: adversarial perturbations in BCI spellers 2021](https://pubmed.ncbi.nlm.nih.gov/34691612/) | Robustness and false-confidence warning. |
| S88 | [P300 audio-visual speller 2011](https://pubmed.ncbi.nlm.nih.gov/21436523/) | Multimodal/accessibility option. |
| S89 | [P300 speller performance under weak hidden conditions 2023](https://pubmed.ncbi.nlm.nih.gov/38002543/) | Weak-signal robustness. |
| S90 | [Environment and electrode configuration impact 2024](https://pubmed.ncbi.nlm.nih.gov/40039598/) | Direct environmental/configuration test. |

The register contains more than the minimum 50 papers because the proposed gap sits at the intersection of clinical use, hardware, signal processing, channel selection, decision theory, and usability. The references should be narrowed to the final preregistered comparison once the team fixes its exact hardware and public dataset.

## 12. Immediate next actions

1. Freeze this outcome statement and get mentor/clinical feedback on the non-inferiority and safety definitions.
2. Pin one public P300 dataset and reproduce its standard baseline before changing the algorithm.
3. Upgrade the current direct-flash demo to a timed row/column or checkerboard interface with a reject state.
4. Add contact-quality and artifact metadata to the NPZ schema.
5. Implement nested channel-selection and session-held-out evaluation.
6. Write a short protocol for wet/dry order, visual accessibility, fatigue, comfort, and no-intent blocks.
7. Only then decide whether a custom headset prototype or a lab collaboration is the next bottleneck.

