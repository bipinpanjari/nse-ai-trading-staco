import os
from dhanhq import dhanhq
from modules.trading import RiskManager
from modules.alerts import TelegramAlerts
from config import BROKER_API, MAX_LOSS_PERCENT

class TradeExecutor:
    """Execute trades automatically on Dhan API"""
    
    def __init__(self):
        client_id = os.getenv('DHAN_CLIENT_ID') or BROKER_API['DHAN']['client_id']
        access_token = os.getenv('DHAN_ACCESS_TOKEN') or BROKER_API['DHAN']['access_token']
        
        self.dhan = dhanhq(client_id, access_token)
        self.risk_manager = RiskManager(initial_capital=100000) # Default capital
        self.alerts = TelegramAlerts()
        self.active_positions = {}

    def place_order(self, symbol, transaction_type, quantity, price=None, order_type="MARKET"):
        """Place an order and set up risk management"""
        try:
            # Place order on Dhan
            order = self.dhan.place_order(
                security_id=symbol, # This should be Dhan security ID
                exchange_segment=self.dhan.NSE_FNO,
                transaction_type=transaction_type,
                quantity=quantity,
                order_type=self.dhan.MARKET if order_type == "MARKET" else self.dhan.LIMIT,
                product_type=self.dhan.INTRA,
                price=price if price else 0
            )
            
            if order.get('status') == 'success':
                order_id = order.get('data', {}).get('orderId')
                entry_price = price or self.get_ltp(symbol)
                
                # Setup SL and Target
                sl_price = self.risk_manager.calculate_stop_loss(entry_price, MAX_LOSS_PERCENT)
                target_price = self.risk_manager.calculate_target(entry_price)
                
                self.active_positions[symbol] = {
                    'order_id': order_id,
                    'qty': quantity,
                    'entry': entry_price,
                    'sl': sl_price,
                    'target': target_price,
                    'type': transaction_type
                }
                
                self.alerts.alert_trade(transaction_type, symbol, entry_price, sl_price, target_price)
                return True
            else:
                print(f"❌ Order failed: {order}")
                return False
                
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return False

    def get_ltp(self, symbol):
        """Get Last Traded Price"""
        # In real scenario, use dhan.get_quote() or similar
        return 0 # Placeholder

    def monitor_positions(self):
        """Check active positions for SL/Target/Trailing SL"""
        to_close = []
        for symbol, data in self.active_positions.items():
            current_price = self.get_ltp(symbol)
            if current_price == 0: continue
            
            # Check Trailing SL
            new_sl = self.risk_manager.calculate_trailing_stop(symbol, current_price)
            if new_sl > data['sl']:
                data['sl'] = new_sl
                print(f"📈 Trailing SL updated for {symbol} to {new_sl}")
            
            # Check Exit Conditions
            if (data['type'] == 'BUY' and current_price <= data['sl']) or \
               (data['type'] == 'SELL' and current_price >= data['sl']):
                print(f"🛑 SL Hit for {symbol} at {current_price}")
                to_close.append(symbol)
                
            elif (data['type'] == 'BUY' and current_price >= data['target']) or \
                 (data['type'] == 'SELL' and current_price <= data['target']):
                print(f"🎯 Target Hit for {symbol} at {current_price}")
                to_close.append(symbol)
                
        for symbol in to_close:
            self.close_position(symbol)

    def close_position(self, symbol):
        """Close an open position"""
        data = self.active_positions.get(symbol)
        if not data: return
        
        # Place opposite order to close
        close_type = 'SELL' if data['type'] == 'BUY' else 'BUY'
        self.place_order(symbol, close_type, data['qty'], order_type="MARKET")
        
        self.alerts.send_message(f"✅ Position Closed for {symbol} at LTP")
        del self.active_positions[symbol]
