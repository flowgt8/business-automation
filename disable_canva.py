#!/usr/bin/env python3
"""
Disable Canva Pro product on Digiseller
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import hashlib

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"
PRODUCT_ID = 5655941  # Canva Pro

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

def update_product_status(token, product_id, active=False):
    """Update product to be inactive"""
    url = f"https://api.digiseller.com/api/seller/products/{product_id}/update"
    
    payload = json.dumps({
        "id": product_id,
        "active": active  # False = inactive
    }).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8')[:300]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("Disabling Canva Pro product...\n")
    
    token = get_token()
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"Token received. Updating product {PRODUCT_ID}...")
    
    result = update_product_status(token, PRODUCT_ID, active=False)
    
    if result:
        print(f"\n✅ Result: {json.dumps(result, indent=2)}")
    else:
        print("❌ Failed to update product")

if __name__ == "__main__":
    main()
