#!/usr/bin/env python3
"""
Daily Niche News - AI Tools & Digital Goods Updates
Fetches news about Gemini, Perplexity, ChatGPT, Adobe, etc.
"""

import json
import os
from datetime import datetime

NEWS_FILE = "/root/.openclaw/workspace/business/digital-goods/daily_news.json"

def load_news():
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, "r") as f:
            return json.load(f)
    return {"last_date": None, "items": []}

def save_news(data):
    with open(NEWS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_daily_digest():
    """Generate daily news digest for AI/digital goods niche"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    digest = f"""📰 **Daily Niche News - {today}**

**🔥 AI Tools Updates:**
• Check latest Gemini updates: https://gemini.google.com
• Perplexity news: https://www.perplexity.ai/hub
• ChatGPT updates: https://openai.com/blog
• Adobe news: https://news.adobe.com

**💼 Your Business:**
• Check Plati sales: https://plati.market/seller/1179730/
• Review pending chats for customer issues
• Monitor stock levels for all products

**📊 Competitor Watch:**
• Check competitor pricing on Plati
• New AI tools trending in your market

**🎯 Today's Tasks:**
• Reply to pending customer messages
• Restock if inventory low
• Check for refund/dispute requests

---
*To get live updates, visit the links above or ask me to check specific items.*
"""
    return digest

if __name__ == "__main__":
    print(get_daily_digest())
