import io
import re
from docx import Document
from docx.shared import Cm, Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def strip_html_tags(text):
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    text = text.replace('&nbsp;', ' ').replace('&ge;', '>=')
    return text

def apply_font_to_table(table, font_name="Times New Roman"):
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = font_name

def generate_project_executive_docx(df_project, project_name, period_label, analysis_text_vn, analysis_text_jp, total_hrs, total_cost, total_staff, fig_emp, fig_time):
    doc = Document()
    
    # 1. Setup Page (A4)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Header Title
    title = doc.add_heading('EXECUTIVE SUMMARY REPORT', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.name = 'Times New Roman'
    title_run.font.color.rgb = RGBColor(0, 176, 240)
    
    # Subtitle
    subtitle = doc.add_paragraph(f"Project: {project_name} | Period: {period_label}")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].bold = True
    
    doc.add_heading('1. KEY PERFORMANCE INDICATORS (KPIs)', level=1)
    
    # KPI Table
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Metric'
    hdr_cells[1].text = 'Value'
    
    row = table.add_row().cells
    row[0].text = 'Total Overtime Hours'
    row[1].text = f"{total_hrs:,.1f} h"
    
    row = table.add_row().cells
    row[0].text = 'Total Estimated Cost'
    row[1].text = f"{total_cost:,.0f} VND"
    
    row = table.add_row().cells
    row[0].text = 'Total Active Staff'
    row[1].text = f"{total_staff} persons"
    
    apply_font_to_table(table)
    
    # AI Commentary
    doc.add_heading('2. AI EXECUTIVE INSIGHTS', level=1)
    if analysis_text_vn:
        p = doc.add_paragraph(strip_html_tags(analysis_text_vn))
    if analysis_text_jp:
        p = doc.add_paragraph(strip_html_tags(analysis_text_jp))
        
    # Top Contributors
    doc.add_heading('3. CORE CONTRIBUTORS (TOP STAFF)', level=1)
    if not df_project.empty:
        df_emp = df_project.groupby('employee_name')['ot_hours'].sum().reset_index()
        df_emp = df_emp.sort_values(by='ot_hours', ascending=False).head(10)
        
        emp_table = doc.add_table(rows=1, cols=3)
        emp_table.style = 'Light Grid Accent 1'
        hdr_cells = emp_table.rows[0].cells
        hdr_cells[0].text = 'No.'
        hdr_cells[1].text = 'Employee Name'
        hdr_cells[2].text = 'OT Hours'
        
        for i, row in enumerate(df_emp.itertuples(), 1):
            r_cells = emp_table.add_row().cells
            r_cells[0].text = str(i)
            r_cells[1].text = str(row.employee_name)
            r_cells[2].text = f"{row.ot_hours:,.1f} h"
            
        apply_font_to_table(emp_table)
            
    # Add Charts
    doc.add_page_break()
    doc.add_heading('4. VISUAL ANALYTICS', level=1)
    
    if fig_emp:
        try:
            # Generate PNG from plotly figure
            img_bytes = fig_emp.to_image(format="png", width=900, height=450, scale=2)
            img_io = io.BytesIO(img_bytes)
            p_img1 = doc.add_paragraph("Biểu đồ Phân Bổ Số Giờ:")
            p_img1.runs[0].bold = True
            doc.add_picture(img_io, width=Inches(6.5))
        except Exception as e:
            doc.add_paragraph(f"Cannot render chart 1: {e}")
            
    if fig_time:
        try:
            img_bytes2 = fig_time.to_image(format="png", width=900, height=450, scale=2)
            img_io2 = io.BytesIO(img_bytes2)
            p_img2 = doc.add_paragraph("Biểu đồ Xu Hướng Bù Đắp OT:")
            p_img2.runs[0].bold = True
            doc.add_picture(img_io2, width=Inches(6.5))
        except Exception as e:
            doc.add_paragraph(f"Cannot render chart 2: {e}")
            
    # Fix Times New Roman fallback in styles
    for style in doc.styles:
        if hasattr(style, 'font') and style.font.name is not None:
            style.font.name = 'Times New Roman'
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
