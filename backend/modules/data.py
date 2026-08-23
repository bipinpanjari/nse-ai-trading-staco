"""
Data management module for SENSEX Options Trading Application
Handles options chain, pricing, and portfolio tracking
"""
import random
import math
from datetime import datetime, timedelta
from config import (
    UNDERLYING, SPOT_PRICE, VOLATILITY, RFR, DEMO_STRIKES,
    DEMO_EXPIRATIONS, PRICE_VOLATILITY, VOLUME_MULTIPLIER,
    MARKET_TIMEZONE, INITIAL_CAPITAL
)
from modules.logger import data_logger

class OptionsChain:
    """Generate and manage live options chain with pricing"""
    
    def __init__(self, spot_price=SPOT_PRICE):
        self.spot_price = spot_price
        self.chain = {}
        self.bid_ask_spread = 0.02  # 0.2% spread
        self.generate_chain()
    
    def black_scholes(self, S, K, T, r, sigma, option_type='CE'):
        """Calculate Black-Scholes option price"""
        if T <= 0:
            T = 0.001
        
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        N_d1 = 0.5 * (1 + math.erf(d1 / math.sqrt(2)))
        N_d2 = 0.5 * (1 + math.erf(d2 / math.sqrt(2)))
        N_neg_d1 = 1 - N_d1
        N_neg_d2 = 1 - N_d2
        
        if option_type == 'CE':  # Call
            price = S * N_d1 - K * math.exp(-r * T) * N_d2
        else:  # Put
            price = K * math.exp(-r * T) * N_neg_d2 - S * N_neg_d1
        
        return max(price, 0)
    
    def generate_chain(self):
        """Generate complete options chain"""
        self.chain = {}
        
        for expiry in DEMO_EXPIRATIONS:
            self.chain[expiry] = {}
            
            for strike in DEMO_STRIKES:
                T = int(expiry[0]) / 365.0  # Time to expiry in years
                
                # Calculate option prices
                call_price = self.black_scholes(
                    self.spot_price, strike, T, RFR, VOLATILITY, 'CE'
                )
                put_price = self.black_scholes(
                    self.spot_price, strike, T, RFR, VOLATILITY, 'PE'
                )
                
                # Add bid-ask spread
                call_bid = call_price * (1 - self.bid_ask_spread / 2)
                call_ask = call_price * (1 + self.bid_ask_spread / 2)
                put_bid = put_price * (1 - self.bid_ask_spread / 2)
                put_ask = put_price * (1 + self.bid_ask_spread / 2)
                
                # Base volume (higher ATM volume)
                atm_distance = abs(strike - self.spot_price)
                volume_decay = math.exp(-atm_distance / 5000)
                base_volume = int(10000 * volume_decay * VOLUME_MULTIPLIER)
                
                self.chain[expiry][strike] = {
                    'strike': strike,
                    'expiry': expiry,
                    'call': {
                        'ltp': call_price,
                        'bid': call_bid,
                        'ask': call_ask,
                        'bid_vol': max(1, base_volume // 2),
                        'ask_vol': max(1, base_volume // 2),
                        'iv': VOLATILITY,
                        'volume': base_volume,
                        'oi': base_volume * 50,
                    },
                    'put': {
                        'ltp': put_price,
                        'bid': put_bid,
                        'ask': put_ask,
                        'bid_vol': max(1, base_volume // 2),
                        'ask_vol': max(1, base_volume // 2),
                        'iv': VOLATILITY,
                        'volume': base_volume,
                        'oi': base_volume * 50,
                    }
                }
        
        data_logger.info(f"Options chain generated for spot: Rs.{self.spot_price:.2f}")
    
    def update_prices(self, spot_price):
        """Update all prices based on new spot price"""
        self.spot_price = spot_price
        self.generate_chain()
    
    def update_tick(self):
        """Update prices with random walk (single tick)"""
        # Random spot price movement
        price_change = self.spot_price * PRICE_VOLATILITY * random.uniform(-1, 1)
        self.spot_price = max(self.spot_price + price_change, 1)
        
        # Add small volume and OI fluctuations
        for expiry in self.chain:
            for strike in self.chain[expiry]:
                for option_type in ['call', 'put']:
                    option = self.chain[expiry][strike][option_type]
                    # Small price fluctuations
                    price_move = option['ltp'] * PRICE_VOLATILITY * random.uniform(-0.5, 0.5)
                    option['ltp'] = max(option['ltp'] + price_move, 0)
                    option['bid'] = option['ltp'] * (1 - self.bid_ask_spread / 2)
                    option['ask'] = option['ltp'] * (1 + self.bid_ask_spread / 2)
                    # Volume fluctuation
                    option['volume'] = int(option['volume'] * random.uniform(0.8, 1.2))
        
        return self.spot_price
    
    def get_atm_strike(self):
        """Get ATM strike closest to spot price"""
        return min(DEMO_STRIKES, key=lambda x: abs(x - self.spot_price))
    
    def get_chain_for_expiry(self, expiry):
        """Get all strikes for an expiry"""
        return self.chain.get(expiry, {})


class Portfolio:
    """Manage portfolio, positions, and P&L"""
    
    def __init__(self, initial_capital=INITIAL_CAPITAL):
        self.capital = initial_capital
        self.available_margin = initial_capital
        self.positions = {}  # {symbol: {qty, entry_price, entry_time}}
        self.trades_history = []
        self.pnl = 0
        self.daily_pnl = 0
        self.max_loss = initial_capital * 0.02  # 2% max loss
        data_logger.info(f"Portfolio initialized with capital: Rs.{initial_capital:.2f}")
    
    def add_position(self, symbol, qty, entry_price, option_type='CE'):
        """Add new position"""
        position_size = qty * entry_price
        
        if position_size > self.available_margin:
            data_logger.warning(f"Insufficient margin for {symbol}")
            return False
        
        symbol_key = f"{symbol}_{option_type}"
        
        if symbol_key in self.positions:
            pos = self.positions[symbol_key]
            avg_price = (pos['entry_price'] * pos['qty'] + entry_price * qty) / (pos['qty'] + qty)
            pos['qty'] += qty
            pos['entry_price'] = avg_price
        else:
            self.positions[symbol_key] = {
                'qty': qty,
                'entry_price': entry_price,
                'entry_time': datetime.now(MARKET_TIMEZONE),
                'symbol': symbol,
                'type': option_type,
                'sl': 0,
                'target': 0,
            }
        
        self.available_margin -= position_size
        data_logger.info(f"Position added: {symbol_key} | Qty: {qty} | Price: Rs.{entry_price:.2f}")
        return True
    
    def close_position(self, symbol, exit_price):
        """Close position and calculate P&L"""
        if symbol not in self.positions:
            return False
        
        pos = self.positions[symbol]
        qty = pos['qty']
        entry_price = pos['entry_price']
        
        trade_pnl = (exit_price - entry_price) * qty
        trade_return_percent = ((exit_price - entry_price) / entry_price) * 100
        
        self.pnl += trade_pnl
        self.daily_pnl += trade_pnl
        
        trade_record = {
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'qty': qty,
            'pnl': trade_pnl,
            'return_percent': trade_return_percent,
            'entry_time': pos['entry_time'],
            'exit_time': datetime.now(MARKET_TIMEZONE),
        }
        
        self.trades_history.append(trade_record)
        del self.positions[symbol]
        
        self.available_margin += (qty * exit_price)
        
        data_logger.info(
            f"Position closed: {symbol} | P&L: Rs.{trade_pnl:.2f} | Return: {trade_return_percent:.2f}%"
        )
        return True
    
    def get_unrealized_pnl(self, current_prices):
        """Calculate unrealized P&L for open positions"""
        unrealized = 0
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                unrealized += (current_price - pos['entry_price']) * pos['qty']
        return unrealized
    
    def get_portfolio_summary(self, current_prices=None):
        """Get complete portfolio summary"""
        unrealized = self.get_unrealized_pnl(current_prices or {})
        total_pnl = self.pnl + unrealized
        
        return {
            'capital': self.capital,
            'available_margin': self.available_margin,
            'open_positions': len(self.positions),
            'realized_pnl': self.pnl,
            'unrealized_pnl': unrealized,
            'total_pnl': total_pnl,
            'daily_pnl': self.daily_pnl,
            'return_percent': (total_pnl / self.capital) * 100,
            'positions': self.positions,
            'max_loss_limit': self.max_loss,
        }
    
    def check_stop_loss(self, current_prices):
        """Check if any position hit stop loss"""
        stopped_positions = []
        for symbol, pos in list(self.positions.items()):
            if symbol in current_prices and pos['sl'] > 0:
                if current_prices[symbol] <= pos['sl']:
                    stopped_positions.append(symbol)
        return stopped_positions
    
    def set_stop_loss(self, symbol, sl_price):
        """Set stop loss for position"""
        if symbol in self.positions:
            self.positions[symbol]['sl'] = sl_price
            data_logger.info(f"Stop loss set for {symbol}: Rs.{sl_price:.2f}")
            return True
        return False
    
    def set_target(self, symbol, target_price):
        """Set profit target for position"""
        if symbol in self.positions:
            self.positions[symbol]['target'] = target_price
            data_logger.info(f"Target set for {symbol}: Rs.{target_price:.2f}")
            return True
        return False
