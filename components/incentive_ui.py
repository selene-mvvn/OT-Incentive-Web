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
    
    if True:
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
            target_hours = st.number_input(t("Giờ công theo kế hoạch", "目標工数"), min_value=0.0, step=1.0, format="%f")
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

        # Ranking Section
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600; margin-top: 20px;'>{t('BẢNG XẾP HẠNG HIỆU SUẤT', 'パフォーマンスランキング')}</h3>", unsafe_allow_html=True)
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
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Show Beautiful Chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=agg_df['employee_name'],
                    y=agg_df['total_incentive'],
                    name=t("Tổng Incentive (JPY)", "総インセンティブ (JPY)"),
                    marker=dict(
                        color=agg_df['total_incentive'],
                        colorscale=[[0, '#e0f7fa'], [1, '#00aced']], # Light cyan to deep cyan
                        line=dict(color='rgba(0,0,0,0)', width=0)
                    ),
                    text=agg_df['total_incentive'].apply(lambda x: f"{x:,.0f}"),
                    textposition='auto',
                ))
                fig.update_layout(
                    title=t("Biểu đồ Tổng Incentive Nhận Được", "総受取額チャート"),
                    xaxis_title="",
                    yaxis_title=t("Incentive (JPY)", "インセンティブ (JPY)"),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'family': "Inter, sans-serif"},
                    margin=dict(l=0, r=0, t=40, b=0),
                    yaxis=dict(gridcolor='#e0e0e0')
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                
                # Show Beautiful Table
                agg_display = agg_df.copy()
                agg_display.index = agg_display.index + 1
                
                col_emp = t("Nhân sự", "担当者")
                col_tgt = t("Tổng Giờ Kế Hoạch", "総目標工数")
                col_act = t("Tổng Giờ Thực Tế", "総実工数")
                col_eff = t("Hiệu Suất (%)", "効率 (%)")
                col_inc = t("Tổng Incentive Nhận (JPY)", "総受取額 (JPY)")
                col_prj = t("Số Dự Án", "案件数")
                
                agg_display.rename(columns={
                    'employee_name': col_emp,
                    'total_target': col_tgt,
                    'total_actual': col_act,
                    'efficiency_pct': col_eff,
                    'total_incentive': col_inc,
                    'projects_count': col_prj
                }, inplace=True)
                
                # Format with Pandas Styler for a beautiful table
                format_dict = {
                    col_tgt: "{:,.0f}",
                    col_act: "{:,.0f}",
                    col_inc: "{:,.0f}",
                    col_eff: "{:,.1f}%"
                }
                
                styled_df = agg_display.style.format(format_dict).background_gradient(
                    subset=[col_inc], 
                    cmap='Blues'
                )
                
                st.dataframe(styled_df, use_container_width=True)
                
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                with st.expander(t("⚙️ Quản lý / Chỉnh sửa Dữ liệu Lịch sử Xếp hạng", "⚙️ 履歴データ管理・編集")):
                    st.markdown(t("Bạn có thể sửa trực tiếp hoặc xóa các hàng dữ liệu nháp ở bảng bên dưới, sau đó bấm **Lưu thay đổi**.", "以下の表で直接データを編集・削除し、「変更を保存」をクリックしてください。"))
                    
                    hist_display = df_hist.copy()
                    if 'date_obj' in hist_display.columns:
                        hist_display = hist_display.drop(columns=['date_obj'])
                        
                    hist_display_map = {
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
                    hist_display = hist_display.rename(columns=hist_display_map)
                    
                    edited_hist_df = st.data_editor(hist_display, use_container_width=True, num_rows="dynamic", key="edit_hist_inc")
                    
                    if st.button(t("💾 Lưu thay đổi Lịch sử", "💾 履歴を保存"), type="primary"):
                        reverse_hist_map = {v: k for k, v in hist_display_map.items()}
                        updated_records = edited_hist_df.rename(columns=reverse_hist_map).to_dict('records')
                        from logic.history_records import save_all_records
                        save_all_records("incentive", updated_records)
                        st.success(t("Đã cập nhật lịch sử thành công!", "履歴を正常に更新しました！"))
                        st.rerun()
                
        # Add to List button
        if st.button(t("➕ Thêm vào Danh sách Chờ xuất", "➕ リストに追加")):
            if not inputs['project_name'] or not inputs['employee_name']:
                st.error(t("Vui lòng nhập Tên dự án và Người thực hiện!", "案件名と担当者を入力してください！"))
            else:
                st.session_state['incentive_records'].append({**inputs, **result})
                st.success(t("Đã thêm vào danh sách!", "リストに追加しました！"))
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
                
    if True:
        info_text = t(
            "Công thức sử dụng:\n- Lợi Nhuận = (Kế hoạch * Đơn giá) - (Thực tế * Charge)\n- Incentive Tiêu Chuẩn = (Đơn giá - Charge) * 0.3\n- Nhận Được = (Kế hoạch - Thực tế) * Incentive Tiêu Chuẩn",
            "使用計算式:\n- 利益 = (目標 × 単価) - (実績 × チャージ)\n- 基準金額 = (単価 - チャージ) × 0.3\n- 受取額 = (目標 - 実績) × 基準金額"
        )
        st.info(info_text)
