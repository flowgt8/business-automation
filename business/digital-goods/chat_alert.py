#!/usr/bin/env python3
"""
Chat Alert System - Checks for new Digiseller messages and sends Telegram alerts
Runs via cron every hour
"""

import json
import os
import subprocess
import sys

# Add parent directory to path to import telegram_sender
sys.path.insert(0, '/root/.openclaw/workspace/business/digital-goods')
from telegram_sender import send_telegram_message

QUEUE_FILE = "/root/.openclaw/workspace/business/digital-goods/chat_queue.json"
STATE_FILE = "/root/.openclaw/workspace/business/digital-goods/chat_state.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def check_and_alert():
    """Check for pending messages and send Telegram alert if any NEW ones"""
    from datetime import datetime, timedelta
    
    # First run chat_monitor to check for new messages
    try:
        result = subprocess.run(
            ["python3", "/root/.openclaw/workspace/business/digital-goods/chat_monitor.py", "--check"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
    except Exception as e:
        print(f"Chat monitor error: {e}")
        return
    
    # Check queue for pending messages
    queue = load_json(QUEUE_FILE, {"pending": [], "auto_delivered": []})
    pending = queue.get("pending", [])
    
    # Filter to only messages from last 2 hours (truly new)
    now = datetime.now()
    recent_messages = []
    
    for item in pending:
        try:
            msg_time = datetime.strptime(item.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
            # Only include messages from last 2 hours
            if now - msg_time <= timedelta(hours=2):
                # Deduplicate by invoice+message combo
                key = f"{item.get('invoice')}_{item.get('message', '')[:20]}"
                if not any(key == f"{m.get('invoice')}_{m.get('message', '')[:20]}" for m in recent_messages):
                    recent_messages.append(item)
        except:
            continue  # Skip if timestamp is invalid
    
    if recent_messages:
        # Build alert message
        message = f"🚨 <b>{len(recent_messages)} New Digiseller Message(s)!</b>\n"
        message += f"<i>(Last 2 hours)</i>\n\n"
        
        for i, item in enumerate(recent_messages[:5], 1):  # Show max 5
            invoice = item.get("invoice", "N/A")
            product = item.get("product", "N/A")[:35]
            email = item.get("email", "N/A")
            msg_text = item.get("message", "")[:40]
            time_str = item.get("timestamp", "")[11:16]  # HH:MM only
            
            message += f"<b>#{i}. Order #{invoice}</b> <i>{time_str}</i>\n"
            message += f"📦 {product}...\n"
            message += f"📧 {email}\n"
            message += f"💬 \"{msg_text}...\"\n\n"
        
        if len(recent_messages) > 5:
            message += f"<i>...and {len(recent_messages) - 5} more</i>\n\n"
        
        message += "Reply with: reply to #<invoice> <message>"
        
        # Send Telegram alert
        success = send_telegram_message(message)
        if success:
            print(f"✅ Alert sent: {len(recent_messages)} new message(s)")
        else:
            print("❌ Failed to send Telegram alert")
    else:
        print("✅ No new messages in last 2 hours")

if __name__ == "__main__":
    check_and_alert()
