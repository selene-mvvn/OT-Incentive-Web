import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import copy
from logic.i18n import t
from logic.history_records import get_records, deduplicate_records

def get_record_cost(r):
    cost = 0.0
    for k, v in r.items():
        if str(k).endswith('%'):
            try:
                if pd.notna(v) and str(v).strip() not in ['', 'nan', 'None']:
                    cost += float(v)
            except:
                pass
    if pd.isna(cost) or cost == 0.0:
        try:
            val = r.get('ot_pay', 0.0)
            if pd.notna(val) and str(val).strip() not in ['', 'nan', 'None']:
                cost = float(val)
        except:
            pass
    return float(cost) if pd.notna(cost) else 0.0

def get_clean_period(row):
    p = str(row.get('payment_period', '')).strip()
    if p and p != 'nan' and p.startswith('T'):
        return p
    d_str = str(row.get('ot_date', '')).strip()
    if d_str and d_str != 'nan':
        try:
            dt = pd.to_datetime(d_str, dayfirst=True)
            if pd.notna(dt):
                return f"T{dt.month:02d}/{dt.year}"
        except:
            pass
    return t("Khác", "その他")

def render_project_history():
    st.markdown("""
    <style>
    /* Hide Streamlit dataframe element toolbar right above tables */
    [data-testid="stDataFrame"] [data-testid="stElementToolbar"],
    [data-testid="stDataFrame"] div[class*="stElementToolbar"],
    [data-testid="stDataFrame"] > div:first-child:has(button) {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Pull dataframe upward closer to the subheader without being too tight */
    [data-testid="stDataFrame"] {
        margin-top: -10px !important;
    }
    [data-testid="stDataFrame"] > div {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)


    # Combine all records: historical + pending manual session + pending excel session
    hist_records = get_records("ot")
    manual_pending = st.session_state.get('ot_records', [])
    excel_pending = st.session_state.get('ot_excel_records', [])

    all_raw = copy.deepcopy(hist_records) + copy.deepcopy(manual_pending) + copy.deepcopy(excel_pending)
    all_records = deduplicate_records(all_raw, "ot")

    if not all_records:
        from components.ui_utils import render_empty_state
        render_empty_state(t('Chưa có dữ liệu dự án nào trong hệ thống hoặc bảng chờ.', 'システムまたは待機リストにプロジェクトデータがありません。'), icon="folder_open", height=150)
        return

    df = pd.DataFrame(all_records)
    
    # Ensure necessary columns exist
    for col in ['order_name', 'order_id', 'client_order_id', 'ot_hours', 'employee_name', 'ot_date']:
        if col not in df.columns:
            df[col] = ''

    def get_full_project_name(row):
        name = str(row.get('order_name', '')).strip()
        if not name or name.lower() in ['nan', 'none', '']:
            return t('Khác / Không tên', 'その他')
        if name.startswith('[') and '] ' in name:
            return name
        code = str(row.get('order_id', '')).strip()
        if not code or code.lower() in ['nan', 'none', '']:
            code = str(row.get('client_order_id', '')).strip()
        if not code or code.lower() in ['nan', 'none', '']:
            try:
                base = st.session_state.get('base', {})
                p_df = base.get('projects_df', pd.DataFrame()) if isinstance(base, dict) else pd.DataFrame()
                if not p_df.empty and 'Tên dự án' in p_df.columns and 'Mã đơn hàng' in p_df.columns:
                    matches = p_df[p_df['Tên dự án'].astype(str).str.strip() == name]
                    if len(matches) == 1:
                        c_val = str(matches.iloc[0]['Mã đơn hàng']).strip()
                        if c_val and c_val.lower() not in ['nan', 'none', '']:
                            code = c_val
            except:
                pass
        if code and code.lower() not in ['nan', 'none', '']:
            return f"[{code}] {name}"
        return name

    df['ot_hours'] = pd.to_numeric(df['ot_hours'], errors='coerce').fillna(0.0)
    df['order_name'] = df.apply(get_full_project_name, axis=1)
    df['employee_name'] = df['employee_name'].astype(str).str.strip().replace({'': t('Chưa rõ', '未定')})
    df['clean_period'] = df.apply(get_clean_period, axis=1)
    df['est_cost'] = df.apply(get_record_cost, axis=1)

    # Sort periods chronologically (e.g. T07/2026 -> 2026-07)
    def sort_key_period(p):
        if p.startswith('T') and '/' in p:
            parts = p[1:].split('/')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return int(parts[1]) * 100 + int(parts[0])
        return 0

    unique_periods = sorted(df['clean_period'].unique().tolist(), key=sort_key_period, reverse=True)
    all_period_opt = t("🌟 Tất cả các tháng", "🌟 すべての月")
    
    years = set()
    for p in unique_periods:
        p_str = str(p)
        if p_str.startswith('T') and '/' in p_str:
            parts = p_str[1:].split('/')
            if len(parts) == 2 and parts[1].isdigit():
                years.add(int(parts[1]))
    year_options = [t("Tất cả", "すべて")] + sorted(list(years), reverse=True)
    month_options = [t("Tất cả", "すべて")] + list(range(1, 13))

    col_hdr_left, col_hdr_right = st.columns([5.5, 4.5])
    with col_hdr_left:
        st.markdown(f"<h2 style='font-size: 28px; font-weight: 600; color: #1e293b; margin-bottom: 4px;'>{t('PHÂN BỔ & LỊCH SỬ DỰ ÁN (OT)', 'プロジェクト分析・履歴')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 14.5px; color: #64748b; margin-bottom: 20px;'>{t('Phân tích tỷ trọng giờ tăng ca và tra cứu chi tiết lịch sử từng dự án theo tháng/kỳ thanh toán.', 'プロジェクト別の残業時間分布と履歴を月別・案件別に詳細分析します。')}</div>", unsafe_allow_html=True)
    with col_hdr_right:
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
        c_spacer, c_btn = st.columns([7.5, 2.5])
        with c_btn:
            if st.button(t("🖨️ In Báo Cáo", "🖨️ 印刷"), use_container_width=True):
                import streamlit.components.v1 as components
                components.html("<script>window.parent.print();</script>", height=0, width=0)

    tab1, tab2 = st.tabs([
        t("1. PHÂN BỔ DỰ ÁN THEO THÁNG", "1. プロジェクト月別分布"),
        t("2. TRA CỨU CHI TIẾT TỪNG DỰ ÁN", "2. プロジェクト別詳細分析")
    ])

    # ==================== TAB 1: PHÂN BỔ DỰ ÁN ====================
    with tab1:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        col_f1_y, col_f1_m, _ = st.columns([2, 2, 6])
        with col_f1_y:
            sel_year_t1 = st.selectbox(
                t(":material/calendar_today: Lọc theo Năm:", ":material/calendar_today: 年を選択:"),
                options=year_options,
                key="tab1_sel_year"
            )
        with col_f1_m:
            sel_month_t1 = st.selectbox(
                t(":material/calendar_month: Lọc theo Tháng:", ":material/calendar_month: 月を選択:"),
                options=month_options,
                format_func=lambda x: t(f"Tháng {x}", f"{x}月") if isinstance(x, int) else x,
                key="tab1_sel_month",
                help=t("Mẹo: Khi để Năm là 'Tất cả', hệ thống sẽ gộp chung dữ liệu của tháng này qua các năm.  \n👉 *Tiện lợi để phân tích tính mùa vụ*.", "ヒント: 「年」を「すべて」にすると、全年の該当月のデータを合算して表示します。  \n👉 *季節性の分析に便利です*。")
            )

        df_tab1 = df.copy()
        period_labels = []
        
        if sel_year_t1 not in ["Tất cả", "すべて"]:
            df_tab1 = df_tab1[df_tab1['clean_period'].astype(str).str.endswith(f"/{sel_year_t1}")]
            period_labels.append(str(sel_year_t1))
            
        if sel_month_t1 not in ["Tất cả", "すべて"]:
            month_str = f"T{sel_month_t1:02d}/"
            df_tab1 = df_tab1[df_tab1['clean_period'].astype(str).str.startswith(month_str)]
            period_labels.append(t(f"Tháng {sel_month_t1}", f"{sel_month_t1}月"))
            
        if not period_labels:
            period_label = t("Toàn bộ thời gian", "全期間")
        else:
            period_label = " - ".join(period_labels)

        if df_tab1.empty or df_tab1['ot_hours'].sum() <= 0:
            from components.ui_utils import render_empty_state
            render_empty_state(t('Không có số giờ OT nào trong kỳ này.', 'この期間の残業データがありません。'), icon="event_busy", height=120)
        else:
            total_hrs = df_tab1['ot_hours'].sum()
            total_cost = df_tab1['est_cost'].sum()
            num_projects = df_tab1['order_name'].nunique()
            num_staff = df_tab1['employee_name'].nunique()

            # Summary Metric Cards
            st.markdown(f"""
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 20px; margin-top: 8px;'>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #00a8e8; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                        <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>
                            {t('TỔNG GIỜ OT', '残業時間合計')}
                        </div>
                        <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #00a8e8 0%, #0077b6 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0, 168, 232, 0.3); flex-shrink: 0;'>
                            <span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">schedule</span>
                        </div>
                    </div>
                    <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'>
                        {total_hrs:,.1f} <span style='font-size: 15px; font-weight: 600; color: #475569;'>h</span>
                    </div>
                </div>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #10b981; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                        <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>
                            {t('DỰ TÍNH CHI PHÍ', '予想支出額')}
                        </div>
                        <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #34d399 0%, #10b981 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); flex-shrink: 0;'>
                            <span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">payments</span>
                        </div>
                    </div>
                    <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'>
                        {total_cost:,.0f} <span style='font-size: 15px; font-weight: 600; color: #475569;'>VNĐ</span>
                    </div>
                </div>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #8b5cf6; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                        <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>
                            {t('SỐ DỰ ÁN THAM GIA', '対象プロジェクト数')}
                        </div>
                        <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(139, 92, 246, 0.3); flex-shrink: 0;'>
                            <span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">folder</span>
                        </div>
                    </div>
                    <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'>
                        {num_projects} <span style='font-size: 15px; font-weight: 600; color: #475569;'>{t('dự án', '件')}</span>
                    </div>
                </div>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #f59e0b; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                        <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>
                            {t('SỐ NHÂN SỰ OT', '対象スタッフ数')}
                        </div>
                        <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3); flex-shrink: 0;'>
                            <span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">group</span>
                        </div>
                    </div>
                    <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'>
                        {num_staff} <span style='font-size: 15px; font-weight: 600; color: #475569;'>{t('người', '名')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_pie, col_tbl = st.columns([5.5, 4.5], gap="large")
            
            proj_summary = df_tab1.groupby('order_name').agg(
                Hours=('ot_hours', 'sum'),
                Cost=('est_cost', 'sum'),
                StaffCount=('employee_name', 'nunique')
            ).reset_index()
            proj_summary['Percentage'] = (proj_summary['Hours'] / total_hrs * 100.0).round(1)
            
            def get_top_employee(p_name):
                p_df = df_tab1[df_tab1['order_name'] == p_name]
                if p_df.empty: return t('Không có', 'なし'), 0.0
                emp_grp = p_df.groupby('employee_name')['ot_hours'].sum().sort_values(ascending=False)
                if emp_grp.empty: return t('Không có', 'なし'), 0.0
                return emp_grp.index[0], emp_grp.iloc[0]
            
            top_emp_data = proj_summary['order_name'].apply(get_top_employee)
            proj_summary['top_employee'] = [x[0] for x in top_emp_data]
            proj_summary['top_employee_hours'] = [x[1] for x in top_emp_data]
            
            proj_summary = proj_summary.sort_values(by='Hours', ascending=False).reset_index(drop=True)

            with col_pie:
                col_pie_hdr1, col_pie_hdr2 = st.columns([6, 4])
                with col_pie_hdr1:
                    st.markdown(f"<div style='font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 4px;'>🎯 {t('Biểu đồ Tỷ trọng Giờ OT theo Dự án', 'プロジェクト別残業時間シェア')} ({period_label})</div>", unsafe_allow_html=True)
                with col_pie_hdr2:
                    chart_mode = st.radio(
                        "Chart mode",
                        options=[t(":material/pie_chart: Tròn (Donut)", ":material/pie_chart: ドーナツ"), t(":material/bar_chart: Cột (Bar)", ":material/bar_chart: 棒グラフ")],
                        label_visibility="collapsed",
                        horizontal=True,
                        key="tab1_chart_mode"
                    )

                if chart_mode == t(":material/pie_chart: Tròn (Donut)", ":material/pie_chart: ドーナツ"):
                    # Display all projects directly without grouping so data is honest and complete
                    pie_df = proj_summary.copy()
                    
                    # Rich saturated curated color palette with enough colors for all projects
                    curated_colors = [
                        '#0088fe', '#00c49f', '#ffbb28', '#ff8042', '#8b5cf6', '#ec4899', '#06b6d4', '#3b82f6',
                        '#10b981', '#f59e0b', '#6366f1', '#ef4444', '#14b8a6', '#a855f7', '#f97316', '#0ea5e9',
                        '#84cc16', '#d946ef', '#64748b', '#0d9488'
                    ]
                    
                    fig_pie = px.pie(
                        pie_df,
                        values='Hours',
                        names='order_name',
                        hole=0.48,
                        color_discrete_sequence=curated_colors,
                        custom_data=['top_employee', 'top_employee_hours']
                    )
                    
                    # Ép các mảnh nhỏ (< 1.5%) hiển thị text ra 'outside' để Plotly buộc phải vẽ đường chỉ dẫn (leader line)
                    textpos_array = ['outside' if row['Percentage'] < 1.5 else 'inside' for i, row in pie_df.iterrows()]
                    
                    # Xoay biểu đồ (rotation=80) để mảnh 0.803% nằm ở góc chéo, buộc Plotly phải vẽ đường chỉ dẫn
                    fig_pie.update_traces(
                        textposition=textpos_array,
                        textinfo='percent',
                        pull=0,
                        rotation=80,
                        domain=dict(x=[0.05, 0.72], y=[0.05, 0.98]),
                        hovertemplate='<b>%{label}</b><br>' + t('Số giờ', '残業時間') + ': %{value:,.1f} h (%{percent})<br>🌟 ' + t('Top nhân sự:', 'トップ:') + ' %{customdata[0]} (%{customdata[1]:.1f}h)<extra></extra>',
                        marker=dict(line=dict(color='#ffffff', width=2))
                    )
                    fig_pie.update_layout(
                        font=dict(family="'Times New Roman', serif"),
                        margin=dict(t=5, b=40, l=0, r=0),
                        showlegend=True,
                        legend=dict(
                            orientation='v',
                            yanchor='top',
                            y=0.85,
                            xanchor='left',
                            x=0.74,
                            font=dict(size=13.5, color='#1e293b'),
                            bgcolor='rgba(255,255,255,0.85)',
                            bordercolor='#cbd5e1',
                            borderwidth=1
                        ),
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                else:
                    # Horizontal bar chart sorted clearly by hours
                    bar_df = proj_summary.sort_values(by='Hours', ascending=True)
                    bar_w_t1 = 0.25 if len(bar_df) == 1 else (0.35 if len(bar_df) == 2 else (0.45 if len(bar_df) == 3 else None))
                    max_hrs_t1 = bar_df['Hours'].max() if not bar_df.empty else 0
                    text_colors_t1 = ['#ffffff' if i == len(bar_df) - 1 else '#0f172a' for i in range(len(bar_df))]
                    pos_list_t1 = ['inside' if (max_hrs_t1 > 0 and bar_df.iloc[i]['Hours'] >= 0.35 * max_hrs_t1) else 'outside' for i in range(len(bar_df))]
                    fig_pbar = go.Figure(go.Bar(
                        x=bar_df['Hours'],
                        y=bar_df['order_name'],
                        orientation='h',
                        width=bar_w_t1,
                        marker=dict(
                            color=bar_df['Hours'],
                            colorscale=[[0, '#7dd3fc'], [1, '#0284c7']],
                        ),
                        customdata=bar_df[['top_employee', 'top_employee_hours']].values,
                        hovertemplate='<b>%{y}</b><br>' + t('Số giờ', '残業時間') + ': %{x:,.1f} h<br>🌟 ' + t('Top nhân sự:', 'トップ:') + ' %{customdata[0]} (%{customdata[1]:.1f}h)<extra></extra>',
                        text=bar_df.apply(lambda r: f"{r['Hours']:,.1f} h ({r['Percentage']}%)", axis=1),
                        textposition=pos_list_t1,
                        textangle=0,
                        cliponaxis=False,
                        insidetextanchor='end',
                        insidetextfont=dict(size=12, color=text_colors_t1, weight='bold'),
                        outsidetextfont=dict(size=12, color='#0f172a', weight='bold')
                    ))
                    fig_pbar.update_layout(
                        font=dict(family="'Times New Roman', serif"),
                        margin=dict(l=0, r=45, t=15, b=15),
                        height=max(380, len(bar_df) * 32),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(title=t("Số giờ (h)", "時間 (h)"), gridcolor='#f1f5f9'),
                        yaxis=dict(tickfont=dict(size=12.5, color='#1e293b'))
                    )
                    st.plotly_chart(fig_pbar, use_container_width=True, config={'displayModeBar': False})

            with col_tbl:
                st.markdown(f"<div style='font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 4px;'>📋 {t('Bảng Tổng Hợp Chi Tiết Dự Án', 'プロジェクト別集計表')}</div>", unsafe_allow_html=True)
                col_proj = t('Tên Dự Án', 'プロジェクト名')
                col_hrs = t('Số Giờ (h)', '時間 (h)')
                col_pct = t('Tỷ Lệ (%)', '割合 (%)')
                col_cost = t('Chi Phí VNĐ', '予想支出額')
                col_staff = t('Số NV', '人数')

                display_df = proj_summary.copy()
                display_df = display_df.rename(columns={
                    'order_name': col_proj,
                    'Hours': col_hrs,
                    'Percentage': col_pct,
                    'Cost': col_cost,
                    'StaffCount': col_staff
                })
                display_df[col_hrs] = display_df[col_hrs].apply(lambda x: f"{x:,.1f}")
                display_df[col_pct] = display_df[col_pct].apply(lambda x: f"{x}%")
                display_df[col_cost] = display_df[col_cost].apply(lambda x: f"{x:,.0f}")

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=380,
                    column_config={
                        col_proj: st.column_config.TextColumn(
                            col_proj
                        ),
                        col_hrs: st.column_config.TextColumn(
                            col_hrs,
                            width=75
                        ),
                        col_cost: st.column_config.TextColumn(
                            col_cost,
                            width=95
                        ),
                        col_staff: st.column_config.TextColumn(
                            col_staff,
                            width=55
                        ),
                        col_pct: st.column_config.TextColumn(
                            col_pct,
                            width=65
                        )
                    }
                )

    # ==================== TAB 2: TRA CỨU CHI TIẾT TỪNG DỰ ÁN ====================
    with tab2:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        unique_projects = sorted(df['order_name'].unique().tolist())
        all_proj_opt = t("📂 --- Tất cả dự án ---", "📂 --- すべてのプロジェクト ---")
        project_options = [all_proj_opt] + unique_projects

        col_t2_1, col_t2_2, col_t2_y, col_t2_m = st.columns([3, 3, 2, 2])
        with col_t2_1:
            sel_project = st.selectbox(
                t("📌 Dự Án Chính:", "📌 メインプロジェクト:"),
                options=project_options,
                key="tab2_sel_project"
            )
        with col_t2_2:
            compare_opt = t("--- Không so sánh ---", "--- 比較しない ---")
            sel_project_compare = st.selectbox(
                t("⚖️ Dự Án So Sánh:", "⚖️ 比較プロジェクト:"),
                options=[compare_opt] + unique_projects,
                key="tab2_sel_project_compare"
            )
        with col_t2_y:
            sel_year_t2 = st.selectbox(
                t(":material/calendar_today: Lọc Năm:", ":material/calendar_today: 年:"),
                options=year_options,
                key="tab2_sel_year"
            )
        with col_t2_m:
            sel_month_t2 = st.selectbox(
                t(":material/calendar_month: Lọc Tháng:", ":material/calendar_month: 月:"),
                options=month_options,
                format_func=lambda x: t(f"Tháng {x}", f"{x}月") if isinstance(x, int) else x,
                key="tab2_sel_month"
            )

        def get_filtered_df(proj_name):
            df_sub = df.copy()
            if proj_name != all_proj_opt:
                df_sub = df_sub[df_sub['order_name'] == proj_name]
            period_labels = []
            if sel_year_t2 not in ["Tất cả", "すべて"]:
                df_sub = df_sub[df_sub['clean_period'].astype(str).str.endswith(f"/{sel_year_t2}")]
                period_labels.append(str(sel_year_t2))
            if sel_month_t2 not in ["Tất cả", "すべて"]:
                df_sub = df_sub[df_sub['clean_period'].astype(str).str.startswith(f"T{sel_month_t2:02d}/")]
                period_labels.append(t(f"Tháng {sel_month_t2}", f"{sel_month_t2}月"))
            lbl = " - ".join(period_labels) if period_labels else all_period_opt
            return df_sub, lbl

        def render_project_details(df_t2, proj_title, period_label, suffix_key):
            if df_t2.empty or df_t2['ot_hours'].sum() <= 0:
                from components.ui_utils import render_empty_state
                render_empty_state(t(f'Không có dữ liệu cho {proj_title}.', f'{proj_title} のデータがありません。'), icon="search_off", height=120)
                return

            p_hrs = df_t2['ot_hours'].sum()
            p_cost = df_t2['est_cost'].sum()
            p_staff = df_t2['employee_name'].nunique()
            p_records = len(df_t2)

            st.markdown(f"<h3 style='font-size: 18px; margin-bottom: 10px; margin-top: 10px; color: #0f172a;'>{proj_title} ({period_label})</h3>", unsafe_allow_html=True)
            
            # Budget Tracker
            b_col1, b_col2 = st.columns([1, 2])
            with b_col1:
                budget = st.number_input(t("Ngân sách OT (VNĐ)", "残業予算 (VNĐ)"), min_value=0, value=0, step=1000000, key=f"budget_{suffix_key}")
            with b_col2:
                if budget > 0:
                    pct = min(1.0, p_cost / budget)
                    color = "green" if pct < 0.8 else ("orange" if pct < 1.0 else "red")
                    st.markdown(f"<div style='margin-top: 32px; font-size: 13.5px; font-weight: 600; color: #475569;'>{t('Đã dùng:', '使用済:')} {pct*100:.1f}% ({p_cost:,.0f} / {budget:,.0f})</div>", unsafe_allow_html=True)
                    st.progress(pct)

            st.markdown(f"""
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 20px; margin-top: 8px;'>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
                    <div style='font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 4px;'>{t('Tổng Giờ', '総残業時間')}</div>
                    <div style='font-size: 19px; font-weight: 800; color: #0f172a;'>{p_hrs:,.1f} <span style='font-size: 13px;'>h</span></div>
                </div>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
                    <div style='font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 4px;'>{t('Nhân Sự', '参加スタッフ')}</div>
                    <div style='font-size: 19px; font-weight: 800; color: #0f172a;'>{p_staff} <span style='font-size: 13px;'>{t('người', '名')}</span></div>
                </div>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
                    <div style='font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 4px;'>{t('Chi Phí', '予想コスト')}</div>
                    <div style='font-size: 19px; font-weight: 800; color: #0f172a;'>{p_cost:,.0f} <span style='font-size: 13px;'>đ</span></div>
                </div>
                <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
                    <div style='font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 4px;'>{t('Tần Suất', '残業頻度')}</div>
                    <div style='font-size: 19px; font-weight: 800; color: #0f172a;'>{df_t2['ot_date'].nunique()} <span style='font-size: 13px;'>{t('ngày', '日')}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            staff_contrib = df_t2.groupby('employee_name').agg(
                Hours=('ot_hours', 'sum'),
                Cost=('est_cost', 'sum'),
                DaysCount=('ot_date', 'nunique')
            ).reset_index().sort_values(by='Hours', ascending=True)

            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                shared_chart_height = max(150, len(staff_contrib) * 55 + 60)
                st.markdown(f"<div style='font-size: 15px; font-weight: 600; color: #334155; margin-bottom: 4px;'>{t('Phân Bổ Theo Nhân Sự', 'スタッフ別残業')}</div>", unsafe_allow_html=True)
                
                max_hrs_t2 = staff_contrib['Hours'].max() if not staff_contrib.empty else 0
                text_colors_t2 = ['#ffffff' if i == len(staff_contrib) - 1 else '#0f172a' for i in range(len(staff_contrib))]
                pos_list_t2 = ['inside' if (max_hrs_t2 > 0 and staff_contrib.iloc[i]['Hours'] >= 0.35 * max_hrs_t2) else 'outside' for i in range(len(staff_contrib))]
                fig_bar = go.Figure(go.Bar(
                    x=staff_contrib['Hours'],
                    y=staff_contrib['employee_name'],
                    orientation='h',
                    marker=dict(color=staff_contrib['Hours'], colorscale=[[0, '#7dd3fc'], [1, '#0284c7']]),
                    text=staff_contrib['Hours'].apply(lambda x: f"{x:,.1f} h"),
                    textposition=pos_list_t2,
                    insidetextfont=dict(size=12, color=text_colors_t2, weight='bold'),
                    outsidetextfont=dict(size=12, color='#0f172a', weight='bold')
                ))
                fig_bar.update_layout(
                    font=dict(family="'Times New Roman', serif"),
                    margin=dict(l=0, r=40, t=15, b=15),
                    height=shared_chart_height,
                    bargap=0.35,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(visible=False),
                    yaxis=dict(tickfont=dict(size=12, color='#1e293b'))
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False}, key=f"bar_{suffix_key}")

            with col_chart2:
                st.markdown(f"<div style='font-size: 15px; font-weight: 600; color: #334155; margin-bottom: 4px;'>{t('Diễn Biến Thời Gian', '日別推移')}</div>", unsafe_allow_html=True)
                time_df = df_t2.groupby('ot_date')['ot_hours'].sum().reset_index()
                time_df['_sort_dt'] = pd.to_datetime(time_df['ot_date'], format='%d/%m/%Y', errors='coerce')
                time_df = time_df.sort_values(by='_sort_dt', ascending=True)
                
                if not time_df.empty:
                    fig_t = go.Figure(go.Bar(
                        x=time_df['_sort_dt'],
                        y=time_df['ot_hours'],
                        marker=dict(color=time_df['ot_hours'], colorscale=[[0, '#fde047'], [1, '#ca8a04']]),
                        text=time_df['ot_hours'].apply(lambda x: f"{x:,.1f}"),
                        textposition='auto',
                        textfont=dict(size=11, color='#0f172a', weight='bold')
                    ))
                    
                    # Add Trendline
                    if len(time_df) > 1:
                        import numpy as np
                        # Normalize timestamps to days offset for stable linear regression calculation
                        x_vals = (time_df['_sort_dt'] - time_df['_sort_dt'].min()).dt.total_seconds().values / 86400.0
                        y_vals = time_df['ot_hours'].values
                        A = np.vstack([x_vals, np.ones(len(x_vals))]).T
                        m, c = np.linalg.lstsq(A, y_vals, rcond=None)[0]
                        fig_t.add_trace(go.Scatter(
                            x=time_df['_sort_dt'], 
                            y=m * x_vals + c, 
                            mode='lines', 
                            name=t('Xu hướng', 'トレンド'), 
                            line=dict(dash='dash', color='#ef4444', width=2),
                            hoverinfo='skip'
                        ))

                    fig_t.update_layout(
                        font=dict(family="'Times New Roman', serif"),
                        margin=dict(l=0, r=0, t=5, b=25),
                        height=250,
                        showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='#f1f5f9', type='date', tickformat='%d/%m/%Y'),
                        yaxis=dict(gridcolor='#f1f5f9')
                    )
                    st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False}, key=f"time_{suffix_key}")

            st.markdown(f"<div style='font-size: 15px; font-weight: 600; color: #334155; margin-top: 15px; margin-bottom: 4px;'>{t('Danh Sách Chi Tiết', '明細一覧')}</div>", unsafe_allow_html=True)
            detail_df = df_t2[['clean_period', 'employee_name', 'ot_date', 'ot_hours', 'est_cost', 'ot_reason']].copy()
            detail_df = detail_df.sort_values(by=['clean_period', 'ot_date'], ascending=[False, False]).reset_index(drop=True)
            detail_df = detail_df.rename(columns={
                'clean_period': t('Tháng', '月'), 'employee_name': t('Tên NV', 'スタッフ'), 
                'ot_date': t('Ngày', '日'), 'ot_hours': t('Giờ', '時間'), 
                'est_cost': t('Chi Phí', 'コスト'), 'ot_reason': t('Lý Do', '理由')
            })
            detail_df[t('Giờ', '時間')] = detail_df[t('Giờ', '時間')].apply(lambda x: f"{x:,.1f}")
            detail_df[t('Chi Phí', 'コスト')] = detail_df[t('Chi Phí', 'コスト')].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
            st.dataframe(detail_df, use_container_width=True, hide_index=True, height=250, key=f"df_{suffix_key}")

        df_main, lbl_main = get_filtered_df(sel_project)
        
        if sel_project_compare != compare_opt:
            df_comp, lbl_comp = get_filtered_df(sel_project_compare)
            c1, c2 = st.columns(2)
            with c1:
                render_project_details(df_main, sel_project if sel_project != all_proj_opt else t('Tất cả dự án', 'すべてのプロジェクト'), lbl_main, "main")
            with c2:
                render_project_details(df_comp, sel_project_compare if sel_project_compare != all_proj_opt else t('Tất cả dự án', 'すべてのプロジェクト'), lbl_comp, "comp")
        else:
            render_project_details(df_main, sel_project if sel_project != all_proj_opt else t('Tất cả dự án', 'すべてのプロジェクト'), lbl_main, "single")

