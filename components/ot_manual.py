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
            # Ensure holidays_df is a proper DataFrame
            if 'holidays_df' not in saved or not isinstance(saved.get('holidays_df'), pd.DataFrame):
                saved['holidays_df'] = pd.DataFrame(columns=["Ngày nghỉ", "Lý do"])
            st.session_state['ot_base_data'] = saved
        else:
            st.session_state['ot_base_data'] = {
                'employee_name': '',
                'working_month': '',
                'standard_days': 22.0,
                'holidays_df': pd.DataFrame(columns=["Ngày nghỉ", "Lý do"]),
                'basic_salary': 0.0,
                'lunch_allowance': 0.0,
                'other_allowance': 0.0,
                'gross_salary': 0.0
            }
    if 'ot_records' not in st.session_state:
        st.session_state['ot_records'] = []

def render_base_data():
    init_session_state()
    
    title = t("DỮ LIỆU NỀN", "基本データ")
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    st.info(t("Dữ liệu ở đây sẽ được lưu lại tự động để dùng cho phần Dữ Liệu Dự Án.", "ここのデータはプロジェクトデータに自動保存されます。"))
    
    tab1, tab2, tab3 = st.tabs([t("1. THÔNG TIN CHUNG", "1. 一般情報"), t("2. TÍNH LƯƠNG GROSS", "2. 給与計算"), t("3. NGÀY NGHỈ & LỄ", "3. 休日・祭日")])
    
    with tab1:
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('THÔNG TIN CHUNG', '一般情報')}</h3>", unsafe_allow_html=True)
        emp = text_input_with_history(t("TÊN NHÂN SỰ", "スタッフ名"), "emp_base", "employees", st.session_state['ot_base_data']['employee_name'])
        
        opt_other = t("Khác (Nhập tay)", "その他（手入力）")
        periods = [f"{m:02d}/{y}" for y in range(2025, 2028) for m in range(1, 13)] + [opt_other]
        
        saved_month = st.session_state['ot_base_data']['working_month']
        # Extract from/to if it was saved as a range "MM/YYYY - MM/YYYY"
        if " - " in saved_month:
            parts = saved_month.split(" - ")
            saved_from = parts[0]
            saved_to = parts[1]
        else:
            saved_from = saved_month
            saved_to = saved_month

        default_idx_from = periods.index(saved_from) if saved_from in periods else (len(periods)-1 if saved_from else 17)
        default_idx_to = periods.index(saved_to) if saved_to in periods else default_idx_from
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            month_from_choice = st.selectbox(
                t("TỪ KỲ", "開始期間"), 
                options=periods, 
                index=default_idx_from, 
                help=t("Kỳ tính lương bắt đầu", "開始給与期間")
            )
            if month_from_choice == opt_other:
                month_from = st.text_input(t("NHẬP TỪ KỲ", "開始期間入力"), value=saved_from if saved_from not in periods else "")
            else:
                month_from = month_from_choice
                
        with col_m2:
            month_to_choice = st.selectbox(
                t("ĐẾN KỲ", "終了期間"), 
                options=periods, 
                index=default_idx_to, 
                help=t("Kỳ tính lương kết thúc (Chọn giống 'Từ kỳ' nếu chỉ tính 1 kỳ)", "終了期間（1期間のみの場合は開始期間と同じにする）")
            )
            if month_to_choice == opt_other:
                month_to = st.text_input(t("NHẬP ĐẾN KỲ", "終了期間入力"), value=saved_to if saved_to not in periods else "")
            else:
                month_to = month_to_choice
                
        month = f"{month_from} - {month_to}" if month_from != month_to and month_from and month_to else month_from
        
        st.caption(f"<div style='margin-top: -10px; margin-bottom: 15px; color: #666; font-style: italic;'>* {t('Lưu ý: 1 kỳ công được tính từ ngày 21 tháng trước đến ngày 20 của tháng hiện tại.', '注意：1給与期間は前月21日から当月20日までとなります。')}</div>", unsafe_allow_html=True)
        
        days = st.number_input(t("SỐ NGÀY LÀM VIỆC TIÊU CHUẨN TRONG THÁNG", "月の標準勤務日数"), min_value=1.0, value=st.session_state['ot_base_data']['standard_days'], step=0.5)
        
    with tab2:
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('THÀNH PHẦN LƯƠNG (VND)', '給与構成')}</h3>", unsafe_allow_html=True)
        basic = st.number_input(t("LƯƠNG CƠ BẢN", "基本給"), min_value=0, value=int(st.session_state['ot_base_data']['basic_salary']), step=100000)
        lunch = st.number_input(t("PHỤ CẤP ĂN TRƯA", "昼食手当"), min_value=0, value=int(st.session_state['ot_base_data']['lunch_allowance']), step=10000)
        other = st.number_input(t("CÁC PHỤ CẤP KHÁC", "その他手当"), min_value=0, value=int(st.session_state['ot_base_data']['other_allowance']), step=10000)
        
        gross = basic + lunch + other
        st.metric(t("TỔNG LƯƠNG GROSS", "総支給額"), f"{gross:,.0f} VND")
        
    with tab3:
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
        if month_from and "/" in month_from:
            try:
                selected_year = int(month_from.split("/")[1])
            except:
                pass
                
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
        
    if st.button(t("LƯU DỮ LIỆU NỀN", "基本データを保存")):
        st.session_state['ot_base_data'] = {
            'employee_name': emp,
            'working_month': month,
            'standard_days': days,
            'holidays_df': holidays_df,
            'basic_salary': basic,
            'lunch_allowance': lunch,
            'other_allowance': other,
            'gross_salary': gross
        }
        add_to_history("employees", emp)
        if month:
            add_to_history("months", month)
        save_base_data(st.session_state['ot_base_data'])
        st.success(t("Đã lưu dữ liệu nền thành công! Dữ liệu sẽ được giữ lại khi bạn quay lại trang web.", "保存完了！データはブラウザを閉じても保持されます。"))

def render_project_data():
    init_session_state()
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{t('DỮ LIỆU DỰ ÁN VÀ TÍNH TĂNG CA', 'プロジェクトデータと残業計算')}</h2>", unsafe_allow_html=True)
    
    base = st.session_state['ot_base_data']
    if base['gross_salary'] <= 0:
        st.warning("⚠️ " + t("Bạn chưa nhập hoặc lưu Dữ Liệu Nền (hoặc Lương Gross đang bằng 0). Vui lòng quay lại mục DỮ LIỆU NỀN ở thanh menu bên trái để thiết lập trước.", "基本データが未入力です。左メニューから設定してください。"))
        return
        
    st.success(f"{t('Đang tính cho nhân sự', '対象者')}: **{base['employee_name']}** | {t('Lương Gross', '総支給額')}: **{base['gross_salary']:,.0f} VND** | {t('Ngày chuẩn', '所定労働日数')}: **{base['standard_days']}**")
    
    from logic.project_data import get_projects_df, save_projects_df
    projects_df = get_projects_df()
    
    with st.expander(t("📂 Quản lý Danh mục Dự án (Master Data)", "📂 プロジェクトリスト管理 (マスターデータ)")):
        st.caption(t("Thêm, sửa, xóa các dự án tại đây để tự động điền thông tin khi tính OT/Incentive.", "ここでプロジェクトを追加・編集・削除すると、OT/Incentive計算時に自動入力されます。"))
        
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
    
    # Combine history names with master names
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
        # Tên đơn hàng from master data only
        order_opts = [t("--- Chọn đơn hàng ---", "--- 注文名を選択 ---")] + master_names
        sel_order_name = st.selectbox(t("TÊN ĐƠN HÀNG (DỰ ÁN)", "注文名 (プロジェクト)"), order_opts, key="sel_order_name_main")
        
        if sel_order_name == t("--- Chọn đơn hàng ---", "--- 注文名を選択 ---"):
            order_name = ""
        else:
            order_name = sel_order_name
        # Calculate defaults based on selected order_name
        default_proj_type = "N"
        default_client_order = ""
        default_order = ""
        default_pm = ""
        
        pure_name = order_name
        pure_code = None
        if isinstance(order_name, str) and order_name.startswith("[") and "] " in order_name:
            split_idx = order_name.index("] ")
            pure_code = order_name[1:split_idx]
            pure_name = order_name[split_idx+2:]
            
        # Explicit auto-fill logic
        last_autofill = st.session_state.get('last_order_name_autofill', None)
        if order_name != last_autofill:
            st.session_state['last_order_name_autofill'] = order_name
            
            # Find in DB
            if pure_name and not projects_df.empty:
                if pure_code:
                    match = projects_df[
                        (projects_df["Tên dự án"].astype(str).str.strip() == pure_name) & 
                        (projects_df["Mã đơn hàng"].astype(str).str.strip() == pure_code)
                    ]
                else:
                    match = projects_df[projects_df["Tên dự án"].astype(str).str.strip() == pure_name]
                    
                if not match.empty:
                    row = match.iloc[0]
                    new_proj_type = str(row.get("Loại dự án", "N")) if pd.notna(row.get("Loại dự án")) else "N"
                    new_client_order = str(row.get("Mã KH", "")) if pd.notna(row.get("Mã KH")) else ""
                    new_order = str(row.get("Mã đơn hàng", "")) if pd.notna(row.get("Mã đơn hàng")) else ""
                    new_pm = str(row.get("Tên PM", "")) if pd.notna(row.get("Tên PM")) else ""
                    
                    st.session_state['txt_proj_type_manual'] = new_proj_type
                    st.session_state['txt_client_order_manual'] = new_client_order
                    st.session_state['txt_order_manual'] = new_order
                    st.session_state['txt_pm_manual'] = new_pm
                    
                    st.rerun()
                    
        project_type = st.text_input(t("LOẠI DỰ ÁN", "プロジェクト種別"), key="txt_proj_type_manual")
        client_order_id = st.text_input(t("MÃ ĐƠN HÀNG KHÁCH", "客先注文番号"), key="txt_client_order_manual")
        order_id = st.text_input(t("MÃ ĐƠN HÀNG", "注文番号"), key="txt_order_manual")
        
    with col4:
        manager_name = st.text_input(t("TÊN NGƯỜI QUẢN LÝ - PM", "プロジェクトマネージャー"), key="txt_pm_manual")
        
        emp_history = get_history("employees")
        # Default to the currently selected employee from base data, but offer all from history
        emp_opts = list(dict.fromkeys([base['employee_name']] + emp_history))
        employee_name_proj = st.selectbox(t("TÊN NHÂN SỰ LÀM VIỆC", "担当スタッフ"), emp_opts, key="sel_emp_proj_manual")
        
        ot_reason = text_input_with_history(t("LÝ DO TĂNG CA", "残業理由"), "reason", "reasons", "")
        
    clean_order_name = pure_name if 'pure_name' in locals() else order_name
        
    st.divider()
    
    st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('CHI TIẾT TĂNG CA', '残業詳細')}</h3>", unsafe_allow_html=True)
    
    ot_date = st.date_input(t("NGÀY THÁNG TĂNG CA", "残業日"))
    calculated_period = get_payroll_period(ot_date)
    st.caption(f"{t('Tự động tính thuộc kỳ lương', '自動計算期間')}: **{calculated_period}**")
    
    # Auto Day-type Label logic
    is_holiday = False
    holiday_reason = ""
    if not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
        try:
            # Convert to date objects for comparison
            holiday_dates = pd.to_datetime(base['holidays_df']['Ngày nghỉ']).dt.date
            holiday_match = base['holidays_df'][holiday_dates == ot_date]
            if not holiday_match.empty:
                is_holiday = True
                holiday_reason = holiday_match.iloc[0]['Lý do']
        except Exception:
            pass
            
    is_weekend = ot_date.weekday() >= 5
    is_last_saturday = False
    if ot_date.weekday() == 5:
        import datetime
        next_week = ot_date + datetime.timedelta(days=7)
        if next_week.month != ot_date.month:
            is_weekend = False
            is_last_saturday = True

    if is_holiday:
        st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>🌟 {t('Ngày lễ', '祭日')} (3.0x - 4.0x)</span> <span style='color: #666; font-size: 14px; font-style: italic;'>- {holiday_reason}</span></div>", unsafe_allow_html=True)
    elif is_weekend:
        st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #fff3e0; color: #ef6c00; border: 1px solid #ffe0b2; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>⛱️ {t('Cuối tuần', '週末')} (2.0x - 2.7x)</span></div>", unsafe_allow_html=True)
    elif is_last_saturday:
        st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>💼 {t('Ngày thường (Thứ 7 đi làm)', '平日（出勤土曜日）')} (1.5x - 2.0x)</span></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='margin-bottom: 15px;'><span style='background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>💼 {t('Ngày thường', '平日')} (1.5x - 2.0x)</span></div>", unsafe_allow_html=True)
    
    tab_auto, tab_manual = st.tabs([t("🕒 Tự động phân bổ theo Giờ", "🕒 時間で自動配分"), t("✍️ Nhập tay Hệ số", "✍️ 係数手動入力")])
    
    with tab_auto:
        st.info(t("Hệ thống sẽ tự động phân bổ số giờ vào các mức hệ số dựa trên loại ngày (Ngày thường, Cuối tuần, Ngày lễ).", "システムは日種（平日・週末・祭日）に基づいて自動配分します。"))
        total_hours_auto = st.number_input(t("TỔNG SỐ GIỞ TĂNG CA", "残業時間合計"), min_value=0.0, step=0.5, value=1.0)
            
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
            with b_col1: st.metric("150%", f"{auto_buckets[150]} h", help=f"{nt}: 17h-22h")
            with b_col2: st.metric("200%", f"{auto_buckets[200]} h", help=f"{nt}: 22h-24h\n{ct}: 08h-22h")
            with b_col3: st.metric("270%", f"{auto_buckets[270]} h", help=f"{ct}: 22h-24h")
            with b_col4: st.metric("300%", f"{auto_buckets[300]} h", help=f"{nl}: 17h-22h")
            with b_col5: st.metric("400%", f"{auto_buckets[400]} h", help=f"{nl}: 08h-17h & 22h-24h")
            
        if st.button(t("➕ THÊM VÀO BẢNG CHỞ XUẤT - TỰ ĐỘNG", "➕ 自動追加"), key="btn_auto"):
            if total_hours_auto <= 0:
                st.error(t("Vui lòng nhập Tổng số giờ tăng ca!", "残業時間を入力してください！"))
            else:
                add_to_history("reasons", ot_reason)
                
                hourly_rate = int(base['gross_salary'] / base['standard_days'] / 8)
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
                
                # Assign to respective bucket columns
                for mult, hrs in auto_buckets.items():
                    if hrs > 0:
                        res = calculate_ot_pay(base['gross_salary'], base['standard_days'], hrs, mult)
                        k_name = f"{int(mult)}%" if float(mult).is_integer() else f"{mult}%"
                        entry[k_name] = int(res["ot_pay"])
                        
                st.session_state['ot_records'].append(entry)
                st.success(f"{t('Đã thêm bản ghi', 'レコード追加完了！')} ({total_hours_auto} {t('giờ', '時間')})")
                
    with tab_manual:
        st.warning(t("Bạn tự gõ số giờ tương ứng vào từng rổ hệ số. Nếu không có phát sinh, vui lòng để trống hoặc bằng 0.", "各係数の時間を手動で入力してください。発生しない場合は0または空白で。"))
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        with m_col1: h_150 = st.number_input(t("Số giờ 150%", "150% 時間"), min_value=0.0, step=0.5)
        with m_col2: h_200 = st.number_input(t("Số giờ 200%", "200% 時間"), min_value=0.0, step=0.5)
        with m_col3: h_270 = st.number_input(t("Số giờ 270%", "270% 時間"), min_value=0.0, step=0.5)
        with m_col4: h_300 = st.number_input(t("Số giờ 300%", "300% 時間"), min_value=0.0, step=0.5)
        with m_col5: h_400 = st.number_input(t("Số giờ 400%", "400% 時間"), min_value=0.0, step=0.5)
        
        st.markdown(f"##### {t('Hệ số Khác (Tuỳ chỉnh)', 'その他係数（カスタム）')}")
        c_col1, c_col2 = st.columns(2)
        with c_col1: c_mult = st.number_input(t("Hệ số tuỳ chỉnh (%)", "カスタム係数 (%)"), min_value=0.0, step=10.0)
        with c_col2: c_hrs = st.number_input(t("Số giờ cho hệ số này", "時間数"), min_value=0.0, step=0.5)
        
        if st.button(t("➕ THÊM VÀO BẢNG CHỜ XUẤT - THỦ CÔNG", "➕ 手動追加"), key="btn_manual"):
            manual_total = h_150 + h_200 + h_270 + h_300 + h_400 + c_hrs
            if manual_total <= 0:
                st.error(t("Vui lòng nhập ít nhất một trường thời gian lớn hơn 0!", "1つ以上の時間を入力してください！"))
            else:
                add_to_history("reasons", ot_reason)
                
                hourly_rate = int(base['gross_salary'] / base['standard_days'] / 8)
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
                        res = calculate_ot_pay(base['gross_salary'], base['standard_days'], hrs, mult)
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
            "hourly_rate": st.column_config.NumberColumn(t("Số Lương/H (VND)", "時給"), format="%d"),
        }
        
        # Add dynamic money formatting for bucket columns
        for key in df.columns:
            if key.endswith("%"):
                col_cfg[key] = st.column_config.NumberColumn(f"{t('Tiền', '金額')} {key}", format="%d")
                    
        edited_df = st.data_editor(
            st.session_state['ot_records'],
            num_rows="dynamic",
            use_container_width=True,
            key="ot_records_editor",
            column_config=col_cfg
        )
        st.session_state['ot_records'] = edited_df
        
        excel_data = export_ot_to_excel(st.session_state['ot_records'])
        
        st.markdown("---")
        c_name, c_dl, c_del = st.columns([5, 3, 2])
        with c_name:
            default_name = t("Bảng tổng hợp tăng ca (OT).xlsx", "残業計算結果_OT.xlsx")
            export_name = st.text_input("📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), value=default_name, key="ot_manual_filename")
            if not export_name.endswith(".xlsx"):
                export_name += ".xlsx"
        with c_dl:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label=t("TẢI FILE EXCEL", "Excelダウンロード"),
                data=excel_data,
                file_name=export_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
                on_click=save_action_log,
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
