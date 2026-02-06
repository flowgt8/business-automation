#!/usr/bin/env python3
"""
Daily News Sender - Sends niche news digest via Telegram
Called by cron job every morning
"""

import requests
from datetime import datetime

BOT_TOKEN = "8307526718:AAHxLCKEWXVRYMpcS-i7no_92iJjf_80_ZQ"
CHAT_ID = "889015099"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json().get("ok", False)
    except:
        return False

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    
    message = f"""📰 <b>Daily Niche News - {today}</b>

🔥 <b>AI Tools Updates:</b>
• Gemini: https://gemini.google.com
• Perplexity: https://www.perplexity.ai/hub
• ChatGPT: https://openai.com/blog
• Adobe: https://news.adobe.com

💼 <b>Your Business:</b>
• Check Plati sales: https://plati.market/seller/1179730/
• Review pending customer chats
• Monitor stock levels

📊 <b>Competitor Watch:</b>
• Check competitor pricing on Plati
• New AI tools trending

🎯 <b>Today's Tasks:</b>
• Reply to pending messages
• Restock if inventory low
• Handle refunds/disputes

⏰ <b>Automated Checks:</b>
• Chat monitoring: Every 5 min
• Inventory check: Every 6 hours
• Daily report: 7:00 AM

---
<i>Reply with "check chats" for latest updates</i>"""
    
    success = send_message(message)
    print(f"Daily news {'sent!' if success else 'failed!'}")

if __name__ == "__main__":
    main()
