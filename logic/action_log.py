import json
import os
import uuid
import base64
import requests
import streamlit as st
from datetime import datetime

def get_firebase_url(path):
    try:
        base_url = st.secrets.get("FIREBASE_URL")
        if base_url:
            return f"{base_url.rstrip('/')}/{path}"
    except Exception:
        pass
    return None

LOG_FILE = "data/action_logs.json"
HISTORY_DIR = "data/history_files"

def init_history_system():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def get_action_logs():
    firebase_url = get_firebase_url("action_logs.json")
    if firebase_url:
        try:
            resp = requests.get(firebase_url, timeout=5)
            if resp.status_code == 200 and resp.json() is not None:
                return resp.json()
        except Exception:
            pass
            
    init_history_system()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_action_log(action_type_vn, action_type_jp, description_vn, description_jp, file_bytes, original_filename):
    file_id = str(uuid.uuid4())
    
    # Encode file to base64
    if hasattr(file_bytes, "getvalue"):
        fb = file_bytes.getvalue()
    else:
        fb = file_bytes
    b64_str = base64.b64encode(fb).decode("utf-8")
        
    logs = get_action_logs()
    
    new_log = {
        "id": file_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action_type_vn": action_type_vn,
        "action_type_jp": action_type_jp,
        "description_vn": description_vn,
        "description_jp": description_jp,
        "original_filename": original_filename,
        "file_b64": b64_str
    }
    
    logs.insert(0, new_log)
    
    if len(logs) > 100:
        logs.pop()
                
    firebase_url = get_firebase_url("action_logs.json")
    if firebase_url:
        try:
            requests.put(firebase_url, json=logs, timeout=5)
        except Exception:
            pass
            
    # Save back to local json as fallback
    init_history_system()
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving action logs: {e}")
        return False

def get_file_bytes(file_path):
    # Deprecated: files are now base64 encoded inside the log
    return None

def clear_all_logs():
    firebase_url = get_firebase_url("action_logs.json")
    if firebase_url:
        try:
            requests.put(firebase_url, json=[], timeout=5)
        except Exception:
            pass
            
    init_history_system()
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

def delete_action_log(log_id):
    try:
        logs = get_action_logs()
        new_logs = [log for log in logs if log.get("id") != log_id]
                
        firebase_url = get_firebase_url("action_logs.json")
        if firebase_url:
            try:
                requests.put(firebase_url, json=new_logs, timeout=5)
            except Exception:
                pass
                
        init_history_system()
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(new_logs, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error deleting action log: {e}")
        return False

def cleanup_missing_files():
    """Removes all log entries where the base64 data is missing."""
    try:
        logs = get_action_logs()
        valid_logs = [log for log in logs if log.get("file_b64") is not None]
                
        firebase_url = get_firebase_url("action_logs.json")
        if firebase_url:
            try:
                requests.put(firebase_url, json=valid_logs, timeout=5)
            except Exception:
                pass
                
        init_history_system()
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(valid_logs, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error cleaning up missing files: {e}")
        return False
