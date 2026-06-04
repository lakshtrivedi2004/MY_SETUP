from dhanhq import DhanContext, dhanhq

# Your verified credentials
CLIENT_ID = "1104646279".strip()
# Paste your newly copied token here
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzgwNjc4NTY4LCJpYXQiOjE3ODA1OTIxNjgsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTAzODE2NjQ1In0.ogdFd5GtBSHAZpr5ONb8FxTpov2YIoFRW_H-hsFepPE1qpbk8464ufpKAL1wI5hmogTgfV7HYXZwm0kWQLIV4w".strip() 

print("[+] Initializing Dhan Trading API...")

try:
    dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
    dhan = dhanhq(dhan_context)
    
    print("[+] Attempting to structure a dummy buy order for 1 share of Tata Motors...")
    
    # Structuring the Order Payload
    # This places a limit order to buy 1 share of Tata Motors at 900 INR
    order_response = dhan.place_order(
        security_id='3456',          # Tata Motors NSE ID
        exchange_segment='NSE_EQ',   
        transaction_type='BUY',
        quantity=1,
        order_type='LIMIT',
        product_type='INTRADAY',     # MIS (Intraday)
        price=900.0                 # The limit price
    )
    
    print("\n--- Order Response ---")
    if order_response.get('status') == 'success':
        order_id = order_response.get('data', {}).get('orderId')
        print(f"[✔] SUCCESS! Order placed. Order ID: {order_id}")
    else:
        print("[-] FAILED to place order.")
        print("Reason:", order_response)

except Exception as e:
    print(f"[X] An error occurred: {e}")