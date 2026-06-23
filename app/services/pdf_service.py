import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(data: Dict[str, Any]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=0,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=18
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10
    )
    
    # Title & Subtitle
    story.append(Paragraph("Semantic Resume Matcher - Analysis Report", title_style))
    story.append(Paragraph("Match analysis and optimization insights.", subtitle_style))
    
    # Score Summary Table
    story.append(Paragraph("Score Summary", h2_style))
    score_data = [
      [Paragraph("Metric", bold_body_style), Paragraph("Score / Status", bold_body_style), Paragraph("Weight", bold_body_style)],
      [Paragraph("Resume Match Score", body_style), Paragraph(f"<b>{data.get('score', 0)}%</b> ({data.get('verdict', 'N/A')})", body_style), Paragraph("100%", body_style)],
      [Paragraph("Keyword Coverage", body_style), Paragraph(f"{data.get('keyword_coverage_percentage', 0)}%", body_style), Paragraph("40%", body_style)],
      [Paragraph("Semantic Similarity", body_style), Paragraph(f"{data.get('semantic_score', 0)}%", body_style), Paragraph("30%", body_style)],
      [Paragraph("Experience Match", body_style), Paragraph(f"{data.get('experience_compatibility', 'N/A')} ({data.get('experience_score', 0)}%)", body_style), Paragraph("20%", body_style)],
      [Paragraph("Education Match", body_style), Paragraph(f"{data.get('education_compatibility', 'N/A')} ({data.get('education_score', 0)}%)", body_style), Paragraph("10%", body_style)],
      [Paragraph("Resume Strength Score", body_style), Paragraph(f"<b>{data.get('resume_strength', 0)}%</b>", body_style), Paragraph("Profile Quality", body_style)]
    ]
    
    t_scores = Table(score_data, colWidths=[200, 200, 140])
    t_scores.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
    ]))
    story.append(t_scores)
    story.append(Spacer(1, 12))
    
    # Summary Box
    story.append(Paragraph("Executive Summary", h2_style))
    summary_text = data.get("summary", "No summary provided.")
    t_summary = Table([[Paragraph(summary_text, body_style)]], colWidths=[540])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor('#bfdbfe')),
        ('TOPPADDING', (0,0), (0,0), 8),
        ('BOTTOMPADDING', (0,0), (0,0), 8),
        ('LEFTPADDING', (0,0), (0,0), 10),
        ('RIGHTPADDING', (0,0), (0,0), 10),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 12))

    # Verification Table
    story.append(Paragraph("Experience & Education Verification", h2_style))
    verif_data = [
        [Paragraph("Parameter", bold_body_style), Paragraph("Detected Value", bold_body_style), Paragraph("Job Requirement / Status", bold_body_style)],
        [Paragraph("Experience Duration", body_style), Paragraph(data.get("internship_duration", "0 months"), body_style), Paragraph(data.get("jd_requirement", "0-1 years"), body_style)],
        [Paragraph("Experience Match", body_style), Paragraph(data.get("experience_compatibility", "N/A"), body_style), Paragraph("Status: " + data.get("experience_compatibility", "N/A"), body_style)],
        [Paragraph("Education Match", body_style), Paragraph(data.get("education_compatibility", "N/A"), body_style), Paragraph(f"Education score: {data.get('education_score', 0)}%", body_style)]
    ]
    t_verif = Table(verif_data, colWidths=[180, 180, 180])
    t_verif.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_verif)
    story.append(Spacer(1, 12))
    
    # Skills Analysis
    story.append(Paragraph("Keywords & Technical Skills", h2_style))
    matched_skills = data.get("matched_skills", [])
    missing_skills = data.get("missing_skills", [])
    additional_skills = data.get("additional_resume_skills", [])
    
    matched_str = ", ".join(matched_skills) if matched_skills else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"
    additional_str = ", ".join(additional_skills) if additional_skills else "None"
    
    skills_data = [
        [Paragraph("Matched Keywords", bold_body_style), Paragraph(matched_str, body_style)],
        [Paragraph("Missing Keywords", bold_body_style), Paragraph(missing_str, body_style)],
        [Paragraph("Additional Resume Skills", bold_body_style), Paragraph(additional_str, body_style)]
    ]
    t_skills = Table(skills_data, colWidths=[140, 400])
    t_skills.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_skills)
    story.append(Spacer(1, 12))
    
    # Sections Analysis
    story.append(Paragraph("Resume Section Completeness", h2_style))
    found = ", ".join(data.get("sections_found", []))
    missing = ", ".join(data.get("missing_sections", []))
    sections_data = [
        [Paragraph("Sections Found", bold_body_style), Paragraph(found or "None", body_style)],
        [Paragraph("Missing Sections", bold_body_style), Paragraph(missing or "None", body_style)],
        [Paragraph("Section Score", bold_body_style), Paragraph(f"{data.get('section_score', 0)}%", body_style)]
    ]
    t_sections = Table(sections_data, colWidths=[140, 400])
    t_sections.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sections)
    story.append(Spacer(1, 12))
    
    # Recommendations
    story.append(Paragraph("Actionable Recommendations", h2_style))
    recs = data.get("recommendations", [])
    if recs:
        for r in recs:
            story.append(Paragraph(f"&bull; {r}", bullet_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No recommendations generated.", body_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer
