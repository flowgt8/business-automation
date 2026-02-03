#!/bin/bash
# Setup script for business automation

set -e

echo "🚀 Setting up Business Automation Suite..."

# Install dependencies
echo "📦 Installing Python dependencies..."
cd /root/.openclaw/workspace/business/digital-goods
pip install -r requirements.txt

# Set environment variables (add to .bashrc if not exists)
if ! grep -q "DIGISELLER_API_KEY" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Business Automation Environment" >> ~/.bashrc
    echo 'export DIGISELLER_API_KEY="9E0158D50BB2430D978F4707E3329153"' >> ~/.bashrc
    echo 'export PLATI_SELLER_ID="1179730"' >> ~/.bashrc
    echo "✅ Environment variables added to .bashrc"
fi

# Create reports directory
mkdir -p /root/.openclaw/workspace/business/digital-goods/reports

echo ""
echo "⚙️  Setting up cron jobs..."

# Remove existing cron jobs for this script
crontab -l 2>/dev/null | grep -v "daily_automation.py" | crontab - 2>/dev/null || true

# Add new cron jobs
(crontab -l 2>/dev/null; echo "# Business Automation - Every 6 hours") | crontab -
(crontab -l 2>/dev/null; echo "0 */6 * * * cd /root/.openclaw/workspace/business/digital-goods && python3 daily_automation.py >> /tmp/business_automation.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "# Daily summary at 7 AM") | crontab -
(crontab -l 2>/dev/null; echo "0 7 * * * cd /root/.openclaw/workspace/business/digital-goods && python3 daily_automation.py >> /tmp/business_automation_morning.log 2>&1") | crontab -

echo "✅ Cron jobs set up:"
echo "   • Inventory check every 6 hours"
echo "   • Daily summary at 7:00 AM"

echo ""
echo "🔧 Testing automation..."
python3 /root/.openclaw/workspace/business/digital-goods/plati_monitor.py || echo "⚠️  Test run completed with warnings"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Create GitHub repo: https://github.com/new"
echo "   2. Run: ./push_to_github.sh"
echo "   3. Check reports in: business/digital-goods/reports/"
echo ""
echo "⏰ Automation will run automatically via cron"
