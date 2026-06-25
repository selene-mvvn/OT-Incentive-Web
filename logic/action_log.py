import json
import os
import uuid
from datetime import datetime

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
    init_history_system()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_action_log(action_type_vn, action_type_jp, description_vn, description_jp, file_bytes, original_filename):
    init_history_system()
    
    # Generate a unique filename to store safely on disk
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(original_filename)[1]
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(HISTORY_DIR, safe_filename)
    
    # Save the physical file
    try:
        with open(file_path, "wb") as f:
            if hasattr(file_bytes, "getvalue"):
                f.write(file_bytes.getvalue())
            else:
                f.write(file_bytes)
    except Exception as e:
        print(f"Error saving history file: {e}")
        return False
        
    # Read existing logs
    logs = get_action_logs()
    
    # Create new log entry
    new_log = {
        "id": file_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action_type_vn": action_type_vn,
        "action_type_jp": action_type_jp,
        "description_vn": description_vn,
        "description_jp": description_jp,
        "original_filename": original_filename,
        "saved_path": file_path
    }
    
    # Insert at the beginning so newest is first
    logs.insert(0, new_log)
    
    # Optional: Keep only last 100 logs to prevent disk bloat
    if len(logs) > 100:
        oldest = logs.pop()
        old_file = oldest.get("saved_path")
        if old_file and os.path.exists(old_file):
            try:
                os.remove(old_file)
            except:
                pass
                
    # Save back to json
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving action logs: {e}")
        return False

def get_file_bytes(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()
    return None

def clear_all_logs():
    init_history_system()
    try:
        logs = get_action_logs()
        for log in logs:
            path = log.get("saved_path")
            if path and os.path.exists(path):
                os.remove(path)
                
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

def delete_action_log(log_id):
    init_history_system()
    try:
        logs = get_action_logs()
        new_logs = []
        for log in logs:
            if log.get("id") == log_id:
                path = log.get("saved_path")
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
            else:
                new_logs.append(log)
                
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(new_logs, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error deleting action log: {e}")
        return False

def cleanup_missing_files():
    """Removes all log entries where the physical file no longer exists."""
    init_history_system()
    try:
        logs = get_action_logs()
        valid_logs = []
        for log in logs:
            path = log.get("saved_path")
            if path and os.path.exists(path):
                valid_logs.append(log)
                
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(valid_logs, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error cleaning up missing files: {e}")
        return False
