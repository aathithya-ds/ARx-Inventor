"""
ARX INVENTOR - Report Service
Handles research briefing formatting, Markdown export, and professional PDF generation via ReportLab.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from config.settings import settings

class ReportService:
    """Manages report presentation, citation inspection, and file exports."""

    def __init__(self, reports_dir: Optional[Path] = None):
        self.reports_dir = reports_dir or settings.REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def export_markdown(self, report_markdown: str, filename: str = "research_briefing.md") -> Path:
        """Saves report as a Markdown document."""
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        if not clean_name.endswith(".md"):
            clean_name += ".md"
        out_path = self.reports_dir / clean_name
        out_path.write_text(report_markdown, encoding="utf-8")
        return out_path

    def export_pdf(self, report_markdown: str, filename: str = "research_briefing.pdf") -> Path:
        """
        Generates an executive-styled PDF report using ReportLab.
        """
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
        if not clean_name.endswith(".pdf"):
            clean_name += ".pdf"
        out_path = self.reports_dir / clean_name

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch

            doc = SimpleDocTemplate(
                str(out_path),
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=12
            )

            h2_style = ParagraphStyle(
                'ReportH2',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#1E3A8A'),
                spaceBefore=14,
                spaceAfter=6
            )

            h3_style = ParagraphStyle(
                'ReportH3',
                parent=styles['Heading3'],
                fontSize=11,
                leading=15,
                textColor=colors.HexColor('#3B82F6'),
                spaceBefore=8,
                spaceAfter=4
            )

            body_style = ParagraphStyle(
                'ReportBody',
                parent=styles['Normal'],
                fontSize=9.5,
                leading=13.5,
                textColor=colors.HexColor('#1F2937'),
                spaceAfter=6
            )

            quote_style = ParagraphStyle(
                'ReportQuote',
                parent=styles['Italic'],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor('#4B5563'),
                leftIndent=15,
                spaceAfter=6
            )

            story = []

            # Header brand
            header_brand = Paragraph("<b>ARX INVENTOR</b> — Source-Based AI Research Briefing", h3_style)
            story.append(header_brand)
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=10))

            lines = report_markdown.split('\n')
            for line in lines:
                l_str = line.strip()
                if not l_str:
                    story.append(Spacer(1, 4))
                    continue

                if l_str.startswith("# "):
                    txt = l_str[2:].replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(txt, title_style))
                elif l_str.startswith("## "):
                    txt = l_str[3:].replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(txt, h2_style))
                elif l_str.startswith("### "):
                    txt = l_str[4:].replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(txt, h3_style))
                elif l_str.startswith(">"):
                    txt = l_str[1:].strip().replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(txt, quote_style))
                elif l_str.startswith("- ") or l_str.startswith("* "):
                    txt = "&bull; " + l_str[2:].replace("<", "&lt;").replace(">", "&gt;")
                    # Bold replacement
                    txt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', txt)
                    story.append(Paragraph(txt, body_style))
                elif l_str.startswith("|"):
                    # Skip or render minimal table separator
                    continue
                else:
                    txt = l_str.replace("<", "&lt;").replace(">", "&gt;")
                    txt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', txt)
                    story.append(Paragraph(txt, body_style))

            doc.build(story)
            return out_path
        except Exception:
            # Fallback to plain text written if ReportLab encounters PDF formatting anomaly
            out_path.write_text(report_markdown, encoding="utf-8")
            return out_path

    def inspect_citation(
        self,
        citation_id: str,
        sources: List[Dict[str, Any]],
        passages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Retrieves source record and all matching passages for a citation like [S1].
        """
        clean_id = citation_id.strip().strip("[]")

        matching_source = None
        for s in sources:
            if s.get("source_id_label") == clean_id or s.get("id") == clean_id:
                matching_source = s
                break

        matching_passages = [
            p for p in passages
            if p.get("source_id") == clean_id or p.get("source_id_label") == clean_id
        ]

        return {
            "citation_id": clean_id,
            "source": matching_source,
            "passages": matching_passages,
            "total_passages": len(matching_passages)
        }
