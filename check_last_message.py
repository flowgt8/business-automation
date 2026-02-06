#!/usr/bin/env python3
"""
Check for last message received from Digiseller
Uses urllib (no requests dependency)
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import hashlib

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"

def get_token():
    """Get API token"""
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
            else:
                print(f"Auth failed: {data}")
                return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def get_all_chats(token):
    """Get ALL chats sorted by most recent activity"""
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as r:
            chats = json.loads(r.read().decode('utf-8')).get("chats", [])
            # Sort by last message date (most recent first)
            chats.sort(key=lambda x: x.get('date_last', ''), reverse=True)
            return chats
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8')[:500]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_chat_messages(token, invoice_id):
    """Get all messages for a specific chat"""
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read().decode('utf-8'))
            return result if isinstance(result, list) else []
    except Exception as e:
        print(f"Error fetching messages for #{invoice_id}: {e}")
        return []

def main():
    print("Authenticating with Digiseller...")
    token = get_token()
    if not token:
        print("❌ Failed to get token")
        return
    
    print("Getting all chats...")
    chats = get_all_chats(token)
    if chats is None:
        print("❌ Failed to get chats")
        return
    
    if not chats:
        print("No chats found")
        return
    
    print(f"\nFound {len(chats)} chat(s)\n")
    
    # Get messages for the most recent chat
    most_recent = chats[0]
    invoice = most_recent.get("id_i")
    product = most_recent.get("product", "")
    email = most_recent.get("email", "")
    date_last = most_recent.get("date_last", "")
    
    print(f"Most recent chat:")
    print(f"  Order: #{invoice}")
    print(f"  Product: {product}")
    print(f"  Customer: {email}")
    print(f"  Last activity: {date_last}")
    
    print(f"\nMessages:")
    messages = get_chat_messages(token, invoice)
    if messages:
        # Show last message from buyer
        buyer_msgs = [m for m in messages if m.get("buyer") == 1]
        if buyer_msgs:
            last_buyer = buyer_msgs[-1]
            print(f"  Last buyer message: {last_buyer.get('message', '')}")
            print(f"  Time: {last_buyer.get('date_written', '')}")
        else:
            print("  No messages from buyer")
    else:
        print("  Could not fetch messages")
    
    print("\n" + "="*50)
    print("All chats (sorted by recent):")
    print("="*50)
    for i, chat in enumerate(chats[:10], 1):
        print(f"\n{i}. #{chat.get('id_i')} | {chat.get('product', '')[:40]}")
        print(f"   {chat.get('email', 'N/A')} | {chat.get('date_last', '')}")

if __name__ == "__main__":
    main()
