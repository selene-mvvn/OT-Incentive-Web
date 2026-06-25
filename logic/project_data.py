import json
import os
import pandas as pd

PROJECT_FILE = "data/projects.json"

def init_project_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PROJECT_FILE):
        with open(PROJECT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def get_projects_df():
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
    init_project_data()
    try:
        data = df.to_dict("records")
        with open(PROJECT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving project data: {e}")
        return False
