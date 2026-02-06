#!/usr/bin/env python3
"""
Check for unread messages every 15 minutes
SEND TELEGRAM NOTIFICATIONS ONLY - no customer messages
Checks last 40 conversations only (optimized for speed)
"""
import urllib.request
import json
import time
import hashlib
import os
import fcntl

SELLER_ID = "1179730"
API_KEY = "9E0158D50BB2430D978F4707E3329153"
TELEGRAM_TOKEN = "7715255315:AAEECXyv17D43-9WIv3Xt2Z1FolUS3U9_Mo"
TELEGRAM_CHAT_ID = "8239297708"
STATE_FILE = "/home/node/.openclaw/workspace/unread_check_state.json"
LOCK_FILE = "/tmp/check_unread.lock"
MAX_CHATS = 40  # Check last 40 conversations only

# Russian to English translation dictionary (longer phrases first)
TRANSLATIONS = [
    # Long messages
    ("Приветствую<br><br>Не могу войти в почту", "Greetings, I can't access the email"),
    ("Сервис очень долго загружается", "Service loads very slowly"),
    ("не могу войти в почту", "can't access the email"),
    ("как на почту зайти", "how to access email"),
    ("как зайти на почту", "how to access email"),
    ("На почту не пришло письмо", "Didn't receive email"),
    ("не пришло письмо с логином", "didn't receive login email"),
    ("не пришло письмо с паролем", "didn't receive password email"),
    ("Как войти если запрашивает код", "How to login if it asks for code"),
    ("Что это за ссылка", "What is this link"),
    ("ждать акк", "waiting for account"),
    ("жду аккаунт", "waiting for account"),
    ("жду акк", "waiting for account"),
    ("Уникальный код", "Unique code"),
    
    # Short phrases
    ("Здравствуйте", "Hello"),
    ("Добрый день", "Good afternoon"),
    ("Доброе утро", "Good morning"),
    ("Добрый вечер", "Good evening"),
    ("привет", "hey"),
    ("Привет", "Hey"),
    ("приветствую", "Greetings"),
    ("спасибо", "thanks"),
    ("пожалуйста", "please"),
    
    # Email related
    ("на почту", "to email"),
    ("через какую почту", "which email"),
    ("электронную почту", "email"),
    ("входящие", "inbox"),
    ("спам", "spam"),
    
    # Login/Password
    ("логин и пароль", "login and password"),
    ("войти в почту", "login to email"),
    ("войти в аккаунт", "login to account"),
    
    # Status
    ("не пришло", "didn't arrive"),
    ("не пришла", "didn't arrive"),
    ("не получено", "not received"),
    ("не работает", "not working"),
    ("ошибка", "error"),
    
    # Help
    ("помогите", "help"),
    ("помогите пожалуйста", "please help"),
    
    # Connect
    ("не дает", "won't let"),
    ("не даёт", "won't let"),
    ("подключить", "connect"),
    ("доступ к подписке", "subscription access"),
    
    # Other
    ("попробуйте", "try"),
    ("попробуйте еще раз", "try again"),
]

def translate_to_english(text):
    """Translate Russian text to English"""
    if not text:
        return ""
    
    # Check if already English
    cyrillic = sum(1 for c in text if 'а' <= c.lower() <= 'я')
    latin = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    if latin > cyrillic:
        return text[:80]
    
    # Apply translations (longer phrases first)
    result = text
    for ru, en in TRANSLATIONS:
        result = result.replace(ru, en)
    
    return ' '.join(result.split())[:80]

def acquire_lock():
    try:
        lock_fp = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fp.write(str(os.getpid()))
        lock_fp.flush()
        return lock_fp
    except:
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

def get_recent_chats(token):
    """Get last MAX_CHATS conversations"""
    all_chats = []
    page = 1
    
    while len(all_chats) < MAX_CHATS and page <= 100:
        url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}&page={page}&rows=50"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
                chats = data.get("chats", [])
                if not chats:
                    break
                all_chats.extend(chats)
                page += 1
        except:
            break
    
    return all_chats[:MAX_CHATS]

def get_messages(token, invoice):
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except:
        return []

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return True
    except:
        return False

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_count": 0, "last_invoices": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def main():
    lock = acquire_lock()
    if not lock:
        print("Already running, exiting")
        return
    
    try:
        token = get_token()
        if not token:
            return
        
        chats = get_recent_chats(token)
        print(f"Checked {len(chats)} recent chats")
        
        unread_chats = []
        for c in chats:
            cnt_new = c.get("cnt_new", 0)
            if cnt_new > 0:
                invoice = str(c.get("id_i"))
                email = c.get("email", "")
                product = c.get("product", "")[:40]
                
                messages = get_messages(token, invoice)
                buyer_msgs = [m for m in messages if m.get("buyer") == 1]
                last_msg = buyer_msgs[-1].get("message", "") if buyer_msgs else "(no message)"
                # Translate to English
                last_msg_en = translate_to_english(last_msg.replace("<br>", " "))
                
                unread_chats.append({
                    "invoice": invoice,
                    "email": email,
                    "product": product,
                    "cnt_new": cnt_new,
                    "last_message": last_msg_en
                })
        
        if unread_chats:
            total_unread = sum(c["cnt_new"] for c in unread_chats)
            message = f"🔔 <b>{len(unread_chats)} chats with {total_unread} unread!</b>\n\n"
            for chat in unread_chats:
                message += f"📦 <b>#{chat['invoice']}</b>\n"
                message += f"👤 {chat['email']}\n"
                message += f"📋 {chat['product']}...\n"
                message += f"💬 {chat['last_message']}\n\n"
            send_telegram(message)
            print(f"Sent: {len(unread_chats)} chats ({total_unread} msgs)")
        
        save_state({"last_count": len(unread_chats)})
        print(f"[{time.strftime('%H:%M:%S')}] {len(unread_chats)} unread")
    finally:
        release_lock(lock)

if __name__ == "__main__":
    main()
