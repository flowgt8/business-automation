#!/usr/bin/env python3
"""
Check Digiseller for new messages
Uses urllib (no requests dependency)
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import hashlib
import hmac
import base64

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"

def get_api_token():
    """Get API token for Digiseller"""
    timestamp = str(int(time.time()))
    sign = hmac.new(
        API_KEY.encode('utf-8'),
        timestamp.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    url = f"https://api.digiseller.com/api/apilogin?ticket={timestamp}&sign={sign}"
    
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                return result.get('token')
            else:
                print(f"Failed to get token: {result}")
                return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def get_messages(token):
    """Get pending messages from Digiseller"""
    url = f"https://api.digiseller.com/api/seller/{SELLER_ID}/chats/pending?token={token}"
    
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"Error getting messages: {e}")
        return None

def main():
    print("Checking Digiseller for new messages...")
    
    token = get_api_token()
    if not token:
        print("Could not authenticate with Digiseller")
        return
    
    messages = get_messages(token)
    if messages is None:
        print("Could not fetch messages")
        return
    
    print(f"\n=== Digiseller Messages ===")
    print(f"Total pending: {messages.get('pagination', {}).get('total', 'N/A')}")
    
    chats = messages.get('chats', [])
    if not chats:
        print("\n✅ No new pending messages!")
    else:
        print(f"\n📬 Found {len(chats)} pending messages:")
        for i, chat in enumerate(chats, 1):
            print(f"\n{i}. Order #{chat.get('order_id', 'N/A')}")
            print(f"   Buyer: {chat.get('buyer_email', 'N/A')}")
            print(f"   Product: {chat.get('product_name', 'N/A')}")
            print(f"   Last message: {chat.get('last_message', 'N/A')[:100]}...")
            print(f"   Unread: {chat.get('unread_cnt', 0)}")
    
    print("\n" + "="*30)

if __name__ == "__main__":
    main()
