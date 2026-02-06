#!/usr/bin/env python3
"""
Chat Alert System - Checks for new Digiseller messages and sends Telegram alerts
Runs via cron every hour
"""

import json
import os
import requests
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
    """Check for TRULY unread messages via API and send Telegram alert"""
    import hashlib
    import time
    
    API_KEY = "9E0158D50BB2430D978F4707E3329153"
    SELLER_ID = 1179730
    
    try:
        # Get token
        timestamp = str(int(time.time()))
        sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()
        r = requests.post('https://api.digiseller.com/api/apilogin', 
            json={'seller_id': SELLER_ID, 'timestamp': int(timestamp), 'sign': sign},
            timeout=30)
        token = r.json().get('token')
        
        if not token:
            print("❌ Failed to authenticate")
            return
        
        # Get all chats
        url = f'https://api.digiseller.com/api/debates/v2/chats?token={token}'
        r = requests.get(url, timeout=60)
        chats = r.json().get('chats', [])
        
        found_unread = []
        
        for chat in chats:
            invoice = chat.get('id_i')
            email = chat.get('email', 'N/A')
            product = chat.get('product', 'N/A')[:40]
            
            # Get messages for this chat
            url = f'https://api.digiseller.com/api/debates/v2?token={token}&id_i={invoice}'
            r = requests.get(url, timeout=60)
            messages = r.json() if isinstance(r.json(), list) else []
            
            # Find TRULY unread messages (date_seen is None)
            for msg in messages:
                if msg.get('buyer') == 1 and msg.get('date_seen') is None:
                    found_unread.append({
                        'invoice': invoice,
                        'email': email,
                        'product': product,
                        'message': msg.get('message', ''),
                        'time': msg.get('date_written', 'N/A')
                    })
        
        if found_unread:
            # Build alert message
            message = f"🚨 <b>{len(found_unread)} New Digiseller Message(s)!</b>\n\n"
            
            for i, item in enumerate(found_unread[:5], 1):
                msg_time = item['time'][11:16] if item['time'] != 'N/A' else 'N/A'
                message += f"<b>#{i}. Order #{item['invoice']}</b> <i>{msg_time}</i>\n"
                message += f"📦 {item['product'][:30]}...\n"
                message += f"📧 {item['email']}\n"
                message += f"💬 \"{item['message'][:50]}\"\n\n"
            
            if len(found_unread) > 5:
                message += f"<i>...and {len(found_unread) - 5} more</i>\n\n"
            
            # Send Telegram alert
            success = send_telegram_message(message)
            if success:
                print(f"✅ Alert sent: {len(found_unread)} unread message(s)")
            else:
                print("❌ Failed to send Telegram alert")
        else:
            print("✅ No unread messages")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_and_alert()
