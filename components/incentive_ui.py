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
    
    known_employees = get_history("employees")
    combined_employees = list(dict.fromkeys(master_employees + known_employees))
    
    tab_calc, tab_charts = st.tabs([t("1. TÍNH INCENTIVE", "1. インセンティブ計算"), t("2. BẢNG XẾP HẠNG & BIỂU ĐỒ", "2. ランキング＆チャート")])
    
    with tab_calc:
        st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px;'>{t('1. Thông tin Dự án', '1. プロジェクト情報')}</h3>", unsafe_allow_html=True)
        col_info1, col_info2, col_info3 = st.columns(3)
        
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
                
            clean_project_name = project_name
            if isinstance(project_name, str) and project_name.startswith("[") and "] " in project_name:
                split_idx = project_name.index("] ")
                clean_project_name = project_name[split_idx+2:]
                
        with col_info3:
            opt_choose_emp = t("--- Chọn nhân viên ---", "--- 担当者を選択 ---")
            emp_opts = [opt_choose_emp] + combined_employees
            sel_emp = st.selectbox(t("Người thực hiện", "担当者"), emp_opts)
            
            if sel_emp == opt_choose_emp:
                employee_name = ""
            else:
                employee_name = sel_emp
        
        st.markdown(f"<h3 style='font-size: 18px; font-weight: 600; margin-top: 20px;'>{t('2. Thông số Tính toán', '2. 計算パラメータ')}</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{t('Tính Tự Động Giờ Theo Kế Hoạch', '自動目標工数計算')}**")
            c_calc1, c_calc2, c_calc_btn = st.columns([2, 2, 1])
            with c_calc1:
                calc_from = st.date_input(t("Từ ngày", "開始日"), key="inc_calc_from")
            with c_calc2:
                calc_to = st.date_input(t("Đến ngày", "終了日"), key="inc_calc_to")
            with c_calc_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("TÍNH", key="btn_auto_calc_target"):
                    if sel_emp == opt_choose_emp:
                        st.error("Vui lòng chọn nhân viên!")
                    else:
                        emp_row = emp_df[emp_df['Tên NV'] == sel_emp]
                        if emp_row.empty:
                            st.warning("Nhân viên không tồn tại trong Cài đặt chung!")
                        else:
                            join_date_val = emp_row.iloc[0].get("Ngày vào làm")
                            try:
                                join_date = pd.to_datetime(join_date_val, dayfirst=True).date()
                                # Start date is max of calc_from and join_date
                                start_calc = max(calc_from, join_date)
                                end_calc = calc_to
                                
                                base = st.session_state.get('ot_base_data', {})
                                holidays = []
                                if 'holidays_df' in base and not base['holidays_df'].empty and 'Ngày nghỉ' in base['holidays_df'].columns:
                                    holidays = pd.to_datetime(base['holidays_df']["Ngày nghỉ"], errors="coerce").dropna().dt.date.tolist()
                                    
                                valid_days = 0
                                curr = start_calc
                                while curr <= end_calc:
                                    # check weekend
                                    is_weekend = curr.weekday() >= 5
                                    if curr.weekday() == 5:
                                        next_week = curr + datetime.timedelta(days=7)
                                        if next_week.month != curr.month:
                                            is_weekend = False
                                    
                                    # check holiday
                                    is_holiday = curr in holidays
                                    
                                    if not is_weekend and not is_holiday:
                                        valid_days += 1
                                    curr += datetime.timedelta(days=1)
                                    
                                hours_per_day = float(base.get('hours_per_day', 8.0))
                                st.session_state['auto_target_hours'] = valid_days * hours_per_day
                                st.success(f"Đã tính: {valid_days} ngày * {hours_per_day}h")
                            except:
                                st.error("Ngày vào làm không hợp lệ!")
                                
            auto_val = st.session_state.get('auto_target_hours', 0.0)
            target_hours = st.number_input(t("Giờ công theo kế hoạch", "目標工数"), min_value=0.0, step=1.0, format="%f", value=auto_val)
            actual_hours = st.number_input(t("Giờ công thực tế", "実工数"), min_value=0.0, step=1.0, format="%f")
        
        with col2:
            unit_price = st.number_input(t("Đơn giá", "単価"), min_value=0.0, step=1000.0, format="%f")
            company_charge = st.number_input(t("Company Charge", "会社運用チャージ"), min_value=0.0, step=100.0, format="%f")
            
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
        with tab_calc:
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
                    if st.button(t("🗑️ XÓA TOÀN BỘ", "🗑️ 全データ削除"), use_container_width=True):
                        st.session_state['incentive_records'] = []
                        st.rerun()
                
    with tab_calc:
        info_text = t(
            "Công thức sử dụng:\n- Lợi Nhuận = (Kế hoạch * Đơn giá) - (Thực tế * Charge)\n- Incentive Tiêu Chuẩn = (Đơn giá - Charge) * 0.3\n- Nhận Được = (Kế hoạch - Thực tế) * Incentive Tiêu Chuẩn",
            "使用計算式:\n- 利益 = (目標 × 単価) - (実績 × チャージ)\n- 基準金額 = (単価 - チャージ) × 0.3\n- 受取額 = (目標 - 実績) × 基準金額"
        )
        st.info(info_text)

    # ==========================
    # TAB 2: RANKING & CHARTS
    # ==========================
    with tab_charts:
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('BẢNG XẾP HẠNG HIỆU SUẤT', 'パフォーマンスランキング')}</h3>", unsafe_allow_html=True)
        st.caption(t("Bảng xếp hạng tổng hợp dựa trên dữ liệu Incentive đã được lưu trong lịch sử hệ thống.", "システム履歴に保存されたインセンティブデータに基づく総合ランキング。"))
        
        from logic.history_records import get_records
        inc_history = get_records("incentive")
        if not inc_history:
            st.info(t("Chưa có dữ liệu Incentive nào được lưu.", "保存されたデータがありません。"))
        else:
            df_hist = pd.DataFrame(inc_history)
            df_hist['date_obj'] = pd.to_datetime(df_hist['date'], format='%d/%m/%Y', errors='coerce')
            
            # Ensure proper types
            for col in ['target_hours', 'actual_hours', 'final_incentive']:
                df_hist[col] = pd.to_numeric(df_hist.get(col, 0), errors='coerce').fillna(0)
                
            years = sorted(df_hist['date_obj'].dt.year.dropna().unique().tolist(), reverse=True)
            years = [int(y) for y in years]
            if not years:
                years = [datetime.datetime.now().year]
                
            c_year, c_emp = st.columns(2)
            with c_year:
                sel_year = st.selectbox(t("Chọn năm", "年を選択"), ["Tất cả"] + years)
            
            if sel_year != "Tất cả":
                df_filtered = df_hist[df_hist['date_obj'].dt.year == sel_year]
            else:
                df_filtered = df_hist
                
            if df_filtered.empty:
                st.warning("Không có dữ liệu cho năm này.")
            else:
                # Aggregate by employee
                # Hiệu suất làm việc (Efficiency) = (Target Hours - Actual Hours) / Target Hours?
                # Or total Final Incentive?
                agg_df = df_filtered.groupby('employee_name').agg(
                    total_target=('target_hours', 'sum'),
                    total_actual=('actual_hours', 'sum'),
                    total_incentive=('final_incentive', 'sum'),
                    projects_count=('project_name', 'count')
                ).reset_index()
                
                # Calculate Efficiency (Hiệu suất) %
                agg_df['efficiency_pct'] = (agg_df['total_target'] / agg_df['total_actual'] * 100).fillna(0).replace([float('inf'), float('-inf')], 0)
                
                # Sort by highest Incentive
                agg_df = agg_df.sort_values(by='total_incentive', ascending=False).reset_index(drop=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Show Chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=agg_df['employee_name'],
                    y=agg_df['total_incentive'],
                    name=t("Tổng Incentive (JPY)", "総インセンティブ (JPY)"),
                    marker_color='#4caf50'
                ))
                fig.update_layout(
                    title=t("Biểu đồ Tổng Incentive Nhận Được", "総受取額チャート"),
                    xaxis_title=t("Nhân sự", "スタッフ"),
                    yaxis_title=t("Incentive (JPY)", "インセンティブ (JPY)"),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'family': "Inter, sans-serif"}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show Table
                agg_display = agg_df.copy()
                agg_display.index = agg_display.index + 1
                agg_display.rename(columns={
                    'employee_name': t("Nhân sự", "担当者"),
                    'total_target': t("Tổng Giờ Kế Hoạch", "総目標工数"),
                    'total_actual': t("Tổng Giờ Thực Tế", "総実工数"),
                    'efficiency_pct': t("Hiệu Suất (%)", "効率 (%)"),
                    'total_incentive': t("Tổng Incentive Nhận (JPY)", "総受取額 (JPY)"),
                    'projects_count': t("Số Dự Án", "案件数")
                }, inplace=True)
                
                # Format
                for col in [t("Tổng Giờ Kế Hoạch", "総目標工数"), t("Tổng Giờ Thực Tế", "総実工数"), t("Tổng Incentive Nhận (JPY)", "総受取額 (JPY)")]:
                    agg_display[col] = agg_display[col].apply(lambda x: f"{x:,.0f}")
                agg_display[t("Hiệu Suất (%)", "効率 (%)")] = agg_display[t("Hiệu Suất (%)", "効率 (%)")].apply(lambda x: f"{x:,.1f}%")
                
                st.dataframe(agg_display, use_container_width=True)
