#!/usr/bin/env python3
"""
Background Message Poller
Runs continuously and sends scheduled messages
Bypasses broken OpenClaw cron/heartbeat system
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import time
import datetime
import os
import sys

# Configuration
BOT_TOKEN = "8307526718:AAHxLCKEWXVRYMpcS-i7no_92iJjf_80_ZQ"
CHAT_ID = "889015099"
LOG_FILE = "/home/node/.openclaw/workspace/cron_log.txt"
STATE_FILE = "/home/node/.openclaw/workspace/message_state.json"

# Scheduled messages (hour 24h format, minute)
SCHEDULE = [
    (20, 2, "Hey! Just checking in. How's it going?"),
    (20, 14, "Just a quick check-in! Everything good?"),
    (20, 16, "Hello! How's your day going?"),
    (20, 21, "Quick check! How's everything?"),
    (20, 24, "Hello! How's your evening going?"),
    (20, 52, "👋 Hello! Just a quick hello at 9:52 PM!"),
]

def load_state():
    """Load sent messages state"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    """Save sent messages state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def send_telegram_message(text):
    """Send message via Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                msg = f"[{timestamp}] ✅ SENT: {text[:40]}..."
            else:
                msg = f"[{timestamp}] ❌ FAILED: {result.get('description', 'Unknown')}"
    
    except Exception as e:
        msg = f"[{timestamp}] 💥 ERROR: {str(e)}"
    
    # Write to log
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    
    print(msg)
    return msg

def main():
    print(f"[{datetime.datetime.now()}] Message poller started")
    
    while True:
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        current_minute = now.minute
        
        state = load_state()
        
        for hour, minute, message in SCHEDULE:
            # Create unique key for this message slot
            slot_key = f"{today}_{hour:02d}_{minute:02d}"
            
            # Check if we should send this message (within the last minute)
            if current_hour == hour and current_minute == minute:
                if slot_key not in state.get('sent_today', []):
                    send_telegram_message(message)
                    
                    # Mark as sent
                    if 'sent_today' not in state:
                        state['sent_today'] = []
                    state['sent_today'].append(slot_key)
                    save_state(state)
        
        # Reset daily state at midnight
        if 'last_date' in state and state['last_date'] != today:
            state = {'sent_today': [], 'last_date': today}
            save_state(state)
        elif 'last_date' not in state:
            state['last_date'] = today
            save_state(state)
        
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()
