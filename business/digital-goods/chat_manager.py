#!/usr/bin/env python3
"""
Plati Chat Manager - Auto-reply and Delivery System
Improved version with priority logic
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
    """Load list of already processed order IDs"""
    if not os.path.exists(PROCESSED_FILE):
        return []
    with open(PROCESSED_FILE, "r") as f:
        return f.read().splitlines()

def save_processed(invoice_id):
    """Save order ID as processed"""
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{invoice_id}\n")

def get_token():
    """Get authentication token from Digiseller API"""
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
    """Get list of unread chat conversations"""
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}&filter_new=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json().get("items", [])
    except:
        return []

def get_last_message(token, invoice_id):
    """Get the last message from a specific chat"""
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}&newer=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        msgs = r.json()
        if msgs:
            return msgs[0].get("message", "")
    except:
        pass
    return ""

def send_reply(token, invoice_id, text):
    """Send a reply message to a chat"""
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
                    
                    # --- PRIORITY 1: AUTO-DELIVERY (Perplexity) ---
                    # Logic: If product matches AND we haven't delivered yet
                    is_auto_product = any(auto_prod in product for auto_prod in AUTO_PRODUCTS)
                    
                    if is_auto_product and invoice not in processed:
                        print("⚡️ PERPLEXITY SALE DETECTED! Auto-delivering...")
                        send_reply(token, invoice, DELIVERY_MSG)
                        save_processed(invoice)
                        processed.append(invoice)
                        continue  # Skip the rest, we handled it
                    
                    # --- PRIORITY 2: AWAY MODE ---
                    if away_mode:
                        # Only send "Away" msg if we haven't already marked this chat processed
                        print("🌙 Sending Away Message...")
                        send_reply(token, invoice, AWAY_MSG)
                        continue
                    
                    # --- PRIORITY 3: LIVE INTERACTION ---
                    # Get the actual text the user sent
                    msg_text = get_last_message(token, invoice)
                    print(f"📩 Buyer ({email}) said: \"{msg_text}\"")
                    
                    reply = input(f"Type reply for #{invoice} (or Enter to skip): ")
                    if reply.strip():
                        send_reply(token, invoice, reply)
                    else:
                        print("Skipped.")
            
            # Wait 10 seconds before next check
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Bot Stopped.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot Stopped.")
