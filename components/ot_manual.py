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
        components.html(js_count_up, height=0)
        
    tab1, tab2 = st.tabs([t("1. THÔNG TIN CHUNG", "1. 一般情報"), t("2. NGÀY NGHỈ & LỄ", "2. 休日・祭日")])
    
    components.html("""
    <script>
        const doc = window.parent.document;
        setTimeout(() => {
            const tabsContainers = doc.querySelectorAll('[data-testid="stTabs"]');
            
            // Main Tabs
            if (tabsContainers.length > 0) {
                const tablist = tabsContainers[0].querySelector('div[role="tablist"]');
                if (tablist) {
                    const mainTabs = tablist.children;
                    Array.from(mainTabs).forEach((tab, index) => {
                        tab.addEventListener("click", () => {
                            sessionStorage.setItem("ot_main_tab_idx", index);
                        });
                    });
                    const saved = sessionStorage.getItem("ot_main_tab_idx");
                    if (saved !== null && saved < mainTabs.length) {
                        if (mainTabs[saved].getAttribute("aria-selected") !== "true") {
                            mainTabs[saved].click();
                        }
                    }
                }
            }
            
            // Inner Tabs
            if (tabsContainers.length > 1) {
                const tablist = tabsContainers[1].querySelector('div[role="tablist"]');
                if (tablist) {
                    const innerTabs = tablist.children;
                    Array.from(innerTabs).forEach((tab, index) => {
                        tab.addEventListener("click", () => {
                            sessionStorage.setItem("ot_inner_tab_idx", index);
                        });
                    });
                    const saved = sessionStorage.getItem("ot_inner_tab_idx");
                    if (saved !== null && saved < innerTabs.length) {
                        if (innerTabs[saved].getAttribute("aria-selected") !== "true") {
                            innerTabs[saved].click();
                        }
                    }
                }
            }
        }, 300);
    </script>
    """, height=0)

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

            # Smart Workload Advisor Widget
            holidays_list_adv = []
            if 'holidays_df' in st.session_state['ot_base_data']:
                hdf_adv = st.session_state['ot_base_data']['holidays_df']
                if not hdf_adv.empty and 'Ngày nghỉ' in hdf_adv.columns:
                    try:
                        holidays_list_adv = pd.to_datetime(hdf_adv['Ngày nghỉ'], format='mixed', dayfirst=True).dt.date.tolist()
                    except:
                        holidays_list_adv = []

            adv_total_days = max(0, (to_date - from_date).days + 1)
            adv_weekend_days = 0
            adv_holiday_days = 0
            adv_working_days = 0

            curr_adv = from_date
            while curr_adv <= to_date:
                is_wk = False
                if curr_adv.weekday() < 5:
                    is_wk = True
                elif curr_adv.weekday() == 5:
                    next_wk = curr_adv + datetime.timedelta(days=7)
                    if next_wk.month != curr_adv.month:
                        is_wk = True
                if curr_adv in holidays_list_adv:
                    adv_holiday_days += 1
                elif not is_wk:
                    adv_weekend_days += 1
                else:
                    adv_working_days += 1
                curr_adv += datetime.timedelta(days=1)

            if adv_total_days > 35:
                avg_months = round(adv_total_days / 30.4375, 1)
                avg_work_per_month = round(adv_working_days / avg_months, 1) if avg_months > 0 else adv_working_days
                adv_c1 = st.columns([1])[0]
                with adv_c1:
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        flex-wrap: wrap;
                        gap: 12px;
                        background: #f4fcff;
                        border: 1px solid #b3e8fb;
                        border-left: 4px solid #00B0F0;
                        border-radius: 12px;
                        padding: 0 18px;
                        min-height: 42px;
                        box-sizing: border-box;
                        font-size: 13.5px;
                        color: #0f4c64;
                        margin-top: 8px;
                        margin-bottom: 16px;
                        box-shadow: 0 1px 3px rgba(0, 176, 240, 0.08);
                    ">
                        <span style="display: inline-flex; align-items: center; gap: 8px; font-weight: 700; color: #0c5873;">
                            💡 {t('Lịch thực tế kỳ chọn:', '選択期間の実労働カレンダー:')}
                            <span style="background: #ffffff; color: #00B0F0; border: 1px solid #80d7f7; padding: 2px 10px; border-radius: 6px; font-size: 12.5px; font-weight: 700;">
                                📅 {adv_total_days} {t('ngày', '日')} (~{avg_months} {t('tháng', 'ヶ月')})
                            </span>
                        </span>
                        <span style="color: #80d7f7;">|</span>
                        <span style="color: #0c5873;">🏖️ {t('Cuối tuần', '休日')}: <b style="color: #0f4c64;">{adv_weekend_days}</b></span>
                        <span style="color: #80d7f7;">•</span>
                        <span style="color: #0c5873;">🎊 {t('Lễ', '祭日')}: <b style="color: #0f4c64;">{adv_holiday_days}</b></span>
                        <span style="color: #80d7f7;">|</span>
                        <span style="display: inline-flex; align-items: center; gap: 5px; background: #e6f7ff; border: 1.5px solid #00B0F0; color: #0088ba; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 13px;">
                            💼 {t('Tổng làm việc:', '実労働合計:')} {adv_working_days} {t('ngày', '日')}
                        </span>
                        <span style="display: inline-flex; align-items: center; gap: 5px; background: #00B0F0; color: #ffffff; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 13px; box-shadow: 0 2px 4px rgba(0, 176, 240, 0.3);">
                            📊 {t('Trung bình:', '月平均:')} ~{avg_work_per_month} {t('ngày/tháng', '日/月')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                adv_c1, adv_c2 = st.columns([7.7, 2.3])
                with adv_c1:
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        flex-wrap: wrap;
                        gap: 12px;
                        background: #f4fcff;
                        border: 1px solid #b3e8fb;
                        border-left: 4px solid #00B0F0;
                        border-radius: 12px;
                        padding: 0 18px;
                        height: 42px;
                        box-sizing: border-box;
                        font-size: 13.5px;
                        color: #0f4c64;
                        margin-top: 8px;
                        box-shadow: 0 1px 3px rgba(0, 176, 240, 0.08);
                    ">
                        <span style="display: inline-flex; align-items: center; gap: 8px; font-weight: 700; color: #0c5873;">
                            💡 {t('Lịch thực tế:', '実労働カレンダー:')}
                            <span style="background: #ffffff; color: #00B0F0; border: 1px solid #80d7f7; padding: 2px 10px; border-radius: 6px; font-size: 12.5px; font-weight: 700;">
                                📅 {adv_total_days} {t('ngày', '日')}
                            </span>
                        </span>
                        <span style="color: #80d7f7;">|</span>
                        <span style="color: #0c5873;">🏖️ {t('Cuối tuần', '休日')}: <b style="color: #0f4c64;">{adv_weekend_days}</b></span>
                        <span style="color: #80d7f7;">•</span>
                        <span style="color: #0c5873;">🎊 {t('Lễ', '祭日')}: <b style="color: #0f4c64;">{adv_holiday_days}</b></span>
                        <span style="color: #80d7f7;">|</span>
                        <span style="display: inline-flex; align-items: center; gap: 5px; background: #00B0F0; color: #ffffff; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 13px; box-shadow: 0 2px 4px rgba(0, 176, 240, 0.3);">
                            💼 {t('Làm việc:', '実労働:')} {adv_working_days} {t('ngày', '日')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                with adv_c2:
                    if abs(float(adv_working_days) - float(std_days_mo)) > 0.01 and adv_working_days > 0:
                        st.markdown("""
                        <style>
                        div.element-container:has(#apply-adv-anchor) {
                            display: none !important;
                        }
                        div.element-container:has(#apply-adv-anchor) + div.element-container {
                            margin: 0 !important;
                            padding: 0 !important;
                        }
                        div.element-container:has(#apply-adv-anchor) + div.element-container button {
                            height: 42px !important;
                            min-height: 42px !important;
                            max-height: 42px !important;
                            padding: 0px 18px !important;
                            font-size: 13px !important;
                            border-radius: 21px !important;
                            font-weight: 600 !important;
                            margin-top: 8px !important;
                            white-space: nowrap !important;
                            line-height: 42px !important;
                        }
                        </style>
                        <span id="apply-adv-anchor"></span>
                        """, unsafe_allow_html=True)
                        if st.button(t(f"ÁP DỤNG {adv_working_days} NGÀY", f"{adv_working_days}日を適用"), icon=":material/check_circle:", key="btn_apply_adv_days", type="secondary", use_container_width=True):
                            st.session_state['ot_base_data']['standard_days'] = float(adv_working_days)
                            save_base_data(st.session_state['ot_base_data'])
                            st.session_state['pending_toast'] = t(f"Đã cập nhật số ngày chuẩn thành {adv_working_days} ngày!", f"標準日数を {adv_working_days}日 に更新しました！")
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            head_col1, head_col2 = st.columns([7.8, 2.2])
            with head_col1:
                st.markdown(
                    f"<h3 style='font-size: 20px; font-weight: 600; margin: 0 0 4px 0;'>{t('THÔNG TIN NHÂN SỰ & CƠ CẤU LƯƠNG', 'スタッフ情報と給与構成')}</h3>"
                    f"<div style='font-size: 13.5px; color: #64748b; margin-bottom: 4px;'>{t('Quản lý thông tin nhân sự. Lưu ý: Cột Lương Gross sẽ được tính TỰ ĐỘNG khi bạn bấm Lưu.', 'スタッフ情報の管理。注:「総支給額」は保存時に自動計算されます。')}</div>",
                    unsafe_allow_html=True
                )

            with head_col2:
                st.markdown("""
                <style>
                div.element-container:has(#privacy-toggle-anchor) + div.element-container button {
                    padding: 4px 14px !important;
                    min-height: 36px !important;
                    height: 36px !important;
                    font-size: 13px !important;
                    border-radius: 20px !important;
                    font-weight: 600 !important;
                }
                </style>
                <span id="privacy-toggle-anchor"></span>
                <div style='margin-top: 10px;'></div>
                """, unsafe_allow_html=True)
                is_masked = st.session_state.get('mask_salary_mode', True)
                btn_txt = t(":material/visibility: Hiện lương thực tế", ":material/visibility: 給与を表示") if is_masked else t(":material/visibility_off: Ẩn lương (Bảo mật)", ":material/visibility_off: 給与を隠す")
                if st.button(btn_txt, key="toggle_salary_privacy_btn", use_container_width=True, type="primary" if is_masked else "secondary"):
                    st.session_state['mask_salary_mode'] = not is_masked
                    st.rerun()

            if st.session_state.get('mask_salary_mode', True):
                st.markdown(f"""
                <div style='
                    background: #fef2f2;
                    border: 1px solid #fecaca;
                    border-left: 4px solid #ef4444;
                    border-radius: 8px;
                    padding: 9px 14px;
                    margin-bottom: 12px;
                    display: flex;
                    align-items: center;
                    box-shadow: 0 2px 6px rgba(239, 68, 68, 0.08);
                '>
                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="min-width: 22px; margin-right: 10px;">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" fill="#fee2e2"/>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        <circle cx="12" cy="16.5" r="1.2" fill="#dc2626"/>
                    </svg>
                    <div style='font-size: 13px; color: #991b1b;'>
                        <b style='color: #b91c1c;'>{t("CHẾ ĐỘ BẢO MẬT TIỀN LƯƠNG ĐANG BẬT:", "給与プライバシーモード有効:")}</b> {t("Toàn bộ Lương cơ bản, Phụ cấp & Lương Gross đang được ẩn an toàn dưới dạng •••••• VNĐ. Bấm nút 'Hiện lương thực tế' ở trên để xem.", "基本給・手当・総支給額は •••••• VNĐ として安全に非表示化されています。上のボタンで表示できます。")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

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
            is_masked_active = st.session_state.get('mask_salary_mode', True)
            for c in ["Lương cơ bản", "Lương Gross"] + allowance_cols:
                if is_masked_active:
                    display_df[c] = "•••••• VNĐ"
                    col_label = col_cfg[c].label if c in col_cfg and hasattr(col_cfg[c], 'label') else c
                    col_cfg[c] = st.column_config.TextColumn(col_label, disabled=True)
                else:
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

                if st.session_state.get('mask_salary_mode', True):
                    for c in ["Lương cơ bản", "Lương Gross"] + allowance_cols:
                        if c in edited_emp.columns and c in emp_df.columns:
                            edited_emp[c] = emp_df[c].values
                else:
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
            st.markdown(f"<h3 id='holiday-heading' style='font-size: 20px; font-weight: 600;'>{t('DANH SÁCH NGÀY NGHỈ / LỄ', '休日・祭日一覧')}</h3>", unsafe_allow_html=True)

            guide_text = t(
                "<div style='margin-top: 12px; margin-bottom: 12px;'>✨ <b>HƯỚNG DẪN:</b><br>- <b>Thêm mới:</b> Bấm vào dấu <b>+</b> mờ mờ ở góc dưới cùng bên trái của bảng.<br>- <b>Chọn ngày/Sửa:</b> Click đúp (2 lần) vào ô cần sửa hoặc chọn ngày trên lịch.<br>- <b>Xóa:</b> Click chọn ô vuông ngoài cùng bên trái của dòng đó, sau đó nhấn phím <b>Delete</b> trên bàn phím (hoặc bấm biểu tượng Thùng rác hiện ra ở góc phải).</div>",
                "<div style='margin-top: 12px; margin-bottom: 12px;'>✨ <b>操作ガイド:</b><br>- <b>新規追加:</b> 表の左下にある <b>+</b> ボタンを押してください。<br>- <b>日付選択・編集:</b> セルをダブルクリックして編集 hoặc カレンダーから選択。<br>- <b>削除:</b> 左端のチェックボックスを選択し、<b>Delete</b>キー hoặc ゴミ箱アイコンで削除。</div>"
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

            st.markdown(
                f"<span id='holidays-table-anchor'></span>"
                f"<style>"
                f"div.element-container:has(#holidays-table-anchor) ~ div.element-container:has([data-testid='stDataEditor']),"
                f"div.element-container:has(#holidays-table-anchor) ~ div.element-container:has([data-testid='stDataFrame']) {{"
                f"    margin-top: -38px !important;"
                f"    margin-bottom: -6px !important;"
                f"}}"
                f"div.element-container:has(#holidays-table-anchor) ~ div.element-container:has([data-testid='stDataEditor']) [data-testid='stDataEditor'],"
                f"div.element-container:has(#holidays-table-anchor) ~ div.element-container:has([data-testid='stDataFrame']) [data-testid='stDataFrame'] {{"
                f"    padding-top: 22px !important;"
                f"}}"
                f"div.element-container:has(#holidays-table-anchor) ~ div.element-container:has([data-testid='stDataEditor']) [data-testid='stElementToolbar'],"
                f"div.element-container:has(#holidays-table-anchor) ~ div.element-container:has([data-testid='stDataFrame']) [data-testid='stElementToolbar'] {{"
                f"    top: -28px !important;"
                f"}}"
                f"div.element-container:has(#holidays-save-btn-anchor) + div.element-container {{"
                f"    margin-top: -14px !important;"
                f"}}"
                f"</style>",
                unsafe_allow_html=True
            )

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

            st.markdown("<span id='holidays-save-btn-anchor'></span>", unsafe_allow_html=True)
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
                st.markdown(
                    f"<div style='font-size: 13.5px; color: #64748b; margin: 2px 0 -14px 2px;'>{t('Thêm, sửa, xóa các dự án tại đây để tự động điền thông tin khi tính OT.', 'ここでプロジェクトを追加・編集・削除すると、OT計算時に自動入力されます。')}</div>",
                    unsafe_allow_html=True
                )
            
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
            current_order_id = str(order_id).strip() if 'order_id' in locals() and order_id else ""
            
            if clean_order_name:
                if current_order_id:
                    proj_recs = [r for r in st.session_state.get('ot_records', []) if str(r.get('order_name', '')).strip() == str(clean_order_name).strip() and str(r.get('order_id', '')).strip() == current_order_id]
                    display_proj_label = f"[{current_order_id}] {clean_order_name}"
                else:
                    proj_recs = [r for r in st.session_state.get('ot_records', []) if str(r.get('order_name', '')).strip() == str(clean_order_name).strip()]
                    display_proj_label = clean_order_name
                card_title = f"{t('NGÂN SÁCH OT DỰ ÁN ĐANG CHỌN', '選択中の案件OT予算集計')}: {display_proj_label}"
            else:
                proj_recs = st.session_state.get('ot_records', [])
                card_title = t('TỔNG NGÂN SÁCH OT TRONG BẢNG CHỜ XUẤT', '待機リスト全体のOT予算集計')
            total_proj_hrs = sum(float(r.get('ot_hours', 0)) for r in proj_recs)
            total_proj_cost = 0
            for r in proj_recs:
                for k, v in r.items():
                    if str(k).endswith('%'):
                        try: total_proj_cost += float(v)
                        except: pass
            emp_set = len(set(str(r.get('employee_name', '')) for r in proj_recs if r.get('employee_name')))
            
            border_color = "#00B0F0"
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border-radius: 8px;
                    border-left: 5px solid {border_color};
                    padding: 12px 18px;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    box-shadow: 0 2px 4px rgba(0, 176, 240, 0.1);
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;'>
                        <div style='font-size: 14.5px; font-weight: 700; color: #0369a1;'>
                            <span class="material-symbols-rounded" style="vertical-align: middle; color: #00B0F0; margin-right: 6px; font-size: 20px;">analytics</span>
                            <span style="vertical-align: middle;">{card_title}</span>
                        </div>
                        <div style='display: flex; gap: 18px; font-size: 13.5px; color: #334155; align-items: center;'>
                            <div><b>{total_proj_hrs:,.1f}</b> {t('giờ OT', 'OT時間')} ({len(proj_recs)} {t('bản ghi', '件')})</div>
                            <div style='color: #cbd5e1;'>•</div>
                            <div><b>{emp_set}</b> {t('nhân sự', '名')}</div>
                            <div style='color: #cbd5e1;'>•</div>
                            <div>{t('Chi phí ước tính', '予想支給額')}: <b style='color: #0284c7; font-size: 15px;'>{total_proj_cost:,.0f} VNĐ</b></div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
            st.divider()
            st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('CHI TIẾT TĂNG CA', '残業詳細')}</h3>", unsafe_allow_html=True)
        
            if employee_name_proj and employee_name_proj != opt_emp:
                st.info(f"{t('Đang tính cho nhân sự', '対象者')}: **{employee_name_proj}** | {t('Lương Gross', '総支給額')}: **{emp_gross:,.0f} VND** | {t('Ngày chuẩn', '所定労働日数')}: **{base.get('standard_days', 22.0)}**")
            else:
                st.info(t("Vui lòng chọn nhân sự ở trên để tiếp tục.", "上記でスタッフを選択してください。"))
            
            col_dlbl, col_dopt = st.columns([1.4, 8.6], gap="small")
            with col_dlbl:
                st.markdown(f"<div style='padding-top: 8px; font-weight: 600; color: #1e293b; font-size: 14.5px; white-space: nowrap;'>{t('Chế độ nhập ngày OT:', '残業日入力モード:')}</div>", unsafe_allow_html=True)
            with col_dopt:
                date_mode = st.radio(
                    t("Chế độ nhập ngày OT", "残業日入力モード"),
                    [t("📌 1 ngày đơn lẻ", "📌 単日入力"), t("📅 Nhập liên tục nhiều ngày (Dải ngày)", "📅 期間・連続入力")],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="ot_date_entry_mode"
                )
            
            target_dates = []
            if date_mode == t("📅 Nhập liên tục nhiều ngày (Dải ngày)", "📅 期間・連続入力"):
                date_range_val = st.date_input(
                    t("CHỌN DẢI NGÀY TĂNG CA (TỪ NGÀY - ĐẾN NGÀY)", "残業期間を選択 (開始日 - 終了日)"),
                    value=[datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2)],
                    key="ot_date_range_picker"
                )
                if isinstance(date_range_val, (list, tuple)) and len(date_range_val) == 2:
                    start_date, end_date = date_range_val[0], date_range_val[1]
                elif isinstance(date_range_val, (list, tuple)) and len(date_range_val) == 1:
                    start_date = end_date = date_range_val[0]
                else:
                    start_date = end_date = date_range_val if isinstance(date_range_val, datetime.date) else datetime.date.today()
                
                if start_date > end_date:
                    start_date, end_date = end_date, start_date
                
                raw_range_dates = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
                
                only_workdays = st.checkbox(
                    t("💼 Chỉ tạo cho Ngày đi làm hành chính (Bỏ qua Thứ 7, Chủ nhật & Ngày lễ)", "平日の残業のみ作成（土日・祝日を除外）"),
                    value=True,
                    key="ot_range_workdays_only"
                )
                
                holidays_list = []
                if not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
                    try:
                        holidays_list = pd.to_datetime(base['holidays_df']["Ngày nghỉ"], format='mixed', dayfirst=True).dt.date.tolist()
                    except:
                        pass
                
                for d in raw_range_dates:
                    is_h = (d in holidays_list)
                    is_w = (d.weekday() >= 5)
                    if d.weekday() == 5:
                        next_week = d + datetime.timedelta(days=7)
                        if next_week.month != d.month:
                            is_w = False
                    if only_workdays and (is_h or is_w):
                        continue
                    target_dates.append(d)
                
                if not target_dates:
                    target_dates = [start_date]
                ot_date = start_date
                calculated_period = get_payroll_period(start_date)
                
                date_preview_str = ", ".join(d.strftime("%d/%m") for d in target_dates[:8]) + ("..." if len(target_dates) > 8 else "")
                st.markdown(f"""
                    <div style='background-color: #f0f9ff; border: 1px dashed #00B0F0; border-radius: 6px; padding: 10px 14px; margin-bottom: 15px; font-size: 13.5px; color: #0369a1;'>
                        <b>{t('Sẽ tạo tự động cho', '自動作成対象')}: <span style='color: #00B0F0;'>{len(target_dates)} {t('ngày', '日')}</span></b> ({date_preview_str})
                    </div>
                """, unsafe_allow_html=True)
            else:
                ot_date = st.date_input(t("NGÀY THÁNG TĂNG CA", "残業日"))
                target_dates = [ot_date]
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
                    def get_val(h): return f"{h:.1f} h" + (" ←" if h > 0 else "")
                    with b_col1: st.metric("150%", get_val(auto_buckets[150]), help=f"{nt}: 17h-22h")
                    with b_col2: st.metric("200%", get_val(auto_buckets[200]), help=f"{nt}: 22h-24h\n{ct}: 08h-22h")
                    with b_col3: st.metric("270%", get_val(auto_buckets[270]), help=f"{ct}: 22h-24h")
                    with b_col4: st.metric("300%", get_val(auto_buckets[300]), help=f"{nl}: 17h-22h")
                    with b_col5: st.metric("400%", get_val(auto_buckets[400]), help=f"{nl}: 08h-17h")
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
                        holidays_for_loop = []
                        if not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
                            try: holidays_for_loop = base['holidays_df']['Ngày nghỉ'].tolist()
                            except: pass
                        for d_i in target_dates:
                            d_buckets = breakdown_ot_hours(d_i, total_hours_auto, holidays_for_loop)
                            d_period = get_payroll_period(d_i)
                            entry = {
                                "payment_period": d_period,
                                "project_type": project_type,
                                "order_id": order_id,
                                "client_order_id": client_order_id,
                                "order_name": clean_order_name,
                                "manager_name": manager_name,
                                "employee_name": employee_name_proj,
                                "ot_reason": ot_reason,
                                "ot_date": d_i.strftime("%d/%m/%Y"),
                                "ot_hours": total_hours_auto,
                                "hourly_rate": hourly_rate,
                            }
                            for mult, hrs in d_buckets.items():
                                if hrs > 0:
                                    res = calculate_ot_pay(emp_gross, std_days, hrs, mult)
                                    k_name = f"{int(mult)}%" if float(mult).is_integer() else f"{mult}%"
                                    entry[k_name] = int(res["ot_pay"])
                            st.session_state['ot_records'].append(entry)
                        if len(target_dates) > 1:
                            st.toast(f"{t('Đã thêm thành công', '追加完了！')} {len(target_dates)} {t('bản ghi OT liên tiếp!', '件の連続残業データ')}", icon=":material/check_circle:")
                        else:
                            st.toast(f"{t('Đã thêm bản ghi', 'レコード追加完了！')} ({total_hours_auto} {t('giờ', '時間')})", icon=":material/check_circle:")
                        st.rerun()

            with tab_manual:
                if 'manual_reset_key' not in st.session_state:
                    st.session_state['manual_reset_key'] = 0
                if 'manual_custom_rows' not in st.session_state or not isinstance(st.session_state['manual_custom_rows'], list):
                    st.session_state['manual_custom_rows'] = [{'id': 1, 'mult': 0.0, 'hrs': 0.0}]
                st.info(t("Bạn tự gõ số giờ tương ứng vào từng rổ hệ số. Nếu không có phát sinh, vui lòng để trống hoặc bằng 0.", "各係数の時間を手動で入力してください。発生しない場合は0 hoặc bằng 0."))
                st.markdown(
                    f"""
                    <style>
                    /* Hide marker containers completely so they take 0 space */
                    div.element-container:has(.custom-blue-card-std),
                    div.element-container:has(.custom-blue-card-custom) {{
                        display: none !important;
                        height: 0px !important;
                        margin: 0px !important;
                        padding: 0px !important;
                    }}

                    /* Outer container wrapper gets the rich blue gradient, rounded border and shadow */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std),
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom),
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)),
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) {{
                        background-color: #00B0F0 !important;
                        border: 1.5px solid rgba(255, 255, 255, 0.4) !important;
                        border-radius: 12px !important;
                        padding: 14px 20px 10px 20px !important;
                        margin-bottom: 16px !important;
                        box-shadow: 0 6px 18px rgba(0, 176, 240, 0.25) !important;
                    }}

                    /* Strip inner stBorder and inner stVerticalBlock when border=True is used so there is NO double border or white box inside */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stBorder"],
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stBorder"],
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div.stBorder,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div.stBorder {{
                        background: transparent !important;
                        border: none !important;
                        box-shadow: none !important;
                        padding: 0px !important;
                    }}

                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stVerticalBlock"],
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stVerticalBlock"] {{
                        background: transparent !important;
                        border: none !important;
                        box-shadow: none !important;
                        padding: 0px !important;
                        gap: 6px !important;
                    }}

                    /* Tighten vertical spacing between internal elements inside both blue cards */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stElementContainer"],
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stElementContainer"],
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stElementContainer"],
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stElementContainer"] {{
                        margin-bottom: 0px !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stElementContainer"]:has(hr),
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stElementContainer"]:has(hr),
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stElementContainer"]:has(hr),
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stElementContainer"]:has(hr) {{
                        margin-top: -4px !important;
                        margin-bottom: -4px !important;
                    }}

                    /* Ensure all title & general text inside both blue cards is pure white */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) *,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) * {{
                        color: #ffffff !important;
                    }}

                    /* Ensure horizontal lines hr inside both blue cards are pure white */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) hr,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) hr,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) hr,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) hr {{
                        border: 0 !important;
                        border-top: 1px solid #ffffff !important;
                        opacity: 1 !important;
                        background: transparent !important;
                    }}

                    /* Keep Number Input boxes crisp white with dark navy text so inputs are clear and readable */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] input,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] input,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] input,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] input {{
                        background-color: #ffffff !important;
                        color: #0f172a !important;
                        border: 1.5px solid #cbd5e1 !important;
                        border-radius: 6px !important;
                        font-weight: normal !important;
                    }}

                    /* Number input +/- buttons inside the blue cards */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button {{
                        background-color: #f8fafc !important;
                        color: #0f172a !important;
                        border: none !important;
                        font-weight: normal !important;
                        transition: all 0.2s ease !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button *,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button *,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button svg,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button svg,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button svg,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button svg,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button path,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button path,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button path,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button path {{
                        color: #0f172a !important;
                        fill: #0f172a !important;
                        stroke: none !important;
                        font-weight: normal !important;
                        stroke-width: 0 !important;
                    }}

                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button:hover,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button:hover,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button:hover,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button:hover {{
                        background-color: #e2e8f0 !important;
                        color: #000000 !important;
                        border: none !important;
                        font-weight: normal !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button:hover *,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button:hover *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button:hover *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button:hover *,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button:hover svg,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button:hover svg,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button:hover svg,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button:hover svg,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stNumberInput"] button:hover path,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stNumberInput"] button:hover path,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div[data-testid="stNumberInput"] button:hover path,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stNumberInput"] button:hover path {{
                        color: #000000 !important;
                        fill: #000000 !important;
                        stroke: none !important;
                        font-weight: normal !important;
                        stroke-width: 0 !important;
                    }}

                    /* Compact Reset Button inside Card 1 ONLY */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div.stButton button,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div.stButton button {{
                        text-transform: none !important;
                        min-height: 28px !important;
                        height: 28px !important;
                        padding: 2px 14px !important;
                        font-size: 12px !important;
                        border-radius: 6px !important;
                        margin-top: -6px !important;
                        margin-bottom: 0px !important;
                        border: 1.5px solid #ffffff !important;
                        background-color: #ffffff !important;
                        color: #00B0F0 !important;
                        line-height: 1 !important;
                        box-shadow: none !important;
                        transition: all 0.2s ease !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div[data-testid="stColumn"]:nth-child(2) div[data-testid="stElementContainer"] {{
                        margin-top: -6px !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div.stButton button *,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div.stButton button:hover *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div.stButton button *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div.stButton button:hover * {{
                        color: #00B0F0 !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div.stButton button:hover,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div.stButton button:hover {{
                        background-color: #ffffff !important;
                        color: #0075a0 !important;
                        border-color: #ffffff !important;
                        transform: translateY(-2px) !important;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-std) div.stButton button:hover *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-std):not(:has(.custom-blue-card-custom)) div.stButton button:hover * {{
                        color: #0075a0 !important;
                    }}

                    /* Compact Delete Icon Button inside Card 2 Column 3 ONLY */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stColumn"]:nth-child(3) div.stButton button,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stColumn"]:nth-child(3) div.stButton button {{
                        min-height: 36px !important;
                        height: 36px !important;
                        width: 38px !important;
                        min-width: 38px !important;
                        padding: 0 !important;
                        font-size: 14px !important;
                        border-radius: 6px !important;
                        margin-top: 0px !important;
                        border: 1.5px solid #ffffff !important;
                        background-color: #ffffff !important;
                        color: #ef4444 !important;
                        box-shadow: none !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        transition: all 0.2s ease !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stColumn"]:nth-child(3) div.stButton button *,
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stColumn"]:nth-child(3) div.stButton button:hover *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stColumn"]:nth-child(3) div.stButton button *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stColumn"]:nth-child(3) div.stButton button:hover * {{
                        color: #ef4444 !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stColumn"]:nth-child(3) div.stButton button:hover,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stColumn"]:nth-child(3) div.stButton button:hover {{
                        background-color: #ef4444 !important;
                        color: #ffffff !important;
                        border-color: #ffffff !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stColumn"]:nth-child(3) div.stButton button:hover *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div[data-testid="stColumn"]:nth-child(3) div.stButton button:hover * {{
                        color: #ffffff !important;
                    }}

                    /* Compact "+ Thêm dòng hệ số tùy chỉnh" button inside Card 2 ONLY */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button {{
                        min-height: 34px !important;
                        height: 34px !important;
                        padding: 4px 16px !important;
                        font-size: 13px !important;
                        border-radius: 6px !important;
                        margin-top: -2px !important;
                        border: 1.5px solid #ffffff !important;
                        background-color: #ffffff !important;
                        color: #00B0F0 !important;
                        box-shadow: none !important;
                        transition: all 0.2s ease !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div[data-testid="stElementContainer"]:has(div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton)) {{
                        margin-top: -4px !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button * {{
                        color: #00B0F0 !important;
                        font-size: 13px !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button:hover,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button:hover {{
                        background-color: #ffffff !important;
                        color: #0075a0 !important;
                        border-color: #ffffff !important;
                        transform: translateY(-2px) !important;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
                    }}
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-blue-card-custom) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button:hover *,
                    div[data-testid="stVerticalBlock"]:has(.custom-blue-card-custom):not(:has(.custom-blue-card-std)) div.stButton:not(div[data-testid="stColumn"]:nth-child(3) div.stButton) button:hover * {{
                        color: #0075a0 !important;
                    }}

                    /* Ensure Live summary icons are dark green (#166534) and override global blue icon styles */
                    div.live-summary-box .material-symbols-rounded,
                    div.live-summary-box span.material-symbols-rounded,
                    [data-testid="stMainBlockContainer"] div.live-summary-box .material-symbols-rounded {{
                        color: #166534 !important;
                    }}

                    /* Default state when Live Summary is NOT visible: move + THÊM VÀO BẢNG CHỜ XUẤT up close under Card 2 */
                    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(div.stButton > button) {{
                        margin-top: 4px !important;
                    }}

                    /* When Live Summary box is rendered above the button, automatically push the button down */
                    div[data-testid="stElementContainer"]:has(.live-summary-box) ~ div[data-testid="stElementContainer"]:has(div.stButton > button) {{
                        margin-top: 24px !important;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                with st.container(border=True):
                    st.markdown("<span class='custom-blue-card-std' style='display:none; position:absolute;'></span>", unsafe_allow_html=True)
                    c_title, c_reset = st.columns([7.5, 2.5])
                    with c_title:
                        st.markdown(f"<div style='font-size: 15px; font-weight: 600; text-transform: uppercase; color: #ffffff; margin-top: 2px; display: flex; align-items: center;'><span class='material-symbols-rounded' style='font-size: 20px; margin-right: 6px;'>bolt</span> {t('CÁC RỔ HỆ SỐ CHUẨN (150% - 400%)', '標準係数 (150% - 400%)')}</div>", unsafe_allow_html=True)
                    with c_reset:
                        if st.button(t(":material/refresh: Làm mới rổ giờ", ":material/refresh: リセット"), key=f"btn_reset_manual_{st.session_state['manual_reset_key']}"):
                            st.session_state['manual_reset_key'] += 1
                            st.session_state['manual_custom_rows'] = [{'id': 1, 'mult': 0.0, 'hrs': 0.0}]
                            st.rerun()
                    
                    st.markdown("<hr style='margin: 2px 0 6px 0 !important; border: 0 !important; border-top: 1px solid #ffffff !important; opacity: 1 !important;'>", unsafe_allow_html=True)
                    rk = st.session_state['manual_reset_key']
                    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
                    with m_col1: h_150 = st.number_input(t("Số giờ 150%", "150% 時間"), min_value=0.0, step=0.1, format="%.1f", key=f"h150_{rk}")
                    with m_col2: h_200 = st.number_input(t("Số giờ 200%", "200% 時間"), min_value=0.0, step=0.1, format="%.1f", key=f"h200_{rk}")
                    with m_col3: h_270 = st.number_input(t("Số giờ 270%", "270% 時間"), min_value=0.0, step=0.1, format="%.1f", key=f"h270_{rk}")
                    with m_col4: h_300 = st.number_input(t("Số giờ 300%", "300% 時間"), min_value=0.0, step=0.1, format="%.1f", key=f"h300_{rk}")
                    with m_col5: h_400 = st.number_input(t("Số giờ 400%", "400% 時間"), min_value=0.0, step=0.1, format="%.1f", key=f"h400_{rk}")

                with st.container(border=True):
                    st.markdown("<span class='custom-blue-card-custom' style='display:none; position:absolute;'></span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 15px; font-weight: 600; text-transform: uppercase; color: #ffffff; margin-top: 2px; margin-bottom: 6px; display: flex; align-items: center;'><span class='material-symbols-rounded' style='font-size: 20px; margin-right: 6px;'>tune</span> {t('CÁC RỔ HỆ SỐ KHÁC (TUỲ CHỈNH - NHIỀU DÒNG)', 'その他係数（カスタム・複数行対応）')}</div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 2px 0 6px 0 !important; border: 0 !important; border-top: 1px solid #ffffff !important; opacity: 1 !important;'>", unsafe_allow_html=True)
                    
                    
                    updated_custom_rows = []
                    rows_to_delete = []
                    for i, row in enumerate(st.session_state['manual_custom_rows']):
                        row_id = row['id']
                        rc1, rc2, rc3 = st.columns([4.4, 4.4, 1.2])
                        with rc1:
                            val_mult = st.number_input(
                                t(f"Hệ số tuỳ chỉnh #{i+1} (%)", f"カスタム係数 #{i+1} (%)"),
                                min_value=0.0, step=10.0, value=float(row.get('mult', 0.0)),
                                key=f"cust_mult_{row_id}_{rk}"
                            )
                        with rc2:
                            val_hrs = st.number_input(
                                t(f"Số giờ cho hệ số #{i+1}", f"時間数 #{i+1}"),
                                min_value=0.0, step=0.1, format="%.1f", value=float(row.get('hrs', 0.0)),
                                key=f"cust_hrs_{row_id}_{rk}"
                            )
                        with rc3:
                            st.markdown("<div style='height: 31px;'></div>", unsafe_allow_html=True)
                            if st.button(":material/delete:", key=f"del_cust_{row_id}_{rk}", help=t("Xóa dòng này", "この行を削除")):
                                rows_to_delete.append(row_id)
                        
                        updated_custom_rows.append({'id': row_id, 'mult': val_mult, 'hrs': val_hrs})
                    
                    if rows_to_delete:
                        st.session_state['manual_custom_rows'] = [r for r in updated_custom_rows if r['id'] not in rows_to_delete]
                        if not st.session_state['manual_custom_rows']:
                            st.session_state['manual_custom_rows'] = [{'id': 1, 'mult': 0.0, 'hrs': 0.0}]
                        st.rerun()
                    else:
                        st.session_state['manual_custom_rows'] = updated_custom_rows
                    
                    if st.button(t(":material/add_circle: Thêm dòng hệ số tùy chỉnh", ":material/add_circle: カスタム係数を追加"), key=f"add_cust_row_{rk}"):
                        max_id = max([r['id'] for r in st.session_state['manual_custom_rows']], default=0) + 1
                        st.session_state['manual_custom_rows'].append({'id': max_id, 'mult': 0.0, 'hrs': 0.0})
                        st.rerun()
            
                std_days = float(base.get('standard_days', 22.0))
                std_hrs = float(base.get('standard_hours_per_day', 8.0))
                hourly_rate_est = (emp_gross / std_days / std_hrs) if (std_days > 0 and std_hrs > 0) else 0
                
                bucket_inputs = {150: h_150, 200: h_200, 270: h_270, 300: h_300, 400: h_400}
                for crow in st.session_state['manual_custom_rows']:
                    cmult = crow.get('mult', 0.0)
                    chrs = crow.get('hrs', 0.0)
                    if chrs > 0 and cmult > 0:
                        bucket_inputs[cmult] = bucket_inputs.get(cmult, 0.0) + chrs

                manual_total = sum(bucket_inputs.values())
                est_cost_manual = sum(hrs * (mult / 100.0) * hourly_rate_est for mult, hrs in bucket_inputs.items() if hrs > 0)
                avg_mult = (sum(hrs * mult for mult, hrs in bucket_inputs.items() if hrs > 0) / manual_total) if manual_total > 0 else 0.0
                
                if manual_total > 0:
                    st.markdown(
                        f"""
                        <div class='live-summary-box' style='margin-top: -10px !important; margin-bottom: 18px !important; padding: 12px 18px; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1.5px solid #86efac; border-radius: 10px; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.1);'>
                            <div style='font-size: 14px; font-weight: 600; color: #166534; margin-bottom: 6px; display: flex; align-items: center;'>
                                <span class='material-symbols-rounded' style='font-size: 20px; margin-right: 6px; color: #166534 !important;'>analytics</span> {t('BẢNG TỔNG HỢP SỐ LIỆU OT DỰ TÍNH', '残業集計・予想コストプレビュー')}
                            </div>
                            <div style='display: flex; flex-wrap: wrap; gap: 24px; font-size: 13.5px; color: #15803d;'>
                                <div style='display: flex; align-items: center;'><span class='material-symbols-rounded' style='font-size: 18px; margin-right: 4px; color: #166534 !important;'>schedule</span> {t('Tổng số giờ:', '残業時間合計:')} &nbsp;<strong style='font-size: 15px; color: #166534;'>{manual_total:.1f} h</strong></div>
                                <div style='display: flex; align-items: center;'><span class='material-symbols-rounded' style='font-size: 18px; margin-right: 4px; color: #166534 !important;'>trending_up</span> {t('Hệ số trung bình:', '平均係数:')} &nbsp;<strong style='font-size: 15px; color: #166534;'>{avg_mult:.1f}%</strong></div>
                                <div style='display: flex; align-items: center;'><span class='material-symbols-rounded' style='font-size: 18px; margin-right: 4px; color: #166534 !important;'>payments</span> {t('Dự tính chi phí:', '予想コスト:')} &nbsp;<strong style='font-size: 15px; color: #166534;'>{est_cost_manual:,.0f} VNĐ</strong></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if manual_total > 16.0:
                        st.markdown(
                            f"<div style='margin-bottom: 15px; padding: 10px 14px; background-color: #fef9c3; border-left: 4px solid #eab308; border-radius: 6px; color: #854d0e; font-size: 13.5px; display: flex; align-items: center;'><span class='material-symbols-rounded' style='font-size: 20px; margin-right: 6px;'>warning</span> <div><strong>{t('Cảnh báo an toàn:', '注意:')}</strong> {t(f'Tổng số giờ OT trong ngày đang là <b>{manual_total:.1f} giờ</b> (vượt ngưỡng 16 giờ/ngày). Vui lòng kiểm tra lại dấu chấm/phẩy trước khi thêm!', f'1日の残業合計が<b>{manual_total:.1f}時間</b>に達しています。入力内容をご確認ください！')}</div></div>",
                            unsafe_allow_html=True
                        )
            
                if st.button(t("➕ THÊM VÀO BẢNG CHỜ XUẤT - THỦ CÔNG", "➕ 手動追加"), key="btn_manual"):
                    if employee_name_proj == opt_emp:
                        st.error(t("Vui lòng chọn nhân sự làm việc!", "スタッフを選択してください！"))
                    elif manual_total <= 0:
                        st.error(t("Vui lòng nhập ít nhất một trường thời gian lớn hơn 0!", "1つ以上の時間を入力してください！"))
                    else:
                        add_to_history("reasons", ot_reason)
                        std_days = float(base.get('standard_days', 22.0))
                        hourly_rate = int(emp_gross / std_days / 8) if std_days > 0 else 0
                    
                        for d_i in target_dates:
                            d_period = get_payroll_period(d_i)
                            entry = {
                                "payment_period": d_period,
                                "project_type": project_type,
                                "order_id": order_id,
                                "client_order_id": client_order_id,
                                "order_name": clean_order_name,
                                "manager_name": manager_name,
                                "employee_name": employee_name_proj,
                                "ot_reason": ot_reason,
                                "ot_date": d_i.strftime("%d/%m/%Y"),
                                "ot_hours": manual_total,
                                "hourly_rate": hourly_rate,
                            }
                            for mult, hrs in bucket_inputs.items():
                                if hrs > 0:
                                    res = calculate_ot_pay(emp_gross, std_days, hrs, mult)
                                    k_name = f"{int(mult)}%" if float(mult).is_integer() else f"{mult}%"
                                    entry[k_name] = int(res["ot_pay"])
                            st.session_state['ot_records'].append(entry)
                        
                        if len(target_dates) > 1:
                            st.toast(f"{t('Đã thêm thủ công', '手動追加完了！')} {len(target_dates)} {t('bản ghi cho dải ngày!', '件の連続残業データ')}", icon=":material/check_circle:")
                        else:
                            st.toast(t("Đã thêm bản ghi thủ công!", "手動レコード追加完了！"), icon=":material/check_circle:")
                        st.rerun()

            if len(st.session_state['ot_records']) > 0:
                st.markdown("""
                <span id="ot-records-top-divider-anchor"></span>
                <style>
                /* Pull the hr top divider closer up to the buttons above */
                div.element-container:has(#ot-records-top-divider-anchor) {
                    margin-top: -24px !important;
                    margin-bottom: -12px !important;
                }
                /* Pull the BẢNG DỮ LIỆU ĐÃ NHẬP header container up closer to the divider */
                div.element-container:has(#ot-records-top-divider-anchor) + div.element-container {
                    margin-top: -12px !important;
                }
                </style>
                <hr class="custom-hr-divider" style="margin: 4px 0 4px 0 !important; border: 0; border-top: 1.5px solid #94a3b8 !important;">
                """, unsafe_allow_html=True)
                st.markdown(
                    f"<span id='ot-records-table-header-anchor'></span>"
                    f"<style>"
                    f"div.element-container:has(#ot-records-table-header-anchor) ~ div.element-container:has([data-testid='stDataFrame']) {{"
                    f"    margin-top: -24px !important;"
                    f"}}"
                    f"div.element-container:has(#ot-records-table-header-anchor) ~ div.element-container:has([data-testid='stDataFrame']) [data-testid='stDataFrame'] {{"
                    f"    padding-top: 22px !important;"
                    f"}}"
                    f"div.element-container:has(#ot-records-table-header-anchor) ~ div.element-container:has([data-testid='stDataFrame']) [data-testid='stElementToolbar'] {{"
                    f"    top: -28px !important;"
                    f"}}"
                    f"</style>"
                    f"<h3 style='font-size: 20px; font-weight: 600; margin: 0 0 4px 0;'>{t('BẢNG DỮ LIỆU ĐÃ NHẬP', '入力済みデータ一覧')}</h3>"
                    f"<div style='font-size: 13.5px; color: #64748b; margin-bottom: 4px;'>{t('Bấm vào các ô để chỉnh sửa. Chọn dòng và ấn Delete để xóa.', 'セルをクリックして編集。行を選択してDeleteで削除。')}</div>",
                    unsafe_allow_html=True
                )
            
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
                    "standard_days": st.column_config.NumberColumn(t("Số ngày chuẩn", "基準日数")),
                    "gross_salary": st.column_config.NumberColumn(t("Lương Gross", "総支給額")),
                }
            
                for key in df.columns:
                    if key.endswith("%"):
                        col_cfg[key] = st.column_config.NumberColumn(f"{t('Tiền', '金額')} {key}", format="%,.0f")
                def color_ot_cols(s):
                    name = str(s.name)
                    if "150" in name:
                        return ['background-color: #e8f5e9; color: #2e7d32; font-weight: bold;'] * len(s)
                    elif "200" in name:
                        return ['background-color: #fff3e0; color: #ef6c00; font-weight: bold;'] * len(s)
                    elif "270" in name:
                        return ['background-color: #ffe0b2; color: #e65100; font-weight: bold;'] * len(s)
                    elif "300" in name or "400" in name:
                        return ['background-color: #ffebee; color: #c62828; font-weight: bold;'] * len(s)
                    return [''] * len(s)
                
                styled_df = df.style.apply(color_ot_cols, axis=0)
                        
                edited_df = st.data_editor(
                    styled_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="ot_records_editor",
                    column_config=col_cfg
                )
                st.session_state['ot_records'] = edited_df.to_dict('records')
            
                st.markdown("""
                <style>
                /* Pull the hr divider closer under the table cleanly without overlapping */
                div.element-container:has(#ot-table-bottom-divider) {
                    margin-top: -6px !important;
                    margin-bottom: 0px !important;
                }
                /* Ensure caption Note sits cleanly right below hr with zero overlap */
                div.element-container:has(#ot-table-bottom-divider) + div.element-container {
                    margin-top: 0px !important;
                    margin-bottom: 0px !important;
                }
                /* Ensure action row sits right cleanly below caption Note */
                div.element-container:has(#ot-table-bottom-divider) ~ div.element-container:has([data-testid="stHorizontalBlock"]) {
                    margin-top: -4px !important;
                }
                </style>
                <div id="ot-table-bottom-divider" class="custom-hr-divider" style="margin: 8px 0 10px 0; border-top: 1.5px solid #94a3b8 !important;"></div>
                """, unsafe_allow_html=True)
                st.caption(t("📌 **Lưu ý:** Bạn cần bấm nút **Lưu Dữ Liệu** thì Bảng xếp hạng mới được cập nhật.", "📌 **注意:** ランキングを更新するには「データ保存」ボタンを押してください。"))
                c_name, c_save, c_dl, c_del = st.columns([3.5, 2.0, 2.0, 2.5])
                with c_name:
                    default_name = t("Bảng tổng hợp tăng ca (OT).xlsx", "残業計算結果_OT.xlsx")
                    export_name = st.text_input("📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), value=default_name, key=f"ot_manual_filename_{st.session_state.get('lang', 'VN')}")
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

