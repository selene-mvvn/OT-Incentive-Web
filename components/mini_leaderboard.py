import streamlit as st
import pandas as pd
from logic.history import get_records
from logic.i18n import t

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
        if 'ot_hours' not in df.columns:
            df['ot_hours'] = 0
        df['ot_hours'] = pd.to_numeric(df['ot_hours'], errors='coerce').fillna(0)
        agg_df = df.groupby('employee_name')['ot_hours'].sum().reset_index()
        agg_df = agg_df.sort_values(by='ot_hours', ascending=False).reset_index(drop=True)
        val_col = 'ot_hours'
        val_suffix = "h"
    else:
        if 'final_incentive' not in df.columns:
            df['final_incentive'] = 0
        df['final_incentive'] = pd.to_numeric(df['final_incentive'], errors='coerce').fillna(0)
        agg_df = df.groupby('employee_name')['final_incentive'].sum().reset_index()
        agg_df = agg_df.sort_values(by='final_incentive', ascending=False).reset_index(drop=True)
        val_col = 'final_incentive'
        val_suffix = "¥"

    top_5 = agg_df.head(5)
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    html_content = ""
    for i, row in top_5.iterrows():
        emp_name = row['employee_name']
        val = row[val_col]
        medal = medals[i] if i < len(medals) else "🏅"
        
        # Determine background color for row
        bg_color = "rgba(255,255,255,0.7)"
        if i == 0: bg_color = "rgba(255, 215, 0, 0.2)"
        elif i == 1: bg_color = "rgba(192, 192, 192, 0.2)"
        elif i == 2: bg_color = "rgba(205, 127, 50, 0.2)"
        
        # Format value
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
        '>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 16px;'>{medal}</span>
                <span style='font-weight: 500; color: #34495e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100px;' title='{emp_name}'>{emp_name}</span>
            </div>
            <span style='font-weight: 700; color: {"#00a8e8" if data_type == "ot" else "#e67e22"};'>{formatted_val} {val_suffix}</span>
        </div>
        """
        
    html_content += "</div>"
    st.markdown(html_content, unsafe_allow_html=True)
