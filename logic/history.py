import json
import os
import requests
import streamlit as st

def get_firebase_url(path):
    try:
        base_url = st.secrets.get("FIREBASE_URL")
        if base_url:
            return f"{base_url.rstrip('/')}/{path}"
    except Exception:
        pass
    return None

HISTORY_FILE = "data/history.json"

def load_history():
    firebase_url = get_firebase_url("history.json")
    if firebase_url:
        try:
            resp = requests.get(firebase_url, timeout=5)
            if resp.status_code == 200 and resp.json() is not None:
                return resp.json()
        except Exception:
            pass

    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_history(history_dict):
    firebase_url = get_firebase_url("history.json")
    if firebase_url:
        try:
            requests.put(firebase_url, json=history_dict, timeout=5)
        except Exception:
            pass

    if not os.path.exists("data"):
        os.makedirs("data")
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_dict, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def add_to_history(category, value):
    if not value or str(value).strip() == "":
        return
    
    val_str = str(value).strip()
    
    history = load_history()
    if category not in history:
        history[category] = []
        
    if val_str not in history[category]:
        history[category].append(val_str)
        save_all_history(history)

def get_history(category):
    history = load_history()
    return history.get(category, [])

def remove_from_history(category, values_to_remove):
    """Remove one or more values from a history category."""
    if not values_to_remove:
        return
    history = load_history()
    if category in history:
        history[category] = [v for v in history[category] if v not in values_to_remove]
        save_all_history(history)

# ---- Persistent Base Data ----
BASE_DATA_FILE = "data/base_data.json"

def save_base_data(data_dict):
    """Save base data (salary, employee info, holidays) to a persistent JSON file."""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Convert holidays DataFrame to list of dicts for JSON serialization
    serializable = dict(data_dict)
    if 'holidays_df' in serializable:
        import pandas as pd
        df = serializable['holidays_df']
        if isinstance(df, pd.DataFrame):
            # Convert datetime columns to string
            df_copy = df.copy()
            for col in df_copy.columns:
                if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                    df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d")
            # Replace NaT and NaN with None so JSON encoder generates 'null' instead of invalid 'NaN'
            df_copy = df_copy.replace({pd.NaT: None})
            df_copy = df_copy.where(pd.notnull(df_copy), None)
            serializable['holidays_df'] = df_copy.to_dict(orient='records')
    
    # We also need to recursively clean any other NaNs in the dictionary to be 100% sure Firebase accepts it
    def clean_nans(obj):
        import math
        if isinstance(obj, dict):
            return {k: clean_nans(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nans(v) for v in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        return obj
    
    serializable = clean_nans(serializable)
    
    try:
        firebase_url = get_firebase_url("base_data.json")
        if firebase_url:
            # Dump to string using default=str to handle any unexpected objects (like np.int64)
            import json
            json_str = json.dumps(serializable, ensure_ascii=False, default=str)
            requests.put(firebase_url, data=json_str.encode('utf-8'), timeout=5, headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(f"Firebase save error: {e}")

    try:
        with open(BASE_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=4, default=str)
    except Exception:
        pass

def load_base_data():
    """Load base data from persistent JSON file. Returns None if not found."""
    data = None
    
    firebase_url = get_firebase_url("base_data.json")
    if firebase_url:
        try:
            resp = requests.get(firebase_url, timeout=5)
            if resp.status_code == 200 and resp.json() is not None:
                data = resp.json()
        except Exception:
            pass

    if data is None:
        if not os.path.exists(BASE_DATA_FILE):
            return None
        try:
            with open(BASE_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return None
            
    try:
        import pandas as pd
        
        # Convert holidays back to DataFrame, ensuring correct columns
        if 'holidays_df' in data and isinstance(data['holidays_df'], list):
            if len(data['holidays_df']) > 0:
                data['holidays_df'] = pd.DataFrame(data['holidays_df'])
            else:
                data['holidays_df'] = pd.DataFrame(columns=["Ngày nghỉ", "Lý do"])
        else:
            data['holidays_df'] = pd.DataFrame(columns=["Ngày nghỉ", "Lý do"])
        
        return data
    except Exception:
        return None
