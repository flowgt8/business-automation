#!/usr/bin/env python3
"""
Plati Chat Manager - Auto-reply and Delivery System
"""

import requests
import hashlib
import time
import json
import os

# --- CONFIGURATION ---
SELLER_ID = 1179730
API_KEY = "9E0158D50BB2430D978F4707E3329153"

# Products to Auto-Deliver (Exact Name Match)
AUTO_PRODUCTS = [
    "Perplexity AI Pro Private Account | 1 Month",
    "Приватный аккаунт Perplexity AI Pro | 1 месяц"
]

# The Auto-Delivery Message
DELIVERY_MSG = "Hello! Here is the link to access to inbox: https://s10.asurahosting.com/roundcube/?_task=mail&_mbox=INBOX"

# The Away Message
AWAY_MSG = "I will read your message and reply as soon as I return!"

# System Files
PROCESSED_FILE = "delivered_orders.txt"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return []
    with open(PROCESSED_FILE, "r") as f:
        return f.read().splitlines()

def save_processed(invoice_id):
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{invoice_id}\n")

def get_token():
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()
    url = "https://api.digiseller.com/api/apilogin"
    payload = {"seller_id": SELLER_ID, "timestamp": int(timestamp), "sign": sign}
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if r.json().get("retval") == 0:
            return r.json().get("token")
    except:
        pass
    return None

def get_unread_chats(token):
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}&filter_new=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json().get("items", [])
    except:
        return []

def get_last_message(token, invoice_id):
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}&newer=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        msgs = r.json()
        if msgs:
            return msgs[0].get("message", "")  # Return newest
    except:
        pass
    return ""

def send_reply(token, invoice_id, text):
    url = f"https://api.digiseller.com/api/debates/v2/?token={token}&id_i={invoice_id}"
    payload = {"message": text}
    try:
        requests.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"✅ Sent to #{invoice_id}")
        # Mark as read immediately
        requests.post(f"https://api.digiseller.com/api/debates/v2/seen?token={token}&id_i={invoice_id}", headers=HEADERS)
    except Exception as e:
        print(f"❌ Send Failed: {e}")

def main():
    print("=" * 60)
    print("🤖 Plati Chat Manager - Clawbot Master Control")
    print("=" * 60)
    
    mode = input("\nAre you currently HERE at the computer? (y/n): ").lower()
    away_mode = False
    
    if mode == 'n':
        away_mode = True
        print("🌙 AWAY MODE ACTIVATED. Bot will auto-reply to general questions.")
    else:
        print("🟢 LIVE MODE ACTIVATED. Bot will ask you for replies.")
    
    processed = load_processed()
    token = get_token()
    
    if not token:
        print("❌ Failed to authenticate. Check API key.")
        return
    
    print(f"\n✅ Authenticated. Monitoring for new chats...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            if not token:
                token = get_token()
            
            # Check for NEW chats
            chats = get_unread_chats(token)
            
            if chats:
                for chat in chats:
                    invoice = str(chat.get("id_i"))
                    product = chat.get("product", "")
                    email = chat.get("email", "")
                    
                    print(f"\n🔔 New Chat: Order #{invoice}")
                    print(f"   Product: {product}")
                    print(f"   Email: {email}")
                    
                    # Check if auto-delivery product
                    is_auto_product = any(auto_prod in product for auto_prod in AUTO_PRODUCTS)
                    
                    if is_auto_product and invoice not in processed:
                        # Auto-delivery
                        print(f"   🤖 Auto-delivery triggered!")
                        send_reply(token, invoice, DELIVERY_MSG)
                        save_processed(invoice)
                        print(f"   ✅ Delivery link sent!")
                    
                    elif away_mode:
                        # Away mode - auto-reply
                        print(f"   🌙 Away mode - sending auto-reply...")
                        send_reply(token, invoice, AWAY_MSG)
                    
                    else:
                        # Live mode - ask user for reply
                        last_msg = get_last_message(token, invoice)
                        print(f"\n💬 Buyer message: {last_msg}")
                        print("-" * 60)
                        
                        reply = input("Your reply (or press Enter to skip): ")
                        if reply.strip():
                            send_reply(token, invoice, reply)
                        else:
                            print("   ⏭️  Skipped")
            
            # Check every 30 seconds
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Chat manager stopped.")

if __name__ == "__main__":
    main()
