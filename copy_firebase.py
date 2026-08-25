import requests
import json
import sys

old_url = "https://ot-incentive-db-default-rtdb.asia-southeast1.firebasedatabase.app/vietmos_secure_2024_ot_incentive.json"
new_url = "https://ot-incentive-db-default-rtdb.asia-southeast1.firebasedatabase.app/vietmos_secure_2021_ot_incentive.json"

print("Fetching data from old URL...")
response = requests.get(old_url)
if response.status_code != 200:
    print(f"Failed to fetch data: {response.status_code}")
    print(response.text)
    sys.exit(1)

data = response.json()
print("Data fetched successfully. Size:", len(json.dumps(data)))

print("Writing data to new URL...")
put_response = requests.put(new_url, json=data)
if put_response.status_code != 200:
    print(f"Failed to write data: {put_response.status_code}")
    print(put_response.text)
    sys.exit(1)

print("Data successfully copied to new URL!")
