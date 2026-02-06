#!/usr/bin/env python3
import urllib.request
import json
import time
import hashlib
import html

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"

# Get token
ts = str(int(time.time()))
sign = hashlib.sha256((API_KEY + ts).encode()).hexdigest()
url = "https://api.digiseller.com/api/apilogin"
payload = json.dumps({"seller_id": int(SELLER_ID), "timestamp": int(ts), "sign": sign}).encode()
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=120) as r:
    token = json.loads(r.read().decode("utf-8")).get("token")

# Get messages for #284270433
msg_url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i=284270433"
req = urllib.request.Request(msg_url, headers={"Accept": "application/json"})
with urllib.request.urlopen(req, timeout=120) as r:
    msgs = json.loads(r.read().decode("utf-8"))

print(f"Found {len(msgs)} messages\n")

for m in msgs:
    if m.get("buyer") == 0:  # Seller message
        text = m.get("message", "")
        decoded = html.unescape(text)
        has_link = "s10.asurahosting.com" in decoded.lower()
        print(f"Seller: {decoded}")
        print(f"Has link: {has_link}\n")
