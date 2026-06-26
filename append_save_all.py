with open('logic/history_records.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_func = '''
def save_all_records(file_type, records_list):
    filename = "ot_history.json" if file_type == "ot" else "incentive_history.json"
    local_file = OT_HISTORY_FILE if file_type == "ot" else INCENTIVE_HISTORY_FILE
    
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
'''

if 'def save_all_records' not in text:
    text += '\n' + new_func

with open('logic/history_records.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated history_records.py')
