# NeuroSync compared with prior work and NYAS expectations

**Purpose:** Position NeuroSync accurately for the New York Academy of
Sciences (NYAS) Junior Academy and for research audiences. This is not a claim
that NeuroSync is better than every existing BCI system.

## Executive comparison

NeuroSync should be presented as a **high-rigor student research framework and
boundary study**, not as a finished dry-electrode medical product. Its unusual
strength is that it preserves both a positive and a negative result:

- In a locked ALS active-electrode cohort, six personalised channels retained
  near-eight-channel character accuracy (92.9% versus 93.6%).
- In a complete, file-disjoint 13-person external cohort, six channels did not
  retain full-montage event performance (AUC 0.724 versus 0.773).

That combination makes the project scientifically stronger than a prototype
that reports only its best run. It does **not** make it stronger than prior
work that has already tested real dry hardware, online communication, comfort,
or clinical users.

## Comparison with relevant prior work

| Prior work | What it established | Where it is stronger than NeuroSync | Where NeuroSync is differentiated |
|---|---|---|---|
| [Guger et al., 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3345570/) | A dry-electrode P300 system produced performance comparable to gel in a field validation with 23 users. | Actual dry hardware, closed-loop spelling, user comfort, and preparation burden. | NeuroSync does **not** claim dry parity; it adds a reproducible claim ladder and explicit external boundary test. |
| [Clements et al., 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC6378883/) | Compared wet and dry P300 systems, including people with ALS/PLS, and tested dynamic data collection. Lower dry SNR limited performance. | Direct wet/dry comparison, end-user evidence, and a practical dynamic-stopping question. | NeuroSync carries this limitation forward rather than assuming algorithmic stopping fixes contact loss; it specifies contact/recovery outcomes for the next test. |
| [Throckmorton et al., 2015](https://doi.org/10.1016/j.clinph.2014.09.021) | A population-informed four-electrode set was tested online against fuller montages in healthy users. | Prospective online evaluation and a hardware-relevant common montage. | NeuroSync demonstrates that personalised six-channel performance can be strong in an ALS cohort but also measures external loss rather than extrapolating. |
| [Colwell et al., 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4106671/) | Compared online electrode-subset selection methods for P300 BCIs. | Direct focus on online electrode selection. | NeuroSync adds locked temporal confirmation, event-table audits, and a 13-person file-disjoint external study. |
| [Rivet et al., 2009](https://doi.org/10.1109/TBME.2009.2012869) | Established xDAWN spatial filtering for ERP enhancement. | Mature, established ERP spatial-filter method. | NeuroSync should not claim superiority until it includes a fair full xDAWN baseline; its current template filter is only an ablation. |
| [bigP3BCI, 2025](https://physionet.org/content/bigp3bci/1.0.0/) | Released a large, multi-study, machine-learning-ready P300 resource with standardized EDF markers. | Scale, diversity, and many available study conditions. | NeuroSync provides a conservative Study A EDF adapter and evaluates every available participant in a file-disjoint way, without collapsing incompatible paradigms into one character metric. |

## What is novel versus what is established

| Category | NeuroSync status | How to say it honestly |
|---|---|---|
| P300 decoding, LDA, dynamic stopping, channel selection | Established field methods | “We implemented and compared transparent, training-only components.” |
| Dry-electrode P300 feasibility | Established but mixed literature | “Prior work shows promise and limitations; our project does not yet validate dry hardware.” |
| Six-channel active-EEG result in BNCI ALS data | Confirmed replication/extension | “Our locked analysis supports sparse active-electrode feasibility in this specific cohort.” |
| 13-person external boundary test | Strong project-specific contribution | “We tested whether the sparse conclusion survives a different paradigm and reported the loss when it did not.” |
| Claim ladder plus selective reliability framework | Project-specific integration | “We separate demonstrated performance, external limits, and future geometry/contact hypotheses.” |
| Observable-geometry mechanism | Implemented hypothesis | “It is ready for a measured-forward-model ablation; it is not yet a demonstrated gain.” |

## NYAS Junior Academy alignment

The public [NYAS Innovation Challenge evaluation rubric](https://www.nyas.org/wp-content/uploads/2025/09/Junior-Academy-Innovation-Challenge-Evaluation-Rubric.pdf)
scores Innovation & Design Thinking, Scientific Quality, and Presentation
Quality on a 10-point scale. It describes exemplar work as highly original,
well-supported by references and methods, and exceptionally clear and concise.
The current challenge rubric should always take precedence if it differs.

| NYAS dimension | Current realistic position | What makes it strong | What must be shown to reach exemplar level |
|---|---:|---|---|
| Innovation & Design Thinking | 7–8 / 10 | The novelty is not “another P300 classifier”; it is the failure-aware sparse-BCI evidence architecture: low-channel feasibility, external falsification, and a contact/geometry decision layer. | Show the physical six-channel headset concept, the user journey, the recovery/fallback interaction, and why this is meaningfully lower burden. |
| Scientific Quality | 8–9 / 10 | 50+ literature mapping, provenance, hashes, event audits, locked ALS confirmation, 13-person external testing, negative controls, and reproducible code are unusually strong for a student project. | Avoid overclaiming. Show the one-slide evidence hierarchy and state exactly what is unproven: dry hardware, comfort, cost, home use, and clinical safety. |
| Presentation Quality | 6–8 / 10 until a final deck is built | The narrative and figures are now clear. | Use fewer claims, larger visuals, one result per slide, and lead with the real human problem: a wrong letter is worse than a slow letter. |
| Team collaboration | Not assessable from the repository | International collaboration and a shared reproducible repository are credible positives. | Add a truthful division-of-work slide and document how feedback changed the design. |

## Best NYAS framing

### Title

**NeuroSync: A Failure-Aware Six-Channel BCI for Safer Communication Research**

### 30-second spoken pitch

> People who rely on brain-computer interfaces to communicate need a system
> that does not turn noisy brain signals into confident wrong letters. NeuroSync
> tests whether a smaller six-electrode system can reduce burden without hiding
> failure. In a locked ALS dataset, six active electrodes reached 92.9% accuracy,
> nearly matching eight. But when we tested all 13 people in a second public
> dataset, performance dropped below the full montage. Instead of hiding that,
> we used it to define the next design: a headset that measures contact quality,
> knows when to collect more evidence, and asks for a reset rather than guessing.

### Slide sequence

1. **Human need:** Gel, setup, assistance, and wrong-letter risk.
2. **Central question:** Can six channels reduce burden without unsafe errors?
3. **What exists:** Wet/dry and low-channel prior work; the unresolved gap.
4. **NeuroSync design:** headset concept → signal quality → decoder →
   `ACCEPT / REPEAT / RESEAT / fallback`.
5. **Strong result:** 92.9% six-channel versus 93.6% eight-channel in the
   locked ALS benchmark.
6. **Integrity result:** external 13-person test reveals a 4.9-AUC-point gap.
7. **Why that matters:** it prevents false promises and gives a precise target.
8. **Innovation:** measured-contact + geometry experiment that must beat this
   baseline, with user-centred safety metrics.
9. **Impact and responsibility:** lower setup burden if successful; fallback
   communication, repairability, and no clinical claims until validated.
10. **Ask / next step:** partner with a lab or clinic for a counterbalanced
    wet-versus-semi-dry study.

## Claims that will hurt the project

- “Nothing better exists.” Existing dry-electrode and online P300 studies are
  more mature in hardware validation.
- “We proved dry equals wet.” The present strongest result uses active Ag/AgCl
  EEG, not dry electrodes.
- “We are clinical-ready.” No prospective participant, comfort, safety, or
  clinical study has been done.
- “Our external result is 85% accuracy.” The external Study A metric is event
  AUC because its 9x8 paradigm is not the same as the 6x6 character speller.

## The strongest honest conclusion

> NeuroSync is a research-grade, reproducible student project that demonstrates
> a real sparse-EEG feasibility result, rigorously identifies its external
> limit, and turns that limit into a safer, measurable headset-development
> hypothesis. It is competitive for NYAS on scientific quality precisely because
> it does not pretend that an offline result is a finished medical product.
