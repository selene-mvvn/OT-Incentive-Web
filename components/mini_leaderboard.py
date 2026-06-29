import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from logic.history_records import get_records, save_all_records
from logic.i18n import t

@st.dialog("MINI_EDIT_DIALOG_TITLE", width="large")
def show_mini_edit_dialog(data_type, df):
    dialog_title = t("✏️ SỬA DỮ LIỆU NHANH", "✏️ 簡易データ編集")
    st.markdown(f"""
        <style>
            div[data-testid="stModal"] > div[role="dialog"] {{
                transform: translateY(8vh);
            }}
            div[data-testid="stModal"] h2 {{
                visibility: hidden;
                position: relative;
            }}
            div[data-testid="stModal"] h2::after {{
                content: "{dialog_title}";
                visibility: visible;
                position: absolute;
                left: 0;
                top: 0;
                color: inherit;
            }}
        </style>
    """, unsafe_allow_html=True)
    st.caption(t("Chỉnh sửa trực tiếp trên bảng và nhấn Lưu.", "表上で直接編集し、保存ボタンを押してください。"))
    
    if data_type == "ot":
        col_order = ["payment_period", "ot_date", "employee_name", "manager_name", "project_type", "order_name", "order_id", "client_order_id", "ot_reason", "ot_hours", "hourly_rate"] + [c for c in df.columns if str(c).endswith("%")]
        col_order = [c for c in col_order if c in df.columns] + [c for c in df.columns if c not in col_order]
        col_cfg = {
            "ot_date": st.column_config.TextColumn(t("Ngày OT", "残業日")),
            "employee_name": st.column_config.TextColumn(t("Nhân sự", "担当者")),
            "ot_hours": st.column_config.NumberColumn(t("Giờ OT", "残業時間")),
            "ot_reason": st.column_config.TextColumn(t("Lý do", "残業理由")),
            "manager_name": st.column_config.TextColumn(t("Quản lý", "PM")),
            "project_type": st.column_config.TextColumn(t("Loại dự án", "プロジェクト種別")),
            "order_id": st.column_config.TextColumn(t("Mã dự án", "注文番号")),
            "order_name": st.column_config.TextColumn(t("Tên dự án", "注文名")),
            "client_order_id": st.column_config.TextColumn(t("Mã đơn khách", "客先注文番号")),
            "hourly_rate": st.column_config.NumberColumn(t("Lương/h", "時給"), format="%,.0f"),
            "payment_period": st.column_config.TextColumn(t("Kỳ thanh toán", "支払期間"))
        }
        for c in df.columns:
            if str(c).endswith("%"):
                col_cfg[c] = st.column_config.NumberColumn(c, format="%,.0f")
    else:
        col_order = ["date", "employee_name", "project_name", "target_hours", "actual_hours", "unit_price", "company_charge", "profit", "standard_incentive", "final_incentive", "notes"]
        col_order = [c for c in col_order if c in df.columns] + [c for c in df.columns if c not in col_order]
        col_cfg = {
            "date": st.column_config.TextColumn(t("Ngày ghi nhận", "記録日")),
            "employee_name": st.column_config.TextColumn(t("Nhân sự", "担当者")),
            "project_name": st.column_config.TextColumn(t("Tên dự án", "案件名")),
            "target_hours": st.column_config.NumberColumn(t("Giờ công KH", "目標工数")),
            "actual_hours": st.column_config.NumberColumn(t("Giờ công TT", "実工数")),
            "unit_price": st.column_config.NumberColumn(t("Đơn giá", "単価"), format="%,.0f"),
            "company_charge": st.column_config.NumberColumn(t("Company Charge", "会社運用ﾁｬｰｼﾞ"), format="%,.0f"),
            "profit": st.column_config.NumberColumn(t("Lợi nhuận", "利益"), format="%,.0f"),
            "standard_incentive": st.column_config.NumberColumn(t("Incentive TC", "基準金額"), format="%,.0f"),
            "final_incentive": st.column_config.NumberColumn(t("Nhận được", "受取額"), format="%,.0f"),
            "notes": st.column_config.TextColumn(t("Ghi chú", "備考"))
        }

    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", column_order=col_order, column_config=col_cfg, key=f"dialog_edit_{data_type}")
    if st.button(t("💾 Lưu Thay Đổi", "💾 変更を保存"), use_container_width=True):
        if save_all_records(data_type, edited_df.to_dict('records')):
            st.success(t("Đã lưu thành công!", "保存しました！"))
            st.rerun()

def render_mini_leaderboard(data_type="ot"):
    records = get_records(data_type)
    if not records:
        st.markdown(f"<div style='text-align:center; font-size:13px; color:#7f8c8d; margin-top:50px;'>{t('Chưa có dữ liệu', 'データなし')}</div>", unsafe_allow_html=True)
        return

    df = pd.DataFrame(records).drop_duplicates()
    
    date_col = 'ot_date' if data_type == 'ot' else 'date'
    if date_col in df.columns:
        df['date_obj'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
        years = sorted(df['date_obj'].dt.year.dropna().astype(int).unique().tolist(), reverse=True)
    else:
        years = []
        
    year_options = [t("Tất cả", "すべて")] + years
    border_color = "#00a8e8"
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        </style>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        icon = "timer" if data_type == "ot" else "payments"
        title_text = "TOP OVERTIME" if data_type == "ot" else "TOP INCENTIVE"
        
        # Gradient Title Block
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 8px;
                border-top: 4px solid {border_color};
                padding: 10px;
                margin-bottom: 15px;
                text-align: center; color: #2c3e50; font-size: 16px; font-weight: bold; text-transform: uppercase;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            '>
                <span class="material-symbols-rounded" style="vertical-align: middle; color: #00a8e8; margin-right: 5px; font-size: 20px;">{icon}</span>
                <span style="vertical-align: middle;">{title_text}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Selectbox (Small and centered)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            sel_year = st.selectbox(
                t("Chọn năm", "年を選択"), 
                options=year_options, 
                key=f"mini_year_{data_type}", 
                label_visibility="collapsed"
            )
            
        # Spacing
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
        if sel_year not in ["Tất cả", "すべて"]:
            df_filtered = df[df['date_obj'].dt.year == sel_year].copy()
        else:
            df_filtered = df.copy()

        if df_filtered.empty:
            st.markdown(f"<div style='text-align:center; font-size:13px; color:#7f8c8d; padding-bottom: 15px;'>{t('Không có dữ liệu cho năm này', 'データなし')}</div>", unsafe_allow_html=True)
        else:
            if data_type == "ot":
                if 'ot_hours' not in df_filtered.columns: df_filtered['ot_hours'] = 0
                df_filtered['ot_hours'] = pd.to_numeric(df_filtered['ot_hours'], errors='coerce').fillna(0)
                agg_df = df_filtered.groupby('employee_name')['ot_hours'].sum().reset_index()
                agg_df = agg_df.sort_values(by='ot_hours', ascending=False).reset_index(drop=True)
                val_col = 'ot_hours'
                val_suffix = "h"
                colors = [
                    ("linear-gradient(135deg, #ffcdd2 0%, #ffebee 100%)", "#c62828"),
                    ("linear-gradient(135deg, #ffe0b2 0%, #fff3e0 100%)", "#ef6c00"),
                    ("linear-gradient(135deg, #fff9c4 0%, #fffde7 100%)", "#f57f17")
                ]
            else:
                if 'final_incentive' not in df_filtered.columns: df_filtered['final_incentive'] = 0
                df_filtered['final_incentive'] = pd.to_numeric(df_filtered['final_incentive'], errors='coerce').fillna(0)
                agg_df = df_filtered.groupby('employee_name')['final_incentive'].sum().reset_index()
                agg_df = agg_df.sort_values(by='final_incentive', ascending=False).reset_index(drop=True)
                val_col = 'final_incentive'
                val_suffix = "¥"
                colors = [
                    ("linear-gradient(135deg, #b2ebf2 0%, #e0f7fa 100%)", "#00838f"),
                    ("linear-gradient(135deg, #e0f7fa 0%, #e0f7fa 100%)", "#00bcd4"),
                    ("linear-gradient(135deg, #e0f7fa 0%, #f1fbfc 100%)", "#00acc1")
                ]

            top_5 = agg_df.head(5)
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            
            html_content = ""
            for i, row in top_5.iterrows():
                emp_name = row['employee_name']
                val = row[val_col]
                medal = medals[i] if i < len(medals) else "🏅"
                
                bg_color = "rgba(255,255,255,0.7)"
                text_color = "#e67e22" if data_type != "ot" else "#00a8e8"
                if i < 3:
                    bg_color = colors[i][0]
                    text_color = colors[i][1]
                
                formatted_val = f"{val:,.1f}" if data_type == "ot" else f"{int(val):,}"
                
                html_content += f"""
                <div style='
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: {bg_color};
                    padding: 8px 10px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    font-size: 13px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
                    border-left: 3px solid {text_color};
                '>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='font-size: 16px;'>{medal}</span>
                        <span style='font-weight: 600; color: #34495e;' title='{emp_name}'>{emp_name}</span>
                    </div>
                    <span style='font-weight: 700; color: {text_color};'>{formatted_val} {val_suffix}</span>
                </div>
                """
                
            st.markdown(html_content, unsafe_allow_html=True)
            
            if len(top_5) > 0:
                fig = go.Figure(go.Bar(
                    x=top_5[val_col][::-1],
                    y=top_5['employee_name'][::-1],
                    orientation='h',
                    marker=dict(
                        color=top_5[val_col][::-1],
                        colorscale=[[0, '#e1f5fe'], [1, '#00a8e8']],
                    ),
                    text=top_5[val_col][::-1].apply(lambda x: f"{x:,.1f}" if data_type == "ot" else f"{int(x):,}"),
                    textposition='inside',
                    insidetextanchor='end',
                    textfont=dict(color='white', size=10)
                ))
                fig.update_layout(
                    margin=dict(l=0, r=0, t=5, b=5),
                    height=160,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(visible=False),
                    yaxis=dict(tickfont=dict(size=11, color='#2c3e50')),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button(t("✏️ Sửa dữ liệu (Nhanh)", "✏️ 簡易編集"), use_container_width=True, key=f"btn_edit_mini_{data_type}"):
        show_mini_edit_dialog(data_type, df)
