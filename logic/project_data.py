import json
import os
import pandas as pd
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

PROJECT_FILE = "data/projects.json"

def init_project_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PROJECT_FILE):
        with open(PROJECT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def get_projects_df():
    firebase_url = get_firebase_url("projects.json")
    if firebase_url:
        try:
            resp = requests.get(firebase_url, timeout=5)
            if resp.status_code == 200 and resp.json() is not None:
                data = resp.json()
                if not data:
                    return pd.DataFrame(columns=["Tên dự án", "Mã đơn hàng", "Mã KH", "Loại dự án", "Tên PM"])
                return pd.DataFrame(data)
        except Exception:
            pass

    init_project_data()
    try:
        with open(PROJECT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data:
                return pd.DataFrame(columns=["Tên dự án", "Mã đơn hàng", "Mã KH", "Loại dự án", "Tên PM"])
            return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame(columns=["Tên dự án", "Mã đơn hàng", "Mã KH", "Loại dự án", "Tên PM"])

def save_projects_df(df):
    try:
        data = df.to_dict("records")
        
        firebase_url = get_firebase_url("projects.json")
        if firebase_url:
            try:
                requests.put(firebase_url, json=data, timeout=5)
            except Exception:
                pass
                
        init_project_data()
        with open(PROJECT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving project data: {e}")
        return False
