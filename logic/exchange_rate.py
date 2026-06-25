import urllib.request
import json
import time

# Cache to avoid hitting the API too frequently
_cached_rate = None
_last_fetch_time = 0
CACHE_DURATION_SECONDS = 3600 # 1 hour

def get_jpy_to_vnd_rate():
    global _cached_rate, _last_fetch_time
    
    current_time = time.time()
    
    # Return cached rate if still valid
    if _cached_rate is not None and (current_time - _last_fetch_time) < CACHE_DURATION_SECONDS:
        return _cached_rate
        
    try:
        url = "https://open.er-api.com/v6/latest/JPY"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if "rates" in data and "VND" in data["rates"]:
                _cached_rate = data["rates"]["VND"]
                _last_fetch_time = current_time
                return _cached_rate
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        
    # Fallback rate if API fails (approximate standard rate)
    if _cached_rate is None:
        return 165.0 
    return _cached_rate
