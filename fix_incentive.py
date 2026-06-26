import re

with open('components/incentive_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r"# Input area.*?st\.markdown\(f\"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px;'>\{t\('2\. Thông số Tính toán'"
replacement = """# Collect data for dropdowns
    from logic.project_data import get_projects_df
    projects_df = get_projects_df()
    
    master_names = []
    for _, r in projects_df.iterrows():
        n = str(r.get("Tên dự án", ""))
        c = str(r.get("Mã đơn hàng", ""))
        if n and n != "nan":
            if c and c != "nan" and c.strip():
                master_names.append(f"[{c.strip()}] {n.strip()}")
            else:
                master_names.append(n.strip())
    master_names = list(dict.fromkeys(master_names))
    
    known_projects = get_history("order_names")
    combined_projects = list(dict.fromkeys(master_names + known_projects))
    
    from logic.employee_data import get_employees_df
    emp_df = get_employees_df()
    master_employees = emp_df['Tên NV'].tolist() if not emp_df.empty else []
    
    known_employees = get_history("employees")
    combined_employees = list(dict.fromkeys(master_employees + known_employees))
    
    tab_calc, tab_charts = st.tabs([t("1. TÍNH INCENTIVE", "1. インセンティブ計算"), t("2. BẢNG XẾP HẠNG & BIỂU ĐỒ", "2. ランキング＆チャート")])
    
    with tab_calc:
        st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px;'>{t('1. Thông tin Dự án', '1. プロジェクト情報')}</h3>", unsafe_allow_html=True)
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            record_date = st.date_input(t("Ngày ghi nhận", "記録日"), value=datetime.date.today(), format="DD/MM/YYYY")
            
        with col_info2:
            opt_choose_proj = t("--- Chọn dự án ---", "--- 案件名を選択 ---")
            proj_opts = [opt_choose_proj] + combined_projects
            sel_proj = st.selectbox(t("Tên dự án", "案件名"), proj_opts)
            
            if sel_proj == opt_choose_proj:
                project_name = ""
            else:
                project_name = sel_proj
                
            clean_project_name = project_name
            if isinstance(project_name, str) and project_name.startswith("[") and "] " in project_name:
                split_idx = project_name.index("] ")
                clean_project_name = project_name[split_idx+2:]
                
        with col_info3:
            opt_choose_emp = t("--- Chọn nhân viên ---", "--- 担当者を選択 ---")
            emp_opts = [opt_choose_emp] + combined_employees
            sel_emp = st.selectbox(t("Người thực hiện", "担当者"), emp_opts)
            
            if sel_emp == opt_choose_emp:
                employee_name = ""
            else:
                employee_name = sel_emp
        
        st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px;'>{t('2. Thông số Tính toán'"""

new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
if new_text != text:
    with open('components/incentive_ui.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Success")
else:
    print("Failed to replace")
