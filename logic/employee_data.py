import json
import os
import pandas as pd
import requests
import streamlit as st

EMPLOYEE_FILE = "data/employees.json"

def get_firebase_url(path):
    try:
        base_url = st.secrets.get("FIREBASE_URL")
        if base_url:
            return f"{base_url.rstrip('/')}/{path}"
    except Exception:
        pass
    return None

def init_employee_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(EMPLOYEE_FILE):
        with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def get_employees_df():
    default_cols = ["Mã NV", "Tên NV", "Phòng ban", "Chức vụ", "Lương cơ bản", "PC ăn trưa", "PC khác", "Ngày bắt đầu tính", "Lương Gross"]
    
    def process_df(df):
        if "Ngày bắt đầu tính" not in df.columns:
            df["Ngày bắt đầu tính"] = None
        return df

    firebase_url = get_firebase_url("employees.json")
    if firebase_url:
        try:
            resp = requests.get(firebase_url, timeout=5)
            if resp.status_code == 200 and resp.json() is not None:
                data = resp.json()
                if not data:
                    return pd.DataFrame(columns=default_cols)
                return process_df(pd.DataFrame(data))
        except Exception:
            pass

    init_employee_data()
    try:
        with open(EMPLOYEE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data:
                return pd.DataFrame(columns=default_cols)
            return process_df(pd.DataFrame(data))
    except Exception:
        return pd.DataFrame(columns=default_cols)

def save_employees_df(df):
    try:
        json_str = df.to_json(orient="records", force_ascii=False)
        data = json.loads(json_str)
        
        firebase_url = get_firebase_url("employees.json")
        if firebase_url:
            try:
                resp = requests.put(firebase_url, json=data, timeout=5)
                if resp.status_code != 200:
                    st.toast(f"⚠️ Lỗi Firebase: {resp.text}", icon=":material/error:")
            except Exception as e:
                st.toast(f"⚠️ Lỗi kết nối Firebase: {e}", icon=":material/error:")
                
        init_employee_data()
        with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        # Clean up history and pending records for deleted employees
        try:
            if not df.empty and "Tên NV" in df.columns:
                valid_names = set(df["Tên NV"].dropna().astype(str).str.strip())
                
                # 1. Clean history files
                from logic.history_records import clean_history_records
                clean_history_records(valid_names)
                
                # 2. Clean session state for manual OT records (if currently in session)
                if "ot_records" in st.session_state and isinstance(st.session_state["ot_records"], list):
                    st.session_state["ot_records"] = [
                        r for r in st.session_state["ot_records"] 
                        if str(r.get("employee_name", "")).strip() in valid_names
                    ]
        except Exception as e:
            print(f"Error cleaning up records for deleted employees: {e}")
            
        return True
    except Exception as e:
        print(f"Error saving employee data: {e}")
        return False

