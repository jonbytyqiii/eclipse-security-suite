#!/usr/bin/env python3
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class DocumentReportGenerator:
    """
    Programmatic ReportLab engine compiled cleanly to ensure flawless generation.
    """
    @staticmethod
    def compile_pdf_file(findings: List[Dict[str, Any]], metrics: Dict[str, Any], output_path: str):
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()

        # Build highly customized typographic block patterns layout styles
        title_style = ParagraphStyle(
            'DocTitle', parent=styles['Heading1'], fontSize=24, leading=28,
            textColor=colors.HexColor('#1e3a8a'), spaceAfter=12
        )
        sub_style = ParagraphStyle(
            'DocSub', parent=styles['Normal'], fontSize=11, leading=14,
            textColor=colors.HexColor('#4b5563'), spaceAfter=24
        )
        h2_style = ParagraphStyle(
            'H2', parent=styles['Heading2'], fontSize=14, leading=18,
            textColor=colors.HexColor('#0f172a'), spaceBefore=14, spaceAfter=8
        )
        body_style = ParagraphStyle(
            'Body', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155')
        )
        code_style = ParagraphStyle(
            'Code', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12,
            textColor=colors.HexColor('#b45309'), backColor=colors.HexColor('#fef3c7'),
            borderPadding=8, spaceBefore=6, spaceAfter=12
        )

        # Header Structure
        story.append(Paragraph("DockSentry CSPM Posture Compliance Report", title_style))
        story.append(Paragraph(f"Compiled Programmatic Matrix Evaluation Stack", sub_style))
        story.append(Spacer(1, 10))

        # Core Assessment Overview Table Configuration
        score = metrics.get('compliance_score', 0)
        score_color = '#10b981' if score >= 80 else '#f59e0b' if score >= 50 else '#ef4444'
        
        summary_data = [
            [Paragraph("<b>Compliance Grade Score:</b>", body_style), Paragraph(f"<font color='{score_color}'><b>{score}%</b></font>", title_style)],
            [Paragraph("<b>Total System Flaws:</b>", body_style), str(metrics.get('total_flaws', 0))],
            [Paragraph("<b>Critical Instability Risks:</b>", body_style), str(metrics.get('critical', 0))],
            [Paragraph("<b>High Structural Flaws:</b>", body_style), str(metrics.get('high', 0))],
            [Paragraph("<b>Medium Config Warnings:</b>", body_style), str(metrics.get('medium', 0))]
        ]
        
        t_summary = Table(summary_data, colWidths=[200, 300])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('PADDING', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 20))

        story.append(Paragraph("Vulnerability Logs Detail Ingestion", h2_style))
        
        # Sequentially map findings into the PDF story flow
        for f in findings:
            severity = f.get('severity', 'MEDIUM')
            sev_color = '#ec4899' if severity == 'CRITICAL' else '#ef4444' if severity == 'HIGH' else '#f59e0b' if severity == 'MEDIUM' else '#3b82f6'
            
            story.append(Paragraph(f"<b><font color='{sev_color}'>[{severity}]</font> {f.get('name', 'Policy Breach')}</b>", h2_style))
            story.append(Paragraph(f"<b>Target Node Context Vector:</b> {f.get('target', 'unknown')}", body_style))
            story.append(Paragraph(f"<b>Compliance Link Mapping:</b> {f.get('mapping', 'N/A')} | <b>Category:</b> {f.get('category','General')}", body_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>Description:</b> {f.get('desc', '')}", body_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>Remediation Script Strategy:</b><br/>{f.get('remediation', '')}", code_style))
            story.append(Spacer(1, 8))

        doc.build(story)