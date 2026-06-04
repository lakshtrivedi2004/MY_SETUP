import time
import requests
import json
import yfinance as yf
import pandas as pd

# ==========================================
# 1. CREDENTIALS & SETUP
# ==========================================
CLIENT_ID = "1104646279".strip()
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzgwNjc4NTY4LCJpYXQiOjE3ODA1OTIxNjgsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAzODE2NjQ1In0.ogdFd5GtBSHAZpr5ONb8FxTpov2YIoFRW_H-hsFepPE1qpbk8464ufpKAL1wI5hmogTgfV7HYXZwm0kWQLIV4w".strip() 
URL = "https://api.dhan.co/orders"

HEADERS = {
    'access-token': ACCESS_TOKEN,
    'client-id': CLIENT_ID,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# State Management
position_open = False
print("[+] Alpha Bot Initialized. Connecting to Data Stream...")

# ==========================================
# 2. INGESTION & INFERENCE (THE BRAIN)
# ==========================================
def check_signal():
    try:
        # Fetch latest 1-minute candle for HDFC Bank
        ticker = yf.Ticker("HDFCBANK.NS")
        df = ticker.history(period="1d", interval="1m")
        
        if df.empty:
            return "WAIT"
            
        # Calculate 9-EMA
        df['9_EMA'] = df['Close'].ewm(span=9, adjust=False).mean()
        
        # Get the last fully closed candle (second to last row)
        last_candle = df.iloc[-2] 
        
        # Strategy Logic: If Close crosses ABOVE 9-EMA, Buy!
        if last_candle['Close'] > last_candle['9_EMA']:
            return "BUY"
        return "HOLD"
        
    except Exception as e:
        print(f"[-] Data Fetch Error: {e}")
        return "ERROR"

# ==========================================
# 3. EXECUTION ENGINE
# ==========================================
def execute_trade():
    print("[!] BUY SIGNAL DETECTED. Executing Live Market Order...")
    
    # Raw JSON Payload for a Live Intraday Market Order
    payload = {
        "dhanClientId": CLIENT_ID,
        "correlationId": "AlphaBot_Live_01", 
        "transactionType": "BUY",
        "exchangeSegment": "NSE_EQ",
        "productType": "INTRADAY",
        "orderType": "MARKET",        # Market order for instant execution
        "validity": "DAY",
        "securityId": "1333",         # HDFC Bank
        "quantity": 1,
        "disclosedQuantity": 0,
        "price": 0.0,                 # Market orders don't need a price
        "triggerPrice": 0.0,
        "afterMarketOrder": False,    # This is a LIVE order, not AMO
        "amoTime": "OPEN",
        "boProfitValue": 0.0,
        "boStopLossValue": 0.0,
        "drvExpiryDate": None,
        "drvOptionType": None,
        "drvStrikePrice": 0.0
    }
    
    try:
        response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                order_id = data.get('data', {}).get('orderId', 'UNKNOWN')
                print(f"[✔] BOOM! Live Trade Executed. Order ID: {order_id}")
                return True
            else:
                print("[-] Execution Failed. Reason:", data)
                return False
        else:
            print(f"[-] HTTP Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"[X] Request Error: {e}")
        return False

# ==========================================
# 4. THE MASTER LOOP
# ==========================================
while True:
    try:
        current_time = time.strftime('%H:%M:%S')
        signal = check_signal()
        print(f"[{current_time}] Market Scan -> Signal: {signal} | Position Open: {position_open}")
        
        # Fire condition
        if signal == "BUY" and not position_open:
            success = execute_trade()
            if success:
                position_open = True # Block duplicate trades
                print("[+] Bot entering monitoring mode for open position...")
                
        # Wait 60 seconds before checking the next candle
        time.sleep(60) 
        
    except KeyboardInterrupt:
        print("\n[+] Alpha Bot shutting down gracefully. Good night!")
        break
    except Exception as e:
        print(f"[-] Loop Error: {e}")
        time.sleep(60)