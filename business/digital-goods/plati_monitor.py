#!/usr/bin/env python3
"""
Plati.market / Digiseller API Integration
Monitors inventory, sales, and competitor pricing
"""

import requests
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class DigisellerAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.digiseller.ru"
        
    def get_seller_products(self) -> List[Dict]:
        """Get all seller's products"""
        endpoint = f"{self.base_url}/seller-goods"
        params = {
            "seller_id": self._get_seller_id(),
            "page": 1,
            "rows": 100
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get('rows', [])
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
    
    def get_product_details(self, product_id: str) -> Dict:
        """Get detailed info about a specific product"""
        endpoint = f"{self.base_url}/seller-goods"
        params = {"id": product_id}
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return {}
    
    def check_inventory(self, product_id: str) -> int:
        """Check remaining stock for a product"""
        product = self.get_product_details(product_id)
        # Digiseller returns remaining codes/accounts
        return product.get('in_stock', 0)
    
    def get_sales(self, days: int = 7) -> List[Dict]:
        """Get sales for last N days"""
        endpoint = f"{self.base_url}/sales"
        
        date_start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        date_finish = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            "seller_id": self._get_seller_id(),
            "date_start": date_start,
            "date_finish": date_finish,
            "page": 1,
            "rows": 100
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get('rows', [])
        except Exception as e:
            print(f"Error fetching sales: {e}")
            return []
    
    def _get_seller_id(self) -> str:
        """Extract seller ID from API key or config"""
        return os.getenv('PLATI_SELLER_ID', '1179730')


class InventoryMonitor:
    """Monitors inventory levels and sends alerts"""
    
    LOW_STOCK_THRESHOLD = 10
    CRITICAL_STOCK_THRESHOLD = 3
    
    def __init__(self, api: DigisellerAPI):
        self.api = api
        
    def check_all_products(self) -> Dict:
        """Check inventory for all products"""
        products = self.api.get_seller_products()
        status = {
            'ok': [],
            'low': [],
            'critical': [],
            'errors': []
        }
        
        for product in products:
            try:
                stock = self.api.check_inventory(product['id'])
                product_info = {
                    'id': product['id'],
                    'name': product.get('name', 'Unknown'),
                    'stock': stock
                }
                
                if stock <= 0:
                    status['critical'].append(product_info)
                elif stock <= self.CRITICAL_STOCK_THRESHOLD:
                    status['critical'].append(product_info)
                elif stock <= self.LOW_STOCK_THRESHOLD:
                    status['low'].append(product_info)
                else:
                    status['ok'].append(product_info)
                    
            except Exception as e:
                status['errors'].append({
                    'id': product['id'],
                    'error': str(e)
                })
        
        return status
    
    def generate_report(self) -> str:
        """Generate inventory report"""
        status = self.check_all_products()
        
        report = []
        report.append("📊 INVENTORY REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 50)
        
        if status['critical']:
            report.append("\n🚨 CRITICAL (Restock NOW):")
            for p in status['critical']:
                report.append(f"  • {p['name']}: {p['stock']} left")
        
        if status['low']:
            report.append("\n⚠️  LOW STOCK (Restock soon):")
            for p in status['low']:
                report.append(f"  • {p['name']}: {p['stock']} left")
        
        if status['ok']:
            report.append(f"\n✅ OK ({len(status['ok'])} products)")
        
        return "\n".join(report)


class CompetitorTracker:
    """Tracks competitor pricing on Plati.market"""
    
    def __init__(self):
        self.base_url = "https://plati.market"
    
    def search_competitors(self, query: str) -> List[Dict]:
        """Search for similar products on Plati"""
        search_url = f"{self.base_url}/search/{query}"
        
        try:
            response = requests.get(search_url, timeout=30)
            # Parse HTML for product listings
            # This would need BeautifulSoup for proper parsing
            return []
        except Exception as e:
            print(f"Error searching competitors: {e}")
            return []


def main():
    """Main execution"""
    api_key = os.getenv('DIGISELLER_API_KEY', '9E0158D50BB2430D978F4707E3329153')
    seller_id = os.getenv('PLATI_SELLER_ID', '1179730')
    
    api = DigisellerAPI(api_key)
    monitor = InventoryMonitor(api)
    
    # Generate and print report
    report = monitor.generate_report()
    print(report)
    
    # Save report
    os.makedirs('reports', exist_ok=True)
    filename = f"reports/inventory_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"\n📁 Report saved to: {filename}")


if __name__ == "__main__":
    main()
