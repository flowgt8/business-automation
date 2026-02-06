#!/usr/bin/env python3
"""
Send inbox link to Perplexity customers needing help
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import hashlib

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"

INBOX_LINK = "https://s10.asurahosting.com/roundcube/?_task=mail&_mbox=INBOX"

def get_token():
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()
    
    url = "https://api.digiseller.com/api/apilogin"
    payload = json.dumps({
        "seller_id": int(SELLER_ID),
        "timestamp": int(timestamp),
        "sign": sign
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode('utf-8'))
            return data.get("token") if data.get("retval") == 0 else None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def send_reply(token, invoice_id, message):
    """Send reply to customer"""
    url = f"https://api.digiseller.com/api/debates/v2/?token={token}&id_i={invoice_id}"
    payload = {"message": message}
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), 
                                     headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read().decode('utf-8'))
            return result.get("retval", -1) == 0
    except Exception as e:
        print(f"Error sending to #{invoice_id}: {e}")
        return False

def main():
    # Unread Perplexity customers
    customers = [
        ("284340901", "niggo161161@gmail.com"),
        ("284339895", "vfgbdvvh@gmail.com"),
        ("284339393", "mbmportal2@mail.ru"),
        ("284339064", "cscscsfret1@gmail.com"),
        ("284337757", "heliport2016@gmail.com"),
    ]
    
    message = f"""Здравствуйте!

Для получения кода войдите в почту по ссылке:
👉 {INBOX_LINK}

Войдите в аккаунт, чтобы получить письмо с кодом для входа в Perplexity AI.

Если письмо не пришло, проверьте папку Спам.

Если нужна помощь — напишите здесь."""
    
    print("Getting token...")
    token = get_token()
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"\nSending messages to {len(customers)} customers...\n")
    
    sent = 0
    failed = 0
    
    for invoice_id, email in customers:
        print(f"📤 Sending to #{invoice_id} ({email})...")
        if send_reply(token, invoice_id, message):
            print(f"   ✅ Sent!")
            sent += 1
        else:
            print(f"   ❌ Failed!")
            failed += 1
        time.sleep(1)  # Small delay
    
    print(f"\n{'='*50}")
    print(f"✅ Sent: {sent}")
    print(f"❌ Failed: {failed}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
