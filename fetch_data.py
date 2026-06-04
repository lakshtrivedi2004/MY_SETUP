from dhanhq import DhanContext, dhanhq
import pandas as pd

# Apne details yahan dalo
CLIENT_ID = "1104646279".strip()
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzgwNjc4NTY4LCJpYXQiOjE3ODA1OTIxNjgsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAzODE2NjQ1In0.ogdFd5GtBSHAZpr5ONb8FxTpov2YIoFRW_H-hsFepPE1qpbk8464ufpKAL1wI5hmogTgfV7HYXZwm0kWQLIV4w".strip() 

print("[+] Connecting to Dhan API...")

try:
    dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    dhan = dhanhq(dhan_context)
    
    print("[+] Fetching Intraday 1-Minute Data for HDFC Bank...")
    
    # Updated: from_date aur to_date add kar diya
    historical_data = dhan.intraday_minute_data(
        security_id='1333',
        exchange_segment='NSE_EQ',
        instrument_type='EQUITY',
        from_date='2026-06-04',
        to_date='2026-06-04'
    )
    
    if historical_data.get('status') == 'success':
        data = historical_data.get('data', {})
        
        # DataFrame mein convert kar rahe hain ML input ke liye
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
        print(df.head()) # Shuru ki 5 rows print karega
        print("\n[✔] Data is ready for ML Model ingestion!")
        
    else:
        print("[-] Failed to fetch data.")
        print("Error Payload:", historical_data)

except Exception as e:
    print(f"[X] An error occurred: {e}")