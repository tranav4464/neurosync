# NeuroSync — Milestone 3 results and submission brief

**Team:** Neurosync · **Team number:** 7601  
**Students:** Anushree Kapruwan; Ifra Akhtar  
**Mentor:** Not provided  
**Project page:** Team to add its NYAS project-page URL  
**Public research repository:** https://github.com/tranav4464/neurosync

## The problem and proposed solution

People with severe motor impairment may need communication systems that do
not require reliable muscle movement. P300 spelling can use brain responses to
visual choices, but gel preparation, setup help, and noisy electrodes can make
regular use difficult. NeuroSync studies a six-electrode P300 design with
signal-quality checks and explicit repeat or re-seat actions. The long-term
goal is a comfortable, affordable dry or semi-dry headset. This milestone
tests the algorithm and electrode-count question using public EEG recordings;
it does not test a manufactured headset.

## Data and feedback

We reviewed prior P300 channel-selection, dry-electrode, and adaptive-stopping
studies. Prior dry systems can reduce setup burden, but results vary with the
electrode and contact conditions. Direct wet/dry comparisons found poorer dry
signal quality in some settings, including recordings from people with
communication disabilities. We therefore measured compact-montage accuracy
and looked for the conditions in which it fails.

On [BNCI 2014-008](https://bnci-horizon-2020.eu/database/data-sets), which
contains eight people with ALS using active EEG electrodes, we used A01 for
method development and A02–A08 for confirmation. We preserved the original
15-character calibration and 20-character feedback split. At ten repetitions,
six selected channels achieved **92.9% mean held-out character accuracy**;
eight channels achieved **93.6%**. All seven confirmation participants reached
at least 85% using six channels.

We also tested the method on all 13 available participants in [bigP3BCI Study
A](https://physionet.org/content/bigp3bci/1.0.0/), training and testing on
separate recordings. Here, six channels produced mean target-event AUC 0.724
versus 0.773 with all 32 channels. This is a different 9×8 stimulus paradigm;
AUC is a detection measure, not character accuracy. A training-only
stability-selection method did not close the gap. A second response-strength
and diversity method improved the descriptive mean but not its confirmation
subset. These findings guide the next design instead of implying that every
user or recording works equally well.

## Lessons learned and limitations

- Six carefully selected active electrodes can perform well in one ALS P300
  cohort, but a second dataset exposed a reproducible loss against a larger
  montage. A compact system needs a way to recognize unreliable recordings.
- Extra algorithm steps did not automatically improve confirmation performance.
  Training-only comparisons and a reserved evaluation group matter.
- The public ALS dataset used active Ag/AgCl electrodes. No headset cost,
  comfort, setup time, physical dry-contact quality, or home performance was
  measured. We have not yet run a paired wet/dry human study.
- Our team works remotely across countries and does not currently have a
  shared EEG laboratory or approved ALS participant protocol.

## Community, safety, and environmental effects

If validated, a comfortable compact system could reduce preparation and
caregiver burden. Incorrect letters could cause confusion, frustration, or
fatigue; withholding too many letters would also make communication unusable.
The proposed interface therefore includes repeat, re-seat, and fallback
communication states, which still need testing with real users. Fewer
electrodes may reduce consumables, but the eventual hardware should be
repairable and evaluated for electronics waste. These are design goals, not
measured benefits.

## Next steps and revised testing plan

1. Reproduce strong P300 baselines on the same splits and finish a
   protocol-specific character decoder for an external compatible study.
2. Obtain a documented measured forward model and compare geometry-aware
   selection with ordinary selection and shuffled-geometry controls.
3. Partner with an EEG lab to build and evaluate a six-electrode dry or
   semi-dry prototype. Log contact/impedance, setup time, comfort, fatigue,
   marker timing, and repair cost.
4. With appropriate ethics approval and an accessible fallback communication
   method, counterbalance wet and candidate sessions. Predefine the target for
   correct outputs, wrong outputs, coverage, repetitions, and wet-reference
   comparison before inspecting final sessions.

## Team reflection to complete before submission

The students should add their actual individual contributions and how they
shared literature review, code, testing, design decisions, and remote
coordination. Those personal details are intentionally left for the team to
verify. The NYAS project-page URL and mentor name, if assigned, also need to
be filled in by the team.

## Supporting materials

- [Results and protocol](PUBLIC_DATA_BENCHMARK.md)
- [Data provenance](DATA_MANIFEST.md)
- [Current research manuscript](../manuscript/FLAGSHIP_MANUSCRIPT.md)
- [Source code and tests](https://github.com/tranav4464/neurosync)
