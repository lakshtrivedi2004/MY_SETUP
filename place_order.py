import os
from dhanhq import DhanContext, dhanhq
from dotenv import load_dotenv

# ==========================================
# 1. CREDENTIALS (Via Secure .env)
# ==========================================
load_dotenv()

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

if not CLIENT_ID or not ACCESS_TOKEN:
    print("[X] ERROR: Credentials not found! Please check your .env file.")
    exit()

print("\n" + "="*55)
print(" 🎯 DHAN TERMINAL: MANUAL SNIPER (BRACKET ORDER) 🎯 ")
print("="*55)

# ==========================================
# 2. INTERACTIVE CLI COMMANDS
# ==========================================
try:
    print("[+] Default Asset: Tata Motors (NSE ID: 3456)")
    qty_input = int(input("[?] Enter Quantity (e.g., 1): "))
    entry_price = float(input("[?] Enter Buy Price (Limit, e.g., 900.0): ₹"))
    target_price = float(input("[?] Enter Exact Target Price (e.g., 910.0): ₹"))
    sl_price = float(input("[?] Enter Exact Stoploss Price (e.g., 890.0): ₹"))
except ValueError:
    print("\n[-] Invalid Input! Please enter numbers only. Exiting...")
    exit()

print("\n[+] Initializing Live Market Trading API...")

# ==========================================
# 3. EXECUTION ENGINE
# ==========================================
try:
    dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    dhan = dhanhq(dhan_context)
    
    print(f"[+] Firing Bracket Order: BUY {qty_input} qty @ ₹{entry_price}")
    print(f"    -> Auto Target: ₹{target_price}")
    print(f"    -> Auto Stoploss: ₹{sl_price}")
    
    # Structuring a Bracket Order (BO) Payload using strict Dhan constants
    order_response = dhan.place_order(
        security_id='3456',            
        exchange_segment=dhan.NSE,     
        transaction_type=dhan.BUY,     
        quantity=qty_input,
        order_type=dhan.LIMIT,         
        product_type=dhan.BO,          # [NEW] BO means Bracket Order (Entry + Target + SL)
        price=entry_price,
        bo_profit_value=target_price,  # [NEW] Dhan API Target param
        bo_stop_loss_Value=sl_price    # [NEW] Dhan API SL param
    )
    
    print("\n--- Order Response ---")
    if order_response.get('status') == 'success':
        order_id = order_response.get('data', {}).get('orderId')
        print(f"[✔] SUCCESS! Sniper Order placed. Main Order ID: {order_id}")
        print("[!] Note: Exchange will auto-place your TGT and SL orders once the Entry is triggered.")
    else:
        print("[-] FAILED to place sniper order.")
        print("Reason:", order_response)

except Exception as e:
    print(f"[X] An error occurred: {e}")