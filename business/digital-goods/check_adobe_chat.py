#!/usr/bin/env python3
import requests
import hashlib
import time

API_KEY = '9E0158D50BB2430D978F4707E3329153'
SELLER_ID = 1179730

# Get token
timestamp = str(int(time.time()))
sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()
r = requests.post('https://api.digiseller.com/api/apilogin', 
    json={'seller_id': SELLER_ID, 'timestamp': int(timestamp), 'sign': sign},
    timeout=30)
token = r.json().get('token')
print(f"Token: {token[:20]}...")

# Get all messages for Adobe order
url = f'https://api.digiseller.com/api/debates/v2?token={token}&id_i=283346375'
print(f"Fetching: {url[:80]}...")
r = requests.get(url, headers={'Accept': 'application/json'}, timeout=30)
messages = r.json() if isinstance(r.json(), list) else []

print(f'\nAll messages for Order #283346375 ({len(messages)} total):\n')
for msg in messages:
    sender = 'BUYER' if msg.get('buyer') == 1 else 'SELLER'
    date = msg.get('date_written', 'N/A')
    text = msg.get('message', 'N/A')
    seen = 'READ' if msg.get('date_seen') else 'UNREAD'
    print(f'{sender} | {date} | {seen}')
    print(f'  "{text}"\n')
