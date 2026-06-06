import os
import requests
import json
from dotenv import load_dotenv

# ==========================================
# 1. CREDENTIALS & SETUP (Via .env)
# ==========================================
# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

if not CLIENT_ID or not ACCESS_TOKEN:
    print("[X] ERROR: Credentials not found! Please check your .env file.")
    exit()

print("[+] Bypassing buggy DhanHQ Library...")
print("[+] Initializing Raw API Connection (AMO MODE)...")

url = "https://api.dhan.co/orders"

headers = {
    'access-token': ACCESS_TOKEN,
    'client-id': CLIENT_ID,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Dhan API's exact internal JSON requirement. Koi field miss nahi hogi ab.
payload = {
    "dhanClientId": CLIENT_ID,
    "correlationId": "AlphaBot_AMO_01", # Unique ID for our tracking
    "transactionType": "BUY",
    "exchangeSegment": "NSE_EQ",
    "productType": "INTRADAY",
    "orderType": "LIMIT",
    "validity": "DAY",
    "securityId": "3456",               # Tata Motors
    "quantity": 1,
    "disclosedQuantity": 0,
    "price": 900.0,
    "triggerPrice": 0.0,
    "afterMarketOrder": True,
    "amoTime": "OPEN",
    "boProfitValue": 0.0,
    "boStopLossValue": 0.0,
    "drvExpiryDate": None,
    "drvOptionType": None,
    "drvStrikePrice": 0.0
}

try:
    print("[+] Sending Raw JSON Payload directly to Exchange...")
    
    # Bypassing the wrapper and posting directly to Dhan's servers
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    print("\n--- RAW API RESPONSE ---")
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            order_id = data.get('data', {}).get('orderId', 'UNKNOWN')
            print(f"[✔] BOOM! AMO Successfully placed. Order ID: {order_id}")
            print("[!] ACTION REQUIRED: Open your Dhan App and cancel this order before 9:00 AM tomorrow!")
        else:
            print("[-] FAILED to place AMO.")
            print("Reason:", data)
    else:
        print(f"[-] HTTP Error {response.status_code}")
        print("Reason:", response.text)

except Exception as e:
    print(f"[X] An error occurred: {e}")