from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT = Path(__file__).with_name("NeuroSync_CASP_X_Manuscript.docx")


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, color="D9D9D9"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), color)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        set_cell_shading(cell, "17365D")
        for run in cell.paragraphs[0].runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.bold = True
            run.font.size = Pt(9)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_border(cell)
        if widths:
            cell.width = Inches(widths[i])
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, text in enumerate(row):
            cells[i].text = str(text)
            if row_index % 2:
                set_cell_shading(cells[i], "F3F6F9")
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    run.font.size = Pt(8.5)
            cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_border(cells[i])
            if widths:
                cells[i].width = Inches(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_para(doc, text, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(text)
    run.italic = italic
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.add_run(text)
    p.paragraph_format.space_before = Pt(10 if level == 1 else 7)
    p.paragraph_format.space_after = Pt(4)
    return p


def build_document():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.05
    for style_name, size in [("Title", 18), ("Heading 1", 13), ("Heading 2", 11)]:
        style = styles[style_name]
        style.font.name = "Aptos Display" if style_name == "Title" else "Aptos"
        style._element.rPr.rFonts.set(qn("w:ascii"), style.font.name)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), style.font.name)
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = True
    if "Reference" not in styles:
        ref_style = styles.add_style("Reference", WD_STYLE_TYPE.PARAGRAPH)
        ref_style.font.name = "Aptos"
        ref_style.font.size = Pt(8.5)
        ref_style.paragraph_format.space_after = Pt(2)
        ref_style.paragraph_format.left_indent = Inches(0.22)
        ref_style.paragraph_format.first_line_indent = Inches(-0.22)

    footer = section.footer.paragraphs[0]
    footer.text = "NeuroSync CASP X"
    footer.alignment = WD_ALIGN_PARAGRAPH.LEFT
    footer.runs[0].font.size = Pt(8)
    footer.add_run("                                      ")
    add_page_number(footer)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("Contact Aware Sparse P300 Decoding for Lower Burden Brain Computer Interfaces")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("A Safety Aware Framework and Feasibility Evaluation").italic = True
    subtitle.runs[0].font.size = Pt(12)
    authors = doc.add_paragraph()
    authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    authors.add_run("Team NeuroSync\nAnushree Kapruwan and Ifra Akhtar").font.size = Pt(10.5)
    doc.add_paragraph()

    add_heading(doc, "Abstract")
    add_para(doc, "People with severe motor impairment may benefit from brain computer interfaces that reduce dependence on manual control, but conventional P300 systems often require multi-electrode wet preparation, expert setup, and repeated calibration. Lowering the electrode count and preparation burden is attractive only if communication remains safe. This paper presents Contact Aware Sparse P300 with eXplainable recovery (CASP X), a framework for low-channel P300 communication that treats output reliability as a first-class system decision. CASP X combines training-only 4 to 6 channel selection, ERP waveform and pooled temporal features, sparse channel-time feature selection, an xDAWN-inspired spatial-filter ablation, calibrated sequential evidence accumulation, and contact-quality actions. Instead of forcing a letter whenever a trial ends, the framework produces ACCEPT, REPEAT, REJECT, or RESEAT HEADSET outcomes. We define performance using correct accepted-output rate, wrong accepted-output rate, coverage, repetition burden, and wet-reference comparison rather than accuracy alone. The software implementation includes reproducible stress evaluation and a public P300 benchmark adapter with held-out character evaluation. The current evidence establishes a transparent engineering platform and identifies signal acquisition, contact stability, and validated ERP decoding as the key bottlenecks. CASP X is therefore positioned as a rigorous pathway toward lower-burden P300 communication, with prespecified safety and validation gates required before clinical or hardware-equivalence claims.")
    add_para(doc, "Keywords: P300 speller; brain computer interface; augmentative and alternative communication; sparse EEG; dry electrodes; channel selection; selective prediction; adaptive stopping; safety aware decoding")

    add_heading(doc, "1 Introduction")
    add_para(doc, "Noninvasive brain computer interfaces can provide a communication pathway when neuromuscular disease or injury limits conventional input. The P300 speller remains one of the most established event-related-potential paradigms because it links attended visual events to a measurable response and permits symbol selection through repeated evidence accumulation [1-4]. P300 communication has been studied in people with amyotrophic lateral sclerosis and related severe motor impairments, yet individual variability, fatigue, visual demands, calibration burden, and setup time remain central barriers to dependable use [5-8].")
    add_para(doc, "Wet EEG electrodes provide a conventional signal-quality reference but require skin preparation, conductive gel, cleaning, and often experienced assistance. These burdens matter most in settings where a user depends on caregivers, has limited endurance, or requires repeated sessions. Dry and semi-dry electrodes can reduce preparation burden, but the change in electrode-skin coupling introduces a difficult systems problem: the same design choices that improve convenience can weaken signal stability or increase artifact susceptibility [9-13]. A lower-channel system should therefore not be judged only by whether it produces a label; it must demonstrate that its accepted labels remain reliable when contact degrades.")
    add_para(doc, "A substantial P300 literature already exists on channel selection, spatial filtering, dynamic stopping, language assistance, and error correction [14-22]. The unresolved engineering gap is their integration into a low-burden framework that makes uncertainty and contact quality visible at the moment a communication action is considered. CASP X addresses this gap by coupling sparse decoding with an explicit action policy. The aim is not to claim that a small dry headset is automatically equivalent to a conventional wet system. The aim is to define, implement, and evaluate the conditions under which a lower-burden system could be accepted, repeated, or physically adjusted without silently producing an unsafe output.")

    add_heading(doc, "2 Related Work and Research Gap")
    add_heading(doc, "2.1 P300 decoding and stimulus design", 2)
    add_para(doc, "The original row-column P300 speller translated oddball responses into matrix selections through repeated row and column intensifications [1,2]. Subsequent work established classifier comparisons, feature decimation, reference strategies, and stepwise linear discriminant analysis as practical baseline choices [3,4,23]. Alternative paradigms, including checkerboard and region-based designs, reduce adjacency and double-flash limitations, while personalized stimulus timing can influence both accuracy and information transfer rate [16,24,25]. These findings indicate that electrode count cannot be interpreted independently from the stimulus protocol, evidence budget, and decoder.")
    add_heading(doc, "2.2 Electrode count and wearable acquisition", 2)
    add_para(doc, "Several studies report that a carefully chosen subset of posterior and central electrodes can retain much of the discriminative ERP information observed in larger montages [14,15,26]. In particular, prospective reduced-montage work has demonstrated that four posterior electrodes can be competitive in selected settings, but channel sufficiency is not universal: it depends on participant-specific ERP topography, acquisition quality, paradigm, and validation split [15,26,27]. Dry-electrode P300 studies likewise show that convenience gains coexist with differences in low-frequency drift, transient artifact, and signal-to-noise ratio [9,10]. The hardware contribution must therefore include contact quality and comfort, not only low component count.")
    add_heading(doc, "2.3 Adaptive decisions and safe communication", 2)
    add_para(doc, "Fixed repetition counts waste time when evidence is strong and may still be inadequate when evidence is weak. Bayesian dynamic stopping, sequential evidence policies, self-calibration, and language-informed decoding have been proposed to improve efficiency [18-21,28]. However, high headline accuracy can mask an undesirable operating point: a system can abstain from difficult trials, or it can accept low-quality evidence too readily. Asynchronous and error-related-potential work emphasizes the need to distinguish an intended selection from uncertain or no-intent states [22,29,30]. CASP X builds on this principle by defining communication safety as a joint property of accuracy, coverage, wrong accepted outputs, and recovery behavior.")

    add_heading(doc, "3 Objective and Contributions")
    add_para(doc, "The central question is: can a custom-fit 4 to 6 electrode dry or semi-dry P300 system provide high-quality communication with low wrong-output risk and a transparent recovery path when contact is poor? The target endpoint is not simply 85% accuracy among the small set of outputs the system accepts. The proposed deployment gate is at least 85% correct accepted outputs, at most 5% wrong accepted outputs, at least 90% coverage, at least 90% accepted-output accuracy, and a prespecified repetition or latency budget. A matched wet-reference comparison remains necessary for any claim of comparable performance.")
    add_para(doc, "The contributions of this work are fourfold. First, CASP X defines a contact-aware sparse P300 architecture that separates signal decoding from action selection. Second, it provides an open, dependency-light implementation of training-only channel selection, pooled ERP features, sparse channel-time selection, and a supervised spatial-filter ablation. Third, it introduces an action vocabulary that can return REPEAT, REJECT, or RESEAT HEADSET rather than force every trial into a communication command. Fourth, it provides a reproducible evaluation plan that combines held-out character decoding, selective-risk metrics, hardware-contact logs, and wet-reference noninferiority analysis.")

    add_heading(doc, "4 CASP X Framework")
    add_para(doc, "CASP X is organized as a closed-loop signal-to-action system. EEG and event markers are first screened for timing integrity, excessive transients, slow baseline instability, and line-noise burden. Candidate channels are then selected only from training data. Preprocessed epochs are represented by a 250 to 600 ms waveform segment plus early, peak, and late pooled amplitudes. This representation preserves temporal detail while providing low-variance summaries of the broad P300 complex. A regularized LDA serves as an interpretable baseline, while sparse feature and spatial-filter variants are evaluated as controlled ablations.")
    add_para(doc, "Flash-level scores are accumulated at the symbol level. In a row-column paradigm, evidence for the most likely row and column is aggregated separately and intersected in the matrix. A decision is accepted only if confidence, top-two margin, stability across repetitions, and contact quality meet prespecified thresholds. If evidence is weak but contact remains acceptable, the policy requests additional bounded evidence or a repeat. If repeated low-quality measurements occur, the policy requests a headset re-seat rather than continuing to integrate corrupted data. This design makes the decision trace auditable: each output is associated with its repetitions used, confidence, margin, quality estimate, and action.")

    add_table(doc,
              ["Stage", "Input", "Operation", "Output"],
              [
                  ["Quality", "Raw EEG and markers", "Drift, line-noise, and transient checks relative to calibration", "Quality score and contact flags"],
                  ["Selection", "Training epochs", "Forward selection constrained to 4 to 6 channels", "Compact montage"],
                  ["Features", "Selected epochs", "Waveform window and pooled ERP amplitudes", "Flash feature vector"],
                  ["Decoding", "Flash scores", "Regularized LDA and symbol-level evidence accumulation", "Ranked symbols"],
                  ["Action", "Evidence and quality", "Confidence, margin, stability, burden, and quality rules", "ACCEPT, REPEAT, REJECT, or RESEAT HEADSET"],
              ], [0.9, 1.3, 3.1, 1.1])
    add_para(doc, "Table 1. CASP X processing and action pipeline.", italic=True)

    add_heading(doc, "5 Methods")
    add_heading(doc, "5.1 Signal processing and features", 2)
    add_para(doc, "Each epoch is baseline referenced and band limited before feature extraction. The default analysis window emphasizes the P300 interval from 250 to 600 ms after the event. Downsampled waveform values are flattened across selected channels, and three channel-wise pooled means capture the early, peak, and late morphology of the ERP. This fixed representation is deliberately transparent and can be compared directly with feature-selection or spatial-filter variants. The current spatial module learns regularized channel mixtures from the target-minus-nontarget template energy relative to residual covariance; it is an xDAWN-inspired ablation rather than a claim of a full xDAWN implementation [17].")
    add_heading(doc, "5.2 Sparse selection and classification", 2)
    add_para(doc, "Forward selection uses trial-level folds so all flashes from a character remain together. The selected set is constrained to 4 through 6 channels for the low-burden condition; an all-available-channel condition is retained as a reference. The baseline classifier is diagonal LDA with variance shrinkage, chosen for inspectability and stability with limited calibration data. A sparse channel-time selector ranks standardized target-nontarget shifts using training data only. This ablation captures the feature-sparsity rationale of SWLDA while avoiding an unsupported claim that the lightweight implementation is an exact SWLDA reproduction [3,23].")
    add_heading(doc, "5.3 Contact quality and recovery policy", 2)
    add_para(doc, "The contact-quality gate estimates low-frequency energy, line-noise ratio, and peak-to-peak excursions relative to calibration data. These measures are not substitutes for hardware impedance sensing; rather, they are signal-level indicators that can trigger a safety action while a physical headset is being refined. Repeated poor-quality repetitions invoke RESEAT HEADSET. Moderate uncertainty invokes REPEAT or a bounded additional evidence block. A true no-intent detector is outside the current scope and must be separately validated before REJECT is interpreted as an asynchronous safety guarantee.")
    add_heading(doc, "5.4 Evaluation design", 2)
    add_para(doc, "The evaluation framework uses training-only montage selection and decision calibration. The primary measure is correct accepted-output rate: correct ACCEPT decisions divided by all intended selections. Wrong accepted-output rate is reported separately because an incorrect communication action has a different cost from a repeat. Coverage, accepted-output accuracy, repetitions per selection, early stopping rate, and re-seat rate complete the operating-point description. Wet-reference comparison is evaluated with matched trial identifiers and bootstrap confidence intervals for the candidate-minus-reference correct accepted-output difference.")

    add_heading(doc, "6 Feasibility Evaluation")
    add_heading(doc, "6.1 Controlled software stress evaluation", 2)
    add_para(doc, "The implementation was exercised across eight deterministic stress runs with 48 training trials and 24 matched test trials per run. The reference condition used eight channels and fixed six repetitions. The sparse condition used training-selected 4 to 6 channels, contact-aware actions, and the same repetition budget. This evaluation is useful for regression testing the pipeline and the safety trade-off, but it does not establish headset, human, or clinical performance.")
    add_table(doc,
              ["Condition", "Correct accepted outputs", "Wrong accepted outputs", "Coverage", "Re-seat rate"],
              [
                  ["Eight-channel wet-reference condition", "1.000", "0.000", "1.000", "0.000"],
                  ["Sparse CASP X clean condition", "0.193", "0.099", "0.292", "0.000"],
                  ["Ordinary decoder under contact-failure stress", "0.159", "0.284", "0.443", "0.000"],
                  ["CASP X under contact-failure stress", "0.185", "0.102", "0.286", "0.250"],
              ], [2.7, 1.05, 1.05, 0.8, 0.8])
    add_para(doc, "Table 2. Eight-run controlled software stress evaluation. Correct and wrong accepted outputs are rates over all intended selections.", italic=True)
    add_para(doc, "The principal observation is a safety-coverage trade-off. Under induced contact failure, CASP X reduced wrong accepted outputs relative to the ordinary decoder and produced a re-seat action on the affected proportion of trials. At the same time, coverage remained insufficient for a finished communication system. This result supports the action-policy concept but does not support a claim that sparse dry decoding currently meets the proposed deployment gate.")
    add_heading(doc, "6.2 Public P300 benchmark feasibility analysis", 2)
    add_para(doc, "A public 6 by 6 P300 dataset was converted into flash-level epochs using the documented event markers, 240 Hz acquisition rate, and row-column structure [31]. The importer retained an eight-channel posterior and central candidate montage and evaluated complete character selections using a held-out-character split. Sixty character epochs were used for model development and 25 were held out. The compact LDA condition selected four channels; the sparse-feature condition used all eight candidate channels with 60 training-selected features.")
    add_table(doc,
              ["Configuration", "Channels", "Feature policy", "Flash balanced accuracy", "Character accuracy"],
              [
                  ["Compact LDA", "4 selected", "Waveform plus pooled ERP features", "0.543", "0.160"],
                  ["Sparse-feature LDA", "8", "60 training-selected channel-time features", "0.557", "0.160"],
              ], [1.35, 0.85, 2.25, 1.0, 1.0])
    add_para(doc, "Table 3. Held-out-character feasibility analysis on the public P300 dataset. These results identify an implementation and acquisition challenge, not an endpoint result.", italic=True)
    add_para(doc, "The feasibility analysis confirms that event-level import, trial-wise splitting, row-column decoding, and sparse-montage reporting can be conducted reproducibly. It also shows that the present lightweight baselines are not adequate for a high-performance claim. Published P300 pipelines often use carefully tuned SWLDA, validated xDAWN workflows, full-montage information, and task-specific preprocessing [3,4,17,23]. Accordingly, the immediate technical priority is exact baseline reproduction and event-alignment verification before additional model complexity is introduced.")

    add_heading(doc, "7 Discussion")
    add_para(doc, "The main contribution of CASP X is not a claim that an algorithm alone resolves the dry-electrode problem. Rather, it is a deployment-oriented framework that makes the limiting conditions measurable. The results show why conventional accuracy is insufficient: a decoder can raise accuracy among accepted outputs by declining difficult trials, or it can raise coverage by accepting unreliable outputs. Correct accepted-output rate and wrong accepted-output rate preserve this distinction and provide a clearer basis for communication safety decisions.")
    add_para(doc, "The literature suggests several complementary routes to improve the system. Hardware work should prioritize stable contact in hair-bearing posterior regions, low-pressure mechanics, electrode geometry, and contact sensing [9-13,32]. Algorithm work should compare an exact SWLDA baseline, validated xDAWN plus LDA, covariance-based Riemannian methods, and compact learned models under identical participant- and session-disjoint splits [17,33-35]. Paradigm work should compare row-column, checkerboard, and timing conditions while reporting visual burden and information transfer rate [16,24,25]. None of these components should be selected on a held-out evaluation session.")
    add_para(doc, "A particularly important design choice is the separation of signal confidence from physical contact quality. Low confidence can result from an ambiguous ERP, limited repetitions, attention fluctuation, or a mismatch between the calibration and current session. Poor contact may instead be reflected in drift, intermittent coupling, transients, or saturation. Treating both conditions as a simple wrong-letter problem obscures the intervention required. CASP X responds by asking for more evidence when the signal is clean but inconclusive, and by asking for a physical re-seat when repeated quality indicators are poor.")
    add_para(doc, "The framework also has limits. The contact-quality signals are proxy measures until they are linked to impedance, pressure, and hardware telemetry. The current REJECT action is not a validated asynchronous no-intent classifier. Public benchmark analysis does not answer whether a custom headset is comfortable, whether an ALS user can sustain attention, or whether a semi-dry design can preserve contact across a home session. These questions require counterbalanced wet-versus-candidate recordings, user-centered endpoints, and ethical oversight.")

    add_heading(doc, "8 Translational Study Protocol")
    add_para(doc, "The next study should use a within-participant, counterbalanced crossover design. Each participant completes a conventional wet-reference session and candidate semi-dry or dry session with matched copy-spelling phrases, order randomization, rest periods, and an accessible fallback communication pathway. The hardware record should include channel locations, reference and ground, amplifier configuration, event-marker latency, packet loss, setup time, cleaning time, impedance or contact measurement, cap fit, pressure points, and comfort ratings.")
    add_para(doc, "The analysis plan should be frozen before evaluation. All filtering references, channel selection, spatial filters, feature selection, classifier parameters, temperature, action thresholds, and repetition budgets must be fit within the development partition. The final configuration should be locked and evaluated on an external public dataset before the hardware pilot. The primary endpoint should be correct accepted-output rate. The co-primary safety constraint should be wrong accepted-output rate no greater than 5%. Coverage, accepted-output accuracy, repetition burden, time per selection, and user experience should be reported at participant level with paired confidence intervals.")
    add_table(doc,
              ["Gate", "Minimum requirement", "Decision"],
              [
                  ["Data integrity", "Verified markers, trial-wise split, no leakage", "Proceed to model comparison"],
                  ["Algorithm", "Best frozen method beats transparent baseline on development data", "Lock before external test"],
                  ["Safety", "Wrong accepted outputs at or below 5%", "Eligible for communication pilot"],
                  ["Utility", "Correct accepted outputs at or above 85% and coverage at or above 90%", "Candidate meets target"],
                  ["Hardware", "Counterbalanced wet comparison and acceptable comfort/setup burden", "Consider expanded validation"],
              ], [1.0, 3.75, 1.45])
    add_para(doc, "Table 4. Prespecified go or revise ladder for CASP X.", italic=True)

    add_heading(doc, "9 Reproducibility Ethics and Reporting")
    add_para(doc, "A lower-burden communication system is credible only when its evaluation can be independently inspected. CASP X therefore treats provenance as part of the method. Each evaluation should retain raw recording identifiers, channel labels and order, sampling rate, marker mapping, preprocessing configuration, trial/session/participant split, fitted channel set, feature set, classifier parameters, action thresholds, and output action for every character. These records make it possible to distinguish a true algorithmic improvement from a difference in event alignment, preprocessing, task timing, or a favorable subset of trials. The public implementation separates reusable data adapters from the decoder so that an external dataset can be evaluated without changing the core decision policy.")
    add_para(doc, "Reporting must also preserve the full action distribution. A single accuracy number cannot show whether a system has silently repeated difficult characters, whether it accepted a wrong symbol confidently, or whether contact failure triggered a physical intervention. For every participant and session, results should include raw character accuracy, accepted-output accuracy, correct accepted-output rate, wrong accepted-output rate, coverage, repetition count, time per character, action counts, and channel-selection stability. Reliability diagrams and selective-risk curves should accompany any confidence-based decoder. These measures align the reported result with the user-facing consequence of a decision rather than with a convenient flash-level metric [36,40].")
    add_para(doc, "Ethical translation requires that the BCI never become the participant's only communication route during early evaluation. Participants should retain an independent AAC, eye-gaze, switch, or caregiver-mediated fallback. Recruitment and consent materials must explain that a BCI selection can be delayed, rejected, or incorrect; the protocol should define how a user can pause, terminate, or request a re-seat. Comfort and fatigue are outcome measures, not minor implementation details. A headset that yields an attractive offline metric but causes pressure, poor tolerance, or prolonged setup cannot satisfy the lower-burden design goal.")
    add_para(doc, "The clinical relevance of P300 communication must be considered carefully. ALS and severe motor impairment are heterogeneous with respect to vision, attention, cognitive state, oculomotor control, fatigue, medication, and caregiver support [5,6,37]. A result from an able-bodied participant, a public dataset, or an offline recording cannot by itself establish benefit for a person who requires AAC. Likewise, a language model can improve text fluency while hiding uncertainty in the neural signal. CASP X therefore treats language assistance as a separate optional layer and requires raw decoder performance, corrected output, and text-only baseline performance to be reported separately.")

    add_heading(doc, "10 Limitations and Future Work")
    add_para(doc, "This study has several limitations. The current contact-quality gate relies on EEG-derived proxies rather than direct impedance, pressure, or motion measurements. The spatial-filter and sparse-feature modules are deliberately interpretable approximations and have not yet been benchmarked against a validated reference implementation of SWLDA, xDAWN, or Riemannian geometry. The public-data analysis uses a within-subject held-out-character split and cannot establish cross-user, cross-session, or device-transfer performance. The row-column P300 paradigm itself may not be the optimal interface for every user, especially when visual fatigue, gaze constraints, or double-flash effects are relevant.")
    add_para(doc, "Future work should proceed in a staged sequence. First, the event extraction and benchmark baseline should be verified against the official reference example. Second, exact comparator implementations should be evaluated with nested participant/session-disjoint selection. Third, a semi-dry or mechanically stabilized candidate headset should be assessed against a wet reference while recording physical contact measurements and user experience. Finally, an approved co-design study with AAC clinicians and people with motor impairment should evaluate utility under realistic communication conditions. This ordering limits the risk of interpreting a hardware claim as an algorithm claim or an offline result as a communication outcome.")

    add_heading(doc, "11 Implementation and Open Evaluation Assets")
    add_para(doc, "The CASP X implementation is organized to support incremental verification. The core package contains modules for epoch preprocessing, feature extraction, compact channel selection, classifier fitting, symbol-level decoding, quality assessment, calibration, and matched wet-reference comparison. The decoder configuration exposes the minimum and maximum repetition budget, confidence threshold, margin threshold, stability requirement, quality threshold, and re-seat rule. This explicit configuration is important because adaptive stopping policies are otherwise difficult to compare: a small threshold change can trade speed for false acceptance without a visible change in conventional accuracy.")
    add_para(doc, "The evaluation utilities generate machine-readable reports containing selected channels, action counts, accepted-output metrics, and paired noninferiority summaries. A public-data adapter converts documented event-coded P300 text files into a common epoch format while retaining trial identifiers, repetition indices, row-column codes, and target character information. The held-out-character runner evaluates complete spelled characters rather than treating each flash as an independent sample. This structure makes it possible to add future datasets, hardware streams, and electrode contact sensors while preserving a common reporting schema.")
    add_para(doc, "Open evaluation does not remove the need for careful governance. Any future release should version the event parser, record data licenses, exclude personal identifiers, and avoid publishing clinically sensitive metadata without appropriate review. A public repository should contain code, configurations, split manifests, and aggregate outputs; raw recordings should be distributed only through their authorized source or an approved controlled-access process. This distinction protects participants while still allowing reviewers to reproduce the analytical path from raw event definitions to character-level decisions.")

    add_heading(doc, "12 Conclusion")
    add_para(doc, "CASP X provides a rigorous framework for lower-burden P300 communication research. Its central innovation is to treat contact quality, confidence, repetition burden, and output safety as one integrated decision problem. The implementation supports sparse-montage selection, interpretable ERP decoding, controlled algorithmic ablations, calibrated action states, and reproducible public-data analysis. The present feasibility results do not yet meet the proposed 85% correct accepted-output target, which makes the next scientific priorities unambiguous: validate the data pipeline against established baselines, improve signal acquisition and contact stability, and evaluate a frozen system against a matched wet reference. This evidence-first approach is essential if a comfortable, lower-channel P300 interface is to become a credible assistive communication option.")

    add_heading(doc, "References")
    references = [
        "[1] Farwell LA, Donchin E. Talking off the top of your head: toward a mental prosthesis utilizing event-related brain potentials. Electroencephalography and Clinical Neurophysiology. 1988;70:510-523. doi:10.1016/0013-4694(88)90149-6.",
        "[2] Donchin E, Spencer KM, Wijesinghe R. The mental prosthesis: assessing the speed of a P300-based brain-computer interface. IEEE Transactions on Rehabilitation Engineering. 2000;8:174-179. doi:10.1109/86.847808.",
        "[3] Krusienski DJ, Sellers EW, Cabestaing F, et al. A comparison of classification techniques for the P300 speller. Journal of Neural Engineering. 2006;3:299-305. doi:10.1088/1741-2560/3/4/007.",
        "[4] Krusienski DJ, Sellers EW, McFarland DJ, Vaughan TM, Wolpaw JR. Toward enhanced P300 speller performance. Journal of Neuroscience Methods. 2008;167:15-21. doi:10.1016/j.jneumeth.2007.07.017.",
        "[5] Sellers EW, Donchin E. A P300-based brain-computer interface: initial tests by ALS patients. Clinical Neurophysiology. 2006;117:538-548. doi:10.1016/j.clinph.2005.06.027.",
        "[6] Nijboer F, Sellers EW, Mellinger J, et al. A P300-based brain-computer interface for people with amyotrophic lateral sclerosis. Clinical Neurophysiology. 2008;119:1909-1916. doi:10.1016/j.clinph.2008.03.034.",
        "[7] Wolpaw JR, Birbaumer N, McFarland DJ, Pfurtscheller G, Vaughan TM. Brain-computer interfaces for communication and control. Clinical Neurophysiology. 2002;113:767-791. doi:10.1016/S1388-2457(02)00057-3.",
        "[8] Kübler A, Furdea A, Halder S, Hammer EM, Nijboer F, Kotchoubey B. A brain-computer interface controlled auditory event-related potential spelling system for locked-in patients. Annals of the New York Academy of Sciences. 2009;1157:90-100.",
        "[9] Guger C, Krausz G, Allison BZ, Edlinger G. Comparison of dry and gel based electrodes for P300 brain-computer interfaces. Frontiers in Neuroscience. 2012;6:60. doi:10.3389/fnins.2012.00060.",
        "[10] Clements MA, Colwell KA, Wargnier H, et al. A comparison of dry and wet electrodes for P300 BCI spellers. Journal of Neural Engineering. 2016;13:046006. doi:10.1088/1741-2560/13/4/046006.",
        "[11] Lopez-Gordo MA, Sanchez-Morillo D, Valle FP. Dry EEG electrodes. Sensors. 2014;14:12847-12870. doi:10.3390/s140712847.",
        "[12] Li G, Wu J, Xia Y, He Q, Jin H. Review of semi-dry electrodes for EEG recording. Journal of Neural Engineering. 2020;17:051004.",
        "[13] Kappenman ES, Luck SJ. The effects of electrode impedance on data quality and statistical significance in ERP recordings. Psychophysiology. 2010;47:888-904. doi:10.1111/j.1469-8986.2010.01009.x.",
        "[14] Colwell KA, Whelan R, et al. Channel selection methods for the P300 speller. Journal of Neural Engineering. 2014;11:056006. doi:10.1088/1741-2560/11/5/056006.",
        "[15] Throckmorton CS, Colwell KA, Ryan DB, et al. A four-channel P300-based brain-computer interface. Clinical Neurophysiology. 2015;126:2244-2251. doi:10.1016/j.clinph.2015.01.028.",
        "[16] Townsend G, LaPallo BK, Boulay CB, et al. A novel P300-based brain-computer interface stimulus presentation paradigm: moving beyond rows and columns. Clinical Neurophysiology. 2010;121:1109-1120. doi:10.1016/j.clinph.2010.01.030.",
        "[17] Rivet B, Souloumiac A, Attina V, Gibert G. xDAWN algorithm to enhance evoked potentials: application to brain-computer interface. IEEE Transactions on Biomedical Engineering. 2009;56:2035-2043. doi:10.1109/TBME.2009.2012869.",
        "[18] Höhne J, Schreuder M, Blankertz B, Tangermann M. A novel 9-class auditory ERP paradigm driving a predictive text entry system. Frontiers in Neuroscience. 2011;5:99.",
        "[19] Orhan U, Hekim M, Ozer M. EEG signals classification using the K-means clustering and a multilayer perceptron neural network model. Expert Systems with Applications. 2011;38:13475-13481.",
        "[20] Ryan DB, Frye GE, Townsend G, et al. Predictive spelling with a P300-based brain-computer interface: increasing the rate of communication. International Journal of Human-Computer Interaction. 2011;27:69-84. doi:10.1080/10447318.2011.535753.",
        "[21] Kindermans PJ, Tangermann M, Schrauwen B. Integrating dynamic stopping, transfer learning, and language models in an adaptive zero-training ERP speller. Journal of Neural Engineering. 2014;11:035005.",
        "[22] Xu M, Qi H, Wan B, Yin T, Liu Z, Ming D. A hybrid BCI speller paradigm combining P300 and SSVEP. Journal of Neural Engineering. 2013;10:026001.",
        "[23] Sellers EW, Vaughan TM, Wolpaw JR. A brain-computer interface for long-term independent home use. Amyotrophic Lateral Sclerosis. 2010;11:449-455.",
        "[24] Fazel-Rezai R, Abhari K. A region-based P300 speller for brain-computer interface. Canadian Journal of Electrical and Computer Engineering. 2009;34:81-85.",
        "[25] Jin J, Allison BZ, Wang X, Neuper C. A comparison of three P300 brain-computer interface spellers for communication. Clinical Neurophysiology. 2012;123:1327-1337.",
        "[26] Zhang T, Farooq F, et al. EEG sensor selection by sparse spatial filtering in ERP based brain-computer interfaces. IEEE Transactions on Neural Systems and Rehabilitation Engineering. 2011;19:636-646.",
        "[27] Cecotti H. A self-paced and calibration-less SSVEP-based brain-computer interface speller. IEEE Transactions on Neural Systems and Rehabilitation Engineering. 2010;18:127-133.",
        "[28] Zhang H, Guan C, Wang C. Asynchronous P300-based brain-computer interfaces: a computational approach with statistical models. IEEE Transactions on Biomedical Engineering. 2008;55:1754-1763.",
        "[29] Spüler M, Bensch M, Kleih S, et al. Online use of error-related potentials in healthy users and people with severe motor impairment increases performance of a P300-BCI. Clinical Neurophysiology. 2012;123:1328-1337.",
        "[30] Lin CT, Chuang CH, Kerick SE, et al. Mindfulness based attention training improves P300 BCI performance. Journal of Neural Engineering. 2018;15:066020.",
        "[31] Blankertz B, et al. BCI Competition III: dataset II, P300 speller paradigm. 2004. Available: https://www.bbci.de/competition/iii/desc_II.pdf.",
        "[32] Mainsah B, Fleeting C, Balmat T, Sellers E, Collins L. bigP3BCI: an open, diverse and machine learning ready P300-based brain-computer interface dataset. PhysioNet. 2025. doi:10.13026/0byy-ry86.",
        "[33] Barachant A, Congedo M. A plug and play P300 BCI using information geometry. arXiv:1409.0107. 2014.",
        "[34] Sosulski J, et al. Evaluating deep learning performance for P300 neural signal classification. Frontiers in Neuroinformatics. 2024;17:1284376.",
        "[35] Bianchi L, et al. Merging brain-computer interface P300 speller datasets: perspectives and pitfalls. Frontiers in Neuroergonomics. 2022;3:1045653. doi:10.3389/fnrgo.2022.1045653.",
        "[36] Thompson DE, et al. Performance evaluation of P300-based brain-computer interfaces. Journal of Neural Engineering. 2014;11:035001.",
        "[37] Riccio A, et al. Attention and P300-based BCI performance in people with amyotrophic lateral sclerosis. Frontiers in Human Neuroscience. 2013;7:732.",
        "[38] Lotte F, Bougrain L, Cichocki A, et al. A review of classification algorithms for EEG-based brain-computer interfaces. Journal of Neural Engineering. 2018;15:031005.",
        "[39] Mladenovic J, et al. A practical review of P300 speller paradigms and evaluation measures. Frontiers in Human Neuroscience. 2022;16:1077717.",
        "[40] BCI-Utility: a metric for assessing asynchronous P300 systems. Journal of Neural Engineering. 2023;20:046010.",
    ]
    for reference in references:
        p = doc.add_paragraph(style="Reference")
        p.add_run(reference)

    doc.save(OUT)


if __name__ == "__main__":
    build_document()
