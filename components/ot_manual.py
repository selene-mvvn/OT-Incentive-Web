import streamlit as st
import pandas as pd
from logic.ot_calculator import calculate_ot_pay, export_ot_to_excel, get_payroll_period, breakdown_ot_hours
from logic.action_log import save_action_log
from components.ui_utils import text_input_with_history
from logic.history import add_to_history, save_base_data, load_base_data, get_history
from logic.project_data import get_projects_df, save_projects_df
from logic.i18n import t

def init_session_state():
    if 'ot_base_data' not in st.session_state:
        # Try to load from persistent file first
        saved = load_base_data()
        if saved:
            if 'holidays_df' not in saved or not isinstance(saved.get('holidays_df'), pd.DataFrame):
                saved['holidays_df'] = pd.DataFrame(columns=["Ngày nghỉ", "Lý do"])
            # Provide defaults for new fields if not exist
            saved.setdefault('standard_hours_per_year', 1900.0)
            saved.setdefault('hours_per_day', 8.0)
            saved.setdefault('standard_days', 22.0)
            st.session_state['ot_base_data'] = saved
        else:
            st.session_state['ot_base_data'] = {
                'standard_hours_per_year': 1900.0,
                'hours_per_day': 8.0,
                'standard_days': 22.0,
                'holidays_df': pd.DataFrame(columns=["Ngày nghỉ", "Lý do"])
            }
    if 'ot_records' not in st.session_state:
        st.session_state['ot_records'] = []
    if 'ot_records' not in st.session_state:
        st.session_state['ot_records'] = []

def render_base_data():
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
        if "Ngày vào làm" in emp_df.columns:
            emp_df = emp_df.drop(columns=["Ngày vào làm"])
        
        st.caption(t("Quản lý thông tin nhân sự. Lưu ý: Cột 'Lương Gross' sẽ được tính TỰ ĐỘNG khi bạn bấm Lưu (Lương cơ bản + PC ăn trưa + PC khác).", "スタッフ情報の管理。注:「総支給額」は保存時に自動計算されます。"))
        
        col_cfg = {
            "Mã NV": st.column_config.TextColumn(t("Mã NV", "社員番号"), required=False),
            "Tên NV": st.column_config.TextColumn(t("Tên NV", "氏名"), required=True),
            "Phòng ban": st.column_config.TextColumn(t("Phòng ban", "部署")),
            "Chức vụ": st.column_config.TextColumn(t("Chức vụ", "役職")),
            "Lương cơ bản": st.column_config.TextColumn(t("Lương cơ bản", "基本給")),
            "Lương Gross": st.column_config.TextColumn(t("Lương Gross (Tự động)", "総支給額 (自動)"), disabled=True)
        }
        
        # Determine allowance columns (columns that are not standard)
        standard_cols = ["Mã NV", "Tên NV", "Phòng ban", "Chức vụ", "Lương cơ bản", "Lương Gross"]
        
        # Ensure default allowances exist if not present initially
        if "PC ăn trưa" not in emp_df.columns:
            emp_df.insert(5, "PC ăn trưa", 0)
        if "PC khác" not in emp_df.columns:
            emp_df.insert(6, "PC khác", 0)
            
        allowance_cols = [c for c in emp_df.columns if c not in standard_cols]
        for c in allowance_cols:
            col_cfg[c] = st.column_config.TextColumn(c)
            
        
        # Convert numeric columns to string with commas for display
        display_df = emp_df.copy()
        for c in ["Lương cơ bản", "Lương Gross"] + allowance_cols:
            display_df[c] = pd.to_numeric(display_df[c], errors='coerce').fillna(0)
            display_df[c] = display_df[c].apply(lambda x: f"{int(x):,}").astype(str)

        edited_emp = st.data_editor(
            display_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config=col_cfg,
            key="employees_editor_v2"
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
            # Convert strings back to numeric for calculation and saving
            for c in ["Lương cơ bản", "Lương Gross"] + allowance_cols:
                edited_emp[c] = edited_emp[c].astype(str).str.replace(',', '', regex=False)
                edited_emp[c] = pd.to_numeric(edited_emp[c], errors='coerce').fillna(0)

            edited_emp['Lương cơ bản'] = pd.to_numeric(edited_emp['Lương cơ bản'], errors='coerce').fillna(0)
            gross = edited_emp['Lương cơ bản'].copy()
            for c in allowance_cols:
                edited_emp[c] = pd.to_numeric(edited_emp[c], errors='coerce').fillna(0)
                gross += edited_emp[c]
            edited_emp['Lương Gross'] = gross
            
            save_employees_df(edited_emp)
            st.success(t("Đã lưu Thông tin chung và Danh sách nhân sự thành công!", "設定とスタッフリストを保存しました！"))
            st.rerun()
            
    with tab2:
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('DANH SÁCH NGÀY NGHỈ / LỄ', '休日・祭日一覧')}</h3>", unsafe_allow_html=True)
        
        guide_text = t(
            "✨ **HƯỚNG DẪN:**<br>- **Thêm mới:** Bấm vào dấu **+** mờ mờ ở góc dưới cùng bên trái của bảng.<br>- **Chọn ngày/Sửa:** Click đúp (2 lần) vào ô cần sửa hoặc chọn ngày trên lịch.<br>- **Xóa:** Click chọn ô vuông ngoài cùng bên trái của dòng đó, sau đó nhấn phím **Delete** trên bàn phím (hoặc bấm biểu tượng Thùng rác hiện ra ở góc phải).",
            "✨ **操作ガイド:**<br>- **新規追加:** 表の左下にある **+** ボタンを押してください。<br>- **日付選択・編集:** セルをダブルクリックして編集またはカレンダーから選択。<br>- **削除:** 左端のチェックボックスを選択し、**Delete**キーまたはゴミ箱アイコンで削除。"
        )
        st.caption(guide_text, unsafe_allow_html=True)
        
        current_df = st.session_state['ot_base_data'].get('holidays_df')
        if current_df is None or not isinstance(current_df, pd.DataFrame):
            current_df = pd.DataFrame(columns=["Ngày nghỉ", "Lý do"])
        
        # Ensure correct columns exist
        if "Ngày nghỉ" not in current_df.columns or "Lý do" not in current_df.columns:
            current_df = pd.DataFrame(columns=["Ngày nghỉ", "Lý do"])
            
        # Fix StreamlitAPIException: Ensure the column is a datetime64 dtype so Streamlit doesn't think it's a string
        current_df["Ngày nghỉ"] = pd.to_datetime(current_df["Ngày nghỉ"], errors="coerce")
            
        import datetime
        # Extract year from selected period to make it dynamic
        selected_year = datetime.datetime.now().year
        
        if st.button(t(f"Tự động điền Ngày Lễ VN {selected_year}", f"{selected_year}年ベトナム祝日を自動入力")):
            # Standard Solar Holidays
            solar_holidays = [
                {"Ngày nghỉ": f"{selected_year}-01-01", "Lý do": "Tết Dương lịch"},
                {"Ngày nghỉ": f"{selected_year}-04-30", "Lý do": "Giải phóng Miền Nam"},
                {"Ngày nghỉ": f"{selected_year}-05-01", "Lý do": "Quốc tế Lao động"},
                {"Ngày nghỉ": f"{selected_year}-09-02", "Lý do": "Lễ Quốc khánh"}
            ]
            
            # Mapping of Lunar Holidays (Tết + Giỗ Tổ) for 2025-2028
            lunar_map = {
                2025: [("2025-01-27", "Nghỉ Tết Nguyên Đán"), ("2025-01-28", "Nghỉ Tết Nguyên Đán"), ("2025-01-29", "Nghỉ Tết Nguyên Đán"), ("2025-01-30", "Nghỉ Tết Nguyên Đán"), ("2025-01-31", "Nghỉ Tết Nguyên Đán"), ("2025-04-07", "Giỗ Tổ Hùng Vương")],
                2026: [("2026-02-16", "Nghỉ Tết Nguyên Đán"), ("2026-02-17", "Nghỉ Tết Nguyên Đán"), ("2026-02-18", "Nghỉ Tết Nguyên Đán"), ("2026-02-19", "Nghỉ Tết Nguyên Đán"), ("2026-02-20", "Nghỉ Tết Nguyên Đán"), ("2026-04-26", "Giỗ Tổ Hùng Vương")],
                2027: [("2027-02-05", "Nghỉ Tết Nguyên Đán"), ("2027-02-08", "Nghỉ Tết Nguyên Đán"), ("2027-02-09", "Nghỉ Tết Nguyên Đán"), ("2027-02-10", "Nghỉ Tết Nguyên Đán"), ("2027-02-11", "Nghỉ Tết Nguyên Đán"), ("2027-04-16", "Giỗ Tổ Hùng Vương")],
                2028: [("2028-01-25", "Nghỉ Tết Nguyên Đán"), ("2028-01-26", "Nghỉ Tết Nguyên Đán"), ("2028-01-27", "Nghỉ Tết Nguyên Đán"), ("2028-01-28", "Nghỉ Tết Nguyên Đán"), ("2028-01-31", "Nghỉ Tết Nguyên Đán"), ("2028-04-04", "Giỗ Tổ Hùng Vương")]
            }
            
            holidays_data = solar_holidays
            if selected_year in lunar_map:
                for date_str, reason in lunar_map[selected_year]:
                    holidays_data.append({"Ngày nghỉ": date_str, "Lý do": reason})
            else:
                st.warning(t(f"Lưu ý: Hệ thống chỉ có sẵn dữ liệu Dương lịch cho năm {selected_year}, các ngày Lễ Âm lịch (Tết, Giỗ tổ) bạn vui lòng bổ sung thêm thủ công nhé.", f"注意：{selected_year}年の太陽暦の祝日のみ自動入力されました。旧正月などは手動で追加してください。"))
            
            vn_holidays = pd.DataFrame(holidays_data)
            vn_holidays["Ngày nghỉ"] = pd.to_datetime(vn_holidays["Ngày nghỉ"])
            combined = pd.concat([current_df, vn_holidays]).drop_duplicates(subset=["Ngày nghỉ"], keep="first").reset_index(drop=True)
            st.session_state['ot_base_data']['holidays_df'] = combined
            if "holidays_editor" in st.session_state:
                del st.session_state["holidays_editor"]
            st.rerun()
            
        holidays_df = st.data_editor(
            current_df,
            num_rows="dynamic",
            column_config={
                "Ngày nghỉ": st.column_config.DatetimeColumn(t("Ngày nghỉ (Chọn lịch)", "休日 (カレンダー選択)"), format="YYYY-MM-DD", required=True),
                "Lý do": st.column_config.TextColumn(t("Lý do / Tên ngày lễ", "理由・祭日名"), required=True)
            },
            use_container_width=True,
            key="holidays_editor"
        )
        
        if st.button(t("LƯU NGÀY LỄ", "休日を保存")):
            st.session_state['ot_base_data']['holidays_df'] = holidays_df
            save_base_data(st.session_state['ot_base_data'])
            st.success(t("Đã lưu ngày lễ thành công!", "休日を保存しました！"))

def render_project_data():
    init_session_state()
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{t('DỮ LIỆU DỰ ÁN VÀ TÍNH TĂNG CA', 'プロジェクトデータと残業計算')}</h2>", unsafe_allow_html=True)
    
    from logic.employee_data import get_employees_df
    emp_df = get_employees_df()
    base = st.session_state['ot_base_data']
    
    if emp_df.empty:
        st.warning("⚠️ " + t("Vui lòng thêm ít nhất 1 nhân sự trong phần CÀI ĐẶT CHUNG trước.", "一般設定でスタッフを1名以上追加してください。"))
        return
        
    tab_calc, tab_charts = st.tabs([t("1. TÍNH TĂNG CA (OT)", "1. 残業代計算"), t("2. BẢNG XẾP HẠNG & BIỂU ĐỒ", "2. ランキング＆チャート")])
    
    with tab_calc:
        import datetime
        try:
            fd_str = st.session_state['ot_base_data'].get('from_date', '')
            if fd_str:
                from_date = datetime.datetime.strptime(fd_str, "%Y-%m-%d").date()
            else:
                from_date = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
        except:
            from_date = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
            
        try:
            td_str = st.session_state['ot_base_data'].get('to_date', '')
            if td_str:
                to_date = datetime.datetime.strptime(td_str, "%Y-%m-%d").date()
            else:
                to_date = datetime.date.today().replace(day=20)
        except:
            to_date = datetime.date.today().replace(day=20)
            
        calculated_period = f"{from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}"
        
        from logic.project_data import get_projects_df, save_projects_df
        projects_df = get_projects_df()
        
        with st.expander(t("📂 Quản lý Danh mục Dự án (Master Data)", "📂 プロジェクトリスト管理 (マスターデータ)")):
            st.caption(t("Thêm, sửa, xóa các dự án tại đây để tự động điền thông tin khi tính OT.", "ここでプロジェクトを追加・編集・削除すると、OT計算時に自動入力されます。"))
            
            column_config = {
                "Tên dự án": st.column_config.TextColumn(t("Tên dự án", "プロジェクト名"), required=True),
                "Mã đơn hàng": st.column_config.TextColumn(t("Mã đơn hàng", "注文番号")),
                "Mã KH": st.column_config.TextColumn(t("Mã KH", "客先コード")),
                "Loại dự án": st.column_config.TextColumn(t("Loại dự án", "種別")),
                "Tên PM": st.column_config.TextColumn(t("Tên PM", "PM名"))
            }
            
            edited_projects = st.data_editor(
                projects_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config=column_config,
                key="projects_editor"
            )
            
            if st.button(t("💾 Lưu danh mục Dự án", "💾 プロジェクトリストを保存"), key="save_projects"):
                save_projects_df(edited_projects)
                st.success(t("Đã lưu danh mục dự án!", "プロジェクトリストを保存しました！"))
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
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
        
        col3, col4 = st.columns(2)
        with col3:
            order_opts = [t("--- Chọn đơn hàng ---", "--- 注文名を選択 ---")] + master_names
            sel_order_name = st.selectbox(t("TÊN ĐƠN HÀNG (DỰ ÁN)", "注文名 (プロジェクト)"), order_opts, key="sel_order_name_main")
            
            order_name = "" if sel_order_name == t("--- Chọn đơn hàng ---", "--- 注文名を選択 ---") else sel_order_name
            
            pure_name = order_name
            pure_code = None
            if isinstance(order_name, str) and order_name.startswith("[") and "] " in order_name:
                split_idx = order_name.index("] ")
                pure_code = order_name[1:split_idx]
                pure_name = order_name[split_idx+2:]
                
            last_autofill = st.session_state.get('last_order_name_autofill', None)
            if order_name != last_autofill:
                st.session_state['last_order_name_autofill'] = order_name
                if pure_name and not projects_df.empty:
                    if pure_code:
                        match = projects_df[(projects_df["Tên dự án"].astype(str).str.strip() == pure_name) & (projects_df["Mã đơn hàng"].astype(str).str.strip() == pure_code)]
                    else:
                        match = projects_df[projects_df["Tên dự án"].astype(str).str.strip() == pure_name]
                        
                    if not match.empty:
                        row = match.iloc[0]
                        st.session_state['txt_proj_type_manual'] = str(row.get("Loại dự án", "N")) if pd.notna(row.get("Loại dự án")) else "N"
                        st.session_state['txt_client_order_manual'] = str(row.get("Mã KH", "")) if pd.notna(row.get("Mã KH")) else ""
                        st.session_state['txt_order_manual'] = str(row.get("Mã đơn hàng", "")) if pd.notna(row.get("Mã đơn hàng")) else ""
                        st.session_state['txt_pm_manual'] = str(row.get("Tên PM", "")) if pd.notna(row.get("Tên PM")) else ""
                        st.rerun()
                        
            project_type = st.text_input(t("LOẠI DỰ ÁN", "プロジェクト種別"), key="txt_proj_type_manual")
            client_order_id = st.text_input(t("MÃ ĐƠN HÀNG KHÁCH", "客先注文番号"), key="txt_client_order_manual")
            order_id = st.text_input(t("MÃ ĐƠN HÀNG", "注文番号"), key="txt_order_manual")
            
        with col4:
            manager_name = st.text_input(t("TÊN NGƯỜI QUẢN LÝ - PM", "プロジェクトマネージャー"), key="txt_pm_manual")
            
            emp_names = emp_df['Tên NV'].tolist() if not emp_df.empty else []
            employee_name_proj = st.selectbox(t("TÊN NHÂN SỰ LÀM VIỆC", "担当スタッフ"), ["--- Chọn nhân viên ---"] + emp_names, key="sel_emp_proj_manual")
            
            emp_gross = 0.0
            if employee_name_proj and employee_name_proj != "--- Chọn nhân viên ---":
                emp_row = emp_df[emp_df['Tên NV'] == employee_name_proj]
                if not emp_row.empty:
                    emp_gross = float(emp_row.iloc[0].get('Lương Gross', 0.0))
            
            ot_reason = text_input_with_history(t("LÝ DO TĂNG CA", "残業理由"), "reason", "reasons", "")
            
        clean_order_name = pure_name if 'pure_name' in locals() else order_name
        
        st.divider()
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('CHI TIẾT TĂNG CA', '残業詳細')}</h3>", unsafe_allow_html=True)
        
        if employee_name_proj and employee_name_proj != "--- Chọn nhân viên ---":
            st.success(f"{t('Đang tính cho nhân sự', '対象者')}: **{employee_name_proj}** | {t('Lương Gross', '総支給額')}: **{emp_gross:,.0f} VND** | {t('Ngày chuẩn', '所定労働日数')}: **{base.get('standard_days', 22.0)}**")
        else:
            st.info(t("Vui lòng chọn nhân sự ở trên để tiếp tục.", "上記でスタッフを選択してください。"))
            
        ot_date = st.date_input(t("NGÀY THÁNG TĂNG CA", "残業日"))
        st.caption(f"{t('Thuộc kỳ lương', '給与計算期間')}: **{calculated_period}**")
        
        is_holiday = False
        holiday_reason = ""
        if not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
            try:
                holidays_list = pd.to_datetime(base['holidays_df']["Ngày nghỉ"]).dt.date.tolist()
                if ot_date in holidays_list:
                    is_holiday = True
                    reason_row = base['holidays_df'][pd.to_datetime(base['holidays_df']["Ngày nghỉ"]).dt.date == ot_date]
                    if not reason_row.empty:
                        holiday_reason = str(reason_row.iloc[0].get("Lý do", ""))
            except:
                pass
                
        is_weekend = ot_date.weekday() >= 5
        if ot_date.weekday() == 5:
            next_week = ot_date + datetime.timedelta(days=7)
            if next_week.month != ot_date.month:
                is_weekend = False

        if is_holiday:
            st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>🏖️ {t('Ngày lễ', '祭日')} ({holiday_reason}) (3.0x - 4.0x)</span></div>", unsafe_allow_html=True)
        elif is_weekend:
            st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #fff8e1; color: #f57f17; border: 1px solid #ffecb3; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>🌴 {t('Cuối tuần', '週末')} (2.0x - 2.7x)</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>💼 {t('Ngày thường', '平日')} (1.5x - 2.0x)</span></div>", unsafe_allow_html=True)
        
        tab_auto, tab_manual = st.tabs([t("🕒 Tự động phân bổ theo Giờ", "🕒 時間で自動配分"), t("✍️ Nhập tay Hệ số", "✍️ 係数手動入力")])
        
        with tab_auto:
            st.info(t("Hệ thống sẽ tự động phân bổ số giờ vào các mức hệ số dựa trên loại ngày (Ngày thường, Cuối tuần, Ngày lễ).", "システムは日種（平日・週末・祭日）に基づいて自動配分します。"))
            total_hours_auto = st.number_input(t("TỔNG SỐ GIỜ TĂNG CA", "残業時間合計"), min_value=0.0, step=0.1, value=1.0, format="%.1f")
                
            auto_buckets = {150: 0.0, 200: 0.0, 270: 0.0, 300: 0.0, 400: 0.0}
            
            if total_hours_auto > 0:
                holidays = []
                if not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
                    holidays = base['holidays_df']['Ngày nghỉ'].tolist()
                    
                auto_buckets = breakdown_ot_hours(ot_date, total_hours_auto, holidays)
                
                b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
                nt = t("Ngày thường", "平日")
                ct = t("Cuối tuần", "週末")
                nl = t("Ngày lễ", "祭日")
                with b_col1: st.metric("150%", f"{auto_buckets[150]:.1f} h", help=f"{nt}: 17h-22h")
                with b_col2: st.metric("200%", f"{auto_buckets[200]:.1f} h", help=f"{nt}: 22h-24h\n{ct}: 08h-22h")
                with b_col3: st.metric("270%", f"{auto_buckets[270]:.1f} h", help=f"{ct}: 22h-24h")
                with b_col4: st.metric("300%", f"{auto_buckets[300]:.1f} h", help=f"{nl}: 17h-22h")
                with b_col5: st.metric("400%", f"{auto_buckets[400]:.1f} h", help=f"{nl}: 08h-17h & 22h-24h")
                
            if st.button(t("➕ THÊM VÀO BẢNG CHỜ XUẤT - TỰ ĐỘNG", "➕ 自動追加"), key="btn_auto"):
                if employee_name_proj == "--- Chọn nhân viên ---":
                    st.error(t("Vui lòng chọn nhân sự làm việc!", "スタッフを選択してください！"))
                elif total_hours_auto <= 0:
                    st.error(t("Vui lòng nhập Tổng số giờ tăng ca!", "残業時間を入力してください！"))
                else:
                    add_to_history("reasons", ot_reason)
                    std_days = float(base.get('standard_days', 22.0))
                    hourly_rate = int(emp_gross / std_days / 8) if std_days > 0 else 0
                    
                    entry = {
                        "payment_period": calculated_period,
                        "project_type": project_type,
                        "order_id": order_id,
                        "client_order_id": client_order_id,
                        "order_name": clean_order_name,
                        "manager_name": manager_name,
                        "employee_name": employee_name_proj,
                        "ot_reason": ot_reason,
                        "ot_date": ot_date.strftime("%d/%m/%Y"),
                        "ot_hours": total_hours_auto,
                        "hourly_rate": hourly_rate,
                    }
                    
                    for mult, hrs in auto_buckets.items():
                        if hrs > 0:
                            res = calculate_ot_pay(emp_gross, std_days, hrs, mult)
                            k_name = f"{int(mult)}%" if float(mult).is_integer() else f"{mult}%"
                            entry[k_name] = int(res["ot_pay"])
                            
                    st.session_state['ot_records'].append(entry)
                    st.success(f"{t('Đã thêm bản ghi', 'レコード追加完了！')} ({total_hours_auto} {t('giờ', '時間')})")
                    
        with tab_manual:
            st.warning(t("Bạn tự gõ số giờ tương ứng vào từng rổ hệ số. Nếu không có phát sinh, vui lòng để trống hoặc bằng 0.", "各係数の時間を手動で入力してください。発生しない場合は0または空白で。"))
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
            with m_col1: h_150 = st.number_input(t("Số giờ 150%", "150% 時間"), min_value=0.0, step=0.1, format="%.1f")
            with m_col2: h_200 = st.number_input(t("Số giờ 200%", "200% 時間"), min_value=0.0, step=0.1, format="%.1f")
            with m_col3: h_270 = st.number_input(t("Số giờ 270%", "270% 時間"), min_value=0.0, step=0.1, format="%.1f")
            with m_col4: h_300 = st.number_input(t("Số giờ 300%", "300% 時間"), min_value=0.0, step=0.1, format="%.1f")
            with m_col5: h_400 = st.number_input(t("Số giờ 400%", "400% 時間"), min_value=0.0, step=0.1, format="%.1f")
            
            st.markdown(f"##### {t('Hệ số Khác (Tuỳ chỉnh)', 'その他係数（カスタム）')}")
            c_col1, c_col2 = st.columns(2)
            with c_col1: c_mult = st.number_input(t("Hệ số tuỳ chỉnh (%)", "カスタム係数 (%)"), min_value=0.0, step=10.0)
            with c_col2: c_hrs = st.number_input(t("Số giờ cho hệ số này", "時間数"), min_value=0.0, step=0.1, format="%.1f")
            
            if st.button(t("➕ THÊM VÀO BẢNG CHỜ XUẤT - THỦ CÔNG", "➕ 手動追加"), key="btn_manual"):
                manual_total = h_150 + h_200 + h_270 + h_300 + h_400 + c_hrs
                if employee_name_proj == "--- Chọn nhân viên ---":
                    st.error(t("Vui lòng chọn nhân sự làm việc!", "スタッフを選択してください！"))
                elif manual_total <= 0:
                    st.error(t("Vui lòng nhập ít nhất một trường thời gian lớn hơn 0!", "1つ以上の時間を入力してください！"))
                else:
                    add_to_history("reasons", ot_reason)
                    std_days = float(base.get('standard_days', 22.0))
                    hourly_rate = int(emp_gross / std_days / 8) if std_days > 0 else 0
                    
                    entry = {
                        "payment_period": calculated_period,
                        "project_type": project_type,
                        "order_id": order_id,
                        "client_order_id": client_order_id,
                        "order_name": clean_order_name,
                        "manager_name": manager_name,
                        "employee_name": employee_name_proj,
                        "ot_reason": ot_reason,
                        "ot_date": ot_date.strftime("%d/%m/%Y"),
                        "ot_hours": manual_total,
                        "hourly_rate": hourly_rate,
                    }
                    
                    bucket_inputs = {150: h_150, 200: h_200, 270: h_270, 300: h_300, 400: h_400}
                    if c_hrs > 0 and c_mult > 0:
                        bucket_inputs[c_mult] = c_hrs
                        
                    for mult, hrs in bucket_inputs.items():
                        if hrs > 0:
                            res = calculate_ot_pay(emp_gross, std_days, hrs, mult)
                            k_name = f"{int(mult)}%" if float(mult).is_integer() else f"{mult}%"
                            entry[k_name] = int(res["ot_pay"])
                            
                    st.session_state['ot_records'].append(entry)
                    st.success(t("Đã thêm bản ghi thủ công!", "手動レコード追加完了！"))

        if len(st.session_state['ot_records']) > 0:
            st.markdown("---")
            st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('BẢNG DỮ LIỆU ĐÃ NHẬP', '入力済みデータ一覧')}</h3>", unsafe_allow_html=True)
            st.caption(t("Bấm vào các ô để chỉnh sửa. Chọn dòng và ấn Delete để xóa.", "セルをクリックして編集。行を選択してDeleteで削除。"))
            
            df = pd.DataFrame(st.session_state['ot_records'])
            
            col_cfg = {
                "payment_period": t("Kỳ Tính Lương", "給与計算期間"),
                "project_type": t("Loại Dự Án", "プロジェクト種別"),
                "order_id": t("Mã Đơn Hàng", "注文番号"),
                "client_order_id": t("Mã ĐH Khách", "客先注文番号"),
                "order_name": t("Tên Đơn Hàng", "注文名"),
                "manager_name": t("Tên Quản Lý", "PM名"),
                "employee_name": t("Người Thực Hiện", "社員名"),
                "ot_reason": t("Lý Do OT", "残業理由"),
                "ot_date": t("Ngày OT", "残業日"),
                "ot_hours": t("Tổng Giờ OT", "総残業時間"),
                "hourly_rate": st.column_config.NumberColumn(t("Số Lương/H (VND)", "時給"), format="%,d"),
            }
            
            for key in df.columns:
                if key.endswith("%"):
                    col_cfg[key] = st.column_config.NumberColumn(f"{t('Tiền', '金額')} {key}", format="%,d")
                        
            edited_df = st.data_editor(
                st.session_state['ot_records'],
                num_rows="dynamic",
                use_container_width=True,
                key="ot_records_editor",
                column_config=col_cfg
            )
            st.session_state['ot_records'] = edited_df
            
            st.markdown("---")
            c_name, c_dl, c_del = st.columns([5, 3, 2])
            with c_name:
                default_name = t("Bảng tổng hợp tăng ca (OT).xlsx", "残業計算結果_OT.xlsx")
                export_name = st.text_input("📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), value=default_name, key="ot_manual_filename")
                if not export_name.endswith(".xlsx"):
                    export_name += ".xlsx"
                    
            excel_data = export_ot_to_excel(st.session_state['ot_records'], filename=export_name)
            with c_dl:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                
                def download_and_save_ot(*args):
                    save_action_log(*args)
                    from logic.history_records import add_records
                    add_records("ot", st.session_state['ot_records'])
                    
                st.download_button(
                    label=t("TẢI FILE EXCEL", "Excelダウンロード"),
                    data=excel_data,
                    file_name=export_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                    on_click=download_and_save_ot,
                    args=("OT Manual (Thủ công)", "残業代計算 (手入力)", f"Tính OT thủ công ({len(st.session_state['ot_records'])} bản ghi)", f"残業手入力 ({len(st.session_state['ot_records'])} レコード)", excel_data, export_name)
                )
            with c_del:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button(t("XÓA TOÀN BỘ BẢNG", "全データクリア"), use_container_width=True):
                    st.session_state['ot_records'] = []
                    st.success(t("Đã xóa toàn bộ dữ liệu dự án!", "全プロジェクトデータをクリアしました！"))
                    st.rerun()
        else:
            st.info(t("Chưa có bản ghi nào. Vui lòng nhập thông tin ở trên và nhấn 'THÊM VÀO BẢNG CHỜ XUẤT'.", "レコードがありません。上記に情報を入力して「追加」を押してください。"))

    with tab_charts:
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('BẢNG XẾP HẠNG THỜI GIAN OT', '残業時間ランキング')}</h3>", unsafe_allow_html=True)
        st.caption(t("Bảng xếp hạng tổng hợp dựa trên dữ liệu OT đã được lưu trong lịch sử hệ thống.", "システム履歴に保存されたOTデータに基づく総合ランキング。"))
        
        from logic.history_records import get_records
        ot_history = get_records("ot")
        if not ot_history:
            st.info(t("Chưa có dữ liệu OT nào được lưu.", "保存されたデータがありません。"))
        else:
            df_hist = pd.DataFrame(ot_history)
            df_hist['date_obj'] = pd.to_datetime(df_hist['ot_date'], format='%d/%m/%Y', errors='coerce')
            df_hist['ot_hours'] = pd.to_numeric(df_hist.get('ot_hours', 0), errors='coerce').fillna(0)
            
            import datetime
            years = sorted(df_hist['date_obj'].dt.year.dropna().unique().tolist(), reverse=True)
            years = [int(y) for y in years]
            if not years:
                years = [datetime.datetime.now().year]
                
            c_year, c_emp = st.columns(2)
            with c_year:
                sel_year = st.selectbox(t("Chọn năm", "年を選択"), ["Tất cả"] + years, key="sel_year_ot_chart")
            
            if sel_year != "Tất cả":
                df_filtered = df_hist[df_hist['date_obj'].dt.year == sel_year]
            else:
                df_filtered = df_hist
                
            if df_filtered.empty:
                st.warning("Không có dữ liệu cho năm này.")
            else:
                agg_df = df_filtered.groupby('employee_name').agg(
                    total_ot_hours=('ot_hours', 'sum'),
                    projects_count=('order_name', 'count')
                ).reset_index()
                
                agg_df = agg_df.sort_values(by='total_ot_hours', ascending=False).reset_index(drop=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=agg_df['employee_name'],
                    y=agg_df['total_ot_hours'],
                    name=t("Tổng số giờ OT", "総残業時間"),
                    marker=dict(
                        color=agg_df['total_ot_hours'],
                        colorscale=[[0, '#fff3e0'], [1, '#ef6c00']], # Light orange to deep orange to fit OT context, or Blue? Wait, let's use the global cyan/blue
                        line=dict(color='rgba(0,0,0,0)', width=0)
                    ),
                    text=agg_df['total_ot_hours'].apply(lambda x: f"{x:,.1f}"),
                    textposition='auto',
                ))
                fig.update_layout(
                    title=t("Biểu đồ Tổng Số Giờ OT", "総残業時間チャート"),
                    xaxis_title="",
                    yaxis_title=t("Số giờ (h)", "時間 (h)"),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'family': "Inter, sans-serif"},
                    margin=dict(l=0, r=0, t=40, b=0),
                    yaxis=dict(gridcolor='#e0e0e0')
                )
                
                # Let's override colorscale to match "giao diện toàn trang web" (Global theme - cyan/blue)
                fig.data[0].marker.colorscale = [[0, '#e0f7fa'], [1, '#00aced']]
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                
                agg_display = agg_df.copy()
                agg_display.index = agg_display.index + 1
                
                col_emp = t("Nhân sự", "担当者")
                col_ot = t("Tổng Giờ OT", "総残業時間")
                col_prj = t("Số Lượt Báo Cáo", "レポート回数")
                
                agg_display.rename(columns={
                    'employee_name': col_emp,
                    'total_ot_hours': col_ot,
                    'projects_count': col_prj
                }, inplace=True)
                
                format_dict = {
                    col_ot: "{:,.1f}"
                }
                
                def highlight_top3(row):
                    if row.name in [1, 2, 3]:
                        return ['background-color: #e0f7fa; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                
                styled_df = agg_display.style.apply(highlight_top3, axis=1).format(format_dict)
                
                st.dataframe(styled_df, use_container_width=True)
                
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                with st.expander(t("⚙️ Quản lý / Chỉnh sửa Dữ liệu Lịch sử Xếp hạng", "⚙️ 履歴データ管理・編集")):
                    st.markdown(t("Bạn có thể sửa trực tiếp hoặc xóa các hàng dữ liệu nháp ở bảng bên dưới, sau đó bấm **Lưu thay đổi**.", "以下の表で直接データを編集・削除し、「変更を保存」をクリックしてください。"))
                    
                    hist_display = df_hist.copy()
                    if 'date_obj' in hist_display.columns:
                        hist_display = hist_display.drop(columns=['date_obj'])
                        
                    hist_display_map = {
                        "date": t("Ngày", "日"),
                        "order_name": t("Mã đơn hàng", "注文番号"),
                        "project_name": t("Tên dự án", "案件名"),
                        "employee_name": t("Nhân viên", "担当者"),
                        "start_time": t("Bắt đầu", "開始時間"),
                        "end_time": t("Kết thúc", "終了時間"),
                        "break_time": t("Nghỉ (h)", "休憩 (h)"),
                        "ot_hours": t("Giờ OT", "残業時間 (h)"),
                        "meal_allowance": t("Phụ cấp ăn", "食事手当"),
                        "transport_allowance": t("PC đi lại", "交通手当"),
                        "ot_reason": t("Lý do OT", "残業理由")
                    }
                    
                    hist_display = hist_display.rename(columns=hist_display_map)
                    
                    edited_hist_df = st.data_editor(hist_display, use_container_width=True, num_rows="dynamic", key="edit_hist_ot")
                    
                    if st.button(t("💾 Lưu thay đổi Lịch sử", "💾 履歴を保存"), type="primary", key="btn_save_hist_ot"):
                        reverse_hist_map = {v: k for k, v in hist_display_map.items()}
                        updated_records = edited_hist_df.rename(columns=reverse_hist_map).to_dict('records')
                        from logic.history_records import save_all_records
                        save_all_records("ot", updated_records)
                        st.success(t("Đã cập nhật lịch sử thành công!", "履歴を正常に更新しました！"))
                        st.rerun()
