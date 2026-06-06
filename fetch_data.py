import os
import pandas as pd
from datetime import datetime
from dhanhq import DhanContext, dhanhq
from dotenv import load_dotenv

# ==========================================
# 1. CREDENTIALS & SETUP (Via .env)
# ==========================================
load_dotenv()

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

if not CLIENT_ID or not ACCESS_TOKEN:
    print("[X] ERROR: Credentials not found! Please check your .env file.")
    exit()

print("[+] Connecting to Dhan API for Historical Data...")

try:
    dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    dhan = dhanhq(dhan_context)
    
    # Dynamic Date: Hamesha aaj ki date automatically nikalega
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"[+] Fetching Intraday 1-Minute Data for HDFC Bank for {today_date}...")
    
    # Fetch data using Dhan's internal constants for stability
    historical_data = dhan.intraday_minute_data(
        security_id='1333',
        exchange_segment=dhan.NSE,    
        instrument_type=dhan.EQUITY,  
        from_date=today_date,         # Auto-updates to current day
        to_date=today_date            # Auto-updates to current day
    )
    
    if historical_data.get('status') == 'success':
        data = historical_data.get('data', {})
        
        # Check if we actually got data (e.g., market might be closed on weekends)
        if not data or not data.get('start_Time'):
            print(f"[-] No data found for {today_date}. (Market closed ya phir API error)")
        else:
            # Converting to Pandas DataFrame for ML pipeline
            df = pd.DataFrame({
                'Timestamp': pd.to_datetime(data.get('start_Time')),
                'Open': data.get('open'),
                'High': data.get('high'),
                'Low': data.get('low'),
                'Close': data.get('close'),
                'Volume': data.get('volume')
            })
            
            df.set_index('Timestamp', inplace=True)
            
            print("[✔] Data successfully converted to Pandas DataFrame!\n")
            print(df.tail()) # Head ki jagah Tail() print kiya taaki sabse latest candles dikhein
            print("\n[✔] Data is ready for ML Model ingestion!")
            
    else:
        print("[-] Failed to fetch data.")
        print("Error Payload:", historical_data)

except Exception as e:
    print(f"[X] An error occurred: {e}")