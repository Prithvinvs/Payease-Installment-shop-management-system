"""
PDF Generation Script for the Software Requirements Specification (SRS) Document.
Automatically installs reportlab if missing, parses srs.md, and creates docs/SRS.pdf.
"""
import os
import sys
import subprocess

# 1. Self-installation hook for reportlab
try:
    import reportlab
except ImportError:
    print("reportlab library not found. Installing now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    import reportlab

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas to calculate total pages and render running headers and footers with page numbers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        # Skip headers and footers on the cover page (Page 1)
        if self._pageNumber == 1:
            return
            
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4F46E5"))
        self.drawString(54, 750, "SOFTWARE REQUIREMENTS SPECIFICATION: PAYEASE")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.line(54, 55, 558, 55)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 42, "Document Version 1.0.0 | PayEase Instalment Shop ERP")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 42, page_text)
        self.restoreState()


def build_pdf(src_markdown_path, dest_pdf_path):
    print(f"Reading SRS contents from {src_markdown_path}...")
    with open(src_markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    styles = getSampleStyleSheet()
    
    # Custom Styles matching PayEase UI palette
    primary_color = colors.HexColor("#4F46E5")
    text_color = colors.HexColor("#1E293B")
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=primary_color,
        spaceAfter=15,
        alignment=1 # Centered
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=40,
        alignment=1
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        alignment=1
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_color,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []

    # --- COVER PAGE ---
    story.append(Spacer(1, 150))
    story.append(Paragraph("SOFTWARE REQUIREMENTS<br/>SPECIFICATION", title_style))
    story.append(Paragraph("for<br/><b>PayEase - Instalment Shop Management System</b>", subtitle_style))
    story.append(Spacer(1, 150))
    
    meta_html = """
    <b>Prepared For:</b> Academic Project Evaluation & Submission<br/>
    <b>Document Version:</b> 1.0.0 (Production Release)<br/>
    <b>Date of Submission:</b> 24-July-2026<br/>
    <b>Status:</b> Completed and Fully Verified
    """
    story.append(Paragraph(meta_html, meta_style))
    story.append(PageBreak())

    # --- PARSE AND COMPILE MARKDOWN CONTENT ---
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        
        # Skip header lines that are cover info
        if stripped.startswith("# ") and "PayEase" in stripped:
            continue
        if stripped.startswith("**Version**:") or stripped.startswith("**Date**:") or stripped.startswith("**Document Status**:"):
            continue
            
        # Code block handler
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            # Render code block lines in monospace
            code_style = ParagraphStyle(
                'CodeLine',
                fontName='Courier',
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#475569"),
                leftIndent=20
            )
            story.append(Paragraph(stripped.replace("<", "&lt;").replace(">", "&gt;"), code_style))
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(stripped.replace("### ", ""), h2_style))
        elif stripped.startswith("## "):
            story.append(Paragraph(stripped.replace("## ", ""), h1_style))
        elif stripped.startswith("* "):
            bullet_text = stripped.replace("* ", "&bull; ")
            story.append(Paragraph(bullet_text, bullet_style))
        elif stripped:
            # Convert simple markdown bold/italic tags to HTML
            processed = stripped.replace("**", "<b>", 1).replace("**", "</b>", 1)
            processed = processed.replace("**", "<b>").replace("**", "</b>")
            processed = processed.replace("<br/>", "<br/>")
            processed = processed.replace("<", "&lt;").replace(">", "&gt;")
            # Re-convert bold elements safely
            processed = processed.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            processed = processed.replace("&lt;br/&gt;", "<br/>")
            story.append(Paragraph(processed, body_style))
        else:
            story.append(Spacer(1, 6))

    # Compile Doc
    print(f"Compiling PDF into {dest_pdf_path}...")
    doc = SimpleDocTemplate(
        dest_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF generation completed successfully!")


if __name__ == '__main__':
    src = 'docs/srs.md'
    dest = 'docs/SRS.pdf'
    
    # Ensure folders exist
    os.makedirs('docs', exist_ok=True)
    os.makedirs('scripts', exist_ok=True)
    
    try:
        build_pdf(src, dest)
    except Exception as e:
        import traceback
        print(f"Error during PDF compilation: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
