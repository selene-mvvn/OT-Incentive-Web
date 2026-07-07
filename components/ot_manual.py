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
    with st.container():
        from components.ui_utils import make_container_white
        make_container_white()

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

        def make_card(icon_name, title, main_val, sub_val="", is_number=False, badge_html=""):
            svgs = {
                'group': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" fill="#ffffff"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
                'event_busy': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" fill="#ffffff"><path d="M9.31 17l2.44-2.44L14.19 17l1.06-1.06-2.44-2.44 2.44-2.44-1.06-1.06-2.44 2.44-2.44-2.44-1.06 1.06 2.44 2.44-2.44 2.44L9.31 17zM19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>',
                'calendar_month': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" fill="#ffffff"><path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM9 14H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2zm-8 4H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2z"/></svg>'
            }
            icon_svg = svgs.get(icon_name, '')
            
            if is_number:
                val_html = f"<span class='count-up-target' data-target='{main_val}'>0</span> {sub_val}"
            else:
                val_html = f"{main_val} {sub_val}"
                
            return f"""
            <div style="background-color: #00B0F0; border: 4px solid #e0f2fe; border-radius: 50%; aspect-ratio: 1/1; max-width: 180px; margin: 0 auto; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 8px 15px rgba(0, 176, 240, 0.2); text-align: center; padding: 10px; position: relative;">
                <div style="color: rgba(255, 255, 255, 0.95); font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px;">
                    <div style="margin-bottom: 10px; display: flex; justify-content: center;">{icon_svg}</div>
                    {title}
                </div>
                <div style="color: #ffffff; font-size: 22px; font-weight: 700; line-height: 1.2;">{val_html}</div>
                {badge_html}
            </div>
            """

        from logic.holiday_utils import get_countdown_info
        countdown_data = get_countdown_info()
        badge_html = ""
        if countdown_data:
            if countdown_data["type"] == "upcoming":
                days = countdown_data["days_left"]
                msg = t(f"⏳ Còn {days} ngày", f"⏳ あと{days}日")
                bg = "#fff3cd"
                color = "#856404"
            elif countdown_data["type"] == "today_single":
                msg = t("🎉 Đang nghỉ", "🎉 休日")
                bg = "#d4edda"
                color = "#155724"
            elif countdown_data["type"] == "during_block":
                days = countdown_data["days_left"]
                msg = t(f"🏖️ {days} ngày nữa làm", f"🏖️ 出社まで{days}日")
                bg = "#e8f4f8"
                color = "#0075a0"
                
            badge_html = f"""
            <div style="
                position: absolute;
                bottom: -12px;
                left: 50%;
                transform: translateX(-50%);
                background: {bg};
                color: {color};
                font-size: 12px;
                font-weight: 800;
                text-align: center;
                padding: 4px 12px;
                border-radius: 20px;
                white-space: nowrap;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: 2px solid white;
            ">
                {msg}
            </div>
            """

        c_dash1, c_dash2, c_dash3 = st.columns(3)
        with c_dash1:
            st.markdown(make_card("group", t("Tổng nhân sự", "総スタッフ数"), emp_count, f"<span style='font-size: 15px; color: rgba(255,255,255,0.8); font-weight: normal;'>{t('người', '人')}</span>", True), unsafe_allow_html=True)
        with c_dash2:
            st.markdown(make_card("event_busy", t("Ngày nghỉ lễ", "休日・祭日"), holiday_count, f"<span style='font-size: 15px; color: rgba(255,255,255,0.8); font-weight: normal;'>{t('ngày', '日')}</span>", True, badge_html), unsafe_allow_html=True)
        with c_dash3:
            st.markdown(make_card("calendar_month", t("Kỳ tính lương", "給与計算期間"), f"<span style='font-size: 16px; white-space: nowrap;'>{fd_disp} - {td_disp}</span>"), unsafe_allow_html=True)
        
        # Inject Javascript to animate the counting
        js_count_up = """
        <!DOCTYPE html>
        <html>
        <head></head>
        <body>
        <script>
            setTimeout(() => {
                try {
                    const parentDoc = window.parent.document;
                    const targets = parentDoc.querySelectorAll('.count-up-target:not(.animated)');
                    
                    targets.forEach(el => {
                        el.classList.add('animated');
                        const target = parseInt(el.getAttribute('data-target')) || 0;
                        const duration = 1500; // ms
                        const frameRate = 30; // ms per frame
                        const totalFrames = Math.round(duration / frameRate);
                        let frame = 0;
                        
                        const counter = setInterval(() => {
                            frame++;
                            const progress = frame / totalFrames;
                            // easeOutExpo
                            const easeOut = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                            const current = Math.round(target * easeOut);
                            
                            el.innerText = current;
                            
                            if (frame >= totalFrames) {
                                clearInterval(counter);
                                el.innerText = target;
                            }
                        }, frameRate);
                    });
                } catch (e) {}
            }, 100);
        </script>
        </body>
        </html>
        """
        import streamlit.components.v1 as components
        components.html(js_count_up, height=0, width=0)
        
        st.markdown("<div style='margin-bottom: -25px;'></div>", unsafe_allow_html=True)
        # ----------------------
    
    tab1, tab2 = st.tabs([t("1. THÔNG TIN CHUNG", "1. 一般情報"), t("2. NGÀY NGHỈ & LỄ", "2. 休日・祭日")])

    with tab1:
        from logic.employee_data import get_employees_df, save_employees_df
        from logic.history_records import get_records
        import plotly.graph_objects as go
        import datetime
        import pandas as pd
        
        emp_df = get_employees_df()
        if "Ngày vào làm" in emp_df.columns:
            emp_df = emp_df.drop(columns=["Ngày vào làm"])
        if "Ngày bắt đầu tính" not in emp_df.columns:
            emp_df["Ngày bắt đầu tính"] = None
            
        col_left, col_right = st.columns([7.5, 2.5], gap="large")
        
        with col_left:
            st.markdown(f"""
                <h3 style='font-size: 20px; font-weight: 600; margin-bottom: 0px;'>{t('KỲ TÍNH LƯƠNG', '給与計算期間')}</h3>
                <div style='color: #8898aa; font-size: 13px; font-style: italic; margin-top: 10px; margin-bottom: 15px;'>
                    {t('* Lưu ý: Khoảng thời gian này sẽ được sử dụng làm thông tin phụ chú trên file báo cáo Excel.', '* 注記: この期間は、出力されるExcelレポートの補足情報として使用されます。')}
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                try:
                    fd_str = st.session_state['ot_base_data'].get('from_date', '')
                    if fd_str:
                        fd_val = datetime.datetime.strptime(fd_str, "%Y-%m-%d").date()
                    else:
                        fd_val = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
                except:
                    fd_val = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
                from_date = st.date_input(t("TỪ NGÀY", "開始日"), value=fd_val)
            
            with c2:
                try:
                    td_str = st.session_state['ot_base_data'].get('to_date', '')
                    if td_str:
                        td_val = datetime.datetime.strptime(td_str, "%Y-%m-%d").date()
                    else:
                        td_val = datetime.date.today().replace(day=20)
                except:
                    td_val = datetime.date.today().replace(day=20)
                to_date = st.date_input(t("ĐẾN NGÀY", "終了日"), value=td_val)
            
            with c3:
                std_days_mo = st.number_input(t("SỐ NGÀY CHUẨN / THÁNG", "月の標準労働日数"), min_value=1.0, value=float(st.session_state['ot_base_data'].get('standard_days', 22.0)), step=0.5)

            with c4:
                std_hrs = st.number_input(t("SỐ GIỜ CHUẨN / NGÀY", "1日の標準労働時間"), min_value=1.0, value=float(st.session_state['ot_base_data'].get('standard_hours_per_day', 8.0)), step=0.5)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('THÔNG TIN NHÂN SỰ & CƠ CẤU LƯƠNG', 'スタッフ情報と給与構成')}</h3><div style='height: 15px;'></div>", unsafe_allow_html=True)
            st.caption(t("Quản lý thông tin nhân sự. Lưu ý: Cột 'Lương Gross' sẽ được tính TỰ ĐỘNG khi bạn bấm Lưu.", "スタッフ情報の管理。注:「総支給額」は保存時に自動計算されます。"))

            col_cfg = {
                "Mã NV": st.column_config.TextColumn(t("Mã NV", "社員番号"), required=False),
                "Tên NV": st.column_config.TextColumn(t("Tên NV", "氏名"), required=True),
                "Phòng ban": st.column_config.TextColumn(t("Phòng ban", "部署")),
                "Chức vụ": st.column_config.TextColumn(t("Chức vụ", "役職")),
                "Lương cơ bản": st.column_config.TextColumn(t("Lương cơ bản", "基本給")),
                "Lương Gross": st.column_config.TextColumn(t("Lương Gross (Tự động)", "総支給額 (自動)"), disabled=True),
                "Ngày bắt đầu tính": None
            }

            standard_cols = ["Mã NV", "Tên NV", "Phòng ban", "Chức vụ", "Lương cơ bản", "Lương Gross", "Ngày bắt đầu tính"]
            
            if "PC ăn trưa" not in emp_df.columns: emp_df.insert(5, "PC ăn trưa", 0)
            if "PC khác" not in emp_df.columns: emp_df.insert(6, "PC khác", 0)

            allowance_cols = [c for c in emp_df.columns if c not in standard_cols]
            ordered_cols = ["Mã NV", "Tên NV", "Phòng ban", "Chức vụ", "Lương cơ bản"] + allowance_cols + ["Lương Gross", "Ngày bắt đầu tính"]
            emp_df = emp_df[ordered_cols]
            
            for c in allowance_cols:
                if c == "PC ăn trưa": col_cfg[c] = st.column_config.TextColumn(t("PC ăn trưa", "昼食手当"))
                elif c == "PC khác": col_cfg[c] = st.column_config.TextColumn(t("PC khác", "その他手当"))
                else: col_cfg[c] = st.column_config.TextColumn(c)

            display_df = emp_df.copy()
            for c in ["Lương cơ bản", "Lương Gross"] + allowance_cols:
                display_df[c] = pd.to_numeric(display_df[c], errors='coerce').fillna(0)
                display_df[c] = display_df[c].apply(lambda x: f"{int(x):,}").astype(str)

            edited_emp = st.data_editor(
                display_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config=col_cfg,
                column_order=["Mã NV", "Tên NV", "Phòng ban", "Chức vụ", "Lương cơ bản"] + allowance_cols + ["Lương Gross"],
                key="employees_editor_v2"
            )

            ex_col1, ex_col2 = st.columns(2)
            with ex_col1:
                with st.expander(t("➕ Thêm / Xóa Cột Phụ Cấp", "➕ 手当項目の追加・削除")):
                    from components.ui_utils import make_expander_blue
                    make_expander_blue()
                    add_c1, add_c2 = st.columns([2, 1])
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

                    if len(allowance_cols) > 0:
                        del_c1, del_c2 = st.columns([2, 1])
                        with del_c1:
                            pc_mapping = { (t("PC ăn trưa", "昼食手当") if c == "PC ăn trưa" else (t("PC khác", "その他手当") if c == "PC khác" else c)): c for c in allowance_cols }
                            del_pc_translated = st.selectbox(t("Chọn Phụ cấp cần xóa:", "削除する手当を選択:"), options=list(pc_mapping.keys()), key="del_pc_input_translated")
                            del_pc_name = pc_mapping.get(del_pc_translated, "")
                        with del_c2:
                            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                            if st.button(t("Xóa Cột", "列を削除"), use_container_width=True):
                                if del_pc_name in emp_df.columns:
                                    emp_df = emp_df.drop(columns=[del_pc_name])
                                    save_employees_df(emp_df)
                                    st.rerun()
            with ex_col2:
                with st.expander(t("⚡ Thêm Nhanh Nhân Sự", "⚡ スタッフをクイック追加")):
                    make_expander_blue()
                    if 'qa_form_key' not in st.session_state:
                        st.session_state['qa_form_key'] = 0
                    fk = st.session_state['qa_form_key']
                    
                    qa_ma_nv = st.text_input(t("Mã NV", "社員番号"), key=f"qa_ma_nv_{fk}")
                    qa_ten_nv = st.text_input(t("Tên NV (*)", "氏名 (*)"), key=f"qa_ten_nv_{fk}")
                    qa_c1, qa_c2 = st.columns(2)
                    with qa_c1: qa_phong_ban = st.text_input(t("Phòng ban", "部署"), key=f"qa_phong_ban_{fk}")
                    with qa_c2: qa_chuc_vu = st.text_input(t("Chức vụ", "役職"), key=f"qa_chuc_vu_{fk}")
                    qa_luong_cb = st.number_input(t("Lương cơ bản", "基本給"), min_value=0, step=1000000, key=f"qa_luong_cb_{fk}")
                    if st.button(t("Thêm Nhân Sự", "追加する"), use_container_width=True, type="primary"):
                        if not qa_ten_nv.strip():
                            st.warning(t("Vui lòng nhập Tên NV!", "氏名を入力してください！"))
                        else:
                            new_row = {"Mã NV": qa_ma_nv.strip(), "Tên NV": qa_ten_nv.strip(), "Phòng ban": qa_phong_ban.strip(), "Chức vụ": qa_chuc_vu.strip(), "Lương cơ bản": qa_luong_cb}
                            for c in allowance_cols:
                                new_row[c] = 0
                            new_row["Lương Gross"] = qa_luong_cb
                            new_row["Ngày bắt đầu tính"] = None
                            import pandas as pd
                            new_df = pd.DataFrame([new_row])
                            emp_df = pd.concat([emp_df, new_df], ignore_index=True)
                            save_employees_df(emp_df)
                            st.toast(t(f"Đã thêm {qa_ten_nv} thành công!", f"{qa_ten_nv} を追加しました！"), icon="✅")
                            st.session_state['qa_form_key'] += 1
                            import time; time.sleep(0.5)
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(t("💾 LƯU THÔNG TIN", "💾 保存"), key="save_emps", type="primary"):
                st.session_state['ot_base_data']['standard_days'] = std_days_mo
                st.session_state['ot_base_data']['from_date'] = from_date.strftime("%Y-%m-%d")
                st.session_state['ot_base_data']['to_date'] = to_date.strftime("%Y-%m-%d")
                
                st.session_state['ot_base_data']['standard_hours_per_day'] = std_hrs
                save_base_data(st.session_state['ot_base_data'])

                for c in ["Lương cơ bản", "Lương Gross"] + allowance_cols:
                    if c in edited_emp.columns:
                        edited_emp[c] = edited_emp[c].astype(str).str.replace(',', '', regex=False)
                        edited_emp[c] = pd.to_numeric(edited_emp[c], errors='coerce').fillna(0)

                edited_emp['Lương cơ bản'] = pd.to_numeric(edited_emp['Lương cơ bản'], errors='coerce').fillna(0)
                gross = edited_emp['Lương cơ bản'].copy()
                for c in allowance_cols:
                    if c in edited_emp.columns:
                        edited_emp[c] = pd.to_numeric(edited_emp[c], errors='coerce').fillna(0)
                        gross += edited_emp[c]
                edited_emp['Lương Gross'] = gross

                save_employees_df(edited_emp)
                st.session_state['pending_toast'] = t("Đã lưu Thông tin chung thành công!", "設定を保存しました！")
                st.rerun()

        with col_right:
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            with st.container():
                from components.ui_utils import make_container_white
                make_container_white()
                
                st.markdown(f"""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
                    </style>
                    <div style='
                        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        border-radius: 8px;
                        border-top: 4px solid #00B0F0;
                        padding: 10px;
                        margin-bottom: 15px;
                        text-align: center; color: #2c3e50; font-size: 15px; font-weight: bold; text-transform: uppercase;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                    '>
                        <span class="material-symbols-rounded" style="vertical-align: middle; color: #00B0F0; margin-right: 5px; font-size: 20px;">query_stats</span>
                        <span style="vertical-align: middle;">{t('THỐNG KÊ THỜI GIAN', '労働時間統計')}</span>
                    </div>
                """, unsafe_allow_html=True)

                valid_emps = emp_df["Tên NV"].dropna().unique().tolist()
                if not valid_emps:
                    st.info(t("Chưa có nhân sự", "スタッフなし"))
                    selected_emp = None
                else:
                    selected_emp = st.selectbox(t("Chọn nhân sự:", "スタッフを選択:"), valid_emps)

                if selected_emp:
                    emp_row_idx = emp_df.index[emp_df["Tên NV"] == selected_emp].tolist()[0]
                    current_start_date = emp_df.at[emp_row_idx, "Ngày bắt đầu tính"]

                    import datetime
                    try:
                        if current_start_date:
                            default_date = datetime.datetime.strptime(str(current_start_date), "%Y-%m-%d").date()
                        else:
                            default_date = datetime.date.today()
                    except:
                        default_date = datetime.date.today()

                    new_start_date = st.date_input(t("Ngày bắt đầu tính (Tích lũy):", "計算開始日 (累計):"), value=default_date, key=f"start_date_{selected_emp}")
                    
                    days_off = st.number_input(t("Số ngày nghỉ:", "休んだ日数:"), min_value=0.0, value=0.0, step=0.5)

                    if str(new_start_date) != str(current_start_date):
                        emp_df.at[emp_row_idx, "Ngày bắt đầu tính"] = str(new_start_date)
                        save_employees_df(emp_df)
                        st.rerun()

                    today = datetime.date.today()

                    holidays_list = []
                    if 'holidays_df' in st.session_state['ot_base_data']:
                        hdf = st.session_state['ot_base_data']['holidays_df']
                        if not hdf.empty and 'Ngày nghỉ' in hdf.columns:
                            holidays_list = pd.to_datetime(hdf['Ngày nghỉ'], format='mixed', dayfirst=True).dt.date.tolist()

                    regular_days = 0
                    curr_date = new_start_date
                    while curr_date <= today:
                        is_working_day = False
                        if curr_date.weekday() < 5:
                            is_working_day = True
                        elif curr_date.weekday() == 5:
                            next_week = curr_date + datetime.timedelta(days=7)
                            if next_week.month != curr_date.month:
                                is_working_day = True
                                
                        if is_working_day and curr_date not in holidays_list:
                            regular_days += 1
                        curr_date += datetime.timedelta(days=1)

                    regular_days = max(0, regular_days - days_off)
                    std_hrs = float(st.session_state['ot_base_data'].get('standard_hours_per_day', 8.0))
                    regular_hours = regular_days * std_hrs

                    ot_records = get_records('ot')
                    ot_hours_total = 0.0
                    if ot_records:
                        ot_df = pd.DataFrame(ot_records)
                        if all(c in ot_df.columns for c in ['ot_date', 'employee_name', 'order_name', 'ot_hours']):
                            ot_df = ot_df.drop_duplicates(subset=['ot_date', 'employee_name', 'order_name', 'ot_hours'], keep='first')
                        else:
                            ot_df = ot_df.drop_duplicates()
                        if not ot_df.empty and 'employee_name' in ot_df.columns and 'ot_date' in ot_df.columns and 'ot_hours' in ot_df.columns:
                            ot_df['ot_date'] = pd.to_datetime(ot_df['ot_date'], format='mixed', dayfirst=True).dt.date
                            ot_df['ot_hours'] = pd.to_numeric(ot_df['ot_hours'], errors='coerce').fillna(0)

                            mask = (ot_df['employee_name'] == selected_emp) & (ot_df['ot_date'] >= new_start_date) & (ot_df['ot_date'] <= today)
                            ot_hours_total = ot_df[mask]['ot_hours'].sum()

                    cumulative_hours = regular_hours + ot_hours_total

                    # Biểu đồ và Stats
                    if cumulative_hours > 0:
                        fig = go.Figure(data=[go.Pie(
                            labels=[t('Hành chính', '通常業務'), t('Tăng ca', '残業')],
                            values=[regular_hours, ot_hours_total],
                            hole=.6,
                            marker_colors=['#00B0F0', '#ff4757'],
                            textinfo='percent',
                            hoverinfo='label+value'
                        )])
                        fig.update_layout(
                            font=dict(family="'Times New Roman', serif"),
                            margin=dict(t=15, b=0, l=0, r=0),
                            height=170,
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)"
                        )
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        from components.ui_utils import render_empty_state
                        render_empty_state(t('Chưa có dữ liệu', 'データなし'), icon="bar_chart", height=160)

                    st.markdown(f'''
                    <style>
                    .hour-card {{ padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid; border: 1px solid; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }}
                    .hc-title {{ font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 3px; }}
                    .hc-val {{ font-size: 19px; font-weight: 700; }}
                    </style>
                    <div class='hour-card' style='background: #f0f9ff; border-color: #e0f2fe; border-left-color: #00B0F0;'>
                        <div class='hc-title'>🏢 {t("Hành chính", "通常")}</div>
                        <div class='hc-val' style='color: #00B0F0;'>{regular_hours:,.1f} <span style='font-size: 13px; font-weight: 500;'>h</span></div>
                    </div>
                    <div class='hour-card' style='background: #fff5f5; border-color: #ffe4e6; border-left-color: #ff4757;'>
                        <div class='hc-title'>🚀 {t("Tăng ca (OT)", "残業")}</div>
                        <div class='hc-val' style='color: #ff4757;'>{ot_hours_total:,.1f} <span style='font-size: 13px; font-weight: 500;'>h</span></div>
                    </div>
                    <div class='hour-card' style='background: #f0fdf4; border-color: #dcfce7; border-left-color: #10b981;'>
                        <div class='hc-title'>⭐ {t("Tổng", "累計")}</div>
                        <div class='hc-val' style='color: #10b981;'>{cumulative_hours:,.1f} <span style='font-size: 13px; font-weight: 500;'>h</span></div>
                    </div>
                    ''', unsafe_allow_html=True)

    with tab2:
        c1, c2 = st.columns([1.4, 0.9], gap="large")
        with c1:
            st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('DANH SÁCH NGÀY NGHỈ / LỄ', '休日・祭日一覧')}</h3>", unsafe_allow_html=True)

            guide_text = t(
                "<div style='margin-top: 12px; margin-bottom: 12px;'>✨ <b>HƯỚNG DẪN:</b><br>- <b>Thêm mới:</b> Bấm vào dấu <b>+</b> mờ mờ ở góc dưới cùng bên trái của bảng.<br>- <b>Chọn ngày/Sửa:</b> Click đúp (2 lần) vào ô cần sửa hoặc chọn ngày trên lịch.<br>- <b>Xóa:</b> Click chọn ô vuông ngoài cùng bên trái của dòng đó, sau đó nhấn phím <b>Delete</b> trên bàn phím (hoặc bấm biểu tượng Thùng rác hiện ra ở góc phải).</div>",
                "<div style='margin-top: 12px; margin-bottom: 12px;'>✨ <b>操作ガイド:</b><br>- <b>新規追加:</b> 表の左下にある <b>+</b> ボタンを押してください。<br>- <b>日付選択・編集:</b> セルをダブルクリックして編集またはカレンダーから選択。<br>- <b>削除:</b> 左端のチェックボックスを選択し、<b>Delete</b>キーまたはゴミ箱アイコンで削除。</div>"
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
        
            holiday_translations = {
                "Tết Dương lịch": "元日",
                "Giải phóng Miền Nam": "南部解放記念日",
                "Quốc tế Lao động": "メーデー",
                "Lễ Quốc khánh": "建国記念日休暇",
                "Tết Nguyên Đán": "テト（旧正月）",
                "Giỗ Tổ Hùng Vương": "フン王の命日",
                "Nghỉ hoán đổi (30/4-1/5)": "振替休日（南部解放・メーデー）",
                "Nghỉ bù Giỗ Tổ Hùng Vương": "フン王の命日（振替休日）",
                "Nghỉ hoán đổi Quốc khánh": "建国記念日（振替休日）",
                "Nghỉ bù Quốc tế Lao động": "メーデー（振替休日）",
                "Nghỉ bù Tết Dương lịch": "元日（振替休日）",
                "Nghỉ bù Giải phóng Miền Nam": "南部解放記念日（振替休日）",
                "Nghỉ bù Lễ Quốc khánh": "建国記念日（振替休日）"
            }
            reverse_holiday_translations = {v: k for k, v in holiday_translations.items()}
        
            display_df = current_df.copy()
            if st.session_state.get('lang', 'VN') == 'JP':
                display_df['Lý do'] = display_df['Lý do'].apply(lambda x: holiday_translations.get(str(x).strip(), x))
            import datetime
            # Extract year from selected period to make it dynamic
            selected_year = datetime.datetime.now().year

            if st.button(t(f"Tự động điền Ngày Lễ VN {selected_year}", f"{selected_year}年ベトナム祝日を自動入力")):
                # Comprehensive Holiday Map for 2025-2028 (Solar, Lunar, Compensatory, and Swaps)
                holidays_map_all = {
                    2025: [
                        ("2025-01-01", "Tết Dương lịch"),
                        ("2025-01-25", "Tết Nguyên Đán"), ("2025-01-26", "Tết Nguyên Đán"), ("2025-01-27", "Tết Nguyên Đán"), ("2025-01-28", "Tết Nguyên Đán"), ("2025-01-29", "Tết Nguyên Đán"), ("2025-01-30", "Tết Nguyên Đán"), ("2025-01-31", "Tết Nguyên Đán"), ("2025-02-01", "Tết Nguyên Đán"), ("2025-02-02", "Tết Nguyên Đán"),
                        ("2025-04-07", "Giỗ Tổ Hùng Vương"),
                        ("2025-04-30", "Giải phóng Miền Nam"),
                        ("2025-05-01", "Quốc tế Lao động"),
                        ("2025-05-02", "Nghỉ hoán đổi (30/4-1/5)"),
                        ("2025-08-30", "Lễ Quốc khánh"), ("2025-08-31", "Lễ Quốc khánh"), ("2025-09-01", "Lễ Quốc khánh"), ("2025-09-02", "Lễ Quốc khánh")
                    ],
                    2026: [
                        ("2026-01-01", "Tết Dương lịch"),
                        ("2026-02-14", "Tết Nguyên Đán"), ("2026-02-15", "Tết Nguyên Đán"), ("2026-02-16", "Tết Nguyên Đán"), ("2026-02-17", "Tết Nguyên Đán"), ("2026-02-18", "Tết Nguyên Đán"), ("2026-02-19", "Tết Nguyên Đán"), ("2026-02-20", "Tết Nguyên Đán"), ("2026-02-21", "Tết Nguyên Đán"), ("2026-02-22", "Tết Nguyên Đán"),
                        ("2026-04-26", "Giỗ Tổ Hùng Vương"), ("2026-04-27", "Nghỉ bù Giỗ Tổ Hùng Vương"),
                        ("2026-04-30", "Giải phóng Miền Nam"),
                        ("2026-05-01", "Quốc tế Lao động"),
                        ("2026-08-29", "Lễ Quốc khánh"), ("2026-08-30", "Lễ Quốc khánh"), ("2026-08-31", "Nghỉ hoán đổi Quốc khánh"), ("2026-09-01", "Lễ Quốc khánh"), ("2026-09-02", "Lễ Quốc khánh")
                    ],
                    2027: [
                        ("2027-01-01", "Tết Dương lịch"),
                        ("2027-02-04", "Tết Nguyên Đán"), ("2027-02-05", "Tết Nguyên Đán"), ("2027-02-06", "Tết Nguyên Đán"), ("2027-02-07", "Tết Nguyên Đán"), ("2027-02-08", "Tết Nguyên Đán"), ("2027-02-09", "Tết Nguyên Đán"), ("2027-02-10", "Tết Nguyên Đán"), ("2027-02-11", "Tết Nguyên Đán"), ("2027-02-12", "Tết Nguyên Đán"),
                        ("2027-04-16", "Giỗ Tổ Hùng Vương"),
                        ("2027-04-30", "Giải phóng Miền Nam"),
                        ("2027-05-01", "Quốc tế Lao động"), ("2027-05-03", "Nghỉ bù Quốc tế Lao động"),
                        ("2027-09-01", "Lễ Quốc khánh"), ("2027-09-02", "Lễ Quốc khánh")
                    ],
                    2028: [
                        ("2028-01-01", "Tết Dương lịch"), ("2028-01-03", "Nghỉ bù Tết Dương lịch"),
                        ("2028-01-22", "Tết Nguyên Đán"), ("2028-01-23", "Tết Nguyên Đán"), ("2028-01-24", "Tết Nguyên Đán"), ("2028-01-25", "Tết Nguyên Đán"), ("2028-01-26", "Tết Nguyên Đán"), ("2028-01-27", "Tết Nguyên Đán"), ("2028-01-28", "Tết Nguyên Đán"), ("2028-01-29", "Tết Nguyên Đán"), ("2028-01-30", "Tết Nguyên Đán"),
                        ("2028-04-04", "Giỗ Tổ Hùng Vương"),
                        ("2028-04-30", "Giải phóng Miền Nam"),
                        ("2028-05-01", "Quốc tế Lao động"), ("2028-05-02", "Nghỉ bù Giải phóng Miền Nam"),
                        ("2028-09-01", "Lễ Quốc khánh"), ("2028-09-02", "Lễ Quốc khánh"), ("2028-09-04", "Nghỉ bù Lễ Quốc khánh")
                    ]
                }

                holidays_data = []
                if selected_year in holidays_map_all:
                    for date_str, reason in holidays_map_all[selected_year]:
                        holidays_data.append({"Ngày nghỉ": date_str, "Lý do": reason})
                else:
                    # Fallback for years beyond 2028
                    holidays_data = [
                        {"Ngày nghỉ": f"{selected_year}-01-01", "Lý do": "Tết Dương lịch"},
                        {"Ngày nghỉ": f"{selected_year}-04-30", "Lý do": "Giải phóng Miền Nam"},
                        {"Ngày nghỉ": f"{selected_year}-05-01", "Lý do": "Quốc tế Lao động"},
                        {"Ngày nghỉ": f"{selected_year}-09-01", "Lý do": "Lễ Quốc khánh"},
                        {"Ngày nghỉ": f"{selected_year}-09-02", "Lý do": "Lễ Quốc khánh"}
                    ]
                    st.warning(t(f"Hệ thống chỉ điền ngày Lễ Dương lịch cơ bản cho năm {selected_year}. Vui lòng tự thêm Lễ Âm lịch và nghỉ bù.", f"{selected_year}年の太陽暦の祝日のみ自動入力されました。旧正月や振替休日は手動で追加してください。"))

                vn_holidays = pd.DataFrame(holidays_data)
                vn_holidays["Ngày nghỉ"] = pd.to_datetime(vn_holidays["Ngày nghỉ"], format='%Y-%m-%d')
                
                # Filter out standard holidays from current_df to prevent duplicates
                standard_reasons = ["Tết Dương lịch", "Giải phóng Miền Nam", "Quốc tế Lao động", "Lễ Quốc khánh", "Tết Nguyên Đán", "Giỗ Tổ Hùng Vương"]
                current_df = current_df[~current_df["Lý do"].isin(standard_reasons)]
                
                combined = pd.concat([current_df, vn_holidays]).drop_duplicates(subset=["Ngày nghỉ"], keep="last").sort_values("Ngày nghỉ").reset_index(drop=True)
                st.session_state['ot_base_data']['holidays_df'] = combined
                
                # Force widget reset by changing key
                if "holidays_editor_key" not in st.session_state:
                    st.session_state["holidays_editor_key"] = 1
                st.session_state["holidays_editor_key"] += 1
                
                # Save immediately
                save_base_data(st.session_state['ot_base_data'])
                st.toast(t("Đã tự động điền thành công!", "自動入力が完了しました！"), icon="✅")
                
                st.rerun()

            editor_key = f"holidays_editor_{st.session_state.get('holidays_editor_key', 0)}"

            holidays_df = st.data_editor(
                display_df,
                num_rows="dynamic",
                column_order=["Ngày nghỉ", "Lý do"],
                column_config={
                    "Ngày nghỉ": st.column_config.DateColumn(t("Ngày nghỉ (Chọn lịch)", "休日 (カレンダー選択)"), format="YYYY-MM-DD", required=True),
                    "Lý do": st.column_config.TextColumn(t("Lý do / Tên ngày lễ", "理由・祭日名"), required=True)
                },
                use_container_width=True,
                key=editor_key
            )

            if st.button(t("LƯU NGÀY LỄ", "休日を保存")):
                if st.session_state.get('lang', 'VN') == 'JP':
                    holidays_df['Lý do'] = holidays_df['Lý do'].apply(lambda x: reverse_holiday_translations.get(str(x).strip(), x))
                st.session_state['ot_base_data']['holidays_df'] = holidays_df
                save_base_data(st.session_state['ot_base_data'])
                st.toast(t("Đã lưu ngày lễ thành công!", "休日を保存しました！"), icon=":material/check_circle:")
                import time
                time.sleep(0.5)
                st.rerun()

        with c2:
            st.markdown("<div style='margin-top: 45px;'></div>", unsafe_allow_html=True)
            import json
            import streamlit.components.v1 as components
            holidays_list = []
            if current_df is not None and not current_df.empty:
                for _, row in current_df.iterrows():
                    dt = row.get("Ngày nghỉ")
                    reason = row.get("Lý do", "")
                    if pd.notnull(dt):
                        date_str = str(dt)[:10]
                        holidays_list.append({"date": date_str, "reason": reason, "is_jp": False})
            
            # Fetch JP holidays dynamically
            try:
                import jpholiday
                import datetime
                
                jp_vn_map = {
                    "元日": "Tết Dương lịch",
                    "成人の日": "Lễ Thành nhân",
                    "建国記念の日": "Quốc khánh",
                    "天皇誕生日": "SN Thiên hoàng",
                    "春分の日": "Ngày Xuân phân",
                    "昭和の日": "Ngày Chiêu Hòa",
                    "憲法記念日": "Ngày Hiến pháp",
                    "みどりの日": "Ngày Lễ xanh",
                    "こどもの日": "Tết Thiếu nhi",
                    "海の日": "Ngày của Biển",
                    "山の日": "Ngày của Núi",
                    "敬老の日": "Ngày Kính lão",
                    "秋分の日": "Ngày Thu phân",
                    "スポーツの日": "Ngày Thể thao",
                    "文化の日": "Ngày Văn hóa",
                    "勤労感謝の日": "Lễ Cảm tạ",
                    "振替休日": "Nghỉ bù",
                    "国民の休日": "Quốc lễ"
                }

                def get_vn_name(jp_name):
                    res = jp_name
                    for jp, vn in jp_vn_map.items():
                        res = res.replace(jp, vn)
                    return res

                curr_y = datetime.datetime.now().year
                lang = st.session_state.get('lang', 'VN')
                
                for y in [curr_y - 1, curr_y, curr_y + 1]:
                    for jp_date, jp_name in jpholiday.year_holidays(y):
                        display_name = jp_name if lang == 'JP' else get_vn_name(jp_name)
                        holidays_list.append({
                            "date": jp_date.strftime("%Y-%m-%d"),
                            "reason": display_name,
                            "is_jp": True
                        })
            except ImportError:
                pass
        
            holidays_json = json.dumps(holidays_list)
            html_code = f"""
            <style>
            body {{ font-family: 'Times New Roman', serif; margin: 0; padding: 0; color: #334155; }}
            .calendar-container {{ border: 2px solid #00B0F0; border-radius: 8px; padding: 15px; background: #00B0F0; margin-top: 45px; box-shadow: 0 5px 15px rgba(0, 176, 240, 0.3); }}
            .cal-header {{ display: flex; justify-content: space-between; align-items: center; padding: 5px 0 15px 0; }}
            .cal-header button {{ background: white; border: none; border-radius: 4px; padding: 4px 14px; cursor: pointer; color: #00B0F0; font-weight: bold; transition: all 0.2s; font-size: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .cal-header button:hover {{ background: #f8fafc; color: #0089b8; }}
            .cal-header h3 {{ margin: 0; font-size: 18px; font-weight: 600; color: white; text-shadow: 0 1px 2px rgba(0,0,0,0.1); }}
            .cal-grid {{ display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 1px; background: #0098d0; border: 1px solid #0098d0; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }}
            .cal-grid > div {{ background: #fff; min-height: 70px; padding: 4px; box-sizing: border-box; min-width: 0; }}
            .day-name {{ min-height: 30px !important; text-align: center; font-weight: bold; background: #f8fafc !important; font-size: 13px; padding-top: 8px !important; color: #64748b; }}
            .day-number {{ font-weight: 500; font-size: 13px; margin-bottom: 4px; text-align: right; color: #475569; }}
            .holiday-event {{ background: #10b981; color: white; font-size: 11px; padding: 3px 5px; border-radius: 4px; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: default; }}
            .jp-holiday-event {{ background: #ef4444; color: white; font-size: 11px; padding: 3px 5px; border-radius: 4px; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: default; }}
            .joint-holiday-event {{ background: #a855f7; color: white; font-size: 11px; padding: 3px 5px; border-radius: 4px; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: default; }}
            .other-month {{ background: #f1f5f9 !important; color: #94a3b8 !important; }}
            .other-month .day-number {{ color: #94a3b8 !important; }}
            .today {{ background: #f0f9ff !important; }}
            .today .day-number {{ background: #00B0F0; color: white !important; font-weight: bold; border-radius: 50%; width: 22px; height: 22px; line-height: 22px; text-align: center; display: block; margin-left: auto; box-shadow: 0 2px 4px rgba(0, 176, 240, 0.4); margin-bottom: 4px; }}
            .legend-container {{ margin-top: 15px; display: flex; gap: 15px; justify-content: center; font-size: 13px; color: white; font-weight: 500; flex-wrap: wrap; }}
            .legend-item {{ display: flex; align-items: center; gap: 6px; }}
            .legend-color {{ width: 14px; height: 14px; border-radius: 3px; border: 1.5px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}
            .legend-vn {{ background: #10b981; }}
            .legend-jp {{ background: #ef4444; }}
            .legend-joint {{ background: #a855f7; }}
            </style>

            <div class="calendar-container">
                <div class="cal-header">
                    <button onclick="changeMonth(-1)">&lt;</button>
                    <h3 id="monthYear"></h3>
                    <button onclick="changeMonth(1)">&gt;</button>
                </div>
                <div class="cal-grid" id="calGrid"></div>
                <div class="legend-container">
                    <div class="legend-item">
                        <div class="legend-color legend-vn"></div>
                        <span>{t('Lễ Việt Nam', 'ベトナムの祝日')}</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color legend-jp"></div>
                        <span>{t('Lễ Nhật Bản', '日本の祝日')}</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color legend-joint"></div>
                        <span>{t('Lễ chung (VN & JP)', '共通の祝日 (越・日)')}</span>
                    </div>
                </div>
            </div>

            <script>
            const holidays = {holidays_json};
            const currentLang = "{t('vn', 'jp')}";
            const holidayTranslations = {{
                "Tết Dương lịch": "元日",
                "Giải phóng Miền Nam": "南部解放記念日",
                "Quốc tế Lao động": "メーデー",
                "Lễ Quốc khánh": "建国記念日休暇",
                "Tết Nguyên Đán": "テト（旧正月）",
                "Giỗ Tổ Hùng Vương": "フン王の命日",
                "Nghỉ hoán đổi (30/4-1/5)": "振替休日（南部解放・メーデー）",
                "Nghỉ bù Giỗ Tổ Hùng Vương": "フン王の命日（振替休日）",
                "Nghỉ hoán đổi Quốc khánh": "建国記念日（振替休日）",
                "Nghỉ bù Quốc tế Lao động": "メーデー（振替休日）",
                "Nghỉ bù Tết Dương lịch": "元日（振替休日）",
                "Nghỉ bù Giải phóng Miền Nam": "南部解放記念日（振替休日）",
                "Nghỉ bù Lễ Quốc khánh": "建国記念日（振替休日）"
            }};
            let currentDate = new Date();

            function renderCalendar() {{
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();
            
                if (currentLang === 'vn') {{
                    document.getElementById("monthYear").innerText = "Tháng " + (month + 1) + ", " + year;
                }} else {{
                    document.getElementById("monthYear").innerText = year + "年 " + (month + 1) + "月";
                }}
            
                const firstDay = new Date(year, month, 1).getDay();
                const startDay = firstDay === 0 ? 6 : firstDay - 1; 
            
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                const daysInPrevMonth = new Date(year, month, 0).getDate();
            
                let html = `
                    <div class="day-name">{t('T2', '月')}</div>
                    <div class="day-name">{t('T3', '火')}</div>
                    <div class="day-name">{t('T4', '水')}</div>
                    <div class="day-name">{t('T5', '木')}</div>
                    <div class="day-name">{t('T6', '金')}</div>
                    <div class="day-name">{t('T7', '土')}</div>
                    <div class="day-name">{t('CN', '日')}</div>
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
                    let dayHolidays = holidays.filter(h => h.date === dateStr);
                    
                    let hasJoint = false;
                    const jointKeywords = ["tết dương lịch", "quốc tế lao động", "元日", "メーデー"];
                    let filteredHolidays = [];
                    
                    dayHolidays.forEach(h => {{
                        const lowerReason = h.reason.toLowerCase();
                        const isJoint = jointKeywords.some(k => lowerReason.includes(k));
                        if (isJoint) {{
                            if (!hasJoint) {{
                                hasJoint = true;
                                filteredHolidays.push({{ ...h, is_joint: true }});
                            }}
                        }} else {{
                            filteredHolidays.push(h);
                        }}
                    }});

                    filteredHolidays.forEach(h => {{
                        const displayReason = (currentLang === 'jp' && holidayTranslations[h.reason]) ? holidayTranslations[h.reason] : h.reason;
                        let eventClass = h.is_jp ? "jp-holiday-event" : "holiday-event";
                        if (h.is_joint) eventClass = "joint-holiday-event";
                        eventsHtml += `<div class="${{eventClass}}" title="${{displayReason}}">${{displayReason}}</div>`;
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
            st.warning(t("Vui lòng thêm ít nhất 1 nhân sự trong phần CÀI ĐẶT CHUNG trước.", "一般設定でスタッフを1名以上追加してください。"), icon="⚠️")
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
        
            is_holiday = False
            holiday_reason = ""
            if not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
                try:
                    holidays_list = pd.to_datetime(base['holidays_df']["Ngày nghỉ"], format='mixed', dayfirst=True).dt.date.tolist()
                    if ot_date in holidays_list:
                        is_holiday = True
                        reason_row = base['holidays_df'][pd.to_datetime(base['holidays_df']["Ngày nghỉ"], format='mixed', dayfirst=True).dt.date == ot_date]
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
                tag_html = f"<span style='background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>🏖️ {t('Ngày lễ', '祭日')} ({holiday_reason}) (3.0x - 4.0x)</span>"
            elif is_weekend:
                tag_html = f"<span style='background-color: #fff8e1; color: #f57f17; border: 1px solid #ffecb3; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>🌴 {t('Cuối tuần', '週末')} (2.0x - 2.7x)</span>"
            else:
                if ot_date.weekday() == 5:
                    label = t('Ngày đi làm hành chính (Thứ 7 cuối tháng đi làm)', '平日（最終土曜日は出勤）')
                else:
                    label = t('Ngày đi làm hành chính', '平日')
                tag_html = f"<span style='background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px;'>💼 {label} (1.5x - 2.0x)</span>"

            st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 15px; margin-top: -5px;'>
                    <span style='color: rgba(49, 51, 63, 0.6); font-size: 14px;'>{t('Thuộc kỳ lương', '給与計算期間')}: <strong>{calculated_period}</strong></span>
                    {tag_html}
                </div>
            """, unsafe_allow_html=True)
        
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
                    with b_col5: st.metric("400%", f"{auto_buckets[400]:.1f} h", help=f"{nl}: 08h-17h")
                
                    std_days = float(base.get('standard_days', 22.0))
                    std_hrs = float(base.get('standard_hours_per_day', 8.0))
                    hourly_rate_est = (emp_gross / std_days / std_hrs) if (std_days > 0 and std_hrs > 0) else 0
                    
                    est_cost = sum(hrs * (pct / 100.0) * hourly_rate_est for pct, hrs in auto_buckets.items() if hrs > 0)
                    
                    if est_cost > 0:
                        svg_icon = '<svg xmlns="http://www.w3.org/2000/svg" height="18" viewBox="0 -960 960 960" width="18" fill="#2e7d32" style="vertical-align: middle; margin-right: 4px; margin-top: -2px;"><path d="M480-320q-33 0-56.5-23.5T400-400v-160q0-33 23.5-56.5T480-640h160q33 0 56.5 23.5T720-560v160q0 33-23.5 56.5T640-320H480ZM160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm0-80h640v-480H160v480Zm0 0v-480 480Z"/><path d="M560-440q17 0 28.5-11.5T600-480q0-17-11.5-28.5T560-520q-17 0-28.5 11.5T520-480q0 17 11.5 28.5T560-440Z"/></svg>'
                        st.markdown(f"<div style='margin-bottom: 15px; padding: 6px 12px; background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 6px; color: #2e7d32; font-size: 14px; display: inline-block;'>{svg_icon}<strong>{t('Dự tính chi phí:', '予想コスト:')}</strong> {est_cost:,.0f} VNĐ</div>", unsafe_allow_html=True)
                
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
            
                std_days = float(base.get('standard_days', 22.0))
                std_hrs = float(base.get('standard_hours_per_day', 8.0))
                hourly_rate_est = (emp_gross / std_days / std_hrs) if (std_days > 0 and std_hrs > 0) else 0
                
                est_cost_manual = (h_150 * 1.5 + h_200 * 2.0 + h_270 * 2.7 + h_300 * 3.0 + h_400 * 4.0 + c_hrs * (c_mult / 100.0)) * hourly_rate_est
                
                if est_cost_manual > 0:
                    svg_icon = '<svg xmlns="http://www.w3.org/2000/svg" height="18" viewBox="0 -960 960 960" width="18" fill="#2e7d32" style="vertical-align: middle; margin-right: 4px; margin-top: -2px;"><path d="M480-320q-33 0-56.5-23.5T400-400v-160q0-33 23.5-56.5T480-640h160q33 0 56.5 23.5T720-560v160q0 33-23.5 56.5T640-320H480ZM160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm0-80h640v-480H160v480Zm0 0v-480 480Z"/><path d="M560-440q17 0 28.5-11.5T600-480q0-17-11.5-28.5T560-520q-17 0-28.5 11.5T520-480q0 17 11.5 28.5T560-440Z"/></svg>'
                    st.markdown(f"<div style='margin-bottom: 15px; padding: 6px 12px; background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 6px; color: #2e7d32; font-size: 14px; display: inline-block;'>{svg_icon}<strong>{t('Dự tính chi phí:', '予想コスト:')}</strong> {est_cost_manual:,.0f} VNĐ</div>", unsafe_allow_html=True)
            
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
                c_name, c_save, c_dl, c_del = st.columns([3.5, 2.0, 2.0, 2.5])
                with c_name:
                    default_name = t("Bảng tổng hợp tăng ca (OT).xlsx", "残業計算結果_OT.xlsx")
                    export_name = st.text_input("📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), value=default_name, key="ot_manual_filename")
                    if not export_name.endswith(".xlsx"):
                        export_name += ".xlsx"
                with c_save:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button(t("💾 LƯU DỮ LIỆU", "💾 データ保存"), use_container_width=True, type="primary", key="save_ot_data"):
                        from logic.history_records import add_records
                        add_records("ot", st.session_state['ot_records'])
                        st.session_state['pending_toast'] = t("Đã lưu dữ liệu vào hệ thống!", "データをシステムに保存しました！")
                        st.rerun()
                    
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

