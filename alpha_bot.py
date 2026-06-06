import os
import time
import requests
import json
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv

# ==========================================
# 1. CREDENTIALS & SETUP (Via .env)
# ==========================================
load_dotenv()

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
URL = "https://api.dhan.co/orders"

if not CLIENT_ID or not ACCESS_TOKEN:
    print("[X] ERROR: Credentials not found! Please check your .env file.")
    exit()

HEADERS = {
    'access-token': ACCESS_TOKEN,
    'client-id': CLIENT_ID,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# State Management for Risk Engine
position_open = False
buy_price = 0.0
stoploss_price = 0.0
risk_amount = 5.0  # ₹5 ka risk per share for HDFC Bank

# Overtrading Safety Switch
MAX_TRADES_PER_DAY = 3
trades_taken_today = 0

print("[+] Alpha Bot v2.1 (LIVE SECURE MODE) Initialized.")
print("[+] Risk Engine: 1:2 Target with 1:1 Breakeven Trailing SL")
print(f"[+] Safety Switch: Max Daily Trades Limit = {MAX_TRADES_PER_DAY}")
print("[+] Connecting to Live Data Stream...")

# ==========================================
# 2. INGESTION & INFERENCE (TRUE CROSSOVER)
# ==========================================
def get_latest_market_data():
    try:
        df = yf.Ticker("HDFCBANK.NS").history(period="1d", interval="1m")
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"[-] Data Fetch Error: {e}")
        return None

def check_buy_signal(df):
    try:
        df['9_EMA'] = df['Close'].ewm(span=9, adjust=False).mean()
        
        # Tracking 3 points for True Crossover
        prev_candle = df.iloc[-3]            
        last_candle = df.iloc[-2]            
        current_price = df.iloc[-1]['Close'] 
        
        # TRUE CROSSOVER LOGIC:
        if (prev_candle['Close'] <= prev_candle['9_EMA']) and (last_candle['Close'] > last_candle['9_EMA']):
            return True, current_price
            
        return False, current_price
    except Exception as e:
        return False, 0.0

# ==========================================
# 3. LIVE EXECUTION ENGINE
# ==========================================
def execute_trade(transaction_type, price_note="MARKET"):
    print(f"[!] Sending Live {transaction_type} Order to Dhan at {price_note}...")
    
    payload = {
        "dhanClientId": CLIENT_ID,
        "correlationId": f"AlphaBot_Live_{transaction_type}", 
        "transactionType": transaction_type, 
        "exchangeSegment": "NSE_EQ",
        "productType": "INTRADAY",
        "orderType": "MARKET",
        "validity": "DAY",
        "securityId": "1333",         # HDFC Bank Security ID
        "quantity": 1,
        "disclosedQuantity": 0,
        "price": 0.0,
        "triggerPrice": 0.0,
        "afterMarketOrder": False,
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
                print(f"[✔] BOOM! Live {transaction_type} Order Executed. ID: {order_id}")
                return True
            else:
                print(f"[-] {transaction_type} Failed. Reason:", data)
                return False
        else:
            print(f"[-] HTTP Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[X] Request Error: {e}")
        return False

# ==========================================
# 4. THE MASTER LOOP & RISK MANAGER
# ==========================================
while True:
    try:
        # Check if max trades limit is reached
        if trades_taken_today >= MAX_TRADES_PER_DAY:
            print(f"\n[!] STOP: Max daily trades limit ({MAX_TRADES_PER_DAY}) reached. Stopping Bot for today.")
            break

        current_time = time.strftime('%H:%M:%S')
        df = get_latest_market_data()
        
        if df is None:
            time.sleep(10)
            continue
            
        current_price = df.iloc[-1]['Close']
        
        # --- LOOKING FOR A TRADE ---
        if not position_open:
            signal, price = check_buy_signal(df)
            print(f"[{current_time}] Scan HDFC -> Price: ₹{current_price:.2f} | Signal: {'BUY' if signal else 'HOLD'} | Trades Today: {trades_taken_today}/{MAX_TRADES_PER_DAY}")
            
            if signal:
                print(f"\n[+] True Crossover Detected! Executing entry...")
                if execute_trade("BUY"):
                    position_open = True
                    trades_taken_today += 1  # Increment trade counter
                    buy_price = current_price
                    stoploss_price = buy_price - risk_amount
                    print(f"[!] LIVE TRADE ACTIVE! Entry: ₹{buy_price:.2f} | Initial SL: ₹{stoploss_price:.2f} (Trade #{trades_taken_today})")
        
        # --- MANAGING ACTIVE TRADE ---
        else:
            target_1_1 = buy_price + risk_amount
            target_1_2 = buy_price + (risk_amount * 2)
            
            print(f"[{current_time}] Managing Trade -> Current: ₹{current_price:.2f} | SL: ₹{stoploss_price:.2f} | TGT: ₹{target_1_2:.2f}")

            # 1:1 Trailing to Breakeven
            if current_price >= target_1_1 and stoploss_price < buy_price:
                stoploss_price = buy_price
                print(f"[!!!] 1:1 Hit! Stoploss safely trailed to Breakeven: ₹{stoploss_price:.2f}")

            # 1:2 Target Hit
            elif current_price >= target_1_2:
                print(f"\n[$$$] 1:2 Target Hit (₹{current_price:.2f})! Booking Profit...")
                if execute_trade("SELL", "TAKE PROFIT"):
                    position_open = False
                    
            # Stoploss Hit
            elif current_price <= stoploss_price:
                if stoploss_price == buy_price:
                    print(f"\n[-] Stopped out at Breakeven (₹{current_price:.2f}). No loss taken.")
                else:
                    print(f"\n[-] Stoploss Hit (₹{current_price:.2f}). Cutting losses.")
                
                if execute_trade("SELL", "STOPLOSS"):
                    position_open = False
                    
        time.sleep(30) 
        
    except KeyboardInterrupt:
        print("\n[+] Alpha Bot shutting down gracefully. Good luck!")
        break
    except Exception as e:
        print(f"[-] Loop Error: {e}")
        time.sleep(30)