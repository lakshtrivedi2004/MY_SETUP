import time
import yfinance as yf
import pandas as pd

# ==========================================
# 1. SETUP (PAPER TRADING MODE)
# ==========================================
TICKER = "BTC-USD" 

# State Management for Risk Engine
position_open = False
buy_price = 0.0
stoploss_price = 0.0
risk_amount = 50.0  # Risking $50 per trade for BTC test

# Overtrading Safety Switch
MAX_TRADES_PER_DAY = 3
trades_taken_today = 0

print("[+] Alpha Bot v2.1 (PAPER TRADING) Initialized.")
print(f"[+] Target Asset: {TICKER} (Weekend Testing)")
print(f"[+] Risk Engine: 1:2 Target with 1:1 Breakeven Trailing SL")
print(f"[+] Safety Switch: Max Daily Trades Limit = {MAX_TRADES_PER_DAY}")
print("[+] Connecting to Live Data Stream...\n")

# ==========================================
# 2. INGESTION & INFERENCE (TRUE CROSSOVER)
# ==========================================
def get_latest_market_data():
    try:
        df = yf.Ticker(TICKER).history(period="1d", interval="1m")
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
        prev_candle = df.iloc[-3]            # Previous to previous candle
        last_candle = df.iloc[-2]            # Just closed candle
        current_price = df.iloc[-1]['Close'] # Live price
        
        # TRUE CROSSOVER LOGIC:
        # 1. Purani candle EMA ke neeche ya barabar thi
        # 2. Nayi closed candle EMA ke strictly upar close hui hai
        if (prev_candle['Close'] <= prev_candle['9_EMA']) and (last_candle['Close'] > last_candle['9_EMA']):
            return True, current_price
            
        return False, current_price
    except Exception as e:
        return False, 0.0

# ==========================================
# 3. MOCK EXECUTION ENGINE
# ==========================================
def execute_trade(transaction_type, price_note="MARKET"):
    print(f"\n[PAPER TRADE] ---> Executing {transaction_type} Order at {price_note}")
    return True

# ==========================================
# 4. THE MASTER LOOP & RISK MANAGER
# ==========================================
while True:
    try:
        # Check if max trades limit is reached
        if trades_taken_today >= MAX_TRADES_PER_DAY:
            print(f"\n[!] STOP: Max daily trades limit ({MAX_TRADES_PER_DAY}) reached. Shutting down for today.")
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
            print(f"[{current_time}] Scan {TICKER} -> Price: ${current_price:.2f} | Signal: {'BUY' if signal else 'HOLD'} | Trades Today: {trades_taken_today}/{MAX_TRADES_PER_DAY}")
            
            if signal:
                print(f"[+] True Crossover Detected! Attempting entry...")
                if execute_trade("BUY", f"${current_price:.2f}"):
                    position_open = True
                    trades_taken_today += 1  # Increment trade counter
                    buy_price = current_price
                    stoploss_price = buy_price - risk_amount
                    print(f"[!] TRADE ACTIVE! Entry: ${buy_price:.2f} | Initial SL: ${stoploss_price:.2f} (Trade #{trades_taken_today})")
        
        # --- MANAGING ACTIVE TRADE ---
        else:
            target_1_1 = buy_price + risk_amount
            target_1_2 = buy_price + (risk_amount * 2)
            
            print(f"[{current_time}] Managing Trade -> Current: ${current_price:.2f} | SL: ${stoploss_price:.2f} | TGT: ${target_1_2:.2f}")

            # 1:1 Trailing to Breakeven
            if current_price >= target_1_1 and stoploss_price < buy_price:
                stoploss_price = buy_price
                print(f"[!!!] 1:1 Hit! Stoploss safely trailed to Breakeven: ${stoploss_price:.2f}")

            # 1:2 Target Hit
            elif current_price >= target_1_2:
                print(f"\n[$$$] 1:2 Target Hit (${current_price:.2f})! Booking Profit...")
                if execute_trade("SELL", "TAKE PROFIT"):
                    position_open = False
                    
            # Stoploss Hit
            elif current_price <= stoploss_price:
                if stoploss_price == buy_price:
                    print(f"\n[-] Stopped out at Breakeven (${current_price:.2f}). No loss taken.")
                else:
                    print(f"\n[-] Stoploss Hit (${current_price:.2f}). Cutting losses.")
                
                if execute_trade("SELL", "STOPLOSS"):
                    position_open = False
                    
        time.sleep(30) 
        
    except KeyboardInterrupt:
        print("\n[+] Bot shutting down gracefully.")
        break
    except Exception as e:
        print(f"[-] Loop Error: {e}")
        time.sleep(30)