#!/usr/bin/env python3
"""
Plati Sales Tracker - Following Gemini AI guide
"""

import requests
import json
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_KEY = "9E0158D50BB2430D978F4707E3329153"
SELLER_ID = "1179730"
LOG_FILE = "daily_sales_report.txt"

def get_token():
    """Exchange API key for a session token."""
    url = "https://api.digiseller.ru/api/apilogin"
    payload = {
        "seller_id": SELLER_ID,
        "timestamp": int(datetime.now().timestamp()),
        "api_key": API_KEY
    }
    
    print(f"Trying to get token from: {url}")
    print(f"Payload: {payload}")
    
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    return response.json().get("token")

def fetch_sales(token):
    """Fetch sales from the last 24 hours."""
    end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    url = f"https://api.digiseller.ru/api/seller-sales/statistics?token={token}"
    params = {
        "date_start": start_date,
        "date_end": end_date,
        "returned": 0
    }
    
    print(f"\nFetching sales from: {url}")
    print(f"Params: {params}")
    
    response = requests.get(url, params=params, timeout=30)
    print(f"Status: {response.status_code}")
    
    return response.json()

def save_report(sales_data):
    """Format and save the sales to a text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(LOG_FILE, "a") as f:
        f.write(f"\n--- Sales Report for {timestamp} ---\n")
        
        if not sales_data.get("rows"):
            f.write("No sales found in the last 24 hours.\n")
        else:
            for sale in sales_data["rows"]:
                f.write(f"ID: {sale.get('i_id', 'N/A')} | ")
                f.write(f"Product: {sale.get('g_name', 'N/A')} | ")
                f.write(f"Amount: {sale.get('amount', 'N/A')} {sale.get('currency', '')}\n")
    
    print(f"\nReport updated in {LOG_FILE}")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Plati Sales Tracker - Testing Gemini AI Script")
        print("=" * 60)
        
        token = get_token()
        if token:
            print(f"\n✅ Got token: {token[:30]}...")
            data = fetch_sales(token)
            save_report(data)
        else:
            print("\n❌ Failed to retrieve API token")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
