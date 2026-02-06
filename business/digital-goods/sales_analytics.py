#!/usr/bin/env python3
"""
Sales Analytics & Reporting for Digital Goods Business
Tracks revenue, best sellers, and trends
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

class SalesAnalyzer:
    def __init__(self, sales_data: List[Dict]):
        self.sales = sales_data
        
    def daily_revenue(self, days: int = 7) -> Dict:
        """Calculate daily revenue for last N days"""
        revenue = defaultdict(float)
        
        for sale in self.sales:
            date = sale.get('date', '').split()[0]  # Get date part only
            amount = float(sale.get('amount', 0))
            revenue[date] += amount
        
        return dict(revenue)
    
    def best_sellers(self, top_n: int = 5) -> List[Dict]:
        """Get top selling products"""
        product_stats = defaultdict(lambda: {'count': 0, 'revenue': 0})
        
        for sale in self.sales:
            product_id = sale.get('product_id')
            product_name = sale.get('product_name', 'Unknown')
            amount = float(sale.get('amount', 0))
            
            key = f"{product_id}_{product_name}"
            product_stats[key]['count'] += 1
            product_stats[key]['revenue'] += amount
            product_stats[key]['name'] = product_name
            product_stats[key]['id'] = product_id
        
        # Sort by revenue
        sorted_products = sorted(
            product_stats.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )
        
        return sorted_products[:top_n]
    
    def generate_report(self) -> str:
        """Generate comprehensive sales report"""
        report = []
        report.append("💰 SALES ANALYTICS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 50)
        
        # Total stats
        total_revenue = sum(float(s.get('amount', 0)) for s in self.sales)
        total_sales = len(self.sales)
        
        report.append(f"\n📈 Total Revenue (last 7 days): ${total_revenue:.2f}")
        report.append(f"📦 Total Sales: {total_sales}")
        report.append(f"💵 Average Order: ${total_revenue/total_sales:.2f}" if total_sales > 0 else "💵 Average Order: $0.00")
        
        # Daily breakdown
        report.append("\n📅 Daily Revenue:")
        daily = self.daily_revenue()
        for date, amount in sorted(daily.items(), reverse=True)[:7]:
            report.append(f"  {date}: ${amount:.2f}")
        
        # Best sellers
        report.append("\n🏆 Top Products:")
        for i, product in enumerate(self.best_sellers(5), 1):
            report.append(f"  {i}. {product['name']}")
            report.append(f"     Sales: {product['count']} | Revenue: ${product['revenue']:.2f}")
        
        return "\n".join(report)


def main():
    """Example usage"""
    # This would be populated from actual API calls
    sample_sales = [
        # Example data structure
        # {
        #     'product_id': '123',
        #     'product_name': 'Gemini 12 Month Student',
        #     'amount': '15.00',
        #     'date': '2026-02-03 14:30:00'
        # }
    ]
    
    analyzer = SalesAnalyzer(sample_sales)
    print(analyzer.generate_report())


if __name__ == "__main__":
    main()
