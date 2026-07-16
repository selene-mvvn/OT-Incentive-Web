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
                cost += float(v)
            except:
                pass
    if cost == 0.0:
        try:
            cost = float(r.get('ot_pay', 0.0))
        except:
            pass
    return cost

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
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600; color: #1e293b; margin-bottom: 4px;'>{t('PHÂN BỔ & LỊCH SỬ DỰ ÁN (OT)', 'プロジェクト分析・履歴')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 14.5px; color: #64748b; margin-bottom: 20px;'>{t('Phân tích tỷ trọng giờ tăng ca và tra cứu chi tiết lịch sử từng dự án theo tháng/kỳ thanh toán.', 'プロジェクト別の残業時間分布と履歴を月別・案件別に詳細分析します。')}</div>", unsafe_allow_html=True)

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
    for col in ['order_name', 'ot_hours', 'employee_name', 'ot_date']:
        if col not in df.columns:
            df[col] = ''

    df['ot_hours'] = pd.to_numeric(df['ot_hours'], errors='coerce').fillna(0.0)
    df['order_name'] = df['order_name'].astype(str).str.strip().replace({'': t('Khác / Không tên', 'その他')})
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
    period_options = [all_period_opt] + unique_periods

    tab1, tab2 = st.tabs([
        t("📊 PHÂN BỔ DỰ ÁN THEO THÁNG", "📊 プロジェクト月別分布"),
        t("🔍 TRA CỨU CHI TIẾT TỪNG DỰ ÁN", "🔍 プロジェクト別詳細分析")
    ])

    # ==================== TAB 1: PHÂN BỔ DỰ ÁN ====================
    with tab1:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        col_f1, col_f2 = st.columns([3, 7])
        with col_f1:
            sel_period = st.selectbox(
                t("📅 Chọn tháng / Kỳ thanh toán:", "📅 月・支払期を選択:"),
                options=period_options,
                key="tab1_sel_period"
            )

        if sel_period == all_period_opt:
            df_tab1 = df.copy()
            period_label = t("Toàn bộ thời gian", "全期間")
        else:
            df_tab1 = df[df['clean_period'] == sel_period].copy()
            period_label = sel_period

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
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 24px; margin-top: 10px;'>
                <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 1px solid #bae6fd; border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 6px rgba(0, 168, 232, 0.08);'>
                    <div style='font-size: 13px; color: #0369a1; font-weight: 600; display: flex; align-items: center; gap: 6px;'>
                        <span class="material-symbols-rounded" style="font-size: 18px; color: #0284c7;">schedule</span> {t('TỔNG GIỜ OT', '残業時間合計')}
                    </div>
                    <div style='font-size: 24px; font-weight: 700; color: #0c4a6e; margin-top: 6px;'>{total_hrs:,.1f} <span style='font-size: 15px; font-weight: 500;'>h</span></div>
                </div>
                <div style='background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 6px rgba(34, 197, 94, 0.08);'>
                    <div style='font-size: 13px; color: #15803d; font-weight: 600; display: flex; align-items: center; gap: 6px;'>
                        <span class="material-symbols-rounded" style="font-size: 18px; color: #16a34a;">payments</span> {t('DỰ TÍNH CHI PHÍ', '予想支出額')}
                    </div>
                    <div style='font-size: 24px; font-weight: 700; color: #14532d; margin-top: 6px;'>{total_cost:,.0f} <span style='font-size: 15px; font-weight: 500;'>VNĐ</span></div>
                </div>
                <div style='background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border: 1px solid #f0abfc; border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 6px rgba(192, 132, 252, 0.08);'>
                    <div style='font-size: 13px; color: #86198f; font-weight: 600; display: flex; align-items: center; gap: 6px;'>
                        <span class="material-symbols-rounded" style="font-size: 18px; color: #c026d3;">folder</span> {t('SỐ DỰ ÁN THAM GIA', '対象プロジェクト数')}
                    </div>
                    <div style='font-size: 24px; font-weight: 700; color: #701a75; margin-top: 6px;'>{num_projects} <span style='font-size: 15px; font-weight: 500;'>{t('dự án', '件')}</span></div>
                </div>
                <div style='background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 1px solid #fde68a; border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 6px rgba(245, 158, 11, 0.08);'>
                    <div style='font-size: 13px; color: #b45309; font-weight: 600; display: flex; align-items: center; gap: 6px;'>
                        <span class="material-symbols-rounded" style="font-size: 18px; color: #d97706;">group</span> {t('SỐ NHÂN SỰ OT', '対象スタッフ数')}
                    </div>
                    <div style='font-size: 24px; font-weight: 700; color: #78350f; margin-top: 6px;'>{num_staff} <span style='font-size: 15px; font-weight: 500;'>{t('người', '名')}</span></div>
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
            proj_summary = proj_summary.sort_values(by='Hours', ascending=False).reset_index(drop=True)

            with col_pie:
                st.markdown(f"<div style='font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 8px;'>🎯 {t('Biểu đồ Tỷ trọng Giờ OT theo Dự án', 'プロジェクト別残業時間シェア')} ({period_label})</div>", unsafe_allow_html=True)
                fig_pie = px.pie(
                    proj_summary,
                    values='Hours',
                    names='order_name',
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>' + t('Số giờ', '残業時間') + ': %{value:,.1f} h (%{percent})<extra></extra>'
                )
                fig_pie.update_layout(
                    font=dict(family="'Times New Roman', serif"),
                    margin=dict(t=20, b=20, l=10, r=10),
                    showlegend=True,
                    legend=dict(orientation='h', yanchor='top', y=-0.08, xanchor='center', x=0.5, font=dict(size=11)),
                    height=380,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

            with col_tbl:
                st.markdown(f"<div style='font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 8px;'>📋 {t('Bảng Tổng Hợp Chi Tiết Dự Án', 'プロジェクト別集計表')}</div>", unsafe_allow_html=True)
                display_df = proj_summary.copy()
                display_df = display_df.rename(columns={
                    'order_name': t('Tên Dự Án', 'プロジェクト名'),
                    'Hours': t('Số Giờ (h)', '時間 (h)'),
                    'Percentage': t('Tỷ Lệ (%)', '割合 (%)'),
                    'Cost': t('Chi Phí VNĐ', '予想支出額'),
                    'StaffCount': t('Số NV', '人数')
                })
                display_df[t('Số Giờ (h)', '時間 (h)')] = display_df[t('Số Giờ (h)', '時間 (h)')].apply(lambda x: f"{x:,.1f}")
                display_df[t('Tỷ Lệ (%)', '割合 (%)')] = display_df[t('Tỷ Lệ (%)', '割合 (%)')].apply(lambda x: f"{x}%")
                display_df[t('Chi Phí VNĐ', '予想支出額')] = display_df[t('Chi Phí VNĐ', '予想支出額')].apply(lambda x: f"{x:,.0f}")

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=380
                )

    # ==================== TAB 2: TRA CỨU CHI TIẾT TỪNG DỰ ÁN ====================
    with tab2:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        unique_projects = sorted(df['order_name'].unique().tolist())
        all_proj_opt = t("📂 --- Tất cả dự án ---", "📂 --- すべてのプロジェクト ---")
        project_options = [all_proj_opt] + unique_projects

        col_t2_1, col_t2_2 = st.columns([5, 5])
        with col_t2_1:
            sel_project = st.selectbox(
                t("📌 Chọn Dự Án Cần Tra Cứu:", "📌 プロジェクトを選択:"),
                options=project_options,
                key="tab2_sel_project"
            )
        with col_t2_2:
            sel_period_t2 = st.selectbox(
                t("📅 Lọc theo Tháng / Kỳ thanh toán:", "📅 月・支払期を選択:"),
                options=period_options,
                key="tab2_sel_period"
            )

        df_t2 = df.copy()
        if sel_project != all_proj_opt:
            df_t2 = df_t2[df_t2['order_name'] == sel_project]
        if sel_period_t2 != all_period_opt:
            df_t2 = df_t2[df_t2['clean_period'] == sel_period_t2]

        if df_t2.empty or df_t2['ot_hours'].sum() <= 0:
            from components.ui_utils import render_empty_state
            render_empty_state(t('Không tìm thấy bản ghi OT nào phù hợp với bộ lọc.', '条件に一致する残業データがありません。'), icon="search_off", height=120)
        else:
            p_hrs = df_t2['ot_hours'].sum()
            p_cost = df_t2['est_cost'].sum()
            p_staff = df_t2['employee_name'].nunique()
            p_records = len(df_t2)

            st.markdown(f"""
            <div style='background: #f8fafc; border: 1px solid #cbd5e1; border-left: 5px solid #00a8e8; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;'>
                <div>
                    <span style='font-size: 15px; font-weight: 700; color: #0f172a;'>
                        <span class="material-symbols-rounded" style="vertical-align: middle; color: #00a8e8; margin-right: 6px;">manage_search</span>
                        {sel_project if sel_project != all_proj_opt else t('Tất cả dự án', 'すべてのプロジェクト')} ({sel_period_t2 if sel_period_t2 != all_period_opt else t('Toàn bộ thời gian', '全期間')})
                    </span>
                </div>
                <div style='display: flex; gap: 20px; font-size: 13.5px; color: #334155; align-items: center;'>
                    <div><b>{p_hrs:,.1f}</b> {t('giờ OT', '時間')}</div>
                    <div style='color: #cbd5e1;'>•</div>
                    <div><b>{p_staff}</b> {t('nhân sự tham gia', '名参加')}</div>
                    <div style='color: #cbd5e1;'>•</div>
                    <div>{t('Dự tính chi phí:', '予想コスト:')} <b style='color: #0284c7; font-size: 15px;'>{p_cost:,.0f} VNĐ</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_t2_bar, col_t2_list = st.columns([4.5, 5.5], gap="large")

            # Staff contribution in this project/period
            staff_contrib = df_t2.groupby('employee_name').agg(
                Hours=('ot_hours', 'sum'),
                Cost=('est_cost', 'sum'),
                DaysCount=('ot_date', 'nunique')
            ).reset_index().sort_values(by='Hours', ascending=True)

            with col_t2_bar:
                st.markdown(f"<div style='font-size: 15.5px; font-weight: 600; color: #334155; margin-bottom: 8px;'>👥 {t('Phân Bổ Số Giờ Theo Nhân Sự', 'スタッフ別残業時間')}</div>", unsafe_allow_html=True)
                fig_bar = go.Figure(go.Bar(
                    x=staff_contrib['Hours'],
                    y=staff_contrib['employee_name'],
                    orientation='h',
                    marker=dict(
                        color=staff_contrib['Hours'],
                        colorscale=[[0, '#e0f2fe'], [1, '#0284c7']],
                    ),
                    text=staff_contrib['Hours'].apply(lambda x: f"{x:,.1f} h"),
                    textposition='auto',
                    insidetextanchor='end',
                    textfont=dict(size=12, color='#0f172a')
                ))
                fig_bar.update_layout(
                    font=dict(family="'Times New Roman', serif"),
                    margin=dict(l=0, r=0, t=10, b=10),
                    height=max(220, len(staff_contrib) * 36),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(title=t("Số giờ (h)", "時間 (h)"), gridcolor='#f1f5f9'),
                    yaxis=dict(tickfont=dict(size=12, color='#1e293b'))
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

            with col_t2_list:
                st.markdown(f"<div style='font-size: 15.5px; font-weight: 600; color: #334155; margin-bottom: 8px;'>📝 {t('Danh Sách Chi Tiết Các Lượt Làm OT', '残業明細一覧')}</div>", unsafe_allow_html=True)
                detail_df = df_t2[['clean_period', 'employee_name', 'ot_date', 'ot_hours', 'est_cost', 'manager_name', 'ot_reason']].copy()
                detail_df = detail_df.sort_values(by=['clean_period', 'ot_date'], ascending=[False, False]).reset_index(drop=True)
                
                detail_df = detail_df.rename(columns={
                    'clean_period': t('Tháng/Kỳ', '月'),
                    'employee_name': t('Tên NV', 'スタッフ名'),
                    'ot_date': t('Ngày OT', '残業日'),
                    'ot_hours': t('Số Giờ', '時間'),
                    'est_cost': t('Chi Phí VNĐ', '予想支出額'),
                    'manager_name': t('PM', 'PM'),
                    'ot_reason': t('Lý Do', '残業理由')
                })
                detail_df[t('Số Giờ', '時間')] = detail_df[t('Số Giờ', '時間')].apply(lambda x: f"{x:,.1f}")
                detail_df[t('Chi Phí VNĐ', '予想支出額')] = detail_df[t('Chi Phí VNĐ', '予想支出額')].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")

                st.dataframe(
                    detail_df,
                    use_container_width=True,
                    hide_index=True,
                    height=max(280, len(detail_df) * 38)
                )
