#!/usr/bin/env python3
"""
Fixed Chat Monitor - Saves all chats to workspace
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import hashlib
import os

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"

QUEUE_FILE = "/home/node/.openclaw/workspace/business/digital-goods/chat_queue.json"
STATE_FILE = "/home/node/.openclaw/workspace/business/digital-goods/chat_state.json"

def get_token():
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()
    
    url = "https://api.digiseller.com/api/apilogin"
    payload = json.dumps({
        "seller_id": int(SELLER_ID),
        "timestamp": int(timestamp),
        "sign": sign
    }).encode('utf-8')
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode('utf-8'))
            if data.get("retval") == 0:
                return data.get("token")
    except Exception as e:
        print(f"Auth error: {e}")
    return None

def get_all_chats(token):
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as r:
            chats = json.loads(r.read().decode('utf-8')).get("chats", [])
            chats.sort(key=lambda x: x.get('date_last', ''), reverse=True)
            return chats
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_chat_messages(token, invoice_id):
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read().decode('utf-8'))
            return result if isinstance(result, list) else []
    except Exception as e:
        print(f"Error fetching #{invoice_id}: {e}")
        return []

def main():
    print("Fetching chats...")
    token = get_token()
    if not token:
        print("Failed to get token")
        return
    
    chats = get_all_chats(token)
    if not chats:
        print("No chats found")
        return
    
    print(f"Found {len(chats)} chats\n")
    
    # Build queue with all chats
    queue = {"pending": [], "auto_delivered": []}
    state = {"processed": [], "processed_messages": [], "auto_delivered_orders": []}
    
    for chat in chats[:20]:  # Last 20 chats
        invoice = str(chat.get("id_i"))
        product = chat.get("product", "")
        email = chat.get("email", "")
        
        messages = get_chat_messages(token, invoice)
        buyer_msgs = [m for m in messages if m.get("buyer") == 1]
        
        if buyer_msgs:
            last_msg = buyer_msgs[-1]
            last_text = last_msg.get("message", "")
            last_time = last_msg.get("date_written", "")
            
            print(f"#{invoice} | {email} | {last_time}")
            print(f"   Last: {last_text[:50]}...")
            
            # Save all chats with buyer messages
            item = {
                "invoice": invoice,
                "product": product,
                "email": email,
                "message": last_text,
                "message_id": last_msg.get("id"),
                "timestamp": last_time,
                "requires_attention": True,
                "auto_delivered": False
            }
            queue["pending"].append(item)
    
    # Save to workspace
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)
    
    print(f"\n✅ Saved {len(queue['pending'])} chats to {QUEUE_FILE}")

if __name__ == "__main__":
    main()
