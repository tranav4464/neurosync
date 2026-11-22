# Milestone 3 — Results

## Team information

| Field | Entry |
|---|---|
| Team name | Neurosync |
| Project page / team number | Project-page URL: **add the final link** · Team number: **7601** |
| Student members | Anushree Kapruwan; Ifra Akhtar |
| Mentor | To be confirmed |

## Data / Feedback

Our research synthesis suggests that a carefully selected 4–6 electrode montage can be a reasonable target for a P300 speller, but reducing electrode count does not remove the headset-design problem. A smaller headset must still make reliable contact, fit different users, and remain comfortable for long sessions. Dry electrodes could reduce setup time and improve comfort for people with ALS, but the research we reviewed reports more background noise and lower P300 correctness than wet electrodes in direct comparisons. Modified stopping methods alone did not fully compensate for the lower signal-to-noise ratio.

To turn those findings into a testable framework, we built a reproducible software prototype in `Neurotech/Create/Neurosync P300`. It baseline-corrects and band-limits EEG, extracts a P300 response window, selects 4–6 channels by trial-level cross-validation, fits a regularized diagonal LDA, and accumulates evidence by symbol. Its adaptive stopping rule requires confidence, a top-two margin, and consecutive-symbol stability before ending a trial.

The included engineering demonstration used 80 synthetic training trials and 40 synthetic test trials with eight available channels. The selected set was `Pz, CPz, Fz, Oz`. The results were:

| Test condition | Accuracy | Mean repetitions |
|---|---:|---:|
| Simulated wet electrodes, 8 channels, fixed six repetitions | 100.0% | 6.00 |
| Simulated dry electrodes, 8 channels, fixed six repetitions | 47.5% | 6.00 |
| Simulated dry electrodes, selected channels, fixed six repetitions | 57.5% | 6.00 |
| Simulated dry electrodes, selected channels, adaptive stopping | 57.5% | 5.88 |

These numbers demonstrate that the code runs and exposes the expected noise/accuracy trade-off. They are **not** human-subject, ALS, or clinical results. The results are reproducible with:

```powershell
python -m neurosync_p300.demo --output-dir results/demo --seed 7 --train-trials 80 --test-trials 40
```

Potential community and environmental effects are mixed. A lower-cost, comfortable communication device could improve independence and reduce setup burden for people with ALS. On the other hand, an incorrect letter can create confusion, frustration, user fatigue, or unsafe communication if an output is treated as certain. A low-channel headset may also reduce material use, but prototype hardware still creates electronic waste unless it is repairable and durable. The software therefore needs a visible low-confidence/repeat state and must not be presented as a replacement for clinical communication support.

## Lessons Learned

The main lesson is that the solution is not simply “replace wet electrodes with dry electrodes.” A better design combines a made-to-fit and comfortable headset, careful contact-quality monitoring, noise reduction, channel selection, and adaptive data collection. The software prototype makes those assumptions explicit instead of hiding them inside a single accuracy number.

The synthetic test also exposed a failure mode: noisy evidence can look confident too early. We added a stability requirement to the adaptive stopping rule and increased the evidence-temperature calibration. In the current demo, adaptive stopping saves only a small amount of time while preserving the fixed six-repetition accuracy; this is a more responsible result than claiming a large speed improvement from noisy data.

Important limitations remain:

- We do not currently have access to a research lab or a synchronized EEG amplifier.
- Team members are in different countries, so we cannot yet run hands-on experiments together.
- We have not tested a large group of ALS participants.
- We have not tested noisy rooms, movement, conversation, or home use.
- Synthetic data cannot reproduce all electrode-skin interactions, amplifier artifacts, fatigue, or user behavior.
- The current demo flashes six symbols directly; a full row/column P300 keyboard and a hardware timing adapter still need to be added.

## Next Steps

1. Finalize a row/column speller interface with a clear repeat/reject state and an accessible display.
2. Add a hardware adapter for a research EEG amplifier and record synchronized flash markers.
3. Validate the preprocessing and timing on healthy volunteers before any clinical population work.
4. Compare wet and dry electrodes on the same participants, with counterbalanced order and held-out sessions.
5. Record impedance/contact quality, blink and muscle artifacts, low-frequency drift, dropout, fatigue, accuracy, repetitions, and information-transfer rate.
6. Test quiet-room and home-like noise conditions, then run longer sessions to measure slow baseline drift in delta/theta bands.
7. Only after those checks, work with a hospital or ALS research lab under ethics approval, informed consent, and an independent safety/communication fallback.

### Team contribution reflection — confirm before submitting

The team should replace this note with the actual division of work. A truthful reflection should state who led the literature synthesis, who implemented the preprocessing/decoder, who designed the headset concept, who checked the results, and how disagreements or remote coordination were handled. We have intentionally left those individual claims for the team to verify rather than inventing them.

