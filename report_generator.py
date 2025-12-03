import datetime
import os
import zipfile
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from textwrap import wrap

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


def create_pdf(metrics, chart_paths, insights_text, base_name):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"output/{base_name}.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title = styles['Title']
    title.fontSize = 22

    h2 = styles['Heading2']
    h2.spaceAfter = 12

    p = styles['BodyText']
    p.fontSize = 11
    p.leading = 15

    story = []

    # Title
    story.append(Paragraph("📊 Automated Insight Report", title))
    story.append(Spacer(1, 20))

    # AI Insights Section
    story.append(Paragraph("Executive Summary", h2))

    # Clean markdown-like output
    clean = insights_text.replace("* ", "• ").replace("\n", "<br/>")
    story.append(Paragraph(clean, p))
    story.append(Spacer(1, 20))

    # Metrics Section
    story.append(Paragraph("Key Metrics", h2))

    table_rows = [["Metric", "Value"]]

    for k, v in metrics.items():
        if k == "Top Cities" and isinstance(v, dict):
            nice = "<br/>".join([f"{c}: {val}" for c, val in v.items()])
            table_rows.append([k, nice])
        else:
            table_rows.append([k, str(v)])

    table = Table(table_rows, colWidths=[180, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E5E5E5")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6)
    ]))

    story.append(table)
    story.append(Spacer(1, 25))

    # Charts
    story.append(Paragraph("Visual Insights", h2))

    for ch in chart_paths:
        story.append(Image(ch, width=450, height=250))
        story.append(Spacer(1, 18))

    doc.build(story)
    return pdf_path



# ------------------------------------------------------------
# PPT GENERATION (Premium Professional Layout)
# ------------------------------------------------------------

def add_wrapped_textbox(slide, text, left, top, width, height, font_size=18):
    tx = slide.shapes.add_textbox(left, top, width, height)
    tf = tx.text_frame
    tf.word_wrap = True
    tf.margin_left = 2000
    tf.margin_right = 2000
    tf.margin_top = 1000

    for line in text.split("\n"):
        if not line.strip():
            continue
        p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = RGBColor(50, 50, 50)
        p.level = 0


def create_ppt(metrics, chart_paths, insights_text, base_name):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ppt_path = f"output/{base_name}.pptx"
    prs = Presentation()

    # TITLE SLIDE
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Automated Insight Report"
    slide.placeholders[1].text = "Generated using AI insights and performance analytics"

    # EXEC SUMMARY - AUTO SPLIT
    chunks = wrap(insights_text, 450)

    for chunk in chunks:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Executive Summary"

        add_wrapped_textbox(
            slide,
            chunk,
            Inches(0.5),
            Inches(1.5),
            Inches(9),
            Inches(4.5),
            font_size=18
        )

    # METRICS SLIDE
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Key Metrics"

    metric_text = "\n".join([
        f"{k}: {v}" for k, v in metrics.items()
    ])

    add_wrapped_textbox(
        slide,
        metric_text,
        Inches(0.5),
        Inches(1.5),
        Inches(9),
        Inches(4.5),
        font_size=20
    )

    # CHART SLIDES
    for ch in chart_paths:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Visual Insight"
        slide.shapes.add_picture(ch, Inches(1), Inches(1.7), width=Inches(8))

    prs.save(ppt_path)
    return ppt_path

# ------------------------------------------------------------
# ZIP PACKAGING (PDF + PPTX + All Charts)
# ------------------------------------------------------------

def create_zip(pdf_path, ppt_path, chart_paths, base_name):
    zip_path = f"output/{base_name}.zip"

    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(pdf_path, os.path.basename(pdf_path))
        z.write(ppt_path, os.path.basename(ppt_path))

        for chart in chart_paths:
            z.write(chart, os.path.basename(chart))

    return zip_path
