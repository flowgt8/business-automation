import requests
import hashlib
import time
import json
from datetime import datetime, timedelta

# --- CONFIGURATION ---
SELLER_ID = 1179730
API_KEY = "9E0158D50BB2430D978F4707E3329153"
LOG_FILE = "weekly_sales_report.txt"

def get_token():
    """Get the Session Token."""
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()

    url = "https://api.digiseller.com/api/apilogin"
    payload = {
        "seller_id": SELLER_ID,
        "timestamp": int(timestamp),
        "sign": sign
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if data.get("retval") == 0:
            print(f"Auth Success! Token: {data.get('token')[:10]}...")
            return data.get("token")
        else:
            print(f"Auth Failed: {data.get('retdesc')}")
            return None
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

def fetch_sales_v2(token):
    """Fetch sales using the verified /seller-sells/v2 endpoint."""
    # 1. The URL MUST have the token in the query string
    base_url = f"https://api.digiseller.com/api/seller-sells/v2?token={token}"

    # 2. Date format must be 'YYYY-MM-DD HH:MM:SS'
    end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    # 3. JSON Payload
    payload = {
        "date_start": start_date,
        "date_finish": end_date,
        "returned": 0, # 0 = Include refunds, 1 = Exclude
        "page": 1,
        "rows": 50
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"Fetching sales from {start_date} to {end_date}...")

    try:
        # Method must be POST
        r = requests.post(base_url, json=payload, headers=headers, timeout=15)

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            print("Error 404: Endpoint mismatch. Trying fallback...")
            return None
        else:
            print(f"API Error {r.status_code}: {r.text}")
            return None
    except Exception as e:
        print(f"Connection Failed: {e}")
        return None

def save_report(data):
    """Parse and save the sales data."""
    if not data:
        return

    with open(LOG_FILE, "w") as f:
        f.write(f"--- Sales Report (Last 7 Days) ---\n")

        # Digiseller V2 returns a 'rows' array
        rows = data.get("rows", [])

        if not rows:
            print("No sales found in this period.")
            f.write("No sales found.\n")
        else:
            count = 0
            for item in rows:
                # Extract fields from V2 response structure
                date = item.get("date_pay", "Unknown Date")
                name = item.get("product_name", "Unknown Product")
                invoice = item.get("invoice_id", "N/A")
                amount = item.get("amount_in", "0") # Amount received
                curr = item.get("amount_currency", "")
                email = item.get("email", "hidden")

                line = f"[{date}] Order #{invoice} | {name} | {amount} {curr} ({email})"
                f.write(line + "\n")
                print(line)
                count += 1
            print(f"\nSuccess! Found {count} sales. Saved to {LOG_FILE}")

if __name__ == "__main__":
    tk = get_token()
    if tk:
        sales_data = fetch_sales_v2(tk)
        save_report(sales_data)
