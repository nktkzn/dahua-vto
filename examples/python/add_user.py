import requests
import json

# === Device settings ===
DEVICE_IP = "192.168.88.209"
SESSION_ID = "your_session_id_from_browser"
url = f"http://{DEVICE_IP}/RPC2"
headers = {"Content-Type": "application/json"}

# === User and card data ===
user_id = "777"
user_name = "UserName"
room_no = "888"

card_no = "98989"
card_name = "CardName"

# === 1) Create user ===
create_user_payload = {
    "method": "AccessUser.insertMulti",
    "params": {
        "UserList": [
            {
                "UserID": user_id,
                "UserName": user_name,
                "RoomNo": [room_no],
                "Authority": 2,
                "UserType": 0,
                "UserStatus": 0,
                "Doors": [0, 1],
                "UseTime": -1
            }
        ]
    },
    "id": 1,
    "session": SESSION_ID
}

r = requests.post(url, headers=headers, data=json.dumps(create_user_payload))
print("Create user:", r.json())

# === 2) Add card and link to the user ===
insert_card_payload = {
    "method": "AccessCard.insertMulti",
    "params": {
        "CardList": [
            {
                "CardNo": card_no,
                "CardName": card_name,
                "CardStatus": 0,
                "CardType": 0,
                "UserID": user_id,
                "ValidDateStart": "0000-00-00 00:00:00",
                "ValidDateEnd": "0000-00-00 00:00:00"
            }
        ]
    },
    "id": 2,
    "session": SESSION_ID
}

r = requests.post(url, headers=headers, data=json.dumps(insert_card_payload))
print("Add card:", r.json())
