import sys
import re

with open('components/ot_manual.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r"""        col_cfg = \{
            "Mã NV": st.column_config.TextColumn\(t\("Mã NV", "社員番号"\), required=True\),
            "Tên NV": st.column_config.TextColumn\(t\("Tên NV", "氏名"\), required=True\),
            "Phòng ban": st.column_config.TextColumn\(t\("Phòng ban", "部署"\)\),
            "Chức vụ": st.column_config.TextColumn\(t\("Chức vụ", "役職"\)\),
            "Ngày vào làm": st.column_config.DateColumn\(t\("Ngày vào làm", "入社日"\), format="DD/MM/YYYY"\),
            "Lương cơ bản": st.column_config.NumberColumn\(t\("Lương cơ bản", "基本給"\), format="%d", min_value=0\),
            "PC ăn trưa": st.column_config.NumberColumn\(t\("PC ăn trưa", "昼食手当"\), format="%d", min_value=0\),
            "PC khác": st.column_config.NumberColumn\(t\("PC khác", "その他手当"\), format="%d", min_value=0\),
            "Lương Gross": st.column_config.NumberColumn\(t\("Lương Gross \(Tự động\)", "総支給額 \(自動\)"\), format="%d", disabled=True\)
        \}
        
        edited_emp = st.data_editor\(
            emp_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=col_cfg,
            key="employees_editor"
        \)
        
        if st.button\(t\("💾 LƯU THÔNG TIN CHUNG & NHÂN SỰ", "💾 一般情報とスタッフを保存"\), key="save_emps", type="primary"\):
            st.session_state\['ot_base_data'\]\['standard_days'\] = std_days_mo
            st.session_state\['ot_base_data'\]\['from_date'\] = from_date.strftime\("%Y-%m-%d"\)
            st.session_state\['ot_base_data'\]\['to_date'\] = to_date.strftime\("%Y-%m-%d"\)
            save_base_data\(st.session_state\['ot_base_data'\]\)
            
            # Tự động tính Lương Gross
            edited_emp\['Lương cơ bản'\] = pd.to_numeric\(edited_emp\['Lương cơ bản'\], errors='coerce'\).fillna\(0\)
            edited_emp\['PC ăn trưa'\] = pd.to_numeric\(edited_emp\['PC ăn trưa'\], errors='coerce'\).fillna\(0\)
            edited_emp\['PC khác'\] = pd.to_numeric\(edited_emp\['PC khác'\], errors='coerce'\).fillna\(0\)
            edited_emp\['Lương Gross'\] = edited_emp\['Lương cơ bản'\] \+ edited_emp\['PC ăn trưa'\] \+ edited_emp\['PC khác'\]
            
            save_employees_df\(edited_emp\)
            st.success\(t\("Đã lưu Thông tin chung và Danh sách nhân sự thành công!", "設定とスタッフリストを保存しました！"\)\)
            st.rerun\(\)"""

replacement = """        col_cfg = {
            "Mã NV": st.column_config.TextColumn(t("Mã NV", "社員番号"), required=True),
            "Tên NV": st.column_config.TextColumn(t("Tên NV", "氏名"), required=True),
            "Phòng ban": st.column_config.TextColumn(t("Phòng ban", "部署")),
            "Chức vụ": st.column_config.TextColumn(t("Chức vụ", "役職")),
            "Ngày vào làm": st.column_config.DateColumn(t("Ngày vào làm", "入社日"), format="DD/MM/YYYY"),
            "Lương cơ bản": st.column_config.NumberColumn(t("Lương cơ bản", "基本給"), format="%d", min_value=0),
            "Lương Gross": st.column_config.NumberColumn(t("Lương Gross (Tự động)", "総支給額 (自動)"), format="%d", disabled=True)
        }
        
        # Determine allowance columns (columns that are not standard)
        standard_cols = ["Mã NV", "Tên NV", "Phòng ban", "Chức vụ", "Ngày vào làm", "Lương cơ bản", "Lương Gross"]
        
        # Ensure default allowances exist if not present initially
        if "PC ăn trưa" not in emp_df.columns:
            emp_df.insert(5, "PC ăn trưa", 0)
        if "PC khác" not in emp_df.columns:
            emp_df.insert(6, "PC khác", 0)
            
        allowance_cols = [c for c in emp_df.columns if c not in standard_cols]
        for c in allowance_cols:
            col_cfg[c] = st.column_config.NumberColumn(c, format="%d", min_value=0)
            
        edited_emp = st.data_editor(
            emp_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=col_cfg,
            key="employees_editor"
        )
        
        with st.expander(t("➕ Thêm / Xóa Cột Phụ Cấp", "➕ 手当項目の追加・削除")):
            add_c1, add_c2 = st.columns([3, 1])
            with add_c1:
                new_pc_name = st.text_input(t("Nhập tên Phụ cấp mới:", "新しい手当名:"), key="new_pc_input")
            with add_c2:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button(t("Thêm Cột", "列を追加"), use_container_width=True):
                    if new_pc_name and new_pc_name not in emp_df.columns:
                        emp_df[new_pc_name] = 0
                        save_employees_df(emp_df)
                        st.rerun()
                    elif new_pc_name in emp_df.columns:
                        st.warning(t("Cột này đã tồn tại!", "この列は既に存在します！"))
            
            # Feature to remove allowance columns
            if len(allowance_cols) > 0:
                del_pc_name = st.selectbox(t("Chọn cột Phụ cấp để xóa:", "削除する手当列を選択:"), allowance_cols)
                if st.button(t("Xóa Cột", "列を削除")):
                    if del_pc_name in emp_df.columns:
                        emp_df = emp_df.drop(columns=[del_pc_name])
                        save_employees_df(emp_df)
                        st.rerun()
        
        if st.button(t("💾 LƯU THÔNG TIN CHUNG & NHÂN SỰ", "💾 一般情報とスタッフを保存"), key="save_emps", type="primary"):
            st.session_state['ot_base_data']['standard_days'] = std_days_mo
            st.session_state['ot_base_data']['from_date'] = from_date.strftime("%Y-%m-%d")
            st.session_state['ot_base_data']['to_date'] = to_date.strftime("%Y-%m-%d")
            save_base_data(st.session_state['ot_base_data'])
            
            # Tự động tính Lương Gross
            edited_emp['Lương cơ bản'] = pd.to_numeric(edited_emp['Lương cơ bản'], errors='coerce').fillna(0)
            gross = edited_emp['Lương cơ bản'].copy()
            for c in allowance_cols:
                edited_emp[c] = pd.to_numeric(edited_emp[c], errors='coerce').fillna(0)
                gross += edited_emp[c]
            edited_emp['Lương Gross'] = gross
            
            save_employees_df(edited_emp)
            st.success(t("Đã lưu Thông tin chung và Danh sách nhân sự thành công!", "設定とスタッフリストを保存しました！"))
            st.rerun()"""

new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)

if text == new_text:
    print('Failed to match pattern')
else:
    with open('components/ot_manual.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Success adding dynamic columns')
