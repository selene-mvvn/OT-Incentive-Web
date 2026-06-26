import sys
import re

with open('components/ot_manual.py', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'def render_base_data\(\):.*?(?=def render_project_data\(\):)', text, re.DOTALL)
if m:
    old_content = m.group(0)
    
    new_content = '''def render_base_data():
    init_session_state()
    
    title = t("CÀI ĐẶT CHUNG", "一般設定")
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    st.info(t("Cài đặt thông tin hệ thống, nhân sự và ngày nghỉ lễ tại đây.", "システム情報、スタッフ、休日を設定します。"))
    
    tab1, tab2 = st.tabs([t("1. THÔNG TIN CHUNG & NHÂN SỰ", "1. 一般情報・スタッフ"), t("2. NGÀY NGHỈ & LỄ", "2. 休日・祭日")])
    
    with tab1:
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('THÔNG TIN CHUNG', '一般情報')}</h3>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            import datetime
            try:
                fd_str = st.session_state['ot_base_data'].get('from_date', '')
                if fd_str:
                    fd_val = datetime.datetime.strptime(fd_str, "%Y-%m-%d").date()
                else:
                    fd_val = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
            except:
                fd_val = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
            
            from_date = st.date_input(t("TỪ NGÀY (Kỳ Tính Lương)", "開始日 (給与計算期間)"), value=fd_val)
            
        with c2:
            try:
                td_str = st.session_state['ot_base_data'].get('to_date', '')
                if td_str:
                    td_val = datetime.datetime.strptime(td_str, "%Y-%m-%d").date()
                else:
                    td_val = datetime.date.today().replace(day=20)
            except:
                td_val = datetime.date.today().replace(day=20)
                
            to_date = st.date_input(t("ĐẾN NGÀY (Kỳ Tính Lương)", "終了日 (給与計算期間)"), value=td_val)
            
        with c3:
            std_days_mo = st.number_input(t("SỐ NGÀY LÀM VIỆC CHUẨN / THÁNG", "月の標準労働日数"), min_value=1.0, value=float(st.session_state['ot_base_data'].get('standard_days', 22.0)), step=0.5)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('THÔNG TIN NHÂN SỰ', 'スタッフ情報')}</h3>", unsafe_allow_html=True)
        from logic.employee_data import get_employees_df, save_employees_df
        emp_df = get_employees_df()
        
        st.caption(t("Quản lý thông tin nhân sự. Lưu ý: Cột 'Lương Gross' sẽ được tính TỰ ĐỘNG khi bạn bấm Lưu (Lương cơ bản + PC ăn trưa + PC khác).", "スタッフ情報の管理。注:「総支給額」は保存時に自動計算されます。"))
        
        col_cfg = {
            "Mã NV": st.column_config.TextColumn(t("Mã NV", "社員番号"), required=True),
            "Tên NV": st.column_config.TextColumn(t("Tên NV", "氏名"), required=True),
            "Phòng ban": st.column_config.TextColumn(t("Phòng ban", "部署")),
            "Chức vụ": st.column_config.TextColumn(t("Chức vụ", "役職")),
            "Ngày vào làm": st.column_config.DateColumn(t("Ngày vào làm", "入社日"), format="DD/MM/YYYY"),
            "Lương cơ bản": st.column_config.NumberColumn(t("Lương cơ bản", "基本給"), format="%d", min_value=0),
            "PC ăn trưa": st.column_config.NumberColumn(t("PC ăn trưa", "昼食手当"), format="%d", min_value=0),
            "PC khác": st.column_config.NumberColumn(t("PC khác", "その他手当"), format="%d", min_value=0),
            "Lương Gross": st.column_config.NumberColumn(t("Lương Gross (Tự động)", "総支給額 (自動)"), format="%d", disabled=True)
        }
        
        edited_emp = st.data_editor(
            emp_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=col_cfg,
            key="employees_editor"
        )
        
        if st.button(t("💾 LƯU THÔNG TIN CHUNG & NHÂN SỰ", "💾 一般情報とスタッフを保存"), key="save_emps", type="primary"):
            st.session_state['ot_base_data']['standard_days'] = std_days_mo
            st.session_state['ot_base_data']['from_date'] = from_date.strftime("%Y-%m-%d")
            st.session_state['ot_base_data']['to_date'] = to_date.strftime("%Y-%m-%d")
            save_base_data(st.session_state['ot_base_data'])
            
            # Tự động tính Lương Gross
            edited_emp['Lương cơ bản'] = pd.to_numeric(edited_emp['Lương cơ bản'], errors='coerce').fillna(0)
            edited_emp['PC ăn trưa'] = pd.to_numeric(edited_emp['PC ăn trưa'], errors='coerce').fillna(0)
            edited_emp['PC khác'] = pd.to_numeric(edited_emp['PC khác'], errors='coerce').fillna(0)
            edited_emp['Lương Gross'] = edited_emp['Lương cơ bản'] + edited_emp['PC ăn trưa'] + edited_emp['PC khác']
            
            save_employees_df(edited_emp)
            st.success(t("Đã lưu Thông tin chung và Danh sách nhân sự thành công!", "設定とスタッフリストを保存しました！"))
            st.rerun()
            
    with tab2:
'''
    
    # Extract tab3 content
    tab3_idx = old_content.find('    with tab3:')
    if tab3_idx != -1:
        tab3_content = old_content[tab3_idx + 14:] # skip `    with tab3:`
        new_content += '        ' + tab3_content.lstrip()
    
    new_text = text[:m.start()] + new_content + text[m.end():]
    with open('components/ot_manual.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Success")
else:
    print("Could not find render_base_data()")
