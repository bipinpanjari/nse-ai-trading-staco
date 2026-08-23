#!/usr/bin/env python3
"""
PLACE REAL TRADES ON DHAN BROKER
This script places actual market orders with real money
Only execute this after verifying credentials work!
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv('DHAN_CLIENT_ID')
token = os.getenv('DHAN_ACCESS_TOKEN')

if not client_id or token.startswith('your_'):
    print("\nERROR: Dhan credentials not configured!")
    print("\nTo enable real trading:")
    print("1. Get fresh credentials from: https://dhanhq.co/")
    print("2. Update backend/.env with your credentials")
    print("3. Run: python place_real_dhan_trade.py\n")
    sys.exit(1)

from dhanhq import dhanhq

dhan = dhanhq(client_id, token)

print("\n" + "="*80)
print("REAL DHAN TRADE EXECUTION - LIVE MARKET")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
print(f"Client ID: {client_id}")
print("="*80)

# ============================================================
# EXAMPLE 1: Place a BUY order for NIFTY (Market Order)
# ============================================================

print("\n[1] PLACING BUY ORDER")
print("-"*80)

# Order details
symbol = "NIFTY"
exchange = dhan.NSE
segment = dhan.INDEX
order_type = dhan.MARKET
transaction_type = dhan.BUY
quantity = 1
price = 0  # Market order (0 = execute at best available price)

try:
    response = dhan.place_order(
        security_id=symbol,
        exchange_segment=segment,
        transaction_type=transaction_type,
        quantity=quantity,
        order_type=order_type,
        price=price,
        product_type=dhan.CNC  # CNC = Delivery (can hold overnight)
    )
    
    print(f"Symbol: {symbol}")
    print(f"Type: {transaction_type} (MARKET ORDER)")
    print(f"Quantity: {quantity}")
    print(f"Order Type: {order_type}")
    print(f"Response: {response}")
    
    if response and response.get('status') == 'success':
        order_id = response.get('data', {}).get('orderId')
        print(f"\n✓ ORDER PLACED SUCCESSFULLY!")
        print(f"Order ID: {order_id}")
        print(f"Status: Order is now in market")
    else:
        error = response.get('remarks', {}).get('error_message', 'Unknown error')
        print(f"\n✗ ORDER FAILED: {error}")

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")

# ============================================================
# EXAMPLE 2: Get Current Account Balance
# ============================================================

print("\n\n[2] CHECK ACCOUNT BALANCE")
print("-"*80)

try:
    funds = dhan.get_fund_limits()
    if funds and funds.get('status') == 'success':
        data = funds.get('data', {})
        print(f"Available Balance: Rs {data.get('availableBalance', 0)}")
        print(f"Used Balance: Rs {data.get('usedBalance', 0)}")
        print(f"Total Balance: Rs {data.get('totalBalance', 0)}")
        print(f"Margin Available: Rs {data.get('primaryClearing', 0)}")
    else:
        print("Could not fetch balance")

except Exception as e:
    print(f"ERROR: {str(e)}")

# ============================================================
# EXAMPLE 3: Get Current Holdings
# ============================================================

print("\n\n[3] VIEW YOUR HOLDINGS")
print("-"*80)

try:
    holdings = dhan.get_holdings()
    if holdings and holdings.get('status') == 'success':
        data = holdings.get('data', {})
        if data:
            print(f"Total Holdings: {len(data)}")
            for symbol, details in list(data.items())[:5]:
                qty = details.get('quantity', 0)
                price = details.get('price', 0)
                print(f"  • {symbol}: {qty} units @ Rs {price}")
    else:
        print("No holdings found or API error")

except Exception as e:
    print(f"ERROR: {str(e)}")

# ============================================================
# EXAMPLE 4: Get Live Quote Data
# ============================================================

print("\n\n[4] GET LIVE PRICE DATA")
print("-"*80)

try:
    # For different symbols, use different security IDs
    # Check Dhan documentation for security IDs
    
    quote = dhan.quote_data(
        security_id="99926000",  # NIFTY 50 ID
        exchange_segment=dhan.NSE_INDEX
    )
    
    if quote and quote.get('status') == 'success':
        data = quote.get('data', {})
        print(f"Symbol: NIFTY 50")
        print(f"Current Price: Rs {data.get('lastPrice', 0)}")
        print(f"Bid Price: Rs {data.get('bidPrice', 0)}")
        print(f"Ask Price: Rs {data.get('askPrice', 0)}")
        print(f"52-Week High: Rs {data.get('high52', 0)}")
        print(f"52-Week Low: Rs {data.get('low52', 0)}")
    else:
        print("Could not fetch quote")

except Exception as e:
    print(f"ERROR: {str(e)}")

# ============================================================
# IMPORTANT NOTES
# ============================================================

print("\n" + "="*80)
print("REAL TRADING ENABLED ⚠️")
print("="*80)
print("""
This script places ACTUAL orders on your DHAN account.
All trades are REAL and involve REAL MONEY.

Before running trades:
  ✓ Verify account has sufficient balance
  ✓ Test with small quantities first
  ✓ Monitor order execution in Dhan app
  ✓ Check P&L after each trade
  
Your account is now LIVE for trading!
""")
print("="*80 + "\n")
