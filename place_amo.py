import requests
import json

# Apna Token yahan daalna mat bhoolna (Dhyan se poora token copy karna)
CLIENT_ID = "1104646279".strip()
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzgwNjc4NTY4LCJpYXQiOjE3ODA1OTIxNjgsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAzODE2NjQ1In0.ogdFd5GtBSHAZpr5ONb8FxTpov2YIoFRW_H-hsFepPE1qpbk8464ufpKAL1wI5hmogTgfV7HYXZwm0kWQLIV4w".strip() 

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