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
    }
    [data-testid="stDataFrame"] { margin-top: -10px !important; }
    [data-testid="stDataFrame"] > div { margin-top: 0px !important; padding-top: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600; color: #1e293b; margin-bottom: 4px;'>{t('PHÂN BỔ & LỊCH SỬ DỰ ÁN (OT)', 'プロジェクト分析・履歴')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 14.5px; color: #64748b; margin-bottom: 20px;'>{t('Phân tích tỷ trọng giờ tăng ca và tra cứu chi tiết lịch sử từng dự án theo tháng/kỳ thanh toán.', 'プロジェクト別の残業時間分布と履歴を月別・案件別に詳細分析します。')}</div>", unsafe_allow_html=True)

    # Combine all records: historical + pending manual session + pending excel session
    hist_records = get_records("ot")
    manual_pending = st.session_state.get('ot_records', [])
    excel_pending = st.session_state.get('ot_excel_records', [])

    all_raw = copy.deepcopy(hist_records) + copy.deepcopy(manual_pending) + copy.deepcopy(excel_pending)
    all_records = deduplicate_records(all_raw, "ot")

    # Filter out deleted employees that might be stuck in session state
    try:
        from logic.employee_data import get_employees_df
        emp_df = get_employees_df()
        if not emp_df.empty and "Tên NV" in emp_df.columns:
            valid_names = set(emp_df["Tên NV"].dropna().astype(str).str.strip())
            all_records = [r for r in all_records if str(r.get("employee_name", "")).strip() in valid_names]
    except Exception:
        pass

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
    all_period_opt = t("Toàn bộ thời gian", "全期間")

    def format_period_range_label(df_sub, base_label):
        if df_sub.empty or base_label not in [all_period_opt, t("Toàn bộ thời gian", "全期間"), "Toàn bộ thời gian", "TOÀN BỘ THỜI GIAN", "全期間"]:
            return base_label
        ym_set = set()
        for _, row in df_sub.iterrows():
            cp = str(row.get('clean_period', '')).strip()
            if cp.startswith('T') and '/' in cp:
                parts = cp[1:].split('/')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    ym_set.add((int(parts[1]), int(parts[0])))
            pp = str(row.get('payment_period', '')).strip()
            if pp.startswith('T') and '/' in pp:
                parts = pp[1:].split('/')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    ym_set.add((int(parts[1]), int(parts[0])))
            d_str = str(row.get('ot_date', '')).strip()
            if d_str and d_str not in ['nan', 'None', '']:
                try:
                    dt = pd.to_datetime(d_str, dayfirst=True)
                    if pd.notna(dt):
                        ym_set.add((int(dt.year), int(dt.month)))
                except:
                    pass
        ym_list = sorted(list(ym_set))
        if not ym_list:
            return base_label
        min_ym = ym_list[0]
        max_ym = ym_list[-1]
        if min_ym == max_ym:
            return t(f"{base_label}: Kỳ T{min_ym[1]:02d}/{min_ym[0]}", f"{base_label}: {min_ym[0]}年{min_ym[1]}月分")
        else:
            return t(f"{base_label}: từ T{min_ym[1]:02d}/{min_ym[0]} đến T{max_ym[1]:02d}/{max_ym[0]}", f"{base_label}: {min_ym[0]}年{min_ym[1]}月 〜 {max_ym[0]}年{max_ym[1]}月")
    
    years = set()
    for p in unique_periods:
        p_str = str(p)
        if p_str.startswith('T') and '/' in p_str:
            parts = p_str[1:].split('/')
            if len(parts) == 2 and parts[1].isdigit():
                years.add(int(parts[1]))
    year_options = [t("Tất cả", "すべて")] + sorted(list(years), reverse=True)
    month_options = [t("Tất cả", "すべて")] + list(range(1, 13))

    tab1, tab2, tab3 = st.tabs([
        t("1. PHÂN BỔ DỰ ÁN & NGUỒN LỰC", "1. プロジェクトとリソースの配分"),
        t("2. TRA CỨU CHI TIẾT TỪNG DỰ ÁN", "2. プロジェクト別詳細分析"),
        t("3. TRA CỨU LỊCH SỬ NHÂN SỰ", "3. スタッフ別履歴")
    ])

    # ==================== TAB 1: PHÂN BỔ DỰ ÁN ====================
    with tab1:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        col_f1_y, col_f1_m, _ = st.columns([2, 2, 6])
        with col_f1_y:
            sel_year_t1 = st.selectbox(
                t(":material/calendar_today: Lọc theo Năm:", ":material/calendar_today: 年を選択:"),
                options=year_options,
                format_func=lambda x: f"{x}年" if st.session_state.get('lang', 'VN') == 'JP' and str(x).isdigit() else str(x),
                key="tab1_sel_year"
            )
        with col_f1_m:
            sel_month_t1 = st.selectbox(
                t(":material/calendar_month: Lọc theo Tháng:", ":material/calendar_month: 月を選択:"),
                options=month_options,
                format_func=lambda x: t(f"Tháng {x}", f"{x}月") if isinstance(x, int) else str(x),
                key="tab1_sel_month",
                help=t("Mẹo: Khi để Năm là 'Tất cả', hệ thống sẽ gộp chung dữ liệu của tháng này qua các năm.  \n👉 *Tiện lợi để phân tích tính mùa vụ*.", "ヒント: 「年」を「すべて」にすると、全年の該当月のデータを合算して表示します。  \n👉 *季節性の分析に便利です*。")
            )

        df_tab1 = df.copy()
        period_labels = []
        
        if sel_year_t1 not in ["Tất cả", "すべて"]:
            df_tab1 = df_tab1[df_tab1['clean_period'].astype(str).str.endswith(f"/{sel_year_t1}")]
            period_labels.append(str(sel_year_t1))
            
        if sel_month_t1 not in ["Tất cả", "すべて"]:
            m_val = int(str(sel_month_t1).replace("Tháng ", "").replace("月", "").strip())
            month_str = f"T{m_val:02d}/"
            df_tab1 = df_tab1[df_tab1['clean_period'].astype(str).str.startswith(month_str)]
            period_labels.append(t(f"Tháng {sel_month_t1}", f"{sel_month_t1}月"))
            
        if not period_labels:
            period_label = format_period_range_label(df_tab1, all_period_opt)
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
                        <span class="count-up-target-float" data-target="{total_hrs}">{total_hrs:,.1f}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>h</span>
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
                        <span class="count-up-target" data-target="{num_projects}">{num_projects}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>{t('dự án', '件')}</span>
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
                        <span class="count-up-target" data-target="{total_cost}">{total_cost:,.0f}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>VNĐ</span>
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
                        <span class="count-up-target" data-target="{num_staff}">{num_staff}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>{t('người', '名')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_pie, col_tbl = st.columns([5.5, 4.5], gap="large")
            
            top_contributors = df_tab1.groupby(['order_name', 'employee_name'])['ot_hours'].sum().reset_index()
            # Calculate max hours for each project
            max_hrs_df = top_contributors.groupby('order_name')['ot_hours'].max().reset_index()
            # Get all employees that have the max hours
            top_ties = pd.merge(top_contributors, max_hrs_df, on=['order_name', 'ot_hours'])
            
            def format_top_names(group):
                names = group['employee_name'].tolist()
                first_name = names[0]
                if len(names) > 1:
                    lang = st.session_state.get('lang', 'VN')
                    if lang == 'JP':
                        return f"{first_name} (+{len(names)-1}名)"
                    else:
                        return f"{first_name} (+{len(names)-1} người)"
                return first_name
                
            top_emp_str = top_ties.groupby('order_name').apply(format_top_names).reset_index(name='TopEmployee')
            top_contributors = pd.merge(max_hrs_df, top_emp_str, on='order_name')
            top_contributors = top_contributors.rename(columns={'ot_hours': 'TopEmployeeHours'})
            
            proj_summary = df_tab1.groupby('order_name').agg(
                Hours=('ot_hours', 'sum'),
                Cost=('est_cost', 'sum'),
                StaffCount=('employee_name', 'nunique')
            ).reset_index()
            proj_summary = pd.merge(proj_summary, top_contributors, on='order_name', how='left')
            proj_summary['Percentage'] = (proj_summary['Hours'] / total_hrs * 100.0).round(1)
            
            def format_top_hover(row):
                if pd.isna(row.get('TopEmployee')):
                    return t('Chưa có', 'なし')
                hrs = float(row.get('TopEmployeeHours', 0.0))
                return f"{row['TopEmployee']} ({hrs:.1f} h)"
            proj_summary['TopEmployeeHover'] = proj_summary.apply(format_top_hover, axis=1)
            proj_summary = proj_summary.sort_values(by='Hours', ascending=False).reset_index(drop=True)

            with col_pie:
                col_pie_hdr1, col_pie_hdr2 = st.columns([6, 4])
                with col_pie_hdr1:
                    st.markdown(f"<div style='display: flex; align-items: flex-start; gap: 6px; font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 4px;'><span style='flex-shrink: 0;'>🎯</span> <span>{t('Biểu đồ Tỷ trọng Giờ OT theo Dự án', 'プロジェクト別残業時間シェア')} <span style='display: inline-block;'>({period_label})</span></span></div>", unsafe_allow_html=True)
                with col_pie_hdr2:
                    st.markdown("""
                        <style>
                        div.element-container:has(.tab1-chart-radio) + div.element-container div[data-testid="stRadio"] div[role="radiogroup"] {
                            display: grid !important;
                            grid-template-columns: auto auto;
                            row-gap: 8px;
                            column-gap: 16px;
                            padding-left: 20px;
                        }
                        div.element-container:has(.tab1-chart-radio) + div.element-container div[data-testid="stRadio"] div[role="radiogroup"] label {
                            white-space: nowrap;
                        }
                        </style>
                        <div class="tab1-chart-radio"></div>
                    """, unsafe_allow_html=True)
                    chart_mode = st.radio(
                        "Chart mode",
                        options=[
                            t(":material/pie_chart: Tròn (Donut)", ":material/pie_chart: ドーナツ"),
                            t(":material/bar_chart: Cột (Bar)", ":material/bar_chart: 棒グラフ"),
                            t(":material/hub: Mạng lưới", ":material/hub: ネットワーク"),
                            t(":material/account_tree: Khối nhiệt", ":material/account_tree: ツリーマップ")
                        ],
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
                        color_discrete_sequence=curated_colors
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
                        customdata=pie_df[['TopEmployeeHover']].values,
                        hovertemplate='<b>%{label}</b><br>' + t('Số giờ', '残業時間') + ': %{value:,.1f} h (%{percent})<br>🌟 ' + t('Top nhân sự: ', 'トップスタッフ: ') + '<b>%{customdata[0]}</b><extra></extra>',
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
                elif chart_mode == t(":material/hub: Mạng lưới", ":material/hub: ネットワーク"):
                    try:
                        import networkx as nx
                        
                        df_net = df_tab1.copy()
                        df_net['employee_name'] = df_net['employee_name'].astype(str).str.strip()
                        df_net['order_name'] = df_net['order_name'].astype(str).str.strip()
                        
                        agg_df = df_net.groupby(['employee_name', 'order_name'])['ot_hours'].sum().reset_index()
                        agg_df = agg_df[agg_df['ot_hours'] > 0]
                        if not agg_df.empty:
                            G = nx.Graph()
                            proj_totals = agg_df.groupby('order_name')['ot_hours'].sum().to_dict()
                            emp_totals = agg_df.groupby('employee_name')['ot_hours'].sum().to_dict()
                            
                            max_p = max(proj_totals.values()) if proj_totals else 1
                            max_e = max(emp_totals.values()) if emp_totals else 1

                            for _, row in agg_df.iterrows():
                                emp = str(row['employee_name']).strip()
                                proj = str(row['order_name']).strip()
                                weight = row['ot_hours']
                                if not emp or not proj: continue
                                
                                G.add_node(proj, type='project', total=proj_totals[proj])
                                G.add_node(emp, type='employee', total=emp_totals[emp])
                                G.add_edge(emp, proj, weight=weight)
                                
                            try:
                                pos = nx.kamada_kawai_layout(G)
                            except:
                                pos = nx.spring_layout(G, k=0.8, iterations=150, seed=42, weight=None)
                            
                            edge_x, edge_y = [], []
                            for edge in G.edges():
                                x0, y0 = pos[edge[0]]
                                x1, y1 = pos[edge[1]]
                                edge_x.extend([x0, x1, None])
                                edge_y.extend([y0, y1, None])
                                
                            edge_trace = go.Scatter(
                                x=edge_x, y=edge_y,
                                line=dict(width=0.8, color='rgba(148, 163, 184, 0.4)'),
                                hoverinfo='none',
                                mode='lines'
                            )

                            node_x, node_y, node_hover, node_label, node_color, node_size, node_symbol = [], [], [], [], [], [], []
                            for node in G.nodes():
                                x, y = pos[node]
                                node_x.append(x)
                                node_y.append(y)
                                
                                node_type = G.nodes[node]['type']
                                total = G.nodes[node]['total']
                                
                                if node_type == 'project':
                                    short_node = str(node).strip()
                                    if len(short_node) > 20:
                                        short_node = short_node[:20] + '...'
                                            
                                    node_color.append('#0284c7')
                                    node_size.append(max(15, min(45, 15 + (total / max_p * 30))))
                                    node_symbol.append('diamond')
                                    node_hover.append(f"<b>DỰ ÁN: {node}</b><br>{t('Tổng OT', '総残業')}: {total:,.1f} h")
                                    node_label.append(f"<b>{short_node}</b>")
                                else:
                                    node_color.append('#f59e0b')
                                    node_size.append(max(10, min(25, 10 + (total / max_e * 15))))
                                    node_symbol.append('circle')
                                    node_hover.append(f"<b>NV: {node}</b><br>{t('Tổng OT', '総残業')}: {total:,.1f} h")
                                    name_parts = str(node).strip().split()
                                    short_name = name_parts[-1] if name_parts else str(node).strip()
                                    node_label.append(f"<b>{short_name}</b>")
                                    
                            node_trace = go.Scatter(
                                x=node_x, y=node_y,
                                mode='markers+text',
                                hoverinfo='text',
                                hovertext=node_hover,
                                text=node_label,
                                textposition='bottom center',
                                textfont=dict(size=11, color='#334155'),
                                marker=dict(
                                    showscale=False,
                                    color=node_color,
                                    size=node_size,
                                    symbol=node_symbol,
                                    line=dict(width=1.5, color='white')
                                )
                            )
                            
                            fig_net = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
                                title='', showlegend=False, hovermode='closest',
                                margin=dict(b=10, l=10, r=10, t=10),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                height=400,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            ))
                            st.plotly_chart(fig_net, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.info(t("Không có dữ liệu hợp lệ.", "有効なデータがありません。"))
                    except Exception as e:
                        st.error(t(f"Không thể tải mạng lưới: {str(e)}", f"ネットワークを読み込めません: {str(e)}"))
                elif chart_mode == t(":material/account_tree: Khối nhiệt", ":material/account_tree: ツリーマップ"):
                    tree_df = proj_summary[proj_summary['Hours'] > 0].copy()
                    if not tree_df.empty:
                        tree_df['AvgHours'] = tree_df['Hours'] / tree_df['StaffCount']
                        # Dùng text hiển thị tên viết gọn nếu quá dài
                        tree_df['ShortName'] = tree_df['order_name'].apply(lambda x: x if len(str(x)) <= 25 else str(x)[:25] + '...')
                        
                        fig_tree = px.treemap(
                            tree_df,
                            path=[px.Constant(t("Tất cả Dự án", "全プロジェクト")), 'ShortName'],
                            values='Hours',
                            color='AvgHours',
                            color_continuous_scale='YlOrRd',
                            custom_data=['StaffCount', 'AvgHours', 'Percentage', 'TopEmployeeHover', 'order_name']
                        )
                        
                        fig_tree.update_traces(
                            hovertemplate='<b>%{customdata[4]}</b><br>' + 
                                          t('Tổng giờ OT: ', '総残業: ') + '<b>%{value:,.1f} h</b> (%{customdata[2]}%)<br>' +
                                          t('Số nhân sự: ', 'スタッフ数: ') + '%{customdata[0]}<br>' +
                                          t('Trung bình/người: ', '1人あたり: ') + '<b>%{customdata[1]:,.1f} h</b><br>' +
                                          '🌟 ' + t('Top nhân sự: ', 'トップスタッフ: ') + '<b>%{customdata[3]}</b><extra></extra>',
                            textinfo="label+value",
                            texttemplate="<b>%{label}</b><br>%{value:,.1f}h",
                            textfont=dict(size=14),
                            marker=dict(line=dict(color='white', width=2))
                        )
                        
                        fig_tree.update_layout(
                            font=dict(family="'Times New Roman', serif"),
                            margin=dict(t=20, l=10, r=10, b=10),
                            height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            coloraxis_colorbar=dict(
                                title=dict(
                                    text=t("OT TB/Người", "平均残業/人"),
                                    font=dict(size=12, color='#1e293b')
                                ),
                                thicknessmode="pixels", thickness=15,
                                lenmode="pixels", len=200,
                                yanchor="middle", y=0.5,
                                ticks="outside",
                                tickfont=dict(size=11, color='#1e293b')
                            )
                        )
                        st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.info(t("Không có dữ liệu hợp lệ.", "有効なデータがありません。"))
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
                        customdata=bar_df[['Percentage', 'TopEmployeeHover']].values,
                        text=bar_df.apply(lambda r: f"{r['Hours']:,.1f} h ({r['Percentage']}%)", axis=1),
                        textposition=pos_list_t1,
                        textangle=0,
                        cliponaxis=False,
                        insidetextanchor='end',
                        insidetextfont=dict(size=12, color=text_colors_t1, weight='bold'),
                        outsidetextfont=dict(size=12, color='#0f172a', weight='bold'),
                        hovertemplate='<b>%{y}</b><br>' + t('Số giờ', '残業時間') + ': %{x:,.1f} h (%{customdata[0]}%)<br>🌟 ' + t('Top nhân sự: ', 'トップスタッフ: ') + '<b>%{customdata[1]}</b><extra></extra>'
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
                st.markdown(f"<div style='display: flex; align-items: flex-start; gap: 6px; font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 4px;'><span style='flex-shrink: 0;'>📋</span> <span>{t('Bảng Tổng Hợp Chi Tiết Dự Án', 'プロジェクト別集計表')}</span></div>", unsafe_allow_html=True)
                col_proj = t('Tên Dự Án', 'プロジェクト名')
                col_hrs = t('Số Giờ (h)', '時間 (h)')
                col_pct = t('Tỷ Lệ (%)', '割合 (%)')
                col_cost = t('Chi Phí VNĐ', '予想支出額')
                col_staff = t('Số NV', '人数')

                display_df = proj_summary.drop(columns=['TopEmployee', 'TopEmployeeHours', 'TopEmployeeHover'], errors='ignore').copy()
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

            st.markdown("<hr style='margin: 25px 0;'>", unsafe_allow_html=True)
            st.markdown(f"<div style='display: flex; align-items: flex-start; gap: 6px; font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 12px;'><span style='flex-shrink: 0;'>📊</span> <span>{t('Bảng Phân Bổ Nguồn Lực Chi Tiết (Giờ OT)', 'リソース配分マトリックス (残業時間)')}</span></div>", unsafe_allow_html=True)
            
            if not df_tab1.empty:
                matrix_df = df_tab1.pivot_table(
                    index='employee_name', 
                    columns='order_name', 
                    values='ot_hours', 
                    aggfunc='sum'
                ).fillna(0)
                
                if not matrix_df.empty:
                    matrix_df.index.name = t('Nhân Viên', 'スタッフ名')
                    col_total = t('Tổng (h)', '合計 (h)')
                    matrix_df[col_total] = matrix_df.sum(axis=1)
                    matrix_df = matrix_df.sort_values(col_total, ascending=False)
                    
                    proj_cols = [c for c in matrix_df.columns if c != col_total]
                    
                    def color_cells(val):
                        if val == 0:
                            return 'color: #cbd5e1; background-color: transparent;'
                        elif val < 10:
                            return 'background-color: #e0f2fe; color: #0284c7;'
                        elif val < 20:
                            return 'background-color: #bae6fd; color: #0369a1; font-weight: 500;'
                        elif val < 40:
                            return 'background-color: #38bdf8; color: #082f49; font-weight: 600;'
                        else:
                            return 'background-color: #0284c7; color: #ffffff; font-weight: 700;'
                            
                    if hasattr(matrix_df.style, 'map'):
                        styled_matrix = matrix_df.style.map(color_cells, subset=proj_cols).format("{:.1f}")
                    else:
                        styled_matrix = matrix_df.style.applymap(color_cells, subset=proj_cols).format("{:.1f}")
                        
                    st.dataframe(
                        styled_matrix,
                        use_container_width=True,
                        height=min(450, 45 + len(matrix_df) * 36)
                    )

    # ==================== TAB 2: TRA CỨU CHI TIẾT TỪNG DỰ ÁN ====================
    with tab2:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        unique_projects = sorted(df['order_name'].unique().tolist())
        all_proj_opt = t("❖ --- Tất cả dự án ---", "❖ --- すべてのプロジェクト ---")
        project_options = [all_proj_opt] + unique_projects

        def render_project_comparison_commentary(df_A, name_A, df_B, name_B, period_label, all_proj_opt):
            display_A = name_A if name_A != all_proj_opt else t('Tất cả dự án (A)', 'すべてのプロジェクト (A)')
            display_B = name_B if name_B != all_proj_opt else t('Tất cả dự án (B)', 'すべてのプロジェクト (B)')

            hrs_A = float(df_A['ot_hours'].sum()) if not df_A.empty else 0.0
            cost_A = float(df_A['est_cost'].sum()) if not df_A.empty else 0.0
            rate_A = cost_A / hrs_A if hrs_A > 0 else 0.0

            hrs_B = float(df_B['ot_hours'].sum()) if not df_B.empty else 0.0
            cost_B = float(df_B['est_cost'].sum()) if not df_B.empty else 0.0
            rate_B = cost_B / hrs_B if hrs_B > 0 else 0.0

            # Calculate high multiplier hours (>= 270%)
            def get_high_mult_info(df_sub):
                h_high = 0.0
                if df_sub.empty:
                    return 0.0
                for _, r in df_sub.iterrows():
                    # Check if explicit 'multiplier' field exists (e.g. from manual entry)
                    try:
                        mult_raw = str(r.get('multiplier', '')).replace('%', '').strip()
                        if mult_raw and mult_raw not in ['nan', 'None', '0', '0.0']:
                            m = float(mult_raw)
                            if m >= 270:
                                h_high += float(str(r.get('ot_hours', 0.0)).replace(',', '').strip())
                            continue
                    except:
                        pass

                    # Check breakdown percentage columns (e.g. from Excel grid where percentage keys store pay amounts)
                    try:
                        hr_rate = float(str(r.get('hourly_rate', 0.0)).replace(',', '').strip())
                    except:
                        hr_rate = 0.0
                    
                    row_ot_hrs = 0.0
                    try:
                        row_ot_hrs = float(str(r.get('ot_hours', 0.0)).replace(',', '').strip())
                    except:
                        pass

                    total_row_cost = get_record_cost(r)
                    
                    for k, v in r.items():
                        if str(k).endswith('%'):
                            try:
                                m = float(str(k).replace('%', '').strip())
                                if m >= 270:
                                    val = float(str(v).replace(',', '').strip())
                                    if val > 0:
                                        if hr_rate > 0 and m > 0:
                                            h_high += val / (hr_rate * (m / 100.0))
                                        elif total_row_cost > 0 and row_ot_hrs > 0:
                                            h_high += (val / total_row_cost) * row_ot_hrs
                            except:
                                pass
                return h_high

            high_A = get_high_mult_info(df_A)
            high_B = get_high_mult_info(df_B)
            pct_high_A = min(100.0, max(0.0, (high_A / hrs_A * 100.0) if hrs_A > 0 else 0.0))
            pct_high_B = min(100.0, max(0.0, (high_B / hrs_B * 100.0) if hrs_B > 0 else 0.0))

            # Resource intersection
            staff_A = set(df_A['employee_name'].astype(str).str.strip().unique()) if not df_A.empty else set()
            staff_B = set(df_B['employee_name'].astype(str).str.strip().unique()) if not df_B.empty else set()
            staff_A.discard('')
            staff_A.discard(t('Chưa rõ', '未定'))
            staff_B.discard('')
            staff_B.discard(t('Chưa rõ', '未定'))
            shared_staff = sorted(list(staff_A.intersection(staff_B)))

            # Narrative building
            # 1. Cost & Hours text
            if hrs_A == 0 and hrs_B == 0:
                cost_text = t("Cả hai dự án đều chưa phát sinh số giờ hay chi phí tăng ca nào trong kỳ này.", "両プロジェクトともに、この期間の残業時間や費用は発生していません。")
            else:
                diff_cost = cost_A - cost_B
                diff_rate = rate_A - rate_B
                if cost_A > cost_B:
                    cost_comp_str = t(f"tổng chi phí thực tế cao hơn <b>{diff_cost:,.0f} VNĐ</b>", f"実際の総費用は<b>{diff_cost:,.0f} VND</b>高い")
                elif cost_A < cost_B:
                    cost_comp_str = t(f"tổng chi phí thực tế thấp hơn <b>{abs(diff_cost):,.0f} VNĐ</b>", f"実際の総費用は<b>{abs(diff_cost):,.0f} VND</b>低い")
                else:
                    cost_comp_str = t("tổng chi phí thực tế tương đương nhau", "実際の総費用は同等")

                rate_reason_str = ""
                if abs(diff_rate) > 5000:
                    if rate_A > rate_B:
                        if pct_high_A == 0:
                            desc_A = t("hoàn toàn không phân bổ nhân viên làm OT vào cuối tuần hay ngày lễ (hệ số lương cao)", "休日や祝日（高倍率）の残業が全く割り当てられていません")
                        else:
                            desc_A = t(f"có tới <b>{pct_high_A:.1f}%</b> tổng số giờ là OT vào khung ngày nghỉ/Lễ (hệ số cao &ge; 270%)", f"休日/祝日 (高倍率 &ge; 270%) の残業割合が <b>{pct_high_A:.1f}%</b> を占めています")

                        if pct_high_B == 0:
                            desc_B = t("cũng hoàn toàn không có giờ OT hệ số cao" if pct_high_A == 0 else "lại hoàn toàn không phân bổ nhân viên làm OT vào cuối tuần hay ngày lễ", "また、高倍率の残業が全くありません" if pct_high_A == 0 else "一方で、休日や祝日（高倍率）の残業が全く割り当てられていません")
                        else:
                            desc_B = t(f"tỷ lệ này của <b>{display_B}</b> chỉ là <b>{pct_high_B:.1f}%</b>", f"<b>{display_B}</b> の割合は <b>{pct_high_B:.1f}%</b> です")

                        rate_reason_str = t(f"<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>arrow_forward</span><i>Nguyên nhân chênh lệch đơn giá:</i>&nbsp;Đơn giá bình quân của <b>{display_A}</b> ({rate_A:,.0f} VNĐ/h) đang <b>đắt hơn {diff_rate:,.0f} VNĐ/h</b> so với <b>{display_B}</b> ({rate_B:,.0f} VNĐ/h) do {desc_A}, trong khi {desc_B}.", 
                                          f"<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>arrow_forward</span><i>単価差異の原因:</i>&nbsp;<b>{display_A}</b> の平均単価 ({rate_A:,.0f} VND/時間) が <b>{display_B}</b> ({rate_B:,.0f} VND/時間) より <b>{diff_rate:,.0f} VND/時間高い</b>のは、{desc_A}ためです（{desc_B}）。")
                    else:
                        if pct_high_A == 0:
                            part_A = t("hoàn toàn không phân bổ nhân viên làm OT vào cuối tuần hay ngày lễ (hệ số lương cao)", "休日や祝日（高倍率）の残業が全く割り当てられていません")
                        else:
                            part_A = t(f"chỉ có <b>{pct_high_A:.1f}%</b> tổng số giờ là OT vào các khung giờ hệ số cao (cuối tuần/lễ)", f"高倍率時間帯（休日/祝日）の残業は <b>{pct_high_A:.1f}%</b> のみです")
                            
                        if pct_high_B == 0:
                            part_B = t("dự án kia cũng hoàn toàn không có", "対象プロジェクトも全く割り当てられていません")
                        else:
                            part_B = t(f"tỷ lệ này của <b>{display_B}</b> lên tới <b>{pct_high_B:.1f}%</b>", f"<b>{display_B}</b> の割合は <b>{pct_high_B:.1f}%</b> に達しています")

                        rate_reason_str = t(f"<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>arrow_forward</span><i>Nguyên nhân chênh lệch đơn giá:</i>&nbsp;Đơn giá bình quân của <b>{display_A}</b> ({rate_A:,.0f} VNĐ/h) đang <b>tiết kiệm hơn {abs(diff_rate):,.0f} VNĐ/h</b> so với <b>{display_B}</b> ({rate_B:,.0f} VNĐ/h) nhờ ưu tiên phân bổ vào khung giờ ngày thường (hệ số thấp). Cụ thể, dự án này {part_A}, trong khi {part_B}.", 
                                          f"<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>arrow_forward</span><i>単価差異の原因:</i>&nbsp;<b>{display_A}</b> の平均単価 ({rate_A:,.0f} VND/時間) は通常時間帯を優先したため、<b>{display_B}</b> ({rate_B:,.0f} VND/時間) より <b>{abs(diff_rate):,.0f} VND/時間お得</b>です。具体的に、このプロジェクトは{part_A}（{part_B}）。")

                is_all_time = (period_label == all_period_opt or period_label == t("Toàn bộ thời gian", "全期間") or period_label == t("🌟 Tất cả các tháng", "🌟 すべての月") or str(period_label).strip().lower().startswith("toàn bộ thời gian") or str(period_label).strip().startswith("全期間"))
                if is_all_time:
                    df_comb = pd.concat([df_A, df_B], ignore_index=True) if not df_A.empty or not df_B.empty else df_A
                    comb_label = format_period_range_label(df_comb, all_period_opt)
                    range_str = comb_label.replace(all_period_opt, "").strip(" :-()")
                    time_desc_vn = f"Tính trên toàn bộ thời gian (từ {range_str})" if range_str and "từ" not in range_str.lower() and "kỳ" not in range_str.lower() else (f"Tính trên toàn bộ thời gian ({range_str})" if range_str else "Tính trên toàn bộ thời gian")
                    time_desc_jp = f"全期間 ({range_str}) の合計" if range_str else "全期間の合計"
                    cost_text = t(
                        f"<b>{time_desc_vn}</b>, <b>{display_A}</b> ghi nhận <b>{hrs_A:,.1f} giờ OT</b> (tổng tiền <b>{cost_A:,.0f} VNĐ</b>), trong khi <b>{display_B}</b> ghi nhận <b>{hrs_B:,.1f} giờ OT</b> (tổng tiền <b>{cost_B:,.0f} VNĐ</b>).<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>leaderboard</span>Như vậy, <b>{display_A}</b> có {cost_comp_str} so với <b>{display_B}</b>.{rate_reason_str}",
                        f"<b>{time_desc_jp}</b>において、<b>{display_A}</b> は <b>{hrs_A:,.1f}時間の残業</b> (費用 <b>{cost_A:,.0f} VND</b>) であり、<b>{display_B}</b> は <b>{hrs_B:,.1f}時間</b> (費用 <b>{cost_B:,.0f} VND</b>) を記録しました。<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>leaderboard</span>結果として、<b>{display_A}</b> は <b>{display_B}</b> と比べ {cost_comp_str} です。{rate_reason_str}"
                    )
                else:
                    cost_text = t(
                        f"Trong kỳ <b>{period_label}</b>, <b>{display_A}</b> ghi nhận <b>{hrs_A:,.1f} giờ OT</b> (tổng tiền <b>{cost_A:,.0f} VNĐ</b>), trong khi <b>{display_B}</b> ghi nhận <b>{hrs_B:,.1f} giờ OT</b> (tổng tiền <b>{cost_B:,.0f} VNĐ</b>).<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>leaderboard</span>Như vậy, <b>{display_A}</b> có {cost_comp_str} so với <b>{display_B}</b>.{rate_reason_str}",
                        f"期間 <b>{period_label}</b> 中、<b>{display_A}</b> は <b>{hrs_A:,.1f}時間の残業</b> (費用 <b>{cost_A:,.0f} VND</b>) であり、<b>{display_B}</b> は <b>{hrs_B:,.1f}時間</b> (費用 <b>{cost_B:,.0f} VND</b>) を記録しました。<br><span class='material-symbols-rounded' style='font-size: 18px; color: #0284c7; vertical-align: -4px; margin-right: 4px;'>leaderboard</span>結果として、<b>{display_A}</b> は <b>{display_B}</b> と比べ {cost_comp_str} です。{rate_reason_str}"
                    )

            # 2. Resource & Intersection text
            if len(shared_staff) > 0:
                shared_names_str = ", ".join([f"<b>{s}</b>" for s in shared_staff[:4]])
                if len(shared_staff) > 4:
                    shared_names_str += t(f" và {len(shared_staff)-4} người khác", f" 他{len(shared_staff)-4}名")
                
                shared_hrs_A = df_A[df_A['employee_name'].isin(shared_staff)]['ot_hours'].sum() if not df_A.empty else 0
                shared_hrs_B = df_B[df_B['employee_name'].isin(shared_staff)]['ot_hours'].sum() if not df_B.empty else 0
                
                resource_text = t(
                    f"<span class='material-symbols-rounded' style='font-size: 20px; color: #d97706; vertical-align: -5px; margin-right: 5px;'>handshake</span><b>Sự giao thoa nhân sự:</b>&nbsp;Phát hiện có <b>{len(shared_staff)} nhân sự nòng cốt</b> ({shared_names_str}) đang cống hiến OT cho <b>CẢ 2 DỰ ÁN</b> trong phạm vi thời gian này (đóng góp {shared_hrs_A:,.1f}h bên <b>{display_A}</b> và {shared_hrs_B:,.1f}h bên <b>{display_B}</b>).<br><span class='material-symbols-rounded' style='font-size: 18px; color: #d97706; vertical-align: -4px; margin-right: 4px;'>warning</span><i>Khuyến nghị điều phối:</i>&nbsp;Việc hai dự án cùng chia sẻ nhân sự nòng cốt cần được lưu ý sắp xếp lịch trình hợp lý để tránh quá tải hoặc kiệt sức cho nhóm nhân sự này.",
                    f"<span class='material-symbols-rounded' style='font-size: 20px; color: #d97706; vertical-align: -5px; margin-right: 5px;'>handshake</span><b>人的リソースの重複:</b>&nbsp;対象期間において、<b>{len(shared_staff)}名の中核スタッフ</b> ({shared_names_str}) が <b>両方のプロジェクト</b> に従事していることが確認されました (<b>{display_A}</b> で {shared_hrs_A:,.1f}時間、<b>{display_B}</b> で {shared_hrs_B:,.1f}時間貢献)。<br><span class='material-symbols-rounded' style='font-size: 18px; color: #d97706; vertical-align: -4px; margin-right: 4px;'>warning</span><i>推奨事項:</i>&nbsp;双方のプロジェクトで中核人材を共有しているため、過労や業務遅延を防ぐためのスケジュール調整が必要です。"
                )
            else:
                resource_text = t(
                    f"<span class='material-symbols-rounded' style='font-size: 20px; color: #0284c7; vertical-align: -5px; margin-right: 5px;'>groups</span><b>Phân bổ đội ngũ độc lập:</b>&nbsp;Hai dự án sử dụng hai lực lượng nhân sự hoàn toàn riêng biệt (<b>{len(staff_A)} người</b> tham gia bên <b>{display_A}</b> và <b>{len(staff_B)} người</b> bên <b>{display_B}</b>). Không xảy ra tình trạng chồng chéo hay chia sẻ nhân sự giữa 2 bên trong phạm vi thời gian này.",
                    f"<span class='material-symbols-rounded' style='font-size: 20px; color: #0284c7; vertical-align: -5px; margin-right: 5px;'>groups</span><b>独立した人員配置:</b>&nbsp;両プロジェクトは完全に独立したスタッフ構成で作動しています (<b>{display_A}</b> に <b>{len(staff_A)}名</b>、<b>{display_B}</b> に <b>{len(staff_B)}名</b>)。対象期間において、両者間での人的リソースの重複はありません。"
                )

            # 3. Smart Verdict Badge
            if rate_A > 0 and rate_B > 0 and abs(rate_A - rate_B) > 1000:
                if rate_A < rate_B:
                    verdict_winner = display_A
                    verdict_rate = rate_A
                    verdict_save = (rate_B - rate_A) / rate_B * 100.0
                else:
                    verdict_winner = display_B
                    verdict_rate = rate_B
                    verdict_save = (rate_A - rate_B) / rate_A * 100.0
                
                verdict_text = t(
                    f"<b>Chẩn đoán đơn giá bình quân tối ưu hơn:</b>&nbsp;<span style='color: #0284c7; font-weight: 800; font-size: 15.5px;'>{verdict_winner}</span> ({verdict_rate:,.0f} VNĐ/h, tiết kiệm hơn {verdict_save:.1f}%)",
                    f"<b>より平均単価がお得:</b>&nbsp;<span style='color: #0284c7; font-weight: 800; font-size: 15.5px;'>{verdict_winner}</span> ({verdict_rate:,.0f} VND/時間、{verdict_save:.1f}% コスト優位)"
                )
            else:
                verdict_text = t("<b>Chẩn đoán:</b>&nbsp;Đơn giá bình quân của hai dự án đang ở mức cân bằng tương đương nhau.", "<b>評価:</b>&nbsp;両プロジェクトの平均単価は同等レベルにバランスされています。")

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
                        border: 1.5px solid #00B0F0; border-radius: 14px;
                        padding: 22px 26px; margin-top: 10px; margin-bottom: 24px;
                        box-shadow: 0 8px 25px rgba(0, 176, 240, 0.12);">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 14px;">
                    <span style="font-size: 26px;">🔬</span>
                    <span style="font-size: 17.5px; font-weight: 800; color: #0284c7; letter-spacing: 0.3px; text-transform: uppercase;">
                        {t('Báo cáo Phân tích đối chứng chuyên sâu', 'プロジェクト別 深度比較分析 & 運用効率評価')}
                    </span>
                </div>
                <div style="font-size: 14.5px; color: #334155; line-height: 1.75; display: flex; flex-direction: column; gap: 14px;">
                    <div><span class='material-symbols-rounded' style='font-size: 20px; color: #0284c7; vertical-align: -5px; margin-right: 5px;'>payments</span>{cost_text}</div>
                    <div>{resource_text}</div>
                    <div style="background: #e0f2fe; padding: 12px 18px; border-radius: 10px; border-left: 4.5px solid #0284c7; margin-top: 4px; display: flex; align-items: center; gap: 8px;">
                        <span class='material-symbols-rounded' style='font-size: 24px; color: #0284c7;'>emoji_events</span>
                        <div style="flex: 1; line-height: 1.6;">{verdict_text}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        def render_radar_chart(df_A, name_A, df_B, name_B, all_proj_opt):
            import plotly.graph_objects as go
            
            display_A = name_A if name_A != all_proj_opt else t('Tất cả dự án (A)', 'すべてのプロジェクト (A)')
            display_B = name_B if name_B != all_proj_opt else t('Tất cả dự án (B)', 'すべてのプロジェクト (B)')
            
            def safe_div(a, b): return a / b if b > 0 else 0.0

            h_A = df_A['ot_hours'].sum() if not df_A.empty else 0
            h_B = df_B['ot_hours'].sum() if not df_B.empty else 0
            c_A = df_A['est_cost'].sum() if not df_A.empty else 0
            c_B = df_B['est_cost'].sum() if not df_B.empty else 0
            s_A = df_A['employee_name'].nunique() if not df_A.empty else 0
            s_B = df_B['employee_name'].nunique() if not df_B.empty else 0
            r_A = safe_div(c_A, h_A)
            r_B = safe_div(c_B, h_B)
            d_A = df_A['ot_date'].nunique() if not df_A.empty else 0
            d_B = df_B['ot_date'].nunique() if not df_B.empty else 0
            
            def norm(v_A, v_B):
                m = max(v_A, v_B)
                if m == 0: return 0.0, 0.0
                return (v_A/m)*100, (v_B/m)*100

            nh_A, nh_B = norm(h_A, h_B)
            nc_A, nc_B = norm(c_A, c_B)
            ns_A, ns_B = norm(s_A, s_B)
            nr_A, nr_B = norm(r_A, r_B)
            nd_A, nd_B = norm(d_A, d_B)
            
            categories = [
                t('Tổng Giờ', '総時間'),
                t('Tổng Chi Phí', '総費用'),
                t('Số Nhân Sự', '人員数'),
                t('Đơn Giá/h', '時間単価'),
                t('Số Ngày OT', '残業日数')
            ]
            categories += [categories[0]]
            
            r_vals_A = [nh_A, nc_A, ns_A, nr_A, nd_A]
            r_vals_A += [r_vals_A[0]]
            t_vals_A = [f"{h_A:,.1f} h", f"{c_A:,.0f} đ", f"{s_A} ng", f"{r_A:,.0f} đ/h", f"{d_A} ngày"]
            t_vals_A += [t_vals_A[0]]
            
            r_vals_B = [nh_B, nc_B, ns_B, nr_B, nd_B]
            r_vals_B += [r_vals_B[0]]
            t_vals_B = [f"{h_B:,.1f} h", f"{c_B:,.0f} đ", f"{s_B} ng", f"{r_B:,.0f} đ/h", f"{d_B} ngày"]
            t_vals_B += [t_vals_B[0]]
            
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=r_vals_A,
                theta=categories,
                fill='toself',
                name=display_A,
                hoverinfo="text",
                text=t_vals_A,
                line=dict(color='#0284c7'),
                fillcolor='rgba(2, 132, 199, 0.3)'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=r_vals_B,
                theta=categories,
                fill='toself',
                name=display_B,
                hoverinfo="text",
                text=t_vals_B,
                line=dict(color='#f59e0b'),
                fillcolor='rgba(245, 158, 11, 0.3)'
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
                    angularaxis=dict(tickfont=dict(size=12, color='#334155'))
                ),
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                margin=dict(l=40, r=40, t=50, b=80),
                height=370,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="'Times New Roman', serif")
            )
            
            st.markdown(f"<div style='text-align: center; font-size: 16px; font-weight: 700; color: #334155; margin-top: 40px; margin-bottom: -20px;'><span class='material-symbols-rounded' style='vertical-align: -5px; font-size: 22px; color: #0284c7;'>radar</span> {t('Biểu đồ Phân Tích Tương Quan Đa Chiều (Radar)', '多次元相関分析チャート (レーダー)')}</div>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"radar_{display_A}_{display_B}")

        def render_project_details(df_t2, proj_name, sel_period_t2_label, all_proj_opt, all_period_opt, is_compare=False):
            if df_t2.empty or df_t2['ot_hours'].sum() <= 0:
                from components.ui_utils import render_empty_state
                render_empty_state(t('Không tìm thấy bản ghi OT nào phù hợp với bộ lọc.', '条件に一致する残業データがありません。'), icon="search_off", height=120)
                return

            p_hrs = df_t2['ot_hours'].sum()
            p_cost = df_t2['est_cost'].sum()
            p_staff = df_t2['employee_name'].nunique()
            p_records = len(df_t2)

            display_period_label = format_period_range_label(df_t2, sel_period_t2_label) if sel_period_t2_label == all_period_opt else sel_period_t2_label

            min_h = "height: 80px; display: flex; align-items: flex-start; overflow: hidden;" if is_compare else ""
            
            # CSS for Micro-animations (Idea 5)
            st.markdown("""
            <style>
            .kpi-t2-card-1, .kpi-t2-card-2, .kpi-t2-card-3, .kpi-t2-card-4 {
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
                opacity: 0;
            }
            .kpi-t2-card-1:hover, .kpi-t2-card-2:hover, .kpi-t2-card-3:hover, .kpi-t2-card-4:hover {
                transform: translateY(-4px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important;
            }
            @keyframes fadeInUpCards {
                from { opacity: 0; transform: translateY(15px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .kpi-t2-card-1 { animation: fadeInUpCards 0.4s ease-out forwards; }
            .kpi-t2-card-2 { animation: fadeInUpCards 0.5s ease-out forwards; }
            .kpi-t2-card-3 { animation: fadeInUpCards 0.6s ease-out forwards; }
            .kpi-t2-card-4 { animation: fadeInUpCards 0.7s ease-out forwards; }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <h3 style='font-size: 18px; margin-bottom: 20px; {min_h}'>
                <div>{proj_name if proj_name != all_proj_opt else t('Tất cả dự án', 'すべてのプロジェクト')} <span style='display: inline-block;'>({display_period_label})</span></div>
            </h3>
            """, unsafe_allow_html=True)

            if is_compare:
                ck1, ck2 = st.columns(2)
                ck3, ck4 = st.columns(2)
                cols_k = [ck1, ck2, ck3, ck4]
            else:
                cols_k = st.columns(4)

            with cols_k[0]:
                pad_kpi = "8px 12px" if is_compare else "12px 16px"
                marg_kpi = "8px" if is_compare else "15px"
                
                st.markdown(f"""
                <div class='kpi-t2-card-1' style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; border-radius: 8px; padding: {pad_kpi}; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: {marg_kpi};'>
                    <div style='font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; display: flex; align-items: center; gap: 6px;'><span class="material-symbols-rounded" style="font-size: 18px; color: #0284c7;">schedule</span>{t('Tổng Số Giờ OT', '総残業時間')}</div>
                    <div style='font-size: 20px; font-weight: 800; color: #0f172a; margin: 4px 0;'><span class="count-up-target-float" data-target="{p_hrs}">{p_hrs:,.1f}</span> <span style='font-size: 14.5px; font-weight: 600; color: #475569;'>h</span></div>
                    <div style='font-size: 12px; color: #475569;'>{t('TB:', '平均:')} <b>{p_hrs/p_records:,.1f} h</b>/{t('lượt', '回')}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols_k[1]:
                st.markdown(f"""
                <div class='kpi-t2-card-2' style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; border-radius: 8px; padding: {pad_kpi}; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: {marg_kpi};'>
                    <div style='font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; display: flex; align-items: center; gap: 6px;'><span class="material-symbols-rounded" style="font-size: 18px; color: #8b5cf6;">group</span>{t('Nhân Sự Tham Gia', '参加スタッフ数')}</div>
                    <div style='font-size: 20px; font-weight: 800; color: #0f172a; margin: 4px 0;'><span class="count-up-target" data-target="{p_staff}">{p_staff}</span> <span style='font-size: 14.5px; font-weight: 600; color: #475569;'>{t('người', '名')}</span></div>
                    <div style='font-size: 12px; color: #475569;'><b>{p_records}</b> {t('lượt ghi nhận OT', '件の残業記録')}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols_k[2]:
                st.markdown(f"""
                <div class='kpi-t2-card-3' style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; border-radius: 8px; padding: {pad_kpi}; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: {marg_kpi};'>
                    <div style='font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; display: flex; align-items: center; gap: 6px;'><span class="material-symbols-rounded" style="font-size: 18px; color: #10b981;">payments</span>{t('Dự Tính Chi Phí', '予想コスト')}</div>
                    <div style='font-size: 20px; font-weight: 800; color: #0f172a; margin: 4px 0;'><span class="count-up-target" data-target="{p_cost}">{p_cost:,.0f}</span> <span style='font-size: 14.5px; font-weight: 600; color: #475569;'>VNĐ</span></div>
                    <div style='font-size: 12px; color: #475569;'>{t('Dựa trên đơn giá OT', '残業単価に基づく')}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols_k[3]:
                st.markdown(f"""
                <div class='kpi-t2-card-4' style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #f59e0b; border-radius: 8px; padding: {pad_kpi}; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: {marg_kpi};'>
                    <div style='font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; display: flex; align-items: center; gap: 6px;'><span class="material-symbols-rounded" style="font-size: 18px; color: #f59e0b;">calendar_month</span>{t('Tần Suất Làm Việc', '残業頻度')}</div>
                    <div style='font-size: 20px; font-weight: 800; color: #0f172a; margin: 4px 0;'><span class="count-up-target" data-target="{df_t2['ot_date'].nunique()}">{df_t2['ot_date'].nunique()}</span> <span style='font-size: 14.5px; font-weight: 600; color: #475569;'>{t('ngày', '日')}</span></div>
                    <div style='font-size: 12px; color: #475569;'>{t('Có phát sinh OT', '残業発生日数')}</div>
                </div>
                """, unsafe_allow_html=True)

            if is_compare:
                st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
                c_left, c_right = st.container(), st.container()
            else:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                c_left, c_right = st.columns([5, 5], gap="large")

            staff_contrib = df_t2.groupby('employee_name').agg(
                Hours=('ot_hours', 'sum')
            ).reset_index().sort_values(by='Hours', ascending=True)

            base_chart_h = 160 if is_compare else 300
            mult_chart_h = 28 if is_compare else 38
            shared_chart_height = max(base_chart_h, len(staff_contrib) * mult_chart_h)

            with c_left:
                st.markdown(f"<div style='display: flex; align-items: center; font-size: 15.5px; font-weight: 600; color: #334155; margin-bottom: 8px;'><span class='material-symbols-rounded' style='margin-right: 6px; font-size: 20px; color: #0284c7;'>groups</span> {t('Biểu đồ Phân Bổ Số Giờ', 'スタッフ別残業時間グラフ')}</div>", unsafe_allow_html=True)
                max_hrs_t2 = staff_contrib['Hours'].max() if not staff_contrib.empty else 0
                bar_w_t2 = 0.25 if len(staff_contrib) == 1 else (0.35 if len(staff_contrib) == 2 else (0.45 if len(staff_contrib) == 3 else None))
                text_colors_t2 = ['#ffffff' if i == len(staff_contrib) - 1 else '#0f172a' for i in range(len(staff_contrib))]
                pos_list_t2 = ['inside' if (max_hrs_t2 > 0 and staff_contrib.iloc[i]['Hours'] >= 0.35 * max_hrs_t2) else 'outside' for i in range(len(staff_contrib))]
                fig_bar = go.Figure(go.Bar(
                    x=staff_contrib['Hours'],
                    y=staff_contrib['employee_name'],
                    orientation='h',
                    width=bar_w_t2,
                    marker=dict(
                        color=staff_contrib['Hours'],
                        colorscale=[[0, '#7dd3fc'], [1, '#0284c7']],
                    ),
                    text=staff_contrib['Hours'].apply(lambda x: f"{x:,.1f} h"),
                    textposition=pos_list_t2,
                    textangle=0,
                    cliponaxis=False,
                    insidetextanchor='end',
                    insidetextfont=dict(size=12, color=text_colors_t2, weight='bold'),
                    outsidetextfont=dict(size=12, color='#0f172a', weight='bold')
                ))
                fig_bar.update_layout(
                    font=dict(family="'Times New Roman', serif"),
                    margin=dict(l=0, r=45, t=10, b=10),
                    height=shared_chart_height,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(title=t("Số giờ (h)", "時間 (h)"), gridcolor='#f1f5f9'),
                    yaxis=dict(tickfont=dict(size=12, color='#1e293b'))
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False}, key=f"bar_{proj_name}_{'comp' if is_compare else 'main'}")

            with c_right:
                if is_compare:
                    st.markdown("<hr style='margin-top: 15px; margin-bottom: 15px;'>", unsafe_allow_html=True)
                
                st.markdown(f"<div style='display: flex; align-items: center; font-size: 15.5px; font-weight: 600; color: #334155; margin-bottom: 8px;'><span class='material-symbols-rounded' style='margin-right: 6px; font-size: 20px; color: #f59e0b;'>show_chart</span> {t('Biểu đồ Diễn Biến Theo Thời Gian', '日別残業時間の推移グラフ')}</div>", unsafe_allow_html=True)
                time_df = df_t2.groupby('ot_date')['ot_hours'].sum().reset_index()
                time_df['_sort_dt'] = pd.to_datetime(time_df['ot_date'], format='%d/%m/%Y', errors='coerce')
                time_df = time_df.sort_values(by='_sort_dt', ascending=True).drop(columns=['_sort_dt'])

                if time_df.empty:
                    from components.ui_utils import render_empty_state
                    render_empty_state(t("Chưa có dữ liệu thời gian", "時系列データがありません"), height=shared_chart_height-40)
                else:
                    bar_w_t = 0.25 if len(time_df) == 1 else (0.35 if len(time_df) == 2 else (0.45 if len(time_df) == 3 else None))
                    fig_t = go.Figure(go.Bar(
                        x=time_df['ot_date'],
                        y=time_df['ot_hours'],
                        width=bar_w_t,
                        marker=dict(
                            color=time_df['ot_hours'],
                            colorscale=[[0, '#fde047'], [1, '#ca8a04']],
                        ),
                        text=time_df['ot_hours'].apply(lambda x: f"{x:,.1f} h"),
                        textposition='auto',
                        textfont=dict(size=11, color='#0f172a', weight='bold')
                    ))
                    fig_t.update_layout(
                        font=dict(family="'Times New Roman', serif"),
                        margin=dict(l=0, r=10, t=10, b=25),
                        height=shared_chart_height,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(title=t("Ngày OT", "残業日"), gridcolor='#f1f5f9'),
                        yaxis=dict(title=t("Số giờ (h)", "時間 (h)"), gridcolor='#f1f5f9')
                    )
                    st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False}, key=f"time_{proj_name}_{'comp' if is_compare else 'main'}")

            if not is_compare:
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            else:
                st.markdown("<hr style='margin-top: 15px; margin-bottom: 15px;'>", unsafe_allow_html=True)
            
            show_proj_col = (proj_name == all_proj_opt)
            cols_to_select = ['clean_period', 'order_name', 'employee_name', 'ot_date', 'ot_hours', 'est_cost', 'manager_name', 'ot_reason'] if show_proj_col else ['clean_period', 'employee_name', 'ot_date', 'ot_hours', 'est_cost', 'manager_name', 'ot_reason']
            
            detail_df = df_t2[cols_to_select].copy()
            detail_df = detail_df.sort_values(by=['clean_period', 'ot_date'], ascending=[False, False]).reset_index(drop=True)
            
            rename_map = {
                'clean_period': t('Tháng/Kỳ', '月'),
                'order_name': t('Tên Dự Án', 'プロジェクト名'),
                'employee_name': t('Tên NV', 'スタッフ名'),
                'ot_date': t('Ngày OT', '残業日'),
                'ot_hours': t('Số Giờ', '時間'),
                'est_cost': t('Chi Phí VNĐ', '予想支出額'),
                'manager_name': t('PM', 'PM'),
                'ot_reason': t('Lý Do', '残業理由')
            }
            detail_df = detail_df.rename(columns=rename_map)
            detail_df[t('Số Giờ', '時間')] = detail_df[t('Số Giờ', '時間')].apply(lambda x: f"{x:,.1f}")
            detail_df[t('Chi Phí VNĐ', '予想支出額')] = detail_df[t('Chi Phí VNĐ', '予想支出額')].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")

            col_cfg = {
                t('Tháng/Kỳ', '月'): st.column_config.TextColumn(t('Tháng/Kỳ', '月'), width=55),
                t('Tên Dự Án', 'プロジェクト名'): st.column_config.TextColumn(t('Tên Dự Án', 'プロジェクト名'), width=260),
                t('Tên NV', 'スタッフ名'): st.column_config.TextColumn(t('Tên NV', 'スタッフ名'), width=125),
                t('Ngày OT', '残業日'): st.column_config.TextColumn(t('Ngày OT', '残業日'), width=75),
                t('Số Giờ', '時間'): st.column_config.TextColumn(t('Số Giờ', '時間'), width=55),
                t('Chi Phí VNĐ', '予想支出額'): st.column_config.TextColumn(t('Chi Phí VNĐ', '予想支出額'), width=85),
                t('PM', 'PM'): st.column_config.TextColumn(t('PM', 'PM'), width=180),
                t('Lý Do', '残業理由'): st.column_config.TextColumn(t('Lý Do', '残業理由'))
            }

            st.dataframe(
                detail_df,
                use_container_width=True,
                hide_index=True,
                height=max(200, min(350, len(detail_df) * 38)) if is_compare else max(280, min(400, len(detail_df) * 38)),
                column_config=col_cfg
            )

        col_t2_1, col_t2_compare, col_t2_y, col_t2_m = st.columns([3, 3, 2, 2])
        with col_t2_1:
            sel_project = st.selectbox(
                t("📌 Chọn Dự Án Cần Tra Cứu:", "📌 プロジェクトを選択:"),
                options=project_options,
                key="tab2_sel_project"
            )
        with col_t2_compare:
            compare_options = [t("✖ Không so sánh", "✖ 比較しない")] + unique_projects
            sel_project_compare = st.selectbox(
                t("⚖️ Dự Án So Sánh:", "⚖️ 比較プロジェクト:"),
                options=compare_options,
                key="tab2_sel_project_compare"
            )
        with col_t2_y:
            sel_year_t2 = st.selectbox(
                t(":material/calendar_today: Lọc theo Năm:", ":material/calendar_today: 年を選択:"),
                options=year_options,
                format_func=lambda x: f"{x}年" if st.session_state.get('lang', 'VN') == 'JP' and str(x).isdigit() else str(x),
                key="tab2_sel_year"
            )
        with col_t2_m:
            sel_month_t2 = st.selectbox(
                t(":material/calendar_month: Lọc theo Tháng:", ":material/calendar_month: 月を選択:"),
                options=month_options,
                format_func=lambda x: t(f"Tháng {x}", f"{x}月") if isinstance(x, int) else str(x),
                key="tab2_sel_month",
                help=t("Mẹo: Khi để Năm là 'Tất cả', hệ thống sẽ gộp chung dữ liệu của tháng này qua các năm.", "ヒント: 全年の該当月のデータを合算して表示します。")
            )

        # Build period label
        period_labels_t2 = []
        if sel_year_t2 not in ["Tất cả", "すべて"]:
            period_labels_t2.append(str(sel_year_t2))
        if sel_month_t2 not in ["Tất cả", "すべて"]:
            period_labels_t2.append(t(f"Tháng {sel_month_t2}", f"{sel_month_t2}月"))
        sel_period_t2_label = " - ".join(period_labels_t2) if period_labels_t2 else all_period_opt

        # Build main df
        df_t2_main = df.copy()
        if sel_project != all_proj_opt:
            df_t2_main = df_t2_main[df_t2_main['order_name'] == sel_project]
        if sel_year_t2 not in ["Tất cả", "すべて"]:
            df_t2_main = df_t2_main[df_t2_main['clean_period'].astype(str).str.endswith(f"/{sel_year_t2}")]
        if sel_month_t2 not in ["Tất cả", "すべて"]:
            m_val = int(str(sel_month_t2).replace("Tháng ", "").replace("月", "").strip())
            month_str = f"T{m_val:02d}/"
            df_t2_main = df_t2_main[df_t2_main['clean_period'].astype(str).str.startswith(month_str)]

        if sel_project_compare != t("✖ Không so sánh", "✖ 比較しない"):
            df_t2_comp = df.copy()
            if sel_project_compare != all_proj_opt:
                df_t2_comp = df_t2_comp[df_t2_comp['order_name'] == sel_project_compare]
            if sel_year_t2 not in ["Tất cả", "すべて"]:
                df_t2_comp = df_t2_comp[df_t2_comp['clean_period'].astype(str).str.endswith(f"/{sel_year_t2}")]
            if sel_month_t2 not in ["Tất cả", "すべて"]:
                m_val = int(str(sel_month_t2).replace("Tháng ", "").replace("月", "").strip())
                month_str = f"T{m_val:02d}/"
                df_t2_comp = df_t2_comp[df_t2_comp['clean_period'].astype(str).str.startswith(month_str)]

            # Render 3-Way AI Executive Commentary and Radar Chart Side-by-Side
            c_rep, c_rad = st.columns([5.5, 4.5], gap="large")
            with c_rep:
                render_project_comparison_commentary(df_t2_main, sel_project, df_t2_comp, sel_project_compare, sel_period_t2_label, all_proj_opt)
            with c_rad:
                render_radar_chart(df_t2_main, sel_project, df_t2_comp, sel_project_compare, all_proj_opt)
            
            st.markdown("<hr style='margin-top: 15px; margin-bottom: 15px;'>", unsafe_allow_html=True)

            c_left_view, c_right_view = st.columns(2, gap="large")
            
            with c_left_view:
                render_project_details(df_t2_main, sel_project, sel_period_t2_label, all_proj_opt, all_period_opt, is_compare=True)

            with c_right_view:
                render_project_details(df_t2_comp, sel_project_compare, sel_period_t2_label, all_proj_opt, all_period_opt, is_compare=True)
        else:
            render_project_details(df_t2_main, sel_project, sel_period_t2_label, all_proj_opt, all_period_opt, is_compare=False)

    # ==================== TAB 3: TRA CỨU LỊCH SỬ NHÂN SỰ ====================
    with tab3:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        if 'employee_name' in df.columns:
            unique_emps = sorted(df['employee_name'].dropna().astype(str).unique().tolist())
        else:
            unique_emps = []
            
        col_t3_emp, col_t3_y, col_t3_m = st.columns([4, 3, 3])
        with col_t3_emp:
            sel_emp_t3 = st.selectbox(
                t(":material/person: Lọc theo Nhân sự:", ":material/person: スタッフを選択:"),
                options=unique_emps,
                key="tab3_sel_emp"
            )
        with col_t3_y:
            sel_year_t3 = st.selectbox(
                t(":material/calendar_today: Lọc theo Năm:", ":material/calendar_today: 年を選択:"),
                options=year_options,
                format_func=lambda x: f"{x}年" if st.session_state.get('lang', 'VN') == 'JP' and str(x).isdigit() else str(x),
                key="tab3_sel_year"
            )
        with col_t3_m:
            sel_month_t3 = st.selectbox(
                t(":material/calendar_month: Lọc theo Tháng:", ":material/calendar_month: 月を選択:"),
                options=month_options,
                format_func=lambda x: t(f"Tháng {x}", f"{x}月") if isinstance(x, int) else str(x),
                key="tab3_sel_month",
                help=t("Mẹo: Lọc dữ liệu theo tháng.", "ヒント: 月でデータを絞り込みます。")
            )
            
        if not unique_emps:
            from components.ui_utils import render_empty_state
            render_empty_state(t("Chưa có dữ liệu nhân sự.", "スタッフデータがありません。"))
        else:
            df_tab3 = df[df['employee_name'] == sel_emp_t3].copy()
            
            if 'date_obj' not in df_tab3.columns and 'ot_date' in df_tab3.columns:
                df_tab3['date_obj'] = pd.to_datetime(df_tab3['ot_date'], format='%d/%m/%Y', errors='coerce')
                
            if sel_year_t3 not in ["Tất cả", "すべて"]:
                df_tab3 = df_tab3[df_tab3['date_obj'].dt.year == sel_year_t3]
            if sel_month_t3 not in ["Tất cả", "すべて"]:
                df_tab3 = df_tab3[df_tab3['date_obj'].dt.month == sel_month_t3]
                
            if df_tab3.empty:
                from components.ui_utils import render_empty_state
                render_empty_state(t("Không có dữ liệu cho nhân sự này trong khoảng thời gian đã chọn.", "選択した期間にはこのスタッフのデータがありません。"))
            else:
                total_ot_hours = df_tab3['ot_hours'].sum() if 'ot_hours' in df_tab3.columns else 0
                total_ot_pay = df_tab3['est_cost'].sum() if 'est_cost' in df_tab3.columns else 0.0
                num_projects_t3 = df_tab3['order_name'].nunique() if 'order_name' in df_tab3.columns else 0
                num_records_t3 = len(df_tab3)
                
                title1 = t('TỔNG TIỀN OT TÍCH LŨY', '累計残業代')
                title2 = t('TỔNG GIỜ OT', '累計残業時間')
                title3 = t('SỐ DỰ ÁN THAM GIA', '対象プロジェクト数')
                title4 = t('SỐ LƯỢT OT', '残業回数')
                
                st.markdown(f"""
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin-bottom: 20px; margin-top: 8px;'>
                    <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #00a8e8; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                            <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>{title2}</div>
                            <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #00a8e8 0%, #0077b6 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0, 168, 232, 0.3); flex-shrink: 0;'><span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">schedule</span></div>
                        </div>
                        <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'><span class="count-up-target-float" data-target="{total_ot_hours}">{total_ot_hours:,.1f}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>h</span></div>
                    </div>
                    <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #8b5cf6; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                            <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>{title3}</div>
                            <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(139, 92, 246, 0.3); flex-shrink: 0;'><span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">folder</span></div>
                        </div>
                        <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'><span class="count-up-target" data-target="{num_projects_t3}">{num_projects_t3}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>{t('dự án', '件')}</span></div>
                    </div>
                    <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #10b981; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                            <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>{title1}</div>
                            <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #34d399 0%, #10b981 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); flex-shrink: 0;'><span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">payments</span></div>
                        </div>
                        <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'><span class="count-up-target" data-target="{total_ot_pay}">{total_ot_pay:,.0f}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>VNĐ</span></div>
                    </div>
                    <div style='background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #f59e0b; border-radius: 12px; padding: 12px 16px; box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.07), 0 2px 4px -1px rgba(15, 23, 42, 0.04); transition: all 0.2s ease;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px;'>
                            <div style='font-size: 12.5px; font-weight: 700; color: #64748b; letter-spacing: 0.3px; text-transform: uppercase;'>{title4}</div>
                            <div style='width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3); flex-shrink: 0;'><span class="material-symbols-rounded summary-white-icon" style="font-size: 20px; color: #ffffff !important;">receipt_long</span></div>
                        </div>
                        <div style='font-size: 23px; font-weight: 800; color: #0f172a; line-height: 1.2;'><span class="count-up-target" data-target="{num_records_t3}">{num_records_t3}</span> <span style='font-size: 15px; font-weight: 600; color: #475569;'>{t('lượt', '回')}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                        
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
                
                col_chart, col_tbl = st.columns([4.5, 5.5], gap="large")
                
                with col_chart:
                    chart_title = t('XU HƯỚNG GIỜ OT THEO THỜI GIAN', '残業時間の推移')
                    st.markdown(f"<h3 style='font-size: 18px; font-weight: 600;'>{chart_title}</h3>", unsafe_allow_html=True)
                    
                    df_trend = df_tab3.copy()
                    if sel_month_t3 in ["Tất cả", "すべて"]:
                        df_trend['month_label'] = df_trend['date_obj'].dt.strftime('%m/%Y')
                        df_trend['sort_key'] = df_trend['date_obj'].dt.strftime('%Y%m')
                        df_grouped = df_trend.groupby(['month_label', 'sort_key'])['ot_hours'].sum().reset_index()
                        df_grouped = df_grouped.sort_values('sort_key')
                        x_col = 'month_label'
                        x_title = t("Tháng", "月")
                    else:
                        df_trend['date_label'] = df_trend['date_obj'].dt.strftime('%d/%m')
                        df_trend['sort_key'] = df_trend['date_obj'].dt.strftime('%Y%m%d')
                        df_grouped = df_trend.groupby(['date_label', 'sort_key'])['ot_hours'].sum().reset_index()
                        df_grouped = df_grouped.sort_values('sort_key')
                        x_col = 'date_label'
                        x_title = t("Ngày", "日")
                        
                    if not df_grouped.empty:
                        fig_trend = px.bar(
                            df_grouped,
                            x=x_col,
                            y='ot_hours',
                            color_discrete_sequence=['#00a8e8']
                        )
                        fig_trend.update_traces(
                            hovertemplate="<b>%{x}</b><br>"+t("Số giờ", "時間")+": %{y}h<extra></extra>",
                            marker_line_color='rgba(0,0,0,0)',
                            marker_line_width=0
                        )
                        fig_trend.update_layout(
                            margin=dict(t=20, b=20, l=10, r=10),
                            xaxis_title=x_title,
                            yaxis_title=t("Số giờ", "時間"),
                            height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
                    else:
                        from components.ui_utils import render_empty_state
                        render_empty_state(t("Không có dữ liệu giờ OT để vẽ biểu đồ.", "グラフを表示するデータがありません。"), icon="bar_chart", height=200)

                with col_tbl:
                    title = t('CHI TIẾT LỊCH SỬ OT', '残業履歴詳細')
                    st.markdown(f"<h3 style='font-size: 18px; font-weight: 600;'>{title}</h3>", unsafe_allow_html=True)
                    
                    cols_to_show = ['ot_date', 'order_name', 'ot_hours', 'est_cost', 'ot_reason']
                    for c in cols_to_show:
                        if c not in df_tab3.columns:
                            df_tab3[c] = ""
                            
                    disp_df = df_tab3[cols_to_show].copy()
                    disp_df['ot_date'] = disp_df['ot_date'].astype(str)
                    disp_df['est_cost'] = disp_df['est_cost'].apply(lambda x: f"{float(x):,.0f}" if pd.notna(x) and str(x).strip() != "" else "0")
                    
                    if st.session_state.get('lang', 'VN') == 'JP':
                        col_rename = {
                            'ot_date': '日付',
                            'order_name': 'プロジェクト',
                            'ot_hours': '残業時間 (h)',
                            'est_cost': '残業代 (VND)',
                            'ot_reason': '理由'
                        }
                    else:
                        col_rename = {
                            'ot_date': 'Ngày',
                            'order_name': 'Tên dự án',
                            'ot_hours': 'Số giờ',
                            'est_cost': 'Số tiền (VND)',
                            'ot_reason': 'Lý do'
                        }
                    disp_df = disp_df.rename(columns=col_rename)
                    st.dataframe(disp_df, use_container_width=True, hide_index=True)

    # Inject Javascript to animate the counting for metrics
    import streamlit.components.v1 as components
    js_count_up = """
    <script>
        setTimeout(() => {
            try {
                const parentDoc = window.parent.document;
                
                // For integers
                const targets = parentDoc.querySelectorAll('.count-up-target');
                targets.forEach(el => {
                    const targetStr = el.getAttribute('data-target');
                    if (!targetStr) return;
                    
                    const lastAnimated = el.getAttribute('data-last-animated');
                    if (lastAnimated === targetStr) return;
                    el.setAttribute('data-last-animated', targetStr);
                    
                    const target = parseFloat(targetStr.replace(/,/g, '')) || 0;
                    const duration = 1500;
                    const frameRate = 30;
                    const totalFrames = Math.round(duration / frameRate);
                    let frame = 0;
                    const counter = setInterval(() => {
                        frame++;
                        const progress = frame / totalFrames;
                        const easeOut = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                        const current = Math.round(target * easeOut);
                        el.innerText = current.toLocaleString('en-US');
                        if (frame >= totalFrames) {
                            clearInterval(counter);
                            el.innerText = target.toLocaleString('en-US');
                        }
                    }, frameRate);
                });

                // For floats (1 decimal)
                const floatTargets = parentDoc.querySelectorAll('.count-up-target-float');
                floatTargets.forEach(el => {
                    const targetStr = el.getAttribute('data-target');
                    if (!targetStr) return;
                    
                    const lastAnimated = el.getAttribute('data-last-animated');
                    if (lastAnimated === targetStr) return;
                    el.setAttribute('data-last-animated', targetStr);
                    
                    const target = parseFloat(targetStr.replace(/,/g, '')) || 0;
                    const duration = 1500;
                    const frameRate = 30;
                    const totalFrames = Math.round(duration / frameRate);
                    let frame = 0;
                    const counter = setInterval(() => {
                        frame++;
                        const progress = frame / totalFrames;
                        const easeOut = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                        const current = target * easeOut;
                        el.innerText = current.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 1});
                        if (frame >= totalFrames) {
                            clearInterval(counter);
                            el.innerText = target.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 1});
                        }
                    }, frameRate);
                });
            } catch (e) {}
        }, 100);
    </script>
    """ + f"<!-- force_reload_iframe_{__import__('time').time()} -->"
    components.html(js_count_up, height=0)
