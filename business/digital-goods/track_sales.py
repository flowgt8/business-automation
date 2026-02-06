import urllib.request
import urllib.parse
import hashlib
import time
import json
from datetime import datetime, timedelta

# --- CONFIGURATION ---
SELLER_ID = 1179730
API_KEY = "9E0158D50BB2430D978F4707E3329153"
LOG_FILE = "/home/node/.openclaw/workspace/business/digital-goods/weekly_sales_report.txt"

def get_token():
    """Get the Session Token."""
    timestamp = str(int(time.time()))
    sign = hashlib.sha256((API_KEY + timestamp).encode('utf-8')).hexdigest()

    url = "https://api.digiseller.com/api/apilogin"
    payload = json.dumps({
        "seller_id": int(SELLER_ID),
        "timestamp": int(timestamp),
        "sign": sign
    }).encode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
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
    """Fetch sales using the /seller-sells/v2 endpoint."""
    base_url = f"https://api.digiseller.com/api/seller-sells/v2?token={token}"

    end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    payload = json.dumps({
        "date_start": start_date,
        "date_finish": end_date,
        "returned": 0,
        "page": 1,
        "rows": 50
    }).encode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"Fetching sales from {start_date} to {end_date}...")

    try:
        req = urllib.request.Request(base_url, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode('utf-8')}")
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

        rows = data.get("rows", [])

        if not rows:
            print("No sales found in this period.")
            f.write("No sales found.\n")
        else:
            count = 0
            for item in rows:
                date = item.get("date_pay", "Unknown Date")
                name = item.get("product_name", "Unknown Product")
                invoice = item.get("invoice_id", "N/A")
                amount = item.get("amount_in", "0")
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
