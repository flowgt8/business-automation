#!/usr/bin/env python3
"""
Standalone Telegram Message Sender
Used for scheduled messages - bypasses broken cron/heartbeat system
"""
import urllib.request
import urllib.parse
import json
import datetime
import os
import sys

# --- CONFIGURATION ---
BOT_TOKEN = "8307526718:AAHxLCKEWXVRYMpcS-i7no_92iJjf_80_ZQ"
CHAT_ID = "889015099"  # Badro's chat ID
MESSAGE = "Hey! Just checking in. How's it going?"

LOG_FILE = "/home/node/.openclaw/workspace/cron_log.txt"

def send_message(text=None):
    """Send a message via Telegram Bot API"""
    msg = text or MESSAGE
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                log_msg = f"[{timestamp}] SUCCESS: Sent '{msg[:30]}...'"
            else:
                log_msg = f"[{timestamp}] FAILED: {result.get('description', 'Unknown error')}"
    
    except Exception as e:
        log_msg = f"[{timestamp}] ERROR: {str(e)}"
    
    # Write to log
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")
    
    print(log_msg)
    return log_msg

if __name__ == "__main__":
    # Allow passing message as argument
    custom_msg = sys.argv[1] if len(sys.argv) > 1 else None
    send_message(custom_msg)
