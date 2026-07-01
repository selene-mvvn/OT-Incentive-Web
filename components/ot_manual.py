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

    # --- MINI DASHBOARD ---
    import datetime
    from logic.employee_data import get_employees_df
    
    emp_df = get_employees_df()
    if 'Chức vụ' in emp_df.columns:
        active_emp_df = emp_df[~emp_df['Chức vụ'].astype(str).str.contains("Nhân viên cũ", case=False, na=False)]
        emp_count = len(active_emp_df)
    else:
        emp_count = len(emp_df)
    
    holidays_df = st.session_state['ot_base_data'].get('holidays_df')
    holiday_count = len(holidays_df) if hasattr(holidays_df, '__len__') else 0
    
    try:
        fd_str = st.session_state['ot_base_data'].get('from_date', '')
        fd_val = datetime.datetime.strptime(fd_str, "%Y-%m-%d") if fd_str else datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
        fd_disp = fd_val.strftime("%m/%Y")
    except:
        fd_disp = "05/2026"
        
    try:
        td_str = st.session_state['ot_base_data'].get('to_date', '')
        td_val = datetime.datetime.strptime(td_str, "%Y-%m-%d") if td_str else datetime.date.today().replace(day=20)
        td_disp = td_val.strftime("%m/%Y")
    except:
        td_disp = "06/2026"

    def make_card(icon, title, value):
        return f"""
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded" rel="stylesheet" />
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px; text-align: center;">
            <div style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center; justify-content: center; letter-spacing: 0.5px;">
                <span class='material-symbols-rounded' style='font-family: "Material Symbols Rounded", sans-serif !important; color: #00B0F0; margin-right: 8px; font-size: 20px; text-transform: none;'>{icon}</span> {title}
            </div>
            <div style="color: #0f172a; font-size: 24px; font-weight: 700;">{value}</div>
        </div>
        """

    c_dash1, c_dash2, c_dash3 = st.columns(3)
    with c_dash1:
        st.markdown(make_card("group", t("Tổng nhân sự", "総スタッフ数"), f"{emp_count} <span style='font-size: 15px; color: #64748b; font-weight: normal;'>{t('người', '人')}</span>"), unsafe_allow_html=True)
    with c_dash2:
        st.markdown(make_card("event_busy", t("Ngày nghỉ lễ", "休日・祭日"), f"{holiday_count} <span style='font-size: 15px; color: #64748b; font-weight: normal;'>{t('ngày', '日')}</span>"), unsafe_allow_html=True)
    with c_dash3:
        st.markdown(make_card("calendar_month", t("Kỳ tính lương", "給与計算期間"), f"<span style='font-size: 20px;'>{fd_disp} - {td_disp}</span>"), unsafe_allow_html=True)
    # ----------------------
    
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
        c1, c2 = st.columns([1.2, 1], gap="large")
        with c1:
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
                import time
                time.sleep(0.5)
                st.rerun()

        with c2:
            import json
            import streamlit.components.v1 as components
            holidays_list = []
            if current_df is not None and not current_df.empty:
                for _, row in current_df.iterrows():
                    dt = row.get("Ngày nghỉ")
                    reason = row.get("Lý do", "")
                    if pd.notnull(dt):
                        date_str = str(dt)[:10]
                        holidays_list.append({"date": date_str, "reason": reason})
            
            holidays_json = json.dumps(holidays_list)
            
            html_code = f"""
            <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; color: #334155; }}
            .calendar-container {{ border: 2px solid #00B0F0; border-radius: 8px; padding: 15px; background: white; margin-top: 20px; box-shadow: 0 4px 6px rgba(0, 176, 240, 0.1); }}
            .cal-header {{ display: flex; justify-content: space-between; align-items: center; padding: 5px 0 15px 0; }}
            .cal-header button {{ background: none; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px 12px; cursor: pointer; color: #475569; font-weight: bold; background: white; }}
            .cal-header button:hover {{ background: #f1f5f9; }}
            .cal-header h3 {{ margin: 0; font-size: 18px; font-weight: 600; color: #0f172a; }}
            .cal-grid {{ display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 1px; background: #e2e8f0; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            .cal-grid > div {{ background: #fff; min-height: 85px; padding: 4px; box-sizing: border-box; min-width: 0; }}
            .day-name {{ min-height: 30px !important; text-align: center; font-weight: bold; background: #f8fafc !important; font-size: 13px; padding-top: 8px !important; color: #64748b; }}
            .day-number {{ font-weight: 500; font-size: 13px; margin-bottom: 4px; text-align: right; color: #475569; }}
            .holiday-event {{ background: #10b981; color: white; font-size: 11px; padding: 3px 5px; border-radius: 4px; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: default; }}
            .other-month {{ background: #f8fafc !important; color: #cbd5e1 !important; }}
            .other-month .day-number {{ color: #cbd5e1 !important; }}
            .today {{ background: #eff6ff !important; }}
            .today .day-number {{ color: #2563eb; font-weight: bold; }}
            </style>

            <div class="calendar-container">
                <div class="cal-header">
                    <button onclick="changeMonth(-1)">&lt;</button>
                    <h3 id="monthYear"></h3>
                    <button onclick="changeMonth(1)">&gt;</button>
                </div>
                <div class="cal-grid" id="calGrid"></div>
            </div>

            <script>
            const holidays = {holidays_json};
            let currentDate = new Date();

            function renderCalendar() {{
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();
                
                document.getElementById("monthYear").innerText = "Tháng " + (month + 1) + ", " + year;
                
                const firstDay = new Date(year, month, 1).getDay();
                const startDay = firstDay === 0 ? 6 : firstDay - 1; 
                
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                const daysInPrevMonth = new Date(year, month, 0).getDate();
                
                let html = `
                    <div class="day-name">T2</div>
                    <div class="day-name">T3</div>
                    <div class="day-name">T4</div>
                    <div class="day-name">T5</div>
                    <div class="day-name">T6</div>
                    <div class="day-name">T7</div>
                    <div class="day-name">CN</div>
                `;
                
                for (let i = 0; i < startDay; i++) {{
                    const d = daysInPrevMonth - startDay + i + 1;
                    html += `<div class="other-month"><div class="day-number">${{d}}</div></div>`;
                }}
                
                const today = new Date();
                for (let i = 1; i <= daysInMonth; i++) {{
                    const isToday = today.getDate() === i && today.getMonth() === month && today.getFullYear() === year;
                    const cls = isToday ? "today" : "";
                    
                    const m = String(month + 1).padStart(2, '0');
                    const d = String(i).padStart(2, '0');
                    const dateStr = `${{year}}-${{m}}-${{d}}`;
                    
                    let eventsHtml = "";
                    const dayHolidays = holidays.filter(h => h.date === dateStr);
                    dayHolidays.forEach(h => {{
                        eventsHtml += `<div class="holiday-event" title="${{h.reason}}">${{h.reason}}</div>`;
                    }});
                    
                    html += `<div class="${{cls}}"><div class="day-number">${{i}}</div>${{eventsHtml}}</div>`;
                }}
                
                const totalCells = startDay + daysInMonth;
                const nextDays = Math.ceil(totalCells / 7) * 7 - totalCells;
                for (let i = 1; i <= nextDays; i++) {{
                    html += `<div class="other-month"><div class="day-number">${{i}}</div></div>`;
                }}
                
                document.getElementById("calGrid").innerHTML = html;
            }}

            function changeMonth(delta) {{
                currentDate.setMonth(currentDate.getMonth() + delta);
                renderCalendar();
            }}

            renderCalendar();
            </script>
            """
            components.html(html_code, height=650)
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

