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

print("[+] Initializing Dhan API Connection Tester...")

try:
    # Set up connection
    dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    dhan = dhanhq(dhan_context)
    
    # Ping the server for Fund Limits
    funds = dhan.get_fund_limits()
    
    if funds.get('status') == 'success':
        # Dhan's API spelling is sometimes literally 'availabelBalance'
        available_margin = funds.get('data', {}).get('availabelBalance', 0) 
        
        print(f"[✔] BOOM! Successfully Connected to Dhan Server!")
        print(f"[▶] Current Available Margin: ₹{available_margin}")
    else:
        print("[-] Authentication failed. Token might be expired.")
        print("Error Payload:", funds)

except Exception as e:
    print(f"[X] An error occurred: {e}")