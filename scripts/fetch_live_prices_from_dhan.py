#!/usr/bin/env python3
"""
FETCH LIVE PRICES FROM DHAN
Get real-time market data directly from DHAN API
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("LIVE PRICES FROM DHAN API")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
print("="*80)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from dhanhq import dhanhq
    
    client_id = os.getenv("DHAN_CLIENT_ID")
    access_token = os.getenv("DHAN_ACCESS_TOKEN")
    
    dhan = dhanhq(client_id, access_token)
    
    print("\n✅ DHAN Connection: ACTIVE")
    print(f"   Client: {client_id}")
    
    # Try to get available methods
    print("\n📋 Checking available DHAN API methods...")
    print("-"*80)
    
    # List available methods
    available_methods = [method for method in dir(dhan) if not method.startswith('_')]
    print(f"\nAvailable DHAN API methods ({len(available_methods)}):")
    for method in sorted(available_methods):
        print(f"  • {method}")
    
    # ============================================================
    # TRY TO FETCH PRICES
    # ============================================================
    print("\n" + "-"*80)
    print("ATTEMPTING TO FETCH LIVE PRICES")
    print("-"*80)
    
    # Try different security IDs for major instruments
    securities = {
        "NIFTY 50": {
            "security_id": "99926000",
            "exch_token": "99926000",
            "exchange": "NSE_INDEX"
        },
        "RELIANCE": {
            "security_id": "1333345600050",
            "exch_token": "1000220061000",
            "exchange": "NSE_EQ"
        },
        "TCS": {
            "security_id": "1333345600041",
            "exch_token": "1000220001000",
            "exchange": "NSE_EQ"
        },
        "NIFTY FUTURES": {
            "security_id": "99926000",
            "exch_token": "99926000",
            "exchange": "NSE_FNO"
        }
    }
    
    for symbol, details in securities.items():
        print(f"\n🔍 Fetching {symbol}...")
        try:
            # Try get_quotes if it exists
            if hasattr(dhan, 'get_quotes'):
                quote = dhan.get_quotes(
                    security_id=details['security_id'],
                    exch_token=details['exch_token'],
                    exchange_segment=details['exchange']
                )
                print(f"   ✅ Response received:")
                print(f"   {quote}")
                
            elif hasattr(dhan, 'get_market_data'):
                data = dhan.get_market_data(
                    security_id=details['security_id'],
                    exchange_segment=details['exchange']
                )
                print(f"   ✅ Response received:")
                print(f"   {data}")
            else:
                print(f"   ℹ️ Quote method not available, checking other methods...")
                
        except Exception as e:
            print(f"   ⚠️ Error: {type(e).__name__}: {str(e)[:100]}")
    
    # ============================================================
    # CHECK HOLDINGS (Shows prices)
    # ============================================================
    print("\n" + "-"*80)
    print("CHECKING HOLDINGS (Current Positions with Prices)")
    print("-"*80)
    
    try:
        if hasattr(dhan, 'get_holdings'):
            holdings = dhan.get_holdings()
            print(f"\n✅ Holdings Response:")
            print(holdings)
        else:
            print("   ℹ️ get_holdings not available")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # ============================================================
    # CHECK ORDERS (Shows execution prices)
    # ============================================================
    print("\n" + "-"*80)
    print("CHECKING ORDERS (Shows Execution Prices)")
    print("-"*80)
    
    try:
        orders = dhan.get_orders()
        if orders:
            print(f"\n✅ Orders Response:")
            print(orders)
            
            # Parse if dict
            if isinstance(orders, dict):
                if 'data' in orders:
                    print(f"\nOrder Details:")
                    for item in orders['data'][:3]:  # First 3 orders
                        if isinstance(item, dict):
                            for key, val in item.items():
                                print(f"  {key}: {val}")
                        else:
                            print(f"  {item}")
        else:
            print("   No orders returned")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # ============================================================
    # CHECK POSITIONS (Shows current prices)
    # ============================================================
    print("\n" + "-"*80)
    print("CHECKING POSITIONS (Current Market Prices)")
    print("-"*80)
    
    try:
        positions = dhan.get_positions()
        if positions:
            print(f"\n✅ Positions Response:")
            print(positions)
            
            if isinstance(positions, dict) and 'data' in positions:
                data = positions['data']
                if data:
                    print(f"\nPosition Details:")
                    for pos in data[:3]:
                        if isinstance(pos, dict):
                            for key, val in pos.items():
                                print(f"  {key}: {val}")
        else:
            print("   No positions")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")

except ImportError:
    print("❌ dhanhq not installed")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("""
📝 NEXT STEP:

Please check the DHAN Trading App directly and provide:

1. NIFTY 50 Current Price
2. RELIANCE Current Price
3. TCS Current Price
4. Market Bid/Ask prices

Or tell me if you see the prices above in the API responses.

Once you provide the CORRECT PRICES, the system will:
✅ Update trade configurations
✅ Place orders at correct levels
✅ Set accurate stops and targets
✅ Execute real trades with real prices
""")
print("="*80 + "\n")
