#!/usr/bin/env python3
"""
Check for new unread messages AND new Perplexity orders every 10 minutes
AUTO-SEND IS DISABLED - only notifies via Telegram
Only send inbox link if not already in conversation (when approved)
"""
import urllib.request
import json
import time
import hashlib
import os
import sys
import fcntl

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"
TELEGRAM_TOKEN = "8307526718:AAHxLCKEWXVRYMpcS-i7no_92iJjf_80_ZQ"
TELEGRAM_CHAT_ID = "889015099"
INBOX_LINK = "https://s10.asurahosting.com/roundcube/?_task=mail&_mbox=INBOX"
LOG_FILE = "/home/node/.openclaw/workspace/message_checker.log"
STATE_FILE = "/home/node/.openclaw/workspace/message_checker_state.json"
LOCK_FILE = "/tmp/message_checker.lock"

# AUTO-SEND DISABLED - user must approve each message
AUTO_SEND_ENABLED = False

def acquire_lock():
    """Acquire exclusive lock, return lock_fp if success, None if already locked"""
    try:
        lock_fp = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fp.write(str(os.getpid()))
        lock_fp.flush()
        return lock_fp
    except (IOError, OSError):
        return None

def release_lock(lock_fp):
    if lock_fp:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)
        lock_fp.close()
        try:
            os.unlink(LOCK_FILE)
        except:
            pass

def get_token():
    ts = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + ts).encode()).hexdigest()
    url = "https://api.digiseller.com/api/apilogin"
    payload = json.dumps({"seller_id": int(SELLER_ID), "timestamp": int(ts), "sign": sign}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
            return data.get("token") if data.get("retval") == 0 else None
    except:
        return None

def get_all_chats(token):
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            chats = json.loads(r.read().decode()).get("chats", [])
            chats.sort(key=lambda x: x.get('date_last', ''), reverse=True)
            return chats
    except:
        return []

def get_chat_messages(token, invoice_id):
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except:
        return []

def link_already_sent(messages):
    import html
    for msg in messages:
        if msg.get("buyer") in [None, 0]:
            text = html.unescape(msg.get("message", ""))
            if "s10.asurahosting.com" in text.lower() or "roundcube" in text.lower():
                return True
    return False

def send_reply(token, invoice_id, message):
    url = f"https://api.digiseller.com/api/debates/v2/?token={token}&id_i={invoice_id}"
    payload = json.dumps({"message": message}).encode()
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode()).get("retval", -1) == 0
    except:
        return False

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode()
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return True
    except:
        return False

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"notified_orders": [], "last_unread_count": 0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def main():
    # Check for existing instance
    lock = acquire_lock()
    if not lock:
        log("Already running, exiting")
        sys.exit(1)
    
    try:
        log("🔔 Message & Order checker started (Telegram notifications only - auto-send DISABLED)")
        state = load_state()
        notified_orders = set(state.get("notified_orders", []))
        
        while True:
            token = get_token()
            if not token:
                log("Failed to get token")
                time.sleep(600)
                continue
            
            chats = get_all_chats(token)
            if not chats:
                time.sleep(600)
                continue
            
            # Find new Perplexity orders needing inbox link
            new_orders = []
            
            for chat in chats[:20]:
                invoice = str(chat.get("id_i"))
                product = chat.get("product", "")
                
                if "Perplexity" in product and invoice not in notified_orders:
                    messages = get_chat_messages(token, invoice)
                    if isinstance(messages, list):
                        if link_already_sent(messages):
                            notified_orders.add(invoice)
                        else:
                            buyer_msgs = [m for m in messages if m.get("buyer") == 1]
                            if buyer_msgs:
                                new_orders.append({
                                    "invoice": invoice,
                                    "email": chat.get("email", ""),
                                    "product": product[:40],
                                    "message": buyer_msgs[-1].get("message", "")[:100]
                                })
                            else:
                                notified_orders.add(invoice)
            
            # Notify on Telegram (but DON'T auto-send)
            if new_orders:
                msg = f"📦 <b>{len(new_orders)} Perplexity customers need inbox link:</b>\n\n"
                for o in new_orders:
                    msg += f"#{o['invoice']} | {o['email']}\n"
                    msg += f"   💬 {o['message']}\n\n"
                msg += "Reply 'yes' to send inbox links to all."
                send_telegram(msg)
                log(f"Found {len(new_orders)} orders needing inbox link - notified via Telegram")
            
            # Check unread messages
            unread_count = 0
            for chat in chats:
                invoice = str(chat.get("id_i"))
                messages = get_chat_messages(token, invoice)
                if isinstance(messages, list):
                    unread = [m for m in messages if m.get("buyer") == 1 and m.get("date_seen") is None]
                    if unread:
                        unread_count += 1
            
            if unread_count > 0 and unread_count != state.get("last_unread_count", 0):
                send_telegram(f"🔔 {unread_count} unread messages! Check Digiseller.")
            
            save_state({"notified_orders": list(notified_orders), "last_unread_count": unread_count})
            log(f"Checked {len(chats[:20])} chats. New: {len(new_orders)}. Unread: {unread_count}")
            
            time.sleep(600)
    finally:
        release_lock(lock)

if __name__ == "__main__":
    main()
