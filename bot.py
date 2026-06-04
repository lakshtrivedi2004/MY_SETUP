from dhanhq import DhanContext, dhanhq

# Apna actual Client ID yahan dalo
CLIENT_ID = "1104646279".strip() 

# Apna lamba token bina kisi dar ke yahan paste karo
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzgwNjc4NTY4LCJpYXQiOjE3ODA1OTIxNjgsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAzODE2NjQ1In0.ogdFd5GtBSHAZpr5ONb8FxTpov2YIoFRW_H-hsFepPE1qpbk8464ufpKAL1wI5hmogTgfV7HYXZwm0kWQLIV4w" 

# Safety check: Remove any accidental spaces
ACCESS_TOKEN = ACCESS_TOKEN.strip()

print("[+] Initializing Dhan API Connection (v2.2+)...")

try:
    dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    dhan = dhanhq(dhan_context)
    
    funds = dhan.get_fund_limits()
    if funds.get('status') == 'success':
        available_margin = funds.get('data', {}).get('availabelBalance', 0)
        print(f"[✔] Successfully Connected!")
        print(f"[▶] Current Available Margin: ₹{available_margin}")
    else:
        print("[-] Authentication failed. Please check your Client ID or Token.")
        print("Error Payload:", funds)

except Exception as e:
    print(f"[X] An error occurred: {e}")