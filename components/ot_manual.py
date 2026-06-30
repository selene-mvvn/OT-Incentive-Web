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

def render_mini_dashboard():
    import datetime
    from logic.employee_data import get_employees_df
    emp_df = get_employees_df()
    total_emp = len(emp_df)
    
    holidays_df = st.session_state['ot_base_data'].get('holidays_df')
    if holidays_df is not None and isinstance(holidays_df, pd.DataFrame):
        total_hol = len(holidays_df)
    else:
        total_hol = 0
        
    try:
        fd_str = st.session_state['ot_base_data'].get('from_date', '')
        if fd_str:
            fd_val = datetime.datetime.strptime(fd_str, "%Y-%m-%d").date()
        else:
            fd_val = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
    except:
        fd_val = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
        
    try:
        td_str = st.session_state['ot_base_data'].get('to_date', '')
        if td_str:
            td_val = datetime.datetime.strptime(td_str, "%Y-%m-%d").date()
        else:
            td_val = datetime.date.today().replace(day=20)
    except:
        td_val = datetime.date.today().replace(day=20)
        
    period_str = f"{fd_val.strftime('%d/%m/%Y')} - {td_val.strftime('%d/%m/%Y')}"
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0');
        .mini-dashboard-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        .mini-dashboard-icon {
            font-size: 28px;
            color: #00B0F0;
            margin-bottom: 5px;
        }
        .mini-dashboard-value {
            font-size: 22px;
            font-weight: bold;
            color: #31333f;
            margin: 5px 0;
        }
        .mini-dashboard-label {
            font-size: 13px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="mini-dashboard-card">
                <div class="material-symbols-rounded mini-dashboard-icon">group</div>
                <div class="mini-dashboard-value">{total_emp}</div>
                <div class="mini-dashboard-label">{t("Nhân viên", "従業員")}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="mini-dashboard-card">
                <div class="material-symbols-rounded mini-dashboard-icon">event_busy</div>
                <div class="mini-dashboard-value">{total_hol}</div>
                <div class="mini-dashboard-label">{t("Ngày nghỉ lễ", "休日・祭日")}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="mini-dashboard-card">
                <div class="material-symbols-rounded mini-dashboard-icon">date_range</div>
                <div class="mini-dashboard-value" style="font-size: 16px; margin: 10px 0;">{period_str}</div>
                <div class="mini-dashboard-label">{t("Kỳ tính lương", "給与計算期間")}</div>
            </div>
        """, unsafe_allow_html=True)

def render_base_data():
    init_session_state()
    
    title = t("CÀI ĐẶT CHUNG", "一般設定")
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    st.info(t("Cài đặt thông tin hệ thống, nhân sự và ngày nghỉ lễ tại đây.", "システム情報、スタッフ、休日を設定します。"))
    render_mini_dashboard()
    
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
        # Reorder columns logically to fix Firebase's alphabetical sorting
        ordered_cols = ["Mã NV", "Tên NV", "Phòng ban", "Chức vụ", "Lương cơ bản"] + allowance_cols + ["Lương Gross"]
        emp_df = emp_df[ordered_cols]
        
        for c in allowance_cols:
            if c == "PC ăn trưa":
                col_cfg[c] = st.column_config.TextColumn(t("PC ăn trưa", "昼食手当"))
            elif c == "PC khác":
                col_cfg[c] = st.column_config.TextColumn(t("PC khác", "その他手当"))
            else:
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
            from components.ui_utils import make_expander_blue
            make_expander_blue()
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
                del_pc_name = st.selectbox(
                    t("Chọn cột Phụ cấp để xóa:", "削除する手当列を選択:"), 
                    allowance_cols,
                    format_func=lambda x: t("PC ăn trưa", "昼食手当") if x == "PC ăn trưa" else (t("PC khác", "その他手当") if x == "PC khác" else x)
                )
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
            st.session_state['pending_toast'] = t("Đã lưu Thông tin chung và Danh sách nhân sự thành công!", "設定とスタッフリストを保存しました！")
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
            
        import calendar
        if 'cal_year' not in st.session_state:
            st.session_state['cal_year'] = datetime.datetime.now().year
        if 'cal_month' not in st.session_state:
            st.session_state['cal_month'] = datetime.datetime.now().month
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        col_prev, col_month, col_next = st.columns([1, 4, 1], vertical_alignment="center")
        with col_prev:
            if st.button("◀", use_container_width=True, key="prev_month"):
                st.session_state['cal_month'] -= 1
                if st.session_state['cal_month'] < 1:
                    st.session_state['cal_month'] = 12
                    st.session_state['cal_year'] -= 1
                st.rerun()
        with col_month:
            month_name = calendar.month_name[st.session_state['cal_month']]
            st.markdown(f"<h3 style='text-align: center; margin: 0; color: #00B0F0;'>{month_name} {st.session_state['cal_year']}</h3>", unsafe_allow_html=True)
        with col_next:
            if st.button("▶", use_container_width=True, key="next_month"):
                st.session_state['cal_month'] += 1
                if st.session_state['cal_month'] > 12:
                    st.session_state['cal_month'] = 1
                    st.session_state['cal_year'] += 1
                st.rerun()
                
        # Draw calendar grid
        with st.container():
            import calendar
            calendar.setfirstweekday(calendar.SUNDAY)
            st.markdown("<div id='holiday-calendar-wrapper'></div>", unsafe_allow_html=True)
            st.markdown("""
                <style>
                /* Target exactly the innermost vertical block containing the calendar */
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) {
                    border: 1px solid #e0e0e0;
                    background-color: #ffffff;
                }
                /* Remove padding/gap inside the calendar container */
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) > div > div[data-testid="stHorizontalBlock"] {
                    gap: 0 !important;
                }
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) div[data-testid="column"] {
                    padding: 0 !important;
                    border-right: 1px solid #e0e0e0;
                    border-bottom: 1px solid #e0e0e0;
                }
                /* Remove right border from the last column (Saturday) */
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) div[data-testid="column"]:nth-child(7n) {
                    border-right: none;
                }
                /* Highlight weekend columns (Saturday and Sunday, i.e., col 1 and 7) */
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) div[data-testid="column"]:nth-child(7n),
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) div[data-testid="column"]:nth-child(7n+1) {
                    background-color: #ffe6e6 !important; /* Light pink background */
                }

                /* Style the buttons to look like calendar cells */
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) button {
                    width: 100% !important;
                    height: 80px !important;
                    border-radius: 0 !important;
                    border: none !important;
                    background-color: transparent !important;
                    margin: 0 !important;
                    padding: 5px !important;
                    box-shadow: none !important;
                }
                
                /* Align text to top-center like a real calendar */
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) button div[data-testid="stMarkdownContainer"] {
                    width: 100%;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-start;
                    align-items: center;
                }
                
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) button p {
                    font-size: 14px;
                    font-weight: bold;
                    color: #333;
                    margin: 0;
                }

                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) button:hover {
                    background-color: rgba(0, 176, 240, 0.1) !important;
                }

                /* Highlighted Holiday styling (Yellow banner feel) */
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) button[kind="primary"] {
                    background-color: #ffefc2 !important; 
                    border: 1px solid #ffa500 !important;
                }
                div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#holiday-calendar-wrapper))) button[kind="primary"] p {
                    color: #d35400 !important;
                }
                </style>
            """, unsafe_allow_html=True)

            days = [t("CN", "日"), t("T2", "月"), t("T3", "火"), t("T4", "水"), t("T5", "木"), t("T6", "金"), t("T7", "土")]
            cols = st.columns(7)
            for i, day in enumerate(days):
                with cols[i]:
                    st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 10px 0; color: #5f6368; background-color: #f8f9fa; border-bottom: 1px solid #e0e0e0;'>{day}</div>", unsafe_allow_html=True)

            cal = calendar.monthcalendar(st.session_state['cal_year'], st.session_state['cal_month'])
            holiday_dates = current_df["Ngày nghỉ"].dt.date.tolist() if not current_df.empty else []

            for week in cal:
                cols = st.columns(7)
                for i, day in enumerate(week):
                    with cols[i]:
                        if day != 0:
                            current_date = datetime.date(st.session_state['cal_year'], st.session_state['cal_month'], day)
                            is_holiday = current_date in holiday_dates
                            btn_type = "primary" if is_holiday else "secondary"
                            if st.button(str(day), key=f"cal_{current_date}", type=btn_type, use_container_width=True):
                                if is_holiday:
                                    current_df = current_df[current_df["Ngày nghỉ"].dt.date != current_date]
                                else:
                                    new_row = {"Ngày nghỉ": pd.Timestamp(current_date), "Lý do": t("Nghỉ lễ / Cuối tuần", "休日・祭日")}
                                    current_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                                st.session_state['ot_base_data']['holidays_df'] = current_df
                                save_base_data(st.session_state['ot_base_data'])
                                st.rerun()

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='font-size: 16px; font-weight: 600;'>{t('Danh sách chi tiết:', '詳細一覧:')}</h4>", unsafe_allow_html=True)
        holidays_df = st.data_editor(
            current_df,
            num_rows="dynamic",
            column_order=["Ngày nghỉ", "Lý do"],
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
            st.toast(t("Đã lưu ngày lễ thành công!", "休日を保存しました！"), icon=":material/check_circle:")

def render_project_data():
    col_main, col_rank = st.columns([7.5, 2.5], gap="large")
    with col_rank:
        from components.mini_leaderboard import render_mini_leaderboard
        render_mini_leaderboard("ot")
    with col_main:
        init_session_state()
        st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{t('DỮ LIỆU DỰ ÁN VÀ TÍNH TĂNG CA', 'プロジェクトデータと残業計算')}</h2>", unsafe_allow_html=True)
    
        from logic.employee_data import get_employees_df
        emp_df = get_employees_df()
        base = st.session_state['ot_base_data']
    
        if emp_df.empty:
            st.warning("⚠️ " + t("Vui lòng thêm ít nhất 1 nhân sự trong phần CÀI ĐẶT CHUNG trước.", "一般設定でスタッフを1名以上追加してください。"))
            return
        
        with st.container():
            from components.ui_utils import make_container_white
            make_container_white()
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
                from components.ui_utils import make_expander_blue
                make_expander_blue()
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
                    column_order=["Tên dự án", "Mã đơn hàng", "Mã KH", "Loại dự án", "Tên PM"],
                    key="projects_editor"
                )
            
                if st.button(t("💾 Lưu danh mục Dự án", "💾 プロジェクトリストを保存"), key="save_projects"):
                    save_projects_df(edited_projects)
                    st.session_state['pending_toast'] = t("Đã lưu danh mục dự án!", "プロジェクトリストを保存しました！")
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
            
                emp_names = sorted(emp_df['Tên NV'].tolist()) if not emp_df.empty else []
                opt_emp = t("--- Chọn nhân viên ---", "--- スタッフを選択 ---")
                employee_name_proj = st.selectbox(t("TÊN NHÂN SỰ LÀM VIỆC", "担当スタッフ"), [opt_emp] + emp_names, key="sel_emp_proj_manual")
            
                emp_gross = 0.0
                if employee_name_proj and employee_name_proj != opt_emp:
                    emp_row = emp_df[emp_df['Tên NV'] == employee_name_proj]
                    if not emp_row.empty:
                        emp_gross = float(emp_row.iloc[0].get('Lương Gross', 0.0))
            
                ot_reason = text_input_with_history(t("LÝ DO TĂNG CA", "残業理由"), "reason", "reasons", "")
            
            clean_order_name = pure_name if 'pure_name' in locals() else order_name
        
            st.divider()
            st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('CHI TIẾT TĂNG CA', '残業詳細')}</h3>", unsafe_allow_html=True)
        
            if employee_name_proj and employee_name_proj != opt_emp:
                st.info(f"{t('Đang tính cho nhân sự', '対象者')}: **{employee_name_proj}** | {t('Lương Gross', '総支給額')}: **{emp_gross:,.0f} VND** | {t('Ngày chuẩn', '所定労働日数')}: **{base.get('standard_days', 22.0)}**")
            else:
                st.info(t("Vui lòng chọn nhân sự ở trên để tiếp tục.", "上記でスタッフを選択してください。"))
            
            ot_date = st.date_input(t("NGÀY THÁNG TĂNG CA", "残業日"))
            # Auto-calculate the period based on OT date
            calculated_period = get_payroll_period(ot_date)
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
                if ot_date.weekday() == 5:
                    label = t('Ngày đi làm hành chính (Thứ 7 cuối tháng đi làm)', '平日（最終土曜日は出勤）')
                else:
                    label = t('Ngày đi làm hành chính', '平日')
                st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>💼 {label} (1.5x - 2.0x)</span></div>", unsafe_allow_html=True)
        
            tab_auto, tab_manual = st.tabs([t("🕒 Tự động phân bổ theo Giờ", "🕒 時間で自動配分"), t("✍️ Nhập tay Hệ số", "✍️ 係数手動入力")])
        
            with tab_auto:
                st.info(t("Hệ thống sẽ tự động phân bổ số giờ vào các mức hệ số dựa trên loại ngày (Ngày đi làm hành chính, Cuối tuần, Ngày lễ).", "システムは日種（平日・週末・祭日）に基づいて自動配分します。"))
                total_hours_auto = st.number_input(t("TỔNG SỐ GIỜ TĂNG CA", "残業時間合計"), min_value=0.0, step=0.1, value=1.0, format="%.1f")
                
                auto_buckets = {150: 0.0, 200: 0.0, 270: 0.0, 300: 0.0, 400: 0.0}
            
                if total_hours_auto > 0:
                    holidays = []
                    if not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
                        holidays = base['holidays_df']['Ngày nghỉ'].tolist()
                    
                    auto_buckets = breakdown_ot_hours(ot_date, total_hours_auto, holidays)
                
                    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
                    nt = t("Ngày đi làm hành chính", "平日")
                    ct = t("Cuối tuần", "週末")
                    nl = t("Ngày lễ", "祭日")
                    with b_col1: st.metric("150%", f"{auto_buckets[150]:.1f} h", help=f"{nt}: 17h-22h")
                    with b_col2: st.metric("200%", f"{auto_buckets[200]:.1f} h", help=f"{nt}: 22h-24h\n{ct}: 08h-22h")
                    with b_col3: st.metric("270%", f"{auto_buckets[270]:.1f} h", help=f"{ct}: 22h-24h")
                    with b_col4: st.metric("300%", f"{auto_buckets[300]:.1f} h", help=f"{nl}: 17h-22h")
                    with b_col5: st.metric("400%", f"{auto_buckets[400]:.1f} h", help=f"{nl}: 08h-17h & 22h-24h")
                
                if st.button(t("➕ THÊM VÀO BẢNG CHỜ XUẤT - TỰ ĐỘNG", "➕ 自動追加"), key="btn_auto"):
                    if employee_name_proj == opt_emp:
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
                        st.toast(f"{t('Đã thêm bản ghi', 'レコード追加完了！')} ({total_hours_auto} {t('giờ', '時間')})", icon=":material/check_circle:")
                    
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
                    if employee_name_proj == opt_emp:
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
                        st.toast(t("Đã thêm bản ghi thủ công!", "手動レコード追加完了！"), icon=":material/check_circle:")

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
                    "hourly_rate": st.column_config.NumberColumn(t("Số Lương/H (VND)", "時給"), format="%,.0f"),
                }
            
                for key in df.columns:
                    if key.endswith("%"):
                        col_cfg[key] = st.column_config.NumberColumn(f"{t('Tiền', '金額')} {key}", format="%,.0f")
                        
                edited_df = st.data_editor(
                    st.session_state['ot_records'],
                    num_rows="dynamic",
                    use_container_width=True,
                    key="ot_records_editor",
                    column_config=col_cfg
                )
                st.session_state['ot_records'] = edited_df
            
                st.markdown("---")
                c_name, c_dl, c_del = st.columns([4.8, 2.5, 2.7])
                with c_name:
                    default_name = t("Bảng tổng hợp tăng ca (OT).xlsx", "残業計算結果_OT.xlsx")
                    export_name = st.text_input("📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), value=default_name, key="ot_manual_filename")
                    if not export_name.endswith(".xlsx"):
                        export_name += ".xlsx"
                    
                # Extract general period for excel export
                try:
                    gp = f"{from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}"
                except Exception:
                    gp = ""

                excel_data = export_ot_to_excel(st.session_state['ot_records'], filename=export_name, general_period=gp)
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
                        st.session_state['pending_toast'] = t("Đã xóa toàn bộ dữ liệu dự án!", "全プロジェクトデータをクリアしました！")
                        st.rerun()
            else:
                st.info(t("Chưa có bản ghi nào. Vui lòng nhập thông tin ở trên và nhấn 'THÊM VÀO BẢNG CHỜ XUẤT'.", "レコードがありません。上記に情報を入力して「追加」を押してください。"))

