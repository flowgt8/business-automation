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
    """Check for pending messages and send Telegram alert if any"""
    
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
    
    if pending:
        # Build alert message
        message = "🚨 <b>New Digiseller Messages!</b>\n\n"
        
        for i, item in enumerate(pending[:5], 1):  # Show max 5
            invoice = item.get("invoice", "N/A")
            product = item.get("product", "N/A")[:40]
            email = item.get("email", "N/A")
            msg_text = item.get("message", "")[:50]
            
            message += f"<b>#{i}. Order #{invoice}</b>\n"
            message += f"📦 {product}...\n"
            message += f"📧 {email}\n"
            message += f"💬 \"{msg_text}...\"\n\n"
        
        if len(pending) > 5:
            message += f"<i>...and {len(pending) - 5} more</i>\n\n"
        
        message += "Reply here or check: python3 chat_cli.py status"
        
        # Send Telegram alert
        success = send_telegram_message(message)
        if success:
            print(f"✅ Alert sent: {len(pending)} pending message(s)")
        else:
            print("❌ Failed to send Telegram alert")
    else:
        print("✅ No new messages")

if __name__ == "__main__":
    check_and_alert()
