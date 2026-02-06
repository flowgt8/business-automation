#!/usr/bin/env python3
"""
Get pending chats from Digiseller
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

def get_pending_chats(token):
    """Get pending chats"""
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_all_chats(token):
    """Get all chats"""
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Getting Digiseller token...")
    token = get_token()
    if token:
        print("Token received. Checking pending chats...")
        pending = get_pending_chats(token)
        if pending:
            print(f"\nPending chats: {json.dumps(pending, indent=2)[:2000]}")
        else:
            print("No pending chats or error")
        
        print("\nChecking all chats...")
        all_chats = get_all_chats(token)
        if all_chats:
            print(f"\nAll chats: {json.dumps(all_chats, indent=2)[:2000]}")
