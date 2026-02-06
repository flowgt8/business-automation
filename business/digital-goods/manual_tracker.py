#!/usr/bin/env python3
"""
Manual Sales Tracker for Digital Goods Business
Since API is being difficult, this tracks sales manually
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

DATA_FILE = 'sales_data.json'

class ManualSalesTracker:
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing sales data"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {'sales': [], 'last_updated': None}
    
    def _save_data(self):
        """Save sales data"""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_sale(self, product: str, quantity: int = 1, price_usd: float = 0, 
                 price_rub: float = 0, platform: str = 'plati'):
        """Add a new sale manually"""
        sale = {
            'id': len(self.data['sales']) + 1,
            'date': datetime.now().isoformat(),
            'product': product,
            'quantity': quantity,
            'price_usd': price_usd,
            'price_rub': price_rub,
            'platform': platform,
            'total_usd': price_usd * quantity,
            'total_rub': price_rub * quantity
        }
        
        self.data['sales'].append(sale)
        self._save_data()
        
        print(f"✅ Added sale: {product} x{quantity} = ${sale['total_usd']:.2f}")
        return sale
    
    def add_daily_summary(self, date: str, gemini_sales: int, perplexity_sales: int,
                         gemini_price: float = 15, perplexity_price: float = 5):
        """Add a daily summary"""
        summary = {
            'id': len(self.data['sales']) + 1,
            'date': date,
            'type': 'daily_summary',
            'gemini_sales': gemini_sales,
            'perplexity_sales': perplexity_sales,
            'total_sales': gemini_sales + perplexity_sales,
            'revenue_usd': (gemini_sales * gemini_price) + (perplexity_sales * perplexity_price),
            'gemini_price': gemini_price,
            'perplexity_price': perplexity_price
        }
        
        self.data['sales'].append(summary)
        self._save_data()
        
        print(f"✅ Added summary for {date}: {summary['total_sales']} sales, ${summary['revenue_usd']:.2f}")
        return summary
    
    def get_daily_report(self, days: int = 7) -> str:
        """Generate daily sales report"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_sales = [s for s in self.data['sales'] 
                       if datetime.fromisoformat(s['date']) > cutoff]
        
        # Group by date
        by_date = defaultdict(lambda: {'gemini': 0, 'perplexity': 0, 'revenue': 0})
        
        for sale in recent_sales:
            if sale.get('type') == 'daily_summary':
                date = sale['date'][:10]
                by_date[date]['gemini'] += sale['gemini_sales']
                by_date[date]['perplexity'] += sale['perplexity_sales']
                by_date[date]['revenue'] += sale['revenue_usd']
        
        report = []
        report.append("📊 SALES REPORT (Last {} days)".format(days))
        report.append("=" * 60)
        report.append(f"Last updated: {self.data.get('last_updated', 'Never')}")
        report.append("")
        
        total_revenue = 0
        total_gemini = 0
        total_perplexity = 0
        
        for date in sorted(by_date.keys(), reverse=True):
            data = by_date[date]
            total_gemini += data['gemini']
            total_perplexity += data['perplexity']
            total_revenue += data['revenue']
            
            report.append(f"📅 {date}")
            report.append(f"   Gemini 12m: {data['gemini']} sales")
            report.append(f"   Perplexity: {data['perplexity']} sales")
            report.append(f"   💰 Revenue: ${data['revenue']:.2f}")
            report.append("")
        
        report.append("=" * 60)
        report.append("📈 TOTALS:")
        report.append(f"   Gemini 12m: {total_gemini} sales")
        report.append(f"   Perplexity: {total_perplexity} sales")
        report.append(f"   💰 Total Revenue: ${total_revenue:.2f}")
        
        return "\n".join(report)
    
    def get_inventory_alert(self, gemini_stock: int, perplexity_stock: int) -> str:
        """Check inventory levels and alert"""
        LOW_THRESHOLD = 10
        CRITICAL_THRESHOLD = 3
        
        alerts = []
        
        if gemini_stock <= 0:
            alerts.append("🚨 CRITICAL: Gemini 12m OUT OF STOCK!")
        elif gemini_stock <= CRITICAL_THRESHOLD:
            alerts.append(f"🚨 CRITICAL: Gemini 12m only {gemini_stock} left!")
        elif gemini_stock <= LOW_THRESHOLD:
            alerts.append(f"⚠️  LOW: Gemini 12m only {gemini_stock} left")
        
        if perplexity_stock <= 0:
            alerts.append("🚨 CRITICAL: Perplexity OUT OF STOCK!")
        elif perplexity_stock <= CRITICAL_THRESHOLD:
            alerts.append(f"🚨 CRITICAL: Perplexity only {perplexity_stock} left!")
        elif perplexity_stock <= LOW_THRESHOLD:
            alerts.append(f"⚠️  LOW: Perplexity only {perplexity_stock} left")
        
        if not alerts:
            return "✅ Stock levels OK"
        
        return "\n".join(alerts)


def interactive_menu():
    """Interactive menu for manual tracking"""
    tracker = ManualSalesTracker()
    
    while True:
        print("\n" + "=" * 60)
        print("📊 MANUAL SALES TRACKER")
        print("=" * 60)
        print("1. Add daily summary")
        print("2. View report (last 7 days)")
        print("3. Check inventory")
        print("4. View all data")
        print("5. Exit")
        print("-" * 60)
        
        choice = input("Choice: ").strip()
        
        if choice == '1':
            print("\n📅 Add Daily Summary")
            date = input("Date (YYYY-MM-DD, enter for today): ").strip()
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            try:
                gemini = int(input("Gemini 12m sales: "))
                perplexity = int(input("Perplexity sales: "))
                gemini_price = float(input("Gemini price (USD, default 15): ") or 15)
                perplexity_price = float(input("Perplexity price (USD, default 5): ") or 5)
                
                tracker.add_daily_summary(date, gemini, perplexity, gemini_price, perplexity_price)
            except ValueError:
                print("❌ Invalid input")
                
        elif choice == '2':
            print("\n" + tracker.get_daily_report(7))
            
        elif choice == '3':
            print("\n📦 Inventory Check")
            try:
                gemini_stock = int(input("Gemini 12m stock: "))
                perplexity_stock = int(input("Perplexity stock: "))
                print("\n" + tracker.get_inventory_alert(gemini_stock, perplexity_stock))
            except ValueError:
                print("❌ Invalid input")
                
        elif choice == '4':
            print("\n📋 All Data:")
            print(json.dumps(tracker.data, indent=2))
            
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick add from command line
        tracker = ManualSalesTracker()
        # Example: python manual_tracker.py --quick 2026-02-03 5 3
        if len(sys.argv) >= 5:
            date = sys.argv[2]
            gemini = int(sys.argv[3])
            perplexity = int(sys.argv[4])
            tracker.add_daily_summary(date, gemini, perplexity)
        else:
            print("Usage: python manual_tracker.py --quick YYYY-MM-DD gemini_sales perplexity_sales")
    else:
        interactive_menu()
