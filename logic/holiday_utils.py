import datetime
import pandas as pd
import streamlit as st
import json
import os

def get_holidays_df():
    # Helper to get the holidays dataframe
    if 'ot_base_data' in st.session_state and 'holidays_df' in st.session_state['ot_base_data']:
        df = st.session_state['ot_base_data']['holidays_df']
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    
    # Try to load from base_data.json if session state is empty (e.g. on Welcome page load before Settings)
    try:
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'base_data.json')
        if os.path.exists(base_path):
            with open(base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'holidays_df' in data and isinstance(data['holidays_df'], list) and len(data['holidays_df']) > 0:
                    return pd.DataFrame(data['holidays_df'])
    except:
        pass
        
    return pd.DataFrame()

def get_countdown_info(target_date=None):
    if target_date is None:
        target_date = datetime.date.today()
        
    df = get_holidays_df()
    if df.empty or "Ngày nghỉ" not in df.columns:
        return None
        
    try:
        df['date_obj'] = pd.to_datetime(df['Ngày nghỉ'], format='mixed', dayfirst=True).dt.date
    except:
        return None
        
    # Drop NaNs and sort
    df = df.dropna(subset=['date_obj']).sort_values('date_obj').reset_index(drop=True)
    if df.empty:
        return None
        
    dates = df['date_obj'].tolist()
    
    # Group consecutive dates
    blocks = []
    current_block = [dates[0]]
    for d in dates[1:]:
        if (d - current_block[-1]).days == 1:
            current_block.append(d)
        else:
            blocks.append(current_block)
            current_block = [d]
    blocks.append(current_block)
    
    # Find next relevant block
    for block in blocks:
        start_date = block[0]
        end_date = block[-1]
        
        if target_date < start_date:
            days_left = (start_date - target_date).days
            if days_left <= 7:
                is_single = (start_date == end_date)
                reason = df[df['date_obj'] == start_date]['Lý do'].iloc[0] if 'Lý do' in df.columns else ""
                return {
                    "type": "upcoming",
                    "days_left": days_left,
                    "target_date": start_date,
                    "reason": reason,
                    "is_single": is_single
                }
        elif start_date <= target_date <= end_date:
            is_single = (start_date == end_date)
            if is_single:
                reason = df[df['date_obj'] == start_date]['Lý do'].iloc[0] if 'Lý do' in df.columns else ""
                return {
                    "type": "today_single",
                    "reason": reason,
                    "target_date": start_date
                }
            else:
                return_date = end_date + datetime.timedelta(days=1)
                days_left = (return_date - target_date).days
                reason = df[df['date_obj'] == start_date]['Lý do'].iloc[0] if 'Lý do' in df.columns else ""
                return {
                    "type": "during_block",
                    "days_left": days_left,
                    "target_date": return_date,
                    "reason": reason
                }
                
    return None
