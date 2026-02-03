#!/usr/bin/env python3
"""
OpenClaw Integrated Chat Monitor
Runs as background service, notifies AI when new chats arrive
"""

import requests
import hashlib
import time
import json
import os
import sys

# --- CONFIGURATION ---
SELLER_ID = 1179730
API_KEY = "9E0158D50BB2430D978F4707E3329153"

AUTO_PRODUCTS = [
    "Perplexity AI Pro Private Account | 1 Month",
    "Приватный аккаунт Perplexity AI Pro | 1 месяц"
]

DELIVERY_MSG = "Hello! Here is the link to access to inbox: https://s10.asurahosting.com/roundcube/?_task=mail&_mbox=INBOX"
AWAY_MSG = "I will read your message and reply as soon as I return!"

# Files
QUEUE_FILE = "/root/.openclaw/workspace/business/digital-goods/chat_queue.json"
STATE_FILE = "/root/.openclaw/workspace/business/digital-goods/chat_state.json"
LOG_FILE = "/tmp/chat_monitor.log"

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_token():
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()
    url = "https://api.digiseller.com/api/apilogin"
    payload = {"seller_id": SELLER_ID, "timestamp": int(timestamp), "sign": sign}
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if r.json().get("retval") == 0:
            return r.json().get("token")
    except Exception as e:
        log(f"Auth error: {e}")
    return None

def get_unread_chats(token):
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}&filter_new=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json().get("items", [])
    except Exception as e:
        log(f"Fetch error: {e}")
        return []

def get_chat_history(token, invoice_id):
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json() or []
    except:
        return []

def send_reply(token, invoice_id, text):
    url = f"https://api.digiseller.com/api/debates/v2/?token={token}&id_i={invoice_id}"
    payload = {"message": text}
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        # Mark as read
        requests.post(f"https://api.digiseller.com/api/debates/v2/seen?token={token}&id_i={invoice_id}", headers=HEADERS)
        return r.status_code == 200
    except Exception as e:
        log(f"Send error: {e}")
        return False

def check_chats():
    """Main monitoring function - checks for new chats and queues them"""
    state = load_json(STATE_FILE, {"processed": [], "away_mode": False})
    queue = load_json(QUEUE_FILE, {"pending": [], "auto_delivered": []})
    
    token = get_token()
    if not token:
        log("❌ Failed to authenticate")
        return
    
    chats = get_unread_chats(token)
    
    if not chats:
        log("No new chats")
        return
    
    log(f"Found {len(chats)} new chat(s)")
    
    new_items = []
    
    for chat in chats:
        invoice = str(chat.get("id_i"))
        product = chat.get("product", "")
        email = chat.get("email", "")
        
        if invoice in state["processed"]:
            continue
        
        # Get message history
        history = get_chat_history(token, invoice)
        last_message = ""
        if history and len(history) > 0:
            # Get the most recent message from buyer (not from seller)
            for msg in reversed(history):
                if msg.get("type") == "in":  # Message from buyer
                    last_message = msg.get("message", "")
                    break
        
        item = {
            "invoice": invoice,
            "product": product,
            "email": email,
            "message": last_message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "requires_attention": True
        }
        
        # Check if auto-delivery product
        is_auto = any(auto in product for auto in AUTO_PRODUCTS)
        
        if is_auto:
            # Auto-deliver immediately
            log(f"⚡️ Auto-delivering to #{invoice} ({product})")
            if send_reply(token, invoice, DELIVERY_MSG):
                item["auto_delivered"] = True
                item["requires_attention"] = False
                queue["auto_delivered"].append(item)
                state["processed"].append(invoice)
                log(f"✅ Auto-delivered to #{invoice}")
            else:
                log(f"❌ Auto-delivery failed for #{invoice}")
                new_items.append(item)
        elif state.get("away_mode", False):
            # Away mode - send auto-reply
            log(f"🌙 Away mode reply to #{invoice}")
            if send_reply(token, invoice, AWAY_MSG):
                item["away_reply_sent"] = True
                state["processed"].append(invoice)
                log(f"✅ Away reply sent to #{invoice}")
            else:
                new_items.append(item)
        else:
            # Live mode - needs human attention
            new_items.append(item)
            log(f"🔔 Queued #{invoice} for attention")
    
    # Add new items to queue
    queue["pending"].extend(new_items)
    
    # Save state
    save_json(QUEUE_FILE, queue)
    save_json(STATE_FILE, state)
    
    if new_items:
        log(f"📋 {len(new_items)} chat(s) queued for your reply")
        # Print summary for OpenClaw to capture
        print("\n" + "="*60)
        print("🚨 NEW CHATS NEED YOUR ATTENTION")
        print("="*60)
        for item in new_items:
            print(f"\n📩 Order #{item['invoice']}")
            print(f"   Product: {item['product']}")
            print(f"   Email: {item['email']}")
            print(f"   Message: {item['message'][:100]}{'...' if len(item['message']) > 100 else ''}")
        print("\n" + "="*60)
        print("Reply with: chat reply <invoice_id> <your message>")
        print("Or run: python3 chat_cli.py")
        print("="*60 + "\n")

def set_away_mode(enabled):
    """Toggle away mode"""
    state = load_json(STATE_FILE, {"processed": [], "away_mode": False})
    state["away_mode"] = enabled
    save_json(STATE_FILE, state)
    status = "ENABLED" if enabled else "DISABLED"
    log(f"🌙 Away mode {status}")

def get_pending_chats():
    """Get list of chats waiting for reply"""
    queue = load_json(QUEUE_FILE, {"pending": [], "auto_delivered": []})
    return queue.get("pending", [])

def reply_to_chat(invoice_id, message):
    """Send a reply to a specific chat"""
    state = load_json(STATE_FILE, {"processed": [], "away_mode": False})
    queue = load_json(QUEUE_FILE, {"pending": [], "auto_delivered": []})
    
    token = get_token()
    if not token:
        return False, "Authentication failed"
    
    if send_reply(token, invoice_id, message):
        # Mark as processed
        state["processed"].append(invoice_id)
        # Remove from pending
        queue["pending"] = [c for c in queue["pending"] if c["invoice"] != invoice_id]
        
        save_json(STATE_FILE, state)
        save_json(QUEUE_FILE, queue)
        return True, "Reply sent successfully"
    else:
        return False, "Failed to send reply"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Chat Monitor")
    parser.add_argument("--check", action="store_true", help="Check for new chats")
    parser.add_argument("--away", choices=["on", "off"], help="Set away mode")
    parser.add_argument("--reply", metavar="INVOICE", help="Reply to invoice")
    parser.add_argument("--message", help="Message to send")
    parser.add_argument("--pending", action="store_true", help="Show pending chats")
    
    args = parser.parse_args()
    
    if args.check:
        check_chats()
    elif args.away:
        set_away_mode(args.away == "on")
    elif args.reply and args.message:
        success, msg = reply_to_chat(args.reply, args.message)
        print(msg)
    elif args.pending:
        pending = get_pending_chats()
        if pending:
            print(f"\n📋 {len(pending)} chat(s) pending:\n")
            for c in pending:
                print(f"  #{c['invoice']} | {c['product'][:40]}...")
                print(f"     Message: {c['message'][:60]}{'...' if len(c['message']) > 60 else ''}\n")
        else:
            print("No pending chats")
    else:
        # Default: check once
        check_chats()
