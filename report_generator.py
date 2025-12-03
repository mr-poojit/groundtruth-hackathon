from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from pptx import Presentation
from pptx.util import Inches, Pt
import datetime
import zipfile
import os

def create_pdf(metrics, chart_paths, insights_text):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"output/report_{ts}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Weekly Performance Report", styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(insights_text.replace("\n", "<br/>"), styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Metrics", styles['Heading2']))

    rows = [["Metric", "Value"]]
    for k, v in metrics.items():
        rows.append([str(k), str(v)])

    table = Table(rows)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    for ch in chart_paths:
        story.append(Image(ch, width=400, height=200))
        story.append(Spacer(1, 12))

    doc.build(story)
    return pdf_path


def create_ppt(metrics, chart_paths, insights_text):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ppt_path = f"output/report_{ts}.pptx"

    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]

    # Slide 1 – Title
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = "Weekly Performance Report"
    slide.placeholders[1].text = "Auto-generated Insights"

    # Slide 2 – Insights
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Executive Summary"
    body = slide.placeholders[1].text = insights_text

    # Slide 3 – Metrics
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Key Metrics"

    lines = []
    for k, v in metrics.items():
        lines.append(f"{k}: {v}")

    slide.placeholders[1].text = "\n".join(lines)

    # Chart slides
    for ch in chart_paths:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = "Chart"
        slide.shapes.add_picture(ch, Inches(1), Inches(1.5), width=Inches(8))

    prs.save(ppt_path)
    return ppt_path


def create_zip(pdf_path, ppt_path, chart_paths):
    zip_path = pdf_path.replace(".pdf", ".zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(pdf_path, os.path.basename(pdf_path))
        zipf.write(ppt_path, os.path.basename(ppt_path))

        for ch in chart_paths:
            zipf.write(ch, os.path.basename(ch))

    return zip_path
