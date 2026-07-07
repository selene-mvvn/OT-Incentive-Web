import json
import os
import requests
import streamlit as st

OT_HISTORY_FILE = "data/ot_history.json"
INCENTIVE_HISTORY_FILE = "data/incentive_history.json"

def get_firebase_url(path):
    try:
        base_url = st.secrets.get("FIREBASE_URL")
        if base_url:
            return f"{base_url.rstrip('/')}/{path}"
    except Exception:
        pass
    return None

def init_history_records():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(OT_HISTORY_FILE):
        with open(OT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    if not os.path.exists(INCENTIVE_HISTORY_FILE):
        with open(INCENTIVE_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def deduplicate_records(records, file_type="ot"):
    if not records:
        return []
    import pandas as pd
    import json
    df = pd.DataFrame(records)
    if file_type == 'ot':
        if all(c in df.columns for c in ['ot_date', 'employee_name', 'order_name', 'ot_hours']):
            df = df.drop_duplicates(subset=['ot_date', 'employee_name', 'order_name', 'ot_hours'], keep='first')
        else:
            df = df.drop_duplicates()
    else:
        if all(c in df.columns for c in ['date', 'employee_name', 'project_name', 'final_incentive']):
            df = df.drop_duplicates(subset=['date', 'employee_name', 'project_name', 'final_incentive'], keep='first')
        else:
            df = df.drop_duplicates()
    return json.loads(df.to_json(orient='records'))

def get_records(file_type="ot"):
    """file_type can be 'ot' or 'incentive'"""
    filename = "ot_history.json" if file_type == "ot" else "incentive_history.json"
    local_file = OT_HISTORY_FILE if file_type == "ot" else INCENTIVE_HISTORY_FILE
    
    firebase_url = get_firebase_url(filename)
    if firebase_url:
        try:
            resp = requests.get(firebase_url, timeout=5)
            if resp.status_code == 200 and resp.json() is not None:
                return deduplicate_records(resp.json(), file_type)
        except Exception:
            pass

    init_history_records()
    try:
        with open(local_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return deduplicate_records(data if data else [], file_type)
    except Exception:
        return []

def add_records(file_type, new_records_list):
    if not new_records_list:
        return True
        
    filename = "ot_history.json" if file_type == "ot" else "incentive_history.json"
    local_file = OT_HISTORY_FILE if file_type == "ot" else INCENTIVE_HISTORY_FILE
    
    current_records = get_records(file_type)
    current_records.extend(new_records_list)
    
    import pandas as pd
    if current_records:
        import json
        current_records = deduplicate_records(current_records, file_type)

    firebase_url = get_firebase_url(filename)
    if firebase_url:
        try:
            requests.put(firebase_url, json=current_records, timeout=5)
        except Exception:
            pass
            
    init_history_records()
    try:
        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(current_records, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving history records: {e}")
        return False


def save_all_records(file_type, records_list):
    filename = "ot_history.json" if file_type == "ot" else "incentive_history.json"
    local_file = OT_HISTORY_FILE if file_type == "ot" else INCENTIVE_HISTORY_FILE
    
    import pandas as pd
    if records_list:
        import json
        records_list = deduplicate_records(records_list, file_type)

    firebase_url = get_firebase_url(filename)
    if firebase_url:
        try:
            import requests
            requests.put(firebase_url, json=records_list, timeout=5)
        except Exception:
            pass
            
    init_history_records()
    try:
        import json
        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(records_list, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving history records: {e}")
        return False
