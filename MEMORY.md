# MEMORY.md - Long-term Memory for Brix

## User Information
- **Name:** Badro
- **What to call them:** Badro
- **Timezone:** GMT+1 (Europe/Berlin)
- **Communication style:** Middle ground between formal and casual
- **Telegram accounts:**
  - **Main:** 8239297708 (@kryper0) - PRIMARY from Feb 6, 2026
  - Old: 889015099 (@beex99) - no longer used

## Telegram Bot
- **Bot Token:** 7715255315:AAEECXyv17D43-9WIv3Xt2Z1FolUS3U9_Mo
- **Bot Name:** @kroxiibot
- **Bot Username:** kroxiibot
- **Status:** New bot activated, waiting for gateway restart to fully pair

## Customer Support Preferences
- **Adobe customers:** Respond in Russian
- **Perplexity customers:** Send inbox link first, then help with issues
- **All customer messages:** Translate to English in notifications
- **Inbox link:** https://s10.asurahosting.com/roundcube/?_task=mail&_mbox=INBOX
- **Common issue:** Roundcube inbox access (customers need VPN sometimes)

## Digiseller API (1179730)
- **API Key:** 9E0158D50BB2430D978F4707E3329153
- **Auto-send:** DISABLED - user must approve each message
- **Sales API:** /api/seller-sells/v2 (POST method)
- **Chat API:** /api/debates/v2/chats?token={token}

## Automation Scripts
- **check_unread.py:** Runs every 15 min, notifies of unread messages (checks last 40 chats)
- **message_checker.py:** NOTIFICATIONS ONLY - auto-send disabled
- **track_sales.py:** Tracks daily/weekly sales

## Critical Rules
1. Never auto-send customer messages without approval
2. Always translate Russian messages to English
3. Use GMT+1 timezone only
4. Check all pages of chats for unread messages (max 40)
5. Prevent duplicate messages with singleton lock

## Pending Actions
- Gateway restart needed to fully switch to @kryper0
- Re-pair Telegram bot with new admin ID

