import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from logic.incentive import calculate_incentive, generate_incentive_excel
from logic.action_log import save_action_log
from logic.exchange_rate import get_jpy_to_vnd_rate
from logic.history import get_history
from logic.i18n import t

def render_incentive():
    from components.ot_manual import init_session_state
    init_session_state()
    col_main, col_rank = st.columns([7.5, 2.5], gap="large")
    with col_rank:
        from components.mini_leaderboard import render_mini_leaderboard
        render_mini_leaderboard("incentive")
        
        if 'last_incentive_calc' in st.session_state:
            result_rk = st.session_state['last_incentive_calc']
            inputs_rk = st.session_state['last_incentive_inputs']
            
            st.markdown("<div style='height: 45px;'></div>", unsafe_allow_html=True)
            
            with st.container():
                from components.ui_utils import make_container_white
                make_container_white()
                
                exp_rev = inputs_rk['target_hours'] * inputs_rk['unit_price']
                act_cost = inputs_rk['actual_hours'] * inputs_rk['company_charge']
                p_val = result_rk['profit']
                
                border_color = "#00B0F0"
                title_text = t('DÒNG TIỀN DỰ ÁN', 'キャッシュフロー')
                st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        border-radius: 8px;
                        border-top: 4px solid {border_color};
                        padding: 10px;
                        margin-bottom: 15px;
                        text-align: center; color: #2c3e50; font-size: 16px; font-weight: bold; text-transform: uppercase;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                        font-family: "Times New Roman", serif;
                    '>
                        <span class="material-symbols-rounded" style="vertical-align: middle; color: {border_color}; margin-right: 5px; font-size: 20px;">waterfall_chart</span>
                        <span style="vertical-align: middle;">{title_text}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                fig = go.Figure(go.Waterfall(
                    name = "Cashflow", orientation = "v",
                    measure = ["relative", "relative", "total"],
                    x = [t("Doanh thu", "売上"), t("Chi phí", "コスト"), t("Lợi nhuận", "利益")],
                    textposition = "outside",
                    text = [f"+{exp_rev:,.0f}", f"-{act_cost:,.0f}", f"{p_val:,.0f}"],
                    textfont=dict(family="'Times New Roman', serif", size=11, color="#333", weight="bold"),
                    y = [exp_rev, -act_cost, 0],
                    connector = {"line":{"color":"rgba(0,0,0,0.15)", "width": 1, "dash": "dot"}},
                    decreasing = {"marker":{"color":"rgba(255, 107, 107, 0.85)", "line":{"color":"#ff6b6b", "width":1}}},
                    increasing = {"marker":{"color":"rgba(0, 176, 240, 0.85)", "line":{"color":"#00B0F0", "width":1}}},
                    totals = {"marker":{"color":"rgba(32, 201, 151, 0.85)" if p_val >= 0 else "rgba(255, 107, 107, 0.85)", "line":{"color":"#20c997" if p_val >= 0 else "#ff6b6b", "width":1}}},
                    hovertemplate="<b>%{x}</b><br>Giá trị: %{text}<extra></extra>"
                ))
                
                fig.update_layout(
                    font=dict(family="'Times New Roman', serif"),
                    showlegend=False,
                    height=260,
                    bargap=0.3,
                    margin=dict(l=5, r=5, t=10, b=20),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(showgrid=False, zeroline=True, zerolinecolor="rgba(0,0,0,0.1)", zerolinewidth=1, showticklabels=False),
                    xaxis=dict(showgrid=False, tickfont=dict(family="'Times New Roman', serif", size=11, color="#2c3e50", weight="bold")),
                    hoverlabel=dict(bgcolor="white", font_size=12, font_family="'Times New Roman', serif")
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                with st.expander(t(":material/info: Cách đọc biểu đồ", ":material/info: チャートの見方")):
                    st.markdown(f"""
                    <style>
                    div[data-testid="stExpander"] details summary p span {{
                        color: #00B0F0 !important;
                    }}
                    </style>
                    <div style="color: #5f6368; font-size: 13px; line-height: 1.6; font-family: 'Times New Roman', serif; margin-top: -10px; padding-bottom: 5px;">
                        • <b>Doanh thu:</b> {t('(Kế hoạch) x (Đơn giá). Là khoản tiền công ty tính với khách hàng.', '(目標工数) x (単価)。顧客に請求する金額。')}<br>
                        • <b>Chi phí:</b> {t('(Thực tế) x (Charge). Là chi phí nội bộ công ty dùng để vận hành dự án.', '(実工数) x (会社運用費)。プロジェクトの内部運用コスト。')}<br>
                        • <b>Lợi nhuận:</b> {t('(Doanh thu) - (Chi phí). Cột <b style="color:#20c997">Xanh</b> là lãi, cột <b style="color:#ff6b6b">Đỏ</b> là lỗ. Quỹ Incentive được trích từ đây.', '利益 = (売上) - (コスト)。<b style="color:#20c997">緑</b>は黒字、<b style="color:#ff6b6b">赤</b>は赤字。')}
                    </div>
                    """, unsafe_allow_html=True)
    with col_main:
        if 'incentive_records' not in st.session_state:
            st.session_state['incentive_records'] = []
        
        title = t("Tính Incentive (JPY)", "インセンティブ計算")
        st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
        st.info(t("Nhập các thông số dự án bên dưới để tính toán và lưu vào bảng chờ xuất.", "以下にプロジェクトのパラメータを入力して計算し、出力待ちリストに保存してください。"), icon="💡")
    
        # Collect data for dropdowns
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
    
        combined_employees = list(dict.fromkeys(master_employees))
    
        with st.container():
            from components.ui_utils import make_container_white
            make_container_white()
            st.markdown(f"""
                <style>
                /* Force all Material icons inside widget labels to be UI blue */
                [data-testid="stWidgetLabel"] p span.material-symbols-rounded,
                [data-testid="stWidgetLabel"] p span.st-icon,
                [data-testid="stWidgetLabel"] p span[translate="no"] {{
                    color: #00B0F0 !important;
                }}
                </style>
                <h3 style='font-size: 18px; font-weight: 600; margin-top: -10px; margin-bottom: 25px;'>{t('1. Thông tin Dự án', '1. プロジェクト情報')}</h3>
            """, unsafe_allow_html=True)
            col_info1, col_info2, col_info3 = st.columns(3)
        
            with col_info1:
                record_date = st.date_input(t(":material/calendar_today: Ngày ghi nhận", ":material/calendar_today: 記録日"), value=datetime.date.today(), format="DD/MM/YYYY")
            
            with col_info2:
                opt_choose_proj = t("--- Chọn dự án ---", "--- 案件名を選択 ---")
                proj_opts = [opt_choose_proj] + combined_projects
                sel_proj = st.selectbox(t(":material/work: Tên dự án", ":material/work: 案件名"), proj_opts)
            
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
                sel_emp = st.selectbox(t(":material/person: Người thực hiện", ":material/person: 担当者"), emp_opts)
            
                if sel_emp == opt_choose_emp:
                    employee_name = ""
                else:
                    employee_name = sel_emp
        
            st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px; margin-bottom: 25px;'>{t('2. Thông số Tính toán', '2. 計算パラメータ')}</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                target_hours = st.number_input(t(":material/track_changes: Giờ công kế hoạch", ":material/track_changes: 目標工数"), min_value=0.0, step=1.0, format="%f")
                actual_hours = st.number_input(t(":material/timer: Giờ công thực tế", ":material/timer: 実工数"), min_value=0.0, step=1.0, format="%f")
        
            with col2:
                unit_price = st.number_input(t(":material/payments: Đơn giá", ":material/payments: 単価"), min_value=0.0, step=1000.0, format="%f")
                company_charge = st.number_input(t(":material/domain: Company Charge", ":material/domain: 会社運用チャージ"), min_value=0.0, step=100.0, format="%f")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.divider()
            
            # Ước tính nhanh (What-if)
            c_title, c_sl, c_res = st.columns([1.5, 3.5, 1.5], vertical_alignment="center")
            with c_title:
                help_text = t("Kéo thanh trượt bên cạnh để mô phỏng và xem trước số tiền Incentive nhận được khi thay đổi Giờ công thực tế.", "スライダーを動かして、実工数の変化に伴う獲得インセンティブの変動をシミュレーションします。")
                st.markdown(f"<span style='color: #5f6368; font-weight: 600; font-size: 15px;'><span class='material-symbols-rounded' style='vertical-align: -4px; margin-right: 5px; font-size: 18px;'>lightbulb</span> {t('Ước tính Incentive', '予想インセンティブ')}</span>", help=help_text, unsafe_allow_html=True)
            with c_sl:
                max_slider = float(target_hours * 1.5) if target_hours > 0 else 100.0
                if actual_hours > max_slider: max_slider = float(actual_hours * 1.5)
                max_slider = max(max_slider, 10.0) # Ensure max > min
                whatif_hours = st.slider("Slider", min_value=0.0, max_value=max_slider, value=float(actual_hours), step=0.5, format="%f", key="whatif_slider", label_visibility="collapsed")
            with c_res:
                preview_dict = calculate_incentive(target_hours, whatif_hours, unit_price, company_charge)
                preview_val = preview_dict.get("final_incentive", 0)
                color = "#00B0F0" if preview_val > 0 else "#95a5a6"
                st.markdown(f"<div style='text-align: right;'><b style='font-size: 22px; color: {color};'>{preview_val:,.0f}</b> <span style='font-size: 13px; color: {color};'>JPY</span></div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
        from components.ui_utils import render_empty_state
        if st.button(t("Tính Incentive", "インセンティブ計算"), type="primary", use_container_width=True):
            result = calculate_incentive(target_hours, actual_hours, unit_price, company_charge)
            st.session_state['last_incentive_calc'] = result
            st.session_state['last_incentive_inputs'] = {
                "date": record_date.strftime("%d/%m/%Y"),
                "project_name": clean_project_name,
                "employee_name": employee_name,
                "target_hours": target_hours,
                "actual_hours": actual_hours,
                "unit_price": unit_price,
                "company_charge": company_charge
            }
            st.session_state['just_calculated_incentive'] = True
            st.rerun()
        
        if 'last_incentive_calc' in st.session_state:
            result = st.session_state['last_incentive_calc']
            inputs = st.session_state['last_incentive_inputs']
        
            col_title, col_clear = st.columns([7.5, 2.5])
            with col_title:
                st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px; margin-bottom: 0;'>{t('3. Kết quả & Phân tích', '3. 結果と分析')}</h3>", unsafe_allow_html=True)
            with col_clear:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                if st.button(":material/delete: " + t("Xóa kết quả này", "結果をクリア"), use_container_width=True, key="clear_incentive_result"):
                    if 'last_incentive_calc' in st.session_state:
                        del st.session_state['last_incentive_calc']
                    if 'last_incentive_inputs' in st.session_state:
                        del st.session_state['last_incentive_inputs']
                    st.rerun()
            col3, col4, col5 = st.columns(3)
            col3.metric(t("Lợi Nhuận", "利益"), f"{result['profit']:,.0f} JPY")
            col4.metric(t("Incentive Tiêu Chuẩn", "基準金額"), f"{result['standard_incentive']:,.0f} JPY")
        
            delta_val = t("Thưởng", "ボーナス") if result['final_incentive'] > 0 else t("Không đạt", "未達成") if result['final_incentive'] <= 0 else None
            col5.metric(t("Incentive Nhận Được", "スタッフ受取額"), f"{result['final_incentive']:,.0f} JPY", delta=delta_val)
        
            # Display converted VND amount
            try:
                rate = get_jpy_to_vnd_rate()
                vnd_amount = result['final_incentive'] * rate
                if result['final_incentive'] > 0:
                    col5.caption(f"≈ **{vnd_amount:,.0f} VND** ({t('Tỷ giá', 'レート')}: 1 JPY = {rate:,.1f} VND)")
            except:
                pass

            # Add to List button
            if st.button(t("➕ Thêm vào Danh sách Chờ xuất", "➕ リストに追加")):
                if not inputs['project_name'] or not inputs['employee_name']:
                    st.error(t("Vui lòng nhập Tên dự án và Người thực hiện!", "案件名と担当者を入力してください！"))
                else:
                    st.session_state['incentive_records'].append({**inputs, **result})
                    st.session_state['pending_toast'] = t("Đã thêm vào danh sách!", "リストに追加しました！")
                    st.rerun()
                
        if st.session_state.get('incentive_records') and len(st.session_state['incentive_records']) > 0:
            if True:
                st.markdown("---")
                st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('BẢNG DỮ LIỆU CHỜ XUẤT', '出力待ちデータ一覧')}</h3>", unsafe_allow_html=True)
            
                df_records = pd.DataFrame(st.session_state['incentive_records'])
            
                # Mapping to beautiful column names for display
                display_map = {
                    "date": t("Ngày", "日"),
                    "project_name": t("Dự án", "案件名"),
                    "employee_name": t("Nhân sự", "担当者"),
                    "target_hours": t("KH / Mục tiêu (h)", "目標 (h)"),
                    "actual_hours": t("TT / Thực tế (h)", "実績 (h)"),
                    "unit_price": t("Đơn giá", "単価"),
                    "company_charge": t("Charge", "ﾁｬｰｼﾞ"),
                    "profit": t("Lợi nhuận", "利益"),
                    "standard_incentive": t("Incentive TC", "基準金額"),
                    "final_incentive": t("Nhận được", "受取額")
                }
            
                df_display = df_records.rename(columns=display_map)
            
                # Format numbers with commas for display
                format_cols = [t("Đơn giá", "単価"), t("Charge", "ﾁｬｰｼﾞ"), t("Lợi nhuận", "利益"), t("Incentive TC", "基準金額"), t("Nhận được", "受取額")]
                for col in format_cols:
                    if col in df_display.columns:
                        df_display[col] = pd.to_numeric(df_display[col], errors='coerce').apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
            
                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                edited_df = st.data_editor(
                    df_display,
                    use_container_width=True,
                    num_rows="dynamic",
                    disabled=[t("Lợi nhuận", "利益"), t("Incentive TC", "基準金額"), t("Nhận được", "受取額")]
                )
            
                # Sync back edited df
                if not edited_df.equals(df_display):
                    # Convert strings back to numbers before saving
                    for col in format_cols:
                        if col in edited_df.columns:
                            edited_df[col] = edited_df[col].astype(str).str.replace(',', '').apply(pd.to_numeric, errors='coerce').fillna(0)
                
                    reverse_map = {v: k for k, v in display_map.items()}
                    st.session_state['incentive_records'] = edited_df.rename(columns=reverse_map).to_dict('records')
                
                # Export Excel
                if st.session_state['incentive_records']:
                    default_name = f"{t('Bảng tổng hợp Incentive', 'インセンティブ集計表')}.xlsx"

                    st.markdown("---")
                    c_name, c_save, c_dl, c_del = st.columns([3.5, 2.0, 2.0, 2.5])
                    with c_name:
                        export_name = st.text_input("📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), value=default_name, key="incentive_filename_v2")
                    with c_save:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button(t("💾 LƯU DỮ LIỆU", "💾 データ保存"), use_container_width=True, type="primary", key="save_inc_data"):
                            from logic.history_records import add_records
                            add_records("incentive", st.session_state['incentive_records'])
                            st.session_state['pending_toast'] = t("Đã lưu dữ liệu vào hệ thống!", "データをシステムに保存しました！")
                            st.rerun()
                        if not export_name.endswith(".xlsx"):
                            export_name += ".xlsx"
                            
                    title_for_excel = export_name.replace(".xlsx", "").upper()
                    excel_buffer = generate_incentive_excel(st.session_state['incentive_records'], title=title_for_excel)

                    with c_dl:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    
                        def download_and_save_inc(*args):
                            save_action_log(*args)
                            from logic.history_records import add_records
                            add_records("incentive", st.session_state['incentive_records'])
                        
                        st.download_button(
                            label=t("TẢI FILE EXCEL", "Excelダウンロード"),
                            data=excel_buffer,
                            file_name=export_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            use_container_width=True,
                            on_click=download_and_save_inc,
                            args=("Tính Incentive", "インセンティブ計算", f"Tính Incentive ({len(st.session_state['incentive_records'])} bản ghi)", f"インセンティブ計算 ({len(st.session_state['incentive_records'])} レコード)", excel_buffer, export_name)
                        )
                    with c_del:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button(t(":material/delete: XÓA TOÀN BỘ", ":material/delete: 全データ削除"), use_container_width=True):
                            st.session_state['incentive_records'] = []
                            if 'last_incentive_calc' in st.session_state:
                                del st.session_state['last_incentive_calc']
                            if 'last_incentive_inputs' in st.session_state:
                                del st.session_state['last_incentive_inputs']
                            st.rerun()
                
        if True:
            info_text = t(
                "Công thức sử dụng:\n- Lợi Nhuận = (Kế hoạch * Đơn giá) - (Thực tế * Charge)\n- Incentive Tiêu Chuẩn = (Đơn giá - Charge) * 0.3\n- Nhận Được = (Kế hoạch - Thực tế) * Incentive Tiêu Chuẩn",
                "使用計算式:\n- 利益 = (目標 × 単価) - (実績 × チャージ)\n- 基準金額 = (単価 - チャージ) × 0.3\n- 受取額 = (目標 - 実績) × 基準金額"
            )
            st.info(info_text, icon="ℹ️")
