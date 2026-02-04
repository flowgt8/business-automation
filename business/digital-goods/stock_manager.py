#!/usr/bin/env python3
"""
Stock Manager - Add accounts to Digiseller products
Usage: python3 stock_manager.py --product perplexity --file accounts.txt
"""

import requests
import hashlib
import time
import json
import argparse
import os

API_KEY = "9E0158D50BB2430D978F4707E3329153"
SELLER_ID = 1179730

# Product mappings (you can add more)
PRODUCTS = {
    "perplexity": 5659428,  # Приватный аккаунт Perplexity AI Pro | 1 месяц
    "gemini": 5401507,      # GEMINI AI PRO 1-6 МЕСЯЦЕВ
    "canva": 5655941,       # Canva Pro 1/3/6 месяцев
    "chatgpt": 5658505,     # ЧатGPT Plus
    "cursor": 5402197,      # Cursor AI Pro
    "adobe": 5655904,       # Adobe Creative Cloud
}

def get_token():
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()
    url = "https://api.digiseller.com/api/apilogin"
    payload = {"seller_id": SELLER_ID, "timestamp": int(timestamp), "sign": sign}
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.json().get("retval") == 0:
            return r.json().get("token")
    except Exception as e:
        print(f"Auth error: {e}")
    return None

def add_text_content(token, product_id, value, serial=None):
    """Add a text content item to a product"""
    url = f"https://api.digiseller.com/api/product/content/add/text?token={token}"
    content_item = {"value": value, "id_v": 0}
    if serial:
        content_item["serial"] = serial
    
    payload = {
        "product_id": product_id,
        "content": [content_item]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=30)
        result = r.json()
        if result.get("retval") == 0:
            content_id = result.get("content", [{}])[0].get("content_id")
            return True, content_id
        else:
            return False, result.get("retdesc", "Unknown error")
    except Exception as e:
        return False, str(e)

def add_single_account(product_key, account_string):
    """Add a single account to a product"""
    if product_key not in PRODUCTS:
        print(f"❌ Unknown product: {product_key}")
        print(f"Available: {', '.join(PRODUCTS.keys())}")
        return False
    
    product_id = PRODUCTS[product_key]
    token = get_token()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    success, result = add_text_content(token, product_id, account_string)
    if success:
        print(f"✅ Added to {product_key}: {account_string[:30]}... (ID: {result})")
        return True
    else:
        print(f"❌ Failed: {result}")
        return False

def add_from_file(product_key, filepath):
    """Add multiple accounts from a file"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r') as f:
        accounts = [line.strip() for line in f if line.strip()]
    
    print(f"📦 Adding {len(accounts)} accounts to {product_key}...\n")
    
    added = 0
    failed = 0
    
    for account in accounts:
        if add_single_account(product_key, account):
            added += 1
        else:
            failed += 1
        time.sleep(0.5)  # Small delay between requests
    
    print(f"\n{'='*50}")
    print(f"✅ Added: {added}")
    print(f"❌ Failed: {failed}")
    print(f"{'='*50}")

def main():
    parser = argparse.ArgumentParser(description="Add accounts to Digiseller stock")
    parser.add_argument("--product", required=True, help="Product key (perplexity, gemini, canva, etc.)")
    parser.add_argument("--account", help="Single account string (email pass)")
    parser.add_argument("--file", help="File with accounts (one per line)")
    parser.add_argument("--list", action="store_true", help="List available products")
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📦 Available products:")
        for key, pid in PRODUCTS.items():
            print(f"  {key:<12} -> ID: {pid}")
        print()
        return
    
    if args.account:
        add_single_account(args.product, args.account)
    elif args.file:
        add_from_file(args.product, args.file)
    else:
        print("❌ Specify --account or --file")
        parser.print_help()

if __name__ == "__main__":
    main()
