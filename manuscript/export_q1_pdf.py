from html import escape
from pathlib import Path

from docx import Document
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).parent
DOCX = ROOT / "NeuroSync_CASP_X_Manuscript.docx"
PDF = ROOT / "NeuroSync_CASP_X_Manuscript.pdf"


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#4A4A4A"))
    canvas.drawString(0.8 * inch, 0.42 * inch, "NeuroSync CASP X")
    canvas.drawRightString(7.7 * inch, 0.42 * inch, str(document.page))
    canvas.restoreState()


def build():
    source = Document(DOCX)
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=11, leading=14.3, spaceAfter=6.5)
    title = ParagraphStyle("TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17, leading=20, alignment=TA_CENTER, spaceAfter=10)
    subtitle = ParagraphStyle("SubtitleX", parent=body, fontName="Helvetica-Oblique", fontSize=11.5, leading=14, alignment=TA_CENTER, spaceAfter=7)
    author = ParagraphStyle("Author", parent=body, alignment=TA_CENTER, fontSize=9.5, leading=12, spaceAfter=14)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13.2, leading=16, spaceBefore=11, spaceAfter=5, textColor=colors.black)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.2, leading=14, spaceBefore=8, spaceAfter=4, textColor=colors.black)
    caption = ParagraphStyle("Caption", parent=body, fontName="Helvetica-Oblique", fontSize=8.7, leading=10.8, spaceAfter=7)
    reference = ParagraphStyle("Reference", parent=body, fontSize=8.8, leading=11.1, leftIndent=12, firstLineIndent=-12, spaceAfter=3.3)
    story = []
    table_iter = iter(source.tables)

    paragraphs = list(source.paragraphs)
    for p in paragraphs:
        text = p.text.strip()
        if not text:
            continue
        style_name = p.style.name
        if style_name == "Title":
            style = title
        elif style_name == "Heading 1":
            style = h1
        elif style_name == "Heading 2":
            style = h2
        elif style_name == "Reference":
            style = reference
        elif text.startswith("Table "):
            style = caption
        elif text.startswith("A Safety Aware"):
            style = subtitle
        elif text.startswith("Team NeuroSync"):
            style = author
        elif text.startswith("Keywords:"):
            style = ParagraphStyle("Keywords", parent=body, fontName="Helvetica-Oblique", fontSize=8.8, leading=11, spaceAfter=7)
        else:
            style = body
        story.append(Paragraph(escape(text).replace("\n", "<br/>"), style))
        # Tables in the DOCX follow known caption-adjacent content. Insert in sequence
        # when the next available table should occur after a pipeline/result paragraph.
        if text.startswith("CASP X is organized") or text.startswith("The implementation was exercised") or text.startswith("A public 6 by 6") or text.startswith("The next study should"):
            try:
                t = next(table_iter)
            except StopIteration:
                continue
            rows = [[Paragraph(escape(cell.text), ParagraphStyle("TableCell", parent=body, fontSize=7.7, leading=9.2, spaceAfter=0)) for cell in row.cells] for row in t.rows]
            widths = [1.0 * inch, 1.35 * inch, 3.2 * inch, 1.1 * inch]
            if len(rows[0]) == 5:
                widths = [2.4 * inch, 1.05 * inch, 1.05 * inch, 0.85 * inch, 0.85 * inch]
            elif len(rows[0]) == 3:
                widths = [1.0 * inch, 3.75 * inch, 1.45 * inch]
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            commands = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9D9D9")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
            for index in range(1, len(rows)):
                if index % 2:
                    commands.append(("BACKGROUND", (0, index), (-1, index), colors.HexColor("#F3F6F9")))
            table.setStyle(TableStyle(commands))
            story.append(Spacer(1, 3))
            story.append(table)
            story.append(Spacer(1, 4))
    output = SimpleDocTemplate(str(PDF), pagesize=letter, rightMargin=0.8*inch, leftMargin=0.8*inch, topMargin=0.7*inch, bottomMargin=0.65*inch)
    output.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build()
