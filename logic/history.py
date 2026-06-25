import json
import os

HISTORY_FILE = "data/history.json"

def load_history():
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
            serializable['holidays_df'] = df_copy.to_dict(orient='records')
    
    try:
        with open(BASE_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=4, default=str)
    except Exception:
        pass

def load_base_data():
    """Load base data from persistent JSON file. Returns None if not found."""
    if not os.path.exists(BASE_DATA_FILE):
        return None
    try:
        import pandas as pd
        with open(BASE_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
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
