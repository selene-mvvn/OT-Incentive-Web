import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from logic.history_records import get_records, save_all_records
from logic.i18n import t

@st.dialog(t("✏️ SỬA DỮ LIỆU NHANH", "✏️ 簡易データ編集"))
def show_mini_edit_dialog(data_type, df):
    st.caption(t("Chỉnh sửa trực tiếp trên bảng và nhấn Lưu.", "表上で直接編集し、保存ボタンを押してください。"))
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key=f"dialog_edit_{data_type}")
    if st.button(t("💾 Lưu Thay Đổi", "💾 変更を保存"), use_container_width=True):
        if save_all_records(data_type, edited_df.to_dict('records')):
            st.success(t("Đã lưu thành công!", "保存しました！"))
            st.rerun()

def render_mini_leaderboard(data_type="ot"):
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-top: 50px;
            margin-bottom: 20px;
            border-top: 4px solid {"#00a8e8" if data_type == "ot" else "#ff9f43"};
        '>
            <h4 style='text-align: center; color: #2c3e50; font-size: 16px; margin-bottom: 15px; text-transform: uppercase;'>
                {"⏱️ TOP 5 OT" if data_type == "ot" else "💰 TOP 5 INCENTIVE"}
            </h4>
    """, unsafe_allow_html=True)

    records = get_records(data_type)
    if not records:
        st.markdown(f"<div style='text-align:center; font-size:13px; color:#7f8c8d;'>{t('Chưa có dữ liệu', 'データなし')}</div></div>", unsafe_allow_html=True)
        return

    df = pd.DataFrame(records).drop_duplicates()
    
    if data_type == "ot":
        if 'ot_hours' not in df.columns: df['ot_hours'] = 0
        df['ot_hours'] = pd.to_numeric(df['ot_hours'], errors='coerce').fillna(0)
        agg_df = df.groupby('employee_name')['ot_hours'].sum().reset_index()
        agg_df = agg_df.sort_values(by='ot_hours', ascending=False).reset_index(drop=True)
        val_col = 'ot_hours'
        val_suffix = "h"
        colors = [
            ("linear-gradient(135deg, #ffcdd2 0%, #ffebee 100%)", "#c62828"),
            ("linear-gradient(135deg, #ffe0b2 0%, #fff3e0 100%)", "#ef6c00"),
            ("linear-gradient(135deg, #fff9c4 0%, #fffde7 100%)", "#f57f17")
        ]
    else:
        if 'final_incentive' not in df.columns: df['final_incentive'] = 0
        df['final_incentive'] = pd.to_numeric(df['final_incentive'], errors='coerce').fillna(0)
        agg_df = df.groupby('employee_name')['final_incentive'].sum().reset_index()
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
                <span style='font-weight: 600; color: #34495e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 90px;' title='{emp_name}'>{emp_name}</span>
            </div>
            <span style='font-weight: 700; color: {text_color};'>{formatted_val} {val_suffix}</span>
        </div>
        """
        
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Mini Chart
    if len(top_5) > 0:
        fig = go.Figure(go.Bar(
            x=top_5[val_col][::-1],
            y=top_5['employee_name'][::-1],
            orientation='h',
            marker=dict(
                color=top_5[val_col][::-1],
                colorscale=[[0, '#e0f7fa'], [1, '#00aced']] if data_type == "ot" else [[0, '#fff3e0'], [1, '#f57c00']],
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

    # Mini Edit Button
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button(t("✏️ Sửa dữ liệu (Nhanh)", "✏️ 簡易編集"), use_container_width=True, key=f"btn_edit_mini_{data_type}"):
        show_mini_edit_dialog(data_type, df)
