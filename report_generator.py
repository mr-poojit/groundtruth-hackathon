import datetime
import os
import zipfile

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor


# ------------------------------------------------------------
# PDF GENERATION (Polished + Professional Layout)
# ------------------------------------------------------------

def create_pdf(metrics, chart_paths, insights_text):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"output/report_{ts}.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 22
    title_style.leading = 26

    body = styles['BodyText']
    body.fontSize = 11
    body.leading = 16

    story = []

    # Report Title
    story.append(Paragraph("📊 Weekly Performance Report", title_style))
    story.append(Spacer(1, 20))

    # Executive Summary
    story.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
    story.append(Spacer(1, 6))

    formatted_insights = insights_text.replace("\n", "<br/>")
    story.append(Paragraph(formatted_insights, body))
    story.append(Spacer(1, 18))

    # Metrics Table
    story.append(Paragraph("<b>Key Metrics</b>", styles['Heading2']))
    story.append(Spacer(1, 10))

    table_rows = [["Metric", "Value"]]
    for k, v in metrics.items():
        table_rows.append([str(k), str(v)])

    table = Table(table_rows, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 25))

    # Charts Section
    story.append(Paragraph("<b>Generated Charts</b>", styles['Heading2']))
    story.append(Spacer(1, 10))

    for ch in chart_paths:
        story.append(Image(ch, width=450, height=250))
        story.append(Spacer(1, 15))

    doc.build(story)
    return pdf_path


# ------------------------------------------------------------
# PPT GENERATION (Premium Professional Layout)
# ------------------------------------------------------------

def create_ppt(metrics, chart_paths, insights_text):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ppt_path = f"output/report_{ts}.pptx"

    prs = Presentation()

    # ------------------------------
    # Slide 1 — Title Slide
    # ------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Weekly Performance Report"
    subtitle = slide.placeholders[1]
    subtitle.text = "Automated Insight Engine\nGenerated using AI"

    # ------------------------------
    # Slide 2 — Executive Summary
    # ------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Executive Summary"

    tf = slide.placeholders[1].text_frame
    tf.clear()

    for line in insights_text.split("\n"):
        p = tf.add_paragraph()
        p.text = line.strip()
        p.level = 0
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(60, 60, 60)

    # ------------------------------
    # Slide 3 — Metrics Slide
    # ------------------------------
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Metrics Summary"

    tf = slide.placeholders[1].text_frame
    tf.clear()

    for k, v in metrics.items():
        p = tf.add_paragraph()
        p.text = f"{k}: {v}"
        p.level = 0
        p.font.size = Pt(20)
        p.font.bold = True

    # ------------------------------
    # Slide 4+ — Chart Slides
    # ------------------------------
    for ch in chart_paths:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Generated Chart"

        slide.shapes.add_picture(
            ch,
            Inches(1),
            Inches(1.5),
            width=Inches(8)
        )

    prs.save(ppt_path)
    return ppt_path


# ------------------------------------------------------------
# ZIP PACKAGING (PDF + PPTX + All Charts)
# ------------------------------------------------------------

def create_zip(pdf_path, ppt_path, chart_paths):
    zip_path = pdf_path.replace(".pdf", ".zip")

    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(pdf_path, os.path.basename(pdf_path))
        z.write(ppt_path, os.path.basename(ppt_path))

        for chart in chart_paths:
            z.write(chart, os.path.basename(chart))

    return zip_path
