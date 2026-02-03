# 🤖 Business Automation Suite

Automated monitoring and analytics for digital goods business + AI influencer growth.

## 📁 Structure

```
business/
├── digital-goods/          # Plati.market / GGSel automation
│   ├── plati_monitor.py    # Inventory & competitor monitoring
│   ├── sales_analytics.py  # Revenue tracking & reporting
│   ├── daily_automation.py # Main automation runner
│   └── README.md
│
└── ai-influencer/          # OFM AI girl automation (coming soon)
```

## 🚀 Quick Start

1. **Install dependencies:**
```bash
cd business/digital-goods
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export DIGISELLER_API_KEY="your-api-key"
export PLATI_SELLER_ID="your-seller-id"
```

3. **Run automation:**
```bash
python daily_automation.py
```

## 📊 Features

### Digital Goods (Active)
- ✅ Inventory monitoring with low-stock alerts
- ✅ Sales analytics & revenue tracking
- ⚠️ Competitor price tracking (needs implementation)
- 🔄 Auto-restock alerts

### AI Influencer (Planned)
- 📅 Content calendar automation
- 📱 Social media scheduling
- 💬 Engagement automation
- 📈 Growth analytics

## 🔄 Automation Schedule

### Every 6 Hours:
- Check inventory levels
- Alert on low stock

### Daily (Morning):
- Sales report generation
- Competitor price check
- Daily summary notification

### Weekly:
- Revenue trend analysis
- Best-seller identification
- Pricing optimization suggestions

## 🔧 Configuration

Edit `plati_monitor.py` to set:
- `LOW_STOCK_THRESHOLD` (default: 10)
- `CRITICAL_STOCK_THRESHOLD` (default: 3)
- Your seller ID

## 📝 TODO

- [ ] Implement actual Digiseller API integration
- [ ] Add competitor price scraping
- [ ] Create Telegram notifications
- [ ] Build AI influencer content pipeline
- [ ] Add automated price adjustment logic
- [ ] Create dashboard/visualization

## 🤝 Contributing

All changes go through PR review before deployment.

---
*Built by your AI employee while you sleep* 🌙
