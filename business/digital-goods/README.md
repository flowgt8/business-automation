# Business Automation - Digital Goods (Plati/GGSel)

## API Access
- Digiseller API Key: Stored in config
- Base URL: https://api.digiseller.ru

## Automation Priorities

### 1. Inventory Monitoring
- Check stock levels every 6 hours
- Alert when accounts running low (< 10 units)
- Auto-detect if accounts getting flagged/banned

### 2. Price Optimization
- Scrape competitor prices on Plati
- Suggest optimal pricing based on market
- Auto-adjust prices (with approval)

### 3. Sales Analytics
- Daily revenue tracking
- Best-selling products identification
- Customer review monitoring

### 4. Multi-Platform Expansion
- Research other marketplaces
- Cross-list automation

## Current Products
- Gemini 12-month student accounts
- Perplexity 1-month accounts

## Competitors to Monitor
- Other Gemini sellers on Plati
- Other Perplexity sellers

## Automation Scripts Needed
1. `check_inventory.py` - Monitor stock levels
2. `price_scraper.py` - Competitor price tracking
3. `sales_report.py` - Daily analytics
4. `restock_alerter.py` - Low stock notifications
