import os
import io
import requests
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import streamlit as st

def ensure_font_downloaded():
    font_dir = "assets/fonts"
    os.makedirs(font_dir, exist_ok=True)
    font_path = os.path.join(font_dir, "Roboto-Regular.ttf")
    font_bold_path = os.path.join(font_dir, "Roboto-Bold.ttf")
    
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
        r = requests.get(url, allow_redirects=True)
        with open(font_path, 'wb') as f:
            f.write(r.content)
            
    if not os.path.exists(font_bold_path):
        url_bold = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
        r = requests.get(url_bold, allow_redirects=True)
        with open(font_bold_path, 'wb') as f:
            f.write(r.content)
            
    pdfmetrics.registerFont(TTFont('Roboto', font_path))
    pdfmetrics.registerFont(TTFont('Roboto-Bold', font_bold_path))

def strip_html_tags(text):
    import re
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # Replace common HTML entities manually
    text = text.replace('&nbsp;', ' ').replace('&ge;', '>=')
    return text

def generate_project_executive_pdf(df_project, project_name, period_label, analysis_text_vn, analysis_text_jp, total_hrs, total_cost, total_staff):
    ensure_font_downloaded()
    
    buffer = io.BytesIO()
    
    # Setup document
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Styles using Roboto for Unicode support
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Roboto-Bold',
        fontSize=20,
        textColor=colors.HexColor('#00B0F0'),
        alignment=1,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubTitle',
        parent=styles['Normal'],
        fontName='Roboto-Bold',
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        alignment=1,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='Roboto-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Roboto',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=10
    )
    
    # Add Logo if it exists
    if os.path.exists("logo_menu.jpg"):
        try:
            im = RLImage("logo_menu.jpg", width=120, height=35)
            im.hAlign = 'LEFT'
            story.append(im)
            story.append(Spacer(1, 20))
        except:
            pass
            
    # Title
    story.append(Paragraph("EXECUTIVE SUMMARY REPORT", title_style))
    story.append(Paragraph(f"Project: {project_name} | Period: {period_label}", subtitle_style))
    
    # Section 1: KPI Overview
    story.append(Paragraph("1. KEY PERFORMANCE INDICATORS (KPIs)", heading_style))
    
    data_kpi = [
        ['Metric', 'Value'],
        ['Total Overtime Hours', f"{total_hrs:,.1f} h"],
        ['Total Estimated Cost', f"{total_cost:,.0f} VND"],
        ['Total Active Staff', f"{total_staff} persons"]
    ]
    
    t_kpi = Table(data_kpi, colWidths=[200, 300])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f9ff')),
        ('FONTNAME', (0, 1), (-1, -1), 'Roboto'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 20))
    
    # Section 2: AI Commentary
    story.append(Paragraph("2. AI EXECUTIVE INSIGHTS", heading_style))
    if analysis_text_vn:
        # We need to strip HTML since reportlab doesn't support complex HTML easily (unless we use Platypus HTML, which is tricky)
        # So we just extract the text and render as paragraph
        clean_text_vn = strip_html_tags(analysis_text_vn)
        story.append(Paragraph(clean_text_vn, normal_style))
        story.append(Spacer(1, 10))
    
    if analysis_text_jp:
        clean_text_jp = strip_html_tags(analysis_text_jp)
        story.append(Paragraph(clean_text_jp, normal_style))
        
    story.append(Spacer(1, 20))
    
    # Section 3: Core Contributors (Pareto)
    story.append(Paragraph("3. CORE CONTRIBUTORS (TOP STAFF)", heading_style))
    if not df_project.empty:
        df_emp = df_project.groupby('employee_name')['ot_hours'].sum().reset_index()
        df_emp = df_emp.sort_values(by='ot_hours', ascending=False).head(10) # Top 10
        
        data_emp = [['No.', 'Employee Name', 'OT Hours Contribution']]
        for i, row in enumerate(df_emp.itertuples(), 1):
            data_emp.append([str(i), str(row.employee_name), f"{row.ot_hours:,.1f} h"])
            
        t_emp = Table(data_emp, colWidths=[50, 300, 150])
        t_emp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Roboto'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Zebra striping
        for i in range(1, len(data_emp)):
            bg_color = colors.whitesmoke if i % 2 == 0 else colors.white
            t_emp.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bg_color)]))
            
        story.append(t_emp)
    else:
        story.append(Paragraph("No data available for this project in the selected period.", normal_style))
        
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()
