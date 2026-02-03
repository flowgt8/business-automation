import requests
import hashlib
import time
import json
from datetime import datetime

# --- CONFIGURATION ---
SELLER_ID = 1179730
API_KEY = "9E0158D50BB2430D978F4707E3329153"

# How often to check for new messages (in seconds)
CHECK_INTERVAL = 60 

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_token():
    """Get a fresh session token."""
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()

    url = "https://api.digiseller.com/api/apilogin"
    payload = {
        "seller_id": SELLER_ID,
        "timestamp": int(timestamp),
        "sign": sign
    }

    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        data = r.json()
        if data.get("retval") == 0:
            return data.get("token")
        print(f"Auth Failed: {data.get('retdesc')}")
        return None
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def get_unread_chats(token):
    """Find chats with NEW messages."""
    url = f"https://api.digiseller.com/api/debates/v2/chats?token={token}&filter_new=1"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        # If 'items' exists, we have chats
        return data.get("items", [])
    except Exception as e:
        print(f"Check Error: {e}")
        return []

def get_chat_messages(token, invoice_id):
    """Read the latest message from a specific chat."""
    # Get only the newest messages
    url = f"https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice_id}&newer=1"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        # Returns a list of message objects
        return r.json() 
    except Exception as e:
        print(f"Read Error: {e}")
        return []

def send_reply(token, invoice_id, text):
    """Send a message to the buyer."""
    url = f"https://api.digiseller.com/api/debates/v2/?token={token}&id_i={invoice_id}"

    payload = {
        "message": text,
        "files": [] # You can add file uploading later if needed
    }

    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            print(f"✅ Reply sent to Order #{invoice_id}")
            return True
        else:
            print(f"❌ Failed to send: {r.text}")
            return False
    except Exception as e:
        print(f"Send Error: {e}")
        return False

def mark_as_read(token, invoice_id):
    """Tell Digiseller we saw the message (clears the notification)."""
    url = f"https://api.digiseller.com/api/debates/v2/seen?token={token}&id_i={invoice_id}"
    try:
        requests.post(url, headers=HEADERS, timeout=5)
    except:
        pass

def start_monitoring():
    print(f"--- 🤖 Clawbot Chat Manager Started ---")
    print(f"Checking for new messages every {CHECK_INTERVAL} seconds...")

    token = get_token()

    while True:
        # 1. Refresh token if it expired (simple check)
        if not token: 
            token = get_token()

        # 2. Check for unread chats
        chats = get_unread_chats(token)

        if chats:
            print(f"\n🔔 Found {len(chats)} active chat(s)!")

            for chat in chats:
                invoice_id = chat.get("id_i")
                email = chat.get("email")

                # 3. Get the actual message text
                messages = get_chat_messages(token, invoice_id)

                if messages:
                    # Print the latest message
                    last_msg = messages[0] # Usually the first one in the list is the newest
                    print(f"\n📩 NEW MESSAGE from {email} (Order #{invoice_id}):")
                    print(f"🗣️  \"{last_msg.get('message')}\"")

                    # 4. Interactive Reply Mode
                    reply = input(f"Type reply for #{invoice_id} (or press Enter to skip): ")

                    if reply.strip():
                        send_reply(token, invoice_id, reply)
                        mark_as_read(token, invoice_id)
                    else:
                        print("Skipped.")
        else:
            # Print a dot to show it's alive
            print(".", end="", flush=True)

        # Wait before next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
