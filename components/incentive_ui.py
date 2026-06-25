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
    if 'incentive_records' not in st.session_state:
        st.session_state['incentive_records'] = []
        
    title = t("Tính Incentive (JPY)", "インセンティブ計算")
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    st.markdown(t("Nhập các thông số dự án bên dưới để tính toán và lưu vào bảng chờ xuất.", "以下にプロジェクトのパラメータを入力して計算し、出力待ちリストに保存してください。"), unsafe_allow_html=True)
    
    # Input area
    st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px;'>{t('1. Thông tin Dự án', '1. プロジェクト情報')}</h3>", unsafe_allow_html=True)
    col_info1, col_info2, col_info3 = st.columns(3)
    
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
    
    known_employees = get_history("employees")
            
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
            
        # Parse pure name from composite if it exists
        clean_project_name = project_name
        if isinstance(project_name, str) and project_name.startswith("[") and "] " in project_name:
            split_idx = project_name.index("] ")
            clean_project_name = project_name[split_idx+2:]
            
    with col_info3:
        opt_choose_emp = t("--- Chọn nhân viên ---", "--- 担当者を選択 ---")
        emp_opts = [opt_choose_emp] + known_employees
        sel_emp = st.selectbox(t("Người thực hiện", "担当者"), emp_opts)
        
        if sel_emp == opt_choose_emp:
            employee_name = ""
        else:
            employee_name = sel_emp
        
    st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px;'>{t('2. Thông số Tính toán', '2. 計算パラメータ')}</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        target_hours = st.number_input(t("Giờ công theo kế hoạch", "目標工数"), min_value=0.0, step=1.0, format="%f")
        actual_hours = st.number_input(t("Giờ công thực tế", "実工数"), min_value=0.0, step=1.0, format="%f")
    
    with col2:
        unit_price = st.number_input(t("Đơn giá", "単価"), min_value=0.0, step=1000.0, format="%f")
        company_charge = st.number_input(t("Company Charge", "会社運用ﾁｬｰｼﾞ"), min_value=0.0, step=100.0, format="%f")
        
    st.divider()
    
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
        
    if 'last_incentive_calc' in st.session_state:
        result = st.session_state['last_incentive_calc']
        inputs = st.session_state['last_incentive_inputs']
        
        col_title, col_clear = st.columns([8, 2])
        with col_title:
            st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px; margin-bottom: 0;'>{t('3. Kết quả & Phân tích', '3. 結果と分析')}</h3>", unsafe_allow_html=True)
        with col_clear:
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ " + t("Xóa kết quả này", "結果をクリア"), use_container_width=True, key="clear_incentive_result"):
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
            
        # Charts
        c1, c2 = st.columns(2)
        with c1:
            # Progress Gauge
            completion_rate = (inputs['actual_hours'] / inputs['target_hours'] * 100) if inputs['target_hours'] > 0 else 0
            gauge_color = "#66bb6a" if completion_rate <= 100 else "#ef5350" # Lighter Green/Red
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = completion_rate,
                number = {'suffix': "%", 'font': {'size': 40, 'color': gauge_color}},
                gauge = {
                    'axis': {'range': [None, max(150, completion_rate + 20)], 'tickwidth': 1, 'tickcolor': "#b0bec5"},
                    'bar': {'color': gauge_color, 'thickness': 0.75},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 100], 'color': "#e8f5e9"}, # Very light green
                        {'range': [100, max(150, completion_rate + 20)], 'color': "#ffebee"} # Very light red
                    ],
                    'threshold': {
                        'line': {'color': "#ef5350", 'width': 3},
                        'thickness': 0.85,
                        'value': 100
                    }
                }
            ))
            fig_gauge.update_layout(
                height=250, 
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': "Inter, sans-serif"}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown(f"<p style='text-align: center; font-size: 15px; font-weight: 600; color: #455a64;'>{t('TIẾN ĐỘ TIÊU HAO GIỜ CÔNG', '工数消化率')}</p>", unsafe_allow_html=True)
            
        with c2:
            # Pie Chart of Profit Allocation (if there is a positive standard incentive)
            if result['standard_incentive'] > 0 and result['profit'] > 0:
                labels = [t('Incentive Cty cấp', '会社付与分'), t('Incentive Khách cấp thêm', '顧客追加分')]
                values = [result['profit'] - result['standard_incentive'], result['standard_incentive']]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=labels, 
                    values=values, 
                    hole=.6, # Sleek donut
                    textinfo='percent',
                    hoverinfo='label+value',
                    marker=dict(
                        colors=['#90caf9', '#a5d6a7'], # Pastel Blue and Green
                        line=dict(color='#ffffff', width=2)
                    )
                )])
                fig_pie.update_layout(
                    height=250, 
                    margin=dict(l=20, r=20, t=30, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    font={'family': "Inter, sans-serif"}
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown(f"<p style='text-align: center; font-size: 15px; font-weight: 600; color: #455a64; margin-top: -15px;'>{t('CƠ CẤU LỢI NHUẬN', '利益構成')}</p>", unsafe_allow_html=True)
            else:
                st.info(t("Dự án không phát sinh Incentive hoặc đang lỗ.", "プロジェクトでインセンティブが発生していないか、赤字です。"))
                
        # Add to List button
        if st.button(t("➕ Thêm vào Danh sách Chờ xuất", "➕ リストに追加")):
            if not inputs['project_name'] or not inputs['employee_name']:
                st.error(t("Vui lòng nhập Tên dự án và Người thực hiện!", "案件名と担当者を入力してください！"))
            else:
                st.session_state['incentive_records'].append({**inputs, **result})
                st.success(t("Đã thêm vào danh sách!", "リストに追加しました！"))
                
    # Data list
    if st.session_state.get('incentive_records') and len(st.session_state['incentive_records']) > 0:
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
        
        edited_df = st.data_editor(
            df_display,
            use_container_width=True,
            num_rows="dynamic",
            disabled=[t("Lợi nhuận", "利益"), t("Incentive TC", "基準金額"), t("Nhận được", "受取額")]
        )
        
        # Sync back edited df
        if not edited_df.equals(df_display):
            reverse_map = {v: k for k, v in display_map.items()}
            st.session_state['incentive_records'] = edited_df.rename(columns=reverse_map).to_dict('records')
            
        # Export Excel
        excel_buffer = generate_incentive_excel(st.session_state['incentive_records'])
        if excel_buffer:
            today_str = datetime.datetime.now().strftime("%Y%m%d")
            default_name = f"{t('Bảng tổng hợp Incentive_', 'インセンティブ計算結果_')}{today_str}.xlsx"
            
            st.markdown("---")
            c_name, c_dl, c_del = st.columns([5, 3, 2])
            with c_name:
                export_name = st.text_input("📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), value=default_name, key="incentive_filename")
                if not export_name.endswith(".xlsx"):
                    export_name += ".xlsx"
            with c_dl:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                st.download_button(
                    label=t("TẢI FILE EXCEL", "Excelダウンロード"),
                    data=excel_buffer,
                    file_name=export_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                    on_click=save_action_log,
                    args=("Tính Incentive", "インセンティブ計算", f"Tính Incentive ({len(st.session_state['incentive_records'])} bản ghi)", f"インセンティブ計算 ({len(st.session_state['incentive_records'])} レコード)", excel_buffer, export_name)
                )
            with c_del:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button(t("🗑️ XÓA TOÀN BỘ", "🗑️ 全データ削除"), use_container_width=True):
                    st.session_state['incentive_records'] = []
                    st.rerun()
            
    info_text = t(
        "Công thức sử dụng:\n- Lợi Nhuận = (Kế hoạch * Đơn giá) - (Thực tế * Charge)\n- Incentive Tiêu Chuẩn = (Đơn giá - Charge) * 0.3\n- Nhận Được = (Kế hoạch - Thực tế) * Incentive Tiêu Chuẩn",
        "使用計算式:\n- 利益 = (目標 × 単価) - (実績 × チャージ)\n- 基準金額 = (単価 - チャージ) × 0.3\n- 受取額 = (目標 - 実績) × 基準金額"
    )
    st.info(info_text)
