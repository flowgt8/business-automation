# MEMORY.md - Long-term Memory for Brix

## User Information
- **Name:** Badro
- **What to call them:** Badro
- **Timezone:** GMT+1 (Europe/Berlin)
- **Communication style:** Middle ground between formal and casual

## Business Information
- **Plati Seller ID:** 1179730
- **GitHub:** flowgt8/business-automation
- **Digiseller API Key:** 9E0158D50BB2430D978F4707E3329153
- **Telegram Bot Token:** 8033906783:AAEmy_bP6TnMnMnEhyDrRdbIxEXyUWCRuJs
- **Telegram Chat ID:** 8239297708

## Businesses
1. **Digital Goods (Plati/GGSel)** - $1-2k/month
   - Gemini AI Pro accounts (12-month student)
   - Perplexity AI Pro (1-month private accounts)
   - Canva Pro
   - Adobe Creative Cloud
   - ChatGPT Plus
   - Cursor AI Pro

2. **AI Influencer (OFM)** - New, no revenue yet

## Automation Systems Active

### Chat Monitoring
- **Frequency:** Every 5 minutes (chat_monitor.py)
- **Hourly Alert:** Sends Telegram notification if new messages
- **Auto-delivery:** Perplexity AI Pro products get instant inbox link
- **Queue file:** chat_queue.json
- **State file:** chat_state.json

### Stock Management
- **File:** stock_manager.py
- **Product IDs:**
  - perplexity: 5659428
  - gemini: 5401507
  - canva: 5655941
  - chatgpt: 5658505
  - cursor: 5402197
  - adobe: 5655904

### Daily News
- **Time:** 8:00 AM daily (Europe/Berlin)
- **File:** daily_news_sender.py
- **Content:** AI tool updates, business reminders, competitor watch

## Customer Support Preferences
- **Adobe customers:** Respond in Russian
- **Perplexity customers:** Send inbox link first, then help with issues
- **Inbox link:** https://s10.asurahosting.com/roundcube/?_task=mail&_mbox=INBOX
- **Common issue:** Roundcube inbox access (customers need VPN sometimes)

## Recent Issues (Feb 5, 2026)
- Roundcube inbox was down, now restored
- Multiple Perplexity customers couldn't access inbox
- Adobe customer (media.miker@gmail.com, Order #283191273) has 2-day work delay - needs priority
- 4 Perplexity customers notified inbox is working again

## Automation Scripts Location
- `/root/.openclaw/workspace/business/digital-goods/`
- All committed to GitHub: flowgt8/business-automation

## API Notes
- **Digiseller API:** Very slow (90-120 second timeouts)
- **Authentication:** SHA256 signature (api_key + timestamp)
- **Endpoint:** api.digiseller.com (not .ru)

## Session Started
- **Established:** 2026-02-03
- **Major setup completed:** 2026-02-04/05
