#!/usr/bin/env python3
"""
OpenClaw Integrated Chat Monitor - OPTIMIZED VERSION
Prioritizes recent chats and handles slow API better
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
QUEUE_FILE = "/home/node/.openclaw/workspace/business/digital-goods/chat_queue.json"
STATE_FILE = "/home/node/.openclaw/workspace/business/digital-goods/chat_state.json"
LOG_FILE = "/home/node/.openclaw/workspace/chat_monitor.log"

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
API_TIMEOUT = 120  # 2 minutes per API call (Digiseller is very slow)

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
        r = requests.post(url, json=payload, headers=HEADERS, timeout=API_TIMEOUT)
        if r.json().get("retval") == 0:
            return r.json().get("token")
    except Exception as e:
        log(f"Auth error: {e}")
    return None

def get_all_chats(token):
    """Get ALL chats sorted by most recent activity"""
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)
        chats = r.json().get("chats", [])
        # Sort by last message date (most recent first)
        chats.sort(key=lambda x: x.get('date_last', ''), reverse=True)
        return chats
    except Exception as e:
        log(f"Fetch error: {e}")
        return []

def get_chat_messages(token, invoice_id):
    """Get all messages for a specific chat"""
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)
        result = r.json()
        return result if isinstance(result, list) else []
    except Exception as e:
        log(f"Message fetch error for #{invoice_id}: {e}")
        return []

def has_unread_buyer_messages(messages):
    """Check if there are unread messages from buyer"""
    for msg in messages:
        if msg.get("buyer") == 1 and msg.get("date_seen") is None:
            return True
    return False

def get_last_buyer_message(messages):
    """Get the most recent unread message from buyer"""
    unread_buyer_msgs = [m for m in messages if m.get("buyer") == 1 and m.get("date_seen") is None]
    if unread_buyer_msgs:
        return unread_buyer_msgs[-1]
    return None

def send_reply(token, invoice_id, text):
    """Send a reply message to a chat"""
    url = f"https://api.digiseller.com/api/debates/v2/?token={token}&id_i={invoice_id}"
    payload = {"message": text}
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=API_TIMEOUT)
        # Mark as read
        requests.post(f"https://api.digiseller.com/api/debates/v2/seen?token={token}&id_i={invoice_id}", 
                     headers=HEADERS, timeout=API_TIMEOUT)
        return r.status_code == 200
    except Exception as e:
        log(f"Send error: {e}")
        return False

def check_chats():
    """Main monitoring function - checks for new chats and queues them"""
    state = load_json(STATE_FILE, {"processed": [], "processed_messages": [], "auto_delivered_orders": [], "away_mode": False})
    queue = load_json(QUEUE_FILE, {"pending": [], "auto_delivered": []})
    processed_msgs = set(state.get("processed_messages", []))
    auto_delivered_orders = set(state.get("auto_delivered_orders", []))
    
    token = get_token()
    if not token:
        log("❌ Failed to authenticate")
        return
    
    # Get ALL chats sorted by most recent first
    all_chats = get_all_chats(token)
    
    if not all_chats:
        log("No chats found")
        return
    
    # Check ALL chats (don't skip any - causes missed messages!)
    chats_to_check = all_chats
    
    log(f"Checking all {len(chats_to_check)} chat(s)...")
    
    new_items = []
    needs_attention_count = 0
    
    for chat in chats_to_check:
        invoice = str(chat.get("id_i"))
        product = chat.get("product", "")
        email = chat.get("email", "")
        
        # Get messages for this chat
        messages = get_chat_messages(token, invoice)
        
        # Get unread messages from buyer that we haven't processed yet
        unread_msgs = [m for m in messages if m.get("buyer") == 1 and m.get("date_seen") is None]
        new_unread = [m for m in unread_msgs if f"{invoice}_{m.get('id')}" not in processed_msgs]
        
        if not new_unread:
            continue  # No new unread messages, skip
        
        needs_attention_count += 1
        
        # Get the most recent new message
        last_msg = new_unread[-1]
        last_message_text = last_msg.get("message", "")
        last_message_id = last_msg.get("id")
        
        # Use the ACTUAL message timestamp from API (date_written), not current time!
        msg_date_written = last_msg.get("date_written", "")
        if msg_date_written:
            msg_timestamp = msg_date_written  # API format: "2026-02-04 00:25:45"
        else:
            msg_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        item = {
            "invoice": invoice,
            "product": product,
            "email": email,
            "message": last_message_text,
            "message_id": last_message_id,
            "timestamp": msg_timestamp,  # Use API timestamp, not current time!
            "requires_attention": True
        }
        
        # Check if auto-delivery product
        is_auto = any(auto in product for auto in AUTO_PRODUCTS)
        already_delivered = invoice in auto_delivered_orders
        
        if is_auto and not already_delivered:
            # First message - auto-deliver immediately
            log(f"⚡️ Auto-delivering to #{invoice} ({product[:50]}...)")
            if send_reply(token, invoice, DELIVERY_MSG):
                item["auto_delivered"] = True
                item["requires_attention"] = False
                queue["auto_delivered"].append(item)
                if "processed_messages" not in state:
                    state["processed_messages"] = []
                state["processed_messages"].append(f"{invoice}_{last_message_id}")
                if "auto_delivered_orders" not in state:
                    state["auto_delivered_orders"] = []
                state["auto_delivered_orders"].append(invoice)
                log(f"✅ Auto-delivered to #{invoice}")
            else:
                log(f"❌ Auto-delivery failed for #{invoice}")
                new_items.append(item)
        elif is_auto and already_delivered:
            # Already delivered once - now needs human attention
            log(f"🔔 #{invoice} has follow-up question (already auto-delivered)")
            new_items.append(item)
        elif state.get("away_mode", False):
            # Away mode - send auto-reply
            log(f"🌙 Away mode reply to #{invoice}")
            if send_reply(token, invoice, AWAY_MSG):
                item["away_reply_sent"] = True
                if "processed_messages" not in state:
                    state["processed_messages"] = []
                state["processed_messages"].append(f"{invoice}_{last_message_id}")
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
    
    if needs_attention_count == 0:
        log("No new messages from buyers")
    elif new_items:
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
        print("Reply with: reply to #<invoice_id> <your message>")
        print("Or run: python3 chat_cli.py")
        print("="*60 + "\n")

def set_away_mode(enabled):
    """Toggle away mode"""
    state = load_json(STATE_FILE, {"processed": [], "processed_messages": [], "auto_delivered_orders": [], "away_mode": False})
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
    state = load_json(STATE_FILE, {"processed": [], "processed_messages": [], "auto_delivered_orders": [], "away_mode": False})
    queue = load_json(QUEUE_FILE, {"pending": [], "auto_delivered": []})
    
    token = get_token()
    if not token:
        return False, "Authentication failed"
    
    if send_reply(token, invoice_id, message):
        # Mark the message as processed
        pending_chat = None
        for c in queue["pending"]:
            if c["invoice"] == invoice_id:
                pending_chat = c
                break
        
        if pending_chat and "message_id" in pending_chat:
            if "processed_messages" not in state:
                state["processed_messages"] = []
            state["processed_messages"].append(f"{invoice_id}_{pending_chat['message_id']}")
        
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
