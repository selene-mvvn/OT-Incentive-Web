import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from logic.history_records import get_records
from logic.i18n import t

def render_gamified_cards(agg_df, metric_col, title_col, unit, theme="ot"):
    top_3 = agg_df.head(3).to_dict('records')
    while len(top_3) < 3:
        top_3.append({title_col: "-", metric_col: 0})
        
    c1, c2, c3 = st.columns(3)
    
    if theme == "ot":
        t1_bg = "linear-gradient(135deg, #ffcdd2 0%, #ffebee 100%)"
        t1_border = "#c62828"
        t1_color = "#c62828"
        
        t2_bg = "linear-gradient(135deg, #ffe0b2 0%, #fff3e0 100%)"
        t2_border = "#ef6c00"
        t2_color = "#ef6c00"
        
        t3_bg = "linear-gradient(135deg, #fff9c4 0%, #fffde7 100%)"
        t3_border = "#f57f17"
        t3_color = "#f57f17"
    else:
        # Cyan theme for incentive
        t1_bg = "linear-gradient(135deg, #b2ebf2 0%, #e0f7fa 100%)"
        t1_border = "#00838f"
        t1_color = "#00838f"
        
        t2_bg = "linear-gradient(135deg, #e0f7fa 0%, #e0f7fa 100%)"
        t2_border = "#00bcd4"
        t2_color = "#00bcd4"
        
        t3_bg = "linear-gradient(135deg, #e0f7fa 0%, #f1fbfc 100%)"
        t3_border = "#4dd0e1"
        t3_color = "#4dd0e1"
        
    def card_html(rank_icon, rank_text, bg, border, color, name, value):
        val_str = f"{value:,.0f}" if theme == "incentive" else f"{value:,.1f}"
        return f"""
        <div style="background: {bg}; border-left: 5px solid {border}; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <div style="font-size: 20px; margin-bottom: 5px; color: {color};"><b>{rank_icon} {rank_text}</b></div>
            <div style="font-size: 16px; color: {color}; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name}</div>
            <div style="font-size: 24px; color: {color}; font-weight: 900;">{val_str} <span style="font-size: 12px; font-weight: normal;">{unit}</span></div>
        </div>
        """

    with c1:
        st.markdown(card_html("🥇", "TOP 1", t1_bg, t1_border, t1_color, top_3[0][title_col], top_3[0][metric_col]), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("🥈", "TOP 2", t2_bg, t2_border, t2_color, top_3[1][title_col], top_3[1][metric_col]), unsafe_allow_html=True)
    with c3:
        st.markdown(card_html("🥉", "TOP 3", t3_bg, t3_border, t3_color, top_3[2][title_col], top_3[2][metric_col]), unsafe_allow_html=True)

def render_dashboard():
    st.markdown(f"<h2 style='text-align: center; color: #00a8e8; margin-bottom: 30px;'>{t('🏆 XẾP HẠNG CHUNG', '🏆 総合ランキング')}</h2>", unsafe_allow_html=True)
    
    # === OT RANKING ===
    st.markdown(f"<h3 style='font-size: 22px; font-weight: 600; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-top: 20px;'>1. {t('XẾP HẠNG THỜI GIAN OT', '残業時間ランキング')}</h3>", unsafe_allow_html=True)
    ot_history = get_records("ot")
    if not ot_history:
        st.info(t("Chưa có dữ liệu OT nào được lưu.", "保存されたデータがありません。"))
    else:
        df_ot = pd.DataFrame(ot_history)
        df_ot['date_obj'] = pd.to_datetime(df_ot.get('ot_date'), format='%d/%m/%Y', errors='coerce')
        if 'ot_hours' not in df_ot.columns:
            df_ot['ot_hours'] = 0
        df_ot['ot_hours'] = pd.to_numeric(df_ot['ot_hours'], errors='coerce').fillna(0)
        
        years_ot = sorted(df_ot['date_obj'].dt.year.dropna().unique().tolist(), reverse=True)
        years_ot = [int(y) for y in years_ot]
        if not years_ot:
            years_ot = [datetime.datetime.now().year]
            
        c_year, c_emp = st.columns(2)
        with c_year:
            sel_year_ot = st.selectbox(t("Chọn năm (OT)", "年を選択 (OT)"), ["Tất cả"] + years_ot, key="sel_year_ot_dash")
            
        if sel_year_ot != "Tất cả":
            df_ot_filtered = df_ot[df_ot['date_obj'].dt.year == sel_year_ot]
        else:
            df_ot_filtered = df_ot
            
        if df_ot_filtered.empty:
            st.warning("Không có dữ liệu cho năm này.")
        else:
            agg_ot = df_ot_filtered.groupby('employee_name').agg(
                total_ot_hours=('ot_hours', 'sum'),
                projects_count=('order_name', 'count')
            ).reset_index()
            agg_ot = agg_ot.sort_values(by='total_ot_hours', ascending=False).reset_index(drop=True)
            
            # Global metric
            total_ot_sum = agg_ot['total_ot_hours'].sum()
            st.markdown(f"**{t('Tổng OT toàn công ty:', '全社総残業時間:')} {total_ot_sum:,.1f} h**")
            
            # Cards
            render_gamified_cards(agg_ot, 'total_ot_hours', 'employee_name', 'h', theme="ot")
            
            # Side by side Chart and Table
            c_chart, c_table = st.columns([6, 4])
            with c_chart:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=agg_ot['employee_name'],
                    y=agg_ot['total_ot_hours'],
                    name=t("Tổng số giờ OT", "総残業時間"),
                    marker=dict(
                        color=agg_ot['total_ot_hours'],
                        colorscale=[[0, '#e0f7fa'], [1, '#00aced']],
                        line=dict(color='rgba(0,0,0,0)', width=0)
                    ),
                    text=agg_ot['total_ot_hours'].apply(lambda x: f"{x:,.1f}"),
                    textposition='auto',
                ))
                fig.update_layout(
                    title=t("Biểu đồ", "チャート"),
                    xaxis_title="",
                    yaxis_title=t("Số giờ (h)", "時間 (h)"),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'family': "Inter, sans-serif"},
                    margin=dict(l=0, r=0, t=40, b=0),
                    yaxis=dict(gridcolor='#e0e0e0')
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with c_table:
                st.markdown(f"<div style='margin-bottom: 15px;'><b>{t('Bảng chi tiết', '詳細テーブル')}</b></div>", unsafe_allow_html=True)
                agg_display = agg_ot.copy()
                agg_display.index = agg_display.index + 1
                col_emp = t("Nhân sự", "担当者")
                col_ot = t("Giờ OT", "残業時間")
                col_prj = t("Số lượt", "回数")
                agg_display.rename(columns={'employee_name': col_emp, 'total_ot_hours': col_ot, 'projects_count': col_prj}, inplace=True)
                
                def highlight_top3_ot(row):
                    if row.name == 1:
                        return ['background-color: #ffebee; color: #c62828; font-weight: bold;'] * len(row)
                    elif row.name == 2:
                        return ['background-color: #fff3e0; color: #ef6c00; font-weight: bold;'] * len(row)
                    elif row.name == 3:
                        return ['background-color: #fffde7; color: #f57f17; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                    
                st.dataframe(agg_display.style.apply(highlight_top3_ot, axis=1).format({col_ot: "{:,.1f}"}), use_container_width=True, height=400)


    # === INCENTIVE RANKING ===
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size: 22px; font-weight: 600; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-top: 20px;'>2. {t('XẾP HẠNG INCENTIVE', 'インセンティブランキング')}</h3>", unsafe_allow_html=True)
    inc_history = get_records("incentive")
    if not inc_history:
        st.info(t("Chưa có dữ liệu Incentive nào được lưu.", "保存されたデータがありません。"))
    else:
        df_inc = pd.DataFrame(inc_history)
        df_inc['date_obj'] = pd.to_datetime(df_inc.get('date'), format='%d/%m/%Y', errors='coerce')
        for col in ['incentive', 'target_hours', 'actual_hours']:
            if col not in df_inc.columns:
                df_inc[col] = 0
            df_inc[col] = pd.to_numeric(df_inc[col], errors='coerce').fillna(0)
        
        years_inc = sorted(df_inc['date_obj'].dt.year.dropna().unique().tolist(), reverse=True)
        years_inc = [int(y) for y in years_inc]
        if not years_inc:
            years_inc = [datetime.datetime.now().year]
            
        c_year_inc, c_emp_inc = st.columns(2)
        with c_year_inc:
            sel_year_inc = st.selectbox(t("Chọn năm (Incentive)", "年を選択 (Inc)"), ["Tất cả"] + years_inc, key="sel_year_inc_dash")
            
        if sel_year_inc != "Tất cả":
            df_inc_filtered = df_inc[df_inc['date_obj'].dt.year == sel_year_inc]
        else:
            df_inc_filtered = df_inc
            
        if df_inc_filtered.empty:
            st.warning("Không có dữ liệu cho năm này.")
        else:
            agg_inc = df_inc_filtered.groupby('employee_name').agg(
                total_incentive=('incentive', 'sum'),
                total_target=('target_hours', 'sum'),
                total_actual=('actual_hours', 'sum'),
                projects_count=('project_name', 'count')
            ).reset_index()
            agg_inc['efficiency_pct'] = (agg_inc['total_target'] / agg_inc['total_actual'] * 100).where(agg_inc['total_actual'] > 0, 0)
            agg_inc = agg_inc.sort_values(by='total_incentive', ascending=False).reset_index(drop=True)
            
            total_inc_sum = agg_inc['total_incentive'].sum()
            st.markdown(f"**{t('Tổng Incentive toàn công ty:', '全社総インセンティブ:')} {total_inc_sum:,.0f} JPY**")
            
            # Cards
            render_gamified_cards(agg_inc, 'total_incentive', 'employee_name', 'JPY', theme="incentive")
            
            # Side by side Chart and Table
            c_chart2, c_table2 = st.columns([6, 4])
            with c_chart2:
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=agg_inc['employee_name'],
                    y=agg_inc['total_incentive'],
                    name=t("Tổng Incentive", "総インセンティブ"),
                    marker=dict(
                        color=agg_inc['total_incentive'],
                        colorscale=[[0, '#e0f7fa'], [1, '#00aced']],
                        line=dict(color='rgba(0,0,0,0)', width=0)
                    ),
                    text=agg_inc['total_incentive'].apply(lambda x: f"{x:,.0f}"),
                    textposition='auto',
                ))
                fig2.update_layout(
                    title=t("Biểu đồ", "チャート"),
                    xaxis_title="",
                    yaxis_title=t("Incentive (JPY)", "インセンティブ (JPY)"),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'family': "Inter, sans-serif"},
                    margin=dict(l=0, r=0, t=40, b=0),
                    yaxis=dict(gridcolor='#e0e0e0')
                )
                st.plotly_chart(fig2, use_container_width=True)
                
            with c_table2:
                st.markdown(f"<div style='margin-bottom: 15px;'><b>{t('Bảng chi tiết', '詳細テーブル')}</b></div>", unsafe_allow_html=True)
                agg_display2 = agg_inc.copy()
                agg_display2.index = agg_display2.index + 1
                col_emp2 = t("Nhân sự", "担当者")
                col_inc = t("Tổng Nhận", "総受取額")
                col_eff = t("Hiệu suất", "効率")
                agg_display2 = agg_display2[['employee_name', 'total_incentive', 'efficiency_pct']]
                agg_display2.rename(columns={'employee_name': col_emp2, 'total_incentive': col_inc, 'efficiency_pct': col_eff}, inplace=True)
                
                def highlight_top3_inc(row):
                    if row.name in [1, 2, 3]:
                        return ['background-color: #e0f7fa; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                    
                st.dataframe(agg_display2.style.apply(highlight_top3_inc, axis=1).format({col_inc: "{:,.0f}", col_eff: "{:,.1f}%"}), use_container_width=True, height=400)
