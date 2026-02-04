#!/usr/bin/env python3
"""
Direct Telegram Sender for Cron Jobs
Uses OpenClaw's gateway to send messages directly
"""

import requests
import json

# Telegram Bot Token
BOT_TOKEN = "8033906783:AAEmy_bP6TnMnMnEhyDrRdbIxEXyUWCRuJs"
CHAT_ID = "8239297708"

def send_telegram_message(text):
    """Send message directly via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        result = response.json()
        
        # Log result
        with open("/tmp/telegram_sender.log", "a") as f:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if result.get("ok"):
                f.write(f"[{timestamp}] SUCCESS: Message sent to {CHAT_ID}\n")
            else:
                f.write(f"[{timestamp}] FAILED: {result}\n")
        
        return result.get("ok", False)
    except Exception as e:
        with open("/tmp/telegram_sender.log", "a") as f:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] ERROR: {e}\n")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        message = "👋 Hello! This is your scheduled message."
    
    success = send_telegram_message(message)
    print("Sent!" if success else "Failed!")
