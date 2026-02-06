#!/usr/bin/env python3
"""
FIXED Message & Order Checker
- ALWAYS check ALL messages for link before sending
- Never trust state file alone - verify in messages
- Single process only
"""
import urllib.request
import json
import time
import hashlib
import html
import os

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"
INBOX_LINK = "https://s10.asurahosting.com/roundcube/?_task=mail&_mbox=INBOX"

def get_token():
    """Get fresh API token"""
    ts = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + ts).encode()).hexdigest()
    url = "https://api.digiseller.com/api/apilogin"
    payload = json.dumps({"seller_id": int(SELLER_ID), "timestamp": int(ts), "sign": sign}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data.get("token") if data.get("retval") == 0 else None
    except:
        return None

def get_chats(token):
    """Get all chats"""
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8")).get("chats", [])
    except:
        return []

def get_messages(token, invoice):
    """Get ALL messages for an order"""
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except:
        return []

def link_in_messages(messages):
    """
    CRITICAL: Check ALL messages for inbox link
    - Seller messages have buyer=None or buyer=0
    - URLs may have HTML entities (&amp;)
    """
    if not isinstance(messages, list):
        return False
    
    for msg in messages:
        # Check ALL seller messages
        if msg.get("buyer") in [None, 0]:
            text = msg.get("message", "")
            # Decode HTML entities
            decoded = html.unescape(text)
            # Check for link variations
            if "s10.asurahosting.com" in decoded.lower() or "roundcube" in decoded.lower():
                return True
    return False

def check_order_needs_link(token, invoice):
    """
    DEFINITIVE check: Does this order need the inbox link?
    Returns: (needs_link, reason)
    """
    messages = get_messages(token, invoice)
    
    if not messages or not isinstance(messages, list):
        return False, "No messages"
    
    # CRITICAL: Check ALL messages for link first
    if link_in_messages(messages):
        return False, "Link already exists in messages"
    
    # Check if buyer sent any message
    buyer_msgs = [m for m in messages if m.get("buyer") == 1]
    if buyer_msgs:
        return True, f"Buyer message: {buyer_msgs[-1].get('message', '')[:50]}..."
    
    return False, "No buyer messages"

def send_message(token, invoice, message):
    """Send message to customer"""
    url = f"https://api.digiseller.com/api/debates/v2/?token={token}&id_i={invoice}"
    payload = json.dumps({"message": message}).encode()
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return True
    except:
        return False

def main():
    print("=" * 60)
    print("FIXED Message Checker - Single Process")
    print("=" * 60)
    
    while True:
        token = get_token()
        if not token:
            print("Failed to get token, retrying...")
            time.sleep(60)
            continue
        
        chats = get_chats(token)
        print(f"\n[{time.strftime('%H:%M:%S')}] Checking {len(chats)} chats...")
        
        needs_help = []
        
        for chat in chats[:30]:  # Check last 30
            invoice = str(chat.get("id_i"))
            product = chat.get("product", "")
            email = chat.get("email", "")
            
            # Only check Perplexity
            if "Perplexity" not in product:
                continue
            
            # CRITICAL: Always verify by checking ALL messages
            needs, reason = check_order_needs_link(token, invoice)
            
            if needs:
                needs_help.append((invoice, email, reason))
                print(f"  🔔 #{invoice} | {email} - NEEDS LINK")
                print(f"     Reason: {reason}")
        
        print(f"\n📊 Summary: {len(needs_help)} orders need help")
        
        if needs_help:
            print("\n⚠️  Ready to send to:")
            for inv, email, _ in needs_help:
                print(f"   #{inv} | {email}")
            print("\n❌ BLOCKED: Waiting for user approval before sending")
            print("=" * 60)
        
        print(f"\nSleeping 10 minutes...")
        time.sleep(600)

if __name__ == "__main__":
    main()
