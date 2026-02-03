#!/usr/bin/env python3
import requests
import hashlib
import time
import json

SELLER_ID = 1179730
API_KEY = "9E0158D50BB2430D978F4707E3329153"

# Get token
timestamp = str(int(time.time()))
sign = hashlib.sha256((API_KEY + timestamp).encode("utf-8")).hexdigest()
url = "https://api.digiseller.com/api/apilogin"
payload = {"seller_id": SELLER_ID, "timestamp": int(timestamp), "sign": sign}
r = requests.post(url, json=payload, timeout=10)
token = r.json().get("token")

# Check all chats for unread messages
url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
r = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
chats = r.json().get("chats", [])

print("Chats with UNREAD messages from buyer:\n")
found = False

for chat in chats:
    invoice = chat.get("id_i")
    product = chat.get("product", "N/A")[:50]
    email = chat.get("email", "N/A")
    
    # Get messages
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice}"
    r = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
    messages = r.json() if isinstance(r.json(), list) else []
    
    # Check for unread from buyer
    unread = [m for m in messages if m.get("buyer") == 1 and m.get("date_seen") is None]
    
    if unread:
        found = True
        print(f"#{invoice} | {product}")
        print(f"  Email: {email}")
        print(f"  Unread messages: {len(unread)}")
        for msg in unread:
            text = msg.get("message", "N/A")[:80]
            print(f'  💬 "{text}"')
        print()

if not found:
    print("No unread messages found in any chat.")
