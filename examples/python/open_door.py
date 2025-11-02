import requests
import json

# === Device settings ===
DEVICE_IP = "192.168.88.209"
SESSION_ID = "your_session_id_from_browser"
url = f"http://{DEVICE_IP}/RPC2"
headers = {"Content-Type": "application/json"}

# === 1) Initialization ===
initialization_payload = {
    "method": "accessControl.factory.instance",
    "params": {"Channel": 0},
    "id": 3,
    "session": SESSION_ID
}

r = requests.post(url, headers=headers, data=json.dumps(initialization_payload))
print("Initialization:", r.json())

obj_id = r.json().get("result")

# === 2) Open the door ===
open_door_payload = {
    "method": "accessControl.openDoor",
    "object": obj_id,
    "params": {"Type": "Remote", "UserID": 1115},
    "id": 4,
    "session": SESSION_ID
}

r = requests.post(url, headers=headers, data=json.dumps(open_door_payload))
print("Open door response:", r.json())
