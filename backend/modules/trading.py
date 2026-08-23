"""
Trading logic module for SENSEX Options Trading Application
Handles reversal patterns, risk management, and order execution
"""
import math
import numpy as np
from collections import deque
from datetime import datetime
from config import (
    RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD, MACD_FAST, MACD_SLOW,
    MACD_SIGNAL, MAX_LOSS_PERCENT, BROKERAGE_PERCENT, SLIPPAGE_PERCENT
)
from modules.logger import trading_logger

class TechnicalAnalyzer:
    """Calculate technical indicators for reversal pattern detection"""
    
    def __init__(self, period=50):
        self.prices = deque(maxlen=period)
        self.rsi_values = deque(maxlen=period)
        self.macd_values = deque(maxlen=period)
        self.signal_line = deque(maxlen=period)
    
    def add_price(self, price):
        """Add price to analysis"""
        self.prices.append(price)
    
    def calculate_rsi(self):
        """Calculate Relative Strength Index"""
        if len(self.prices) < RSI_PERIOD:
            return None
        
        deltas = np.diff(list(self.prices)[-RSI_PERIOD:])
        seed = deltas[:1]
        up = seed[seed >= 0].sum() / RSI_PERIOD
        down = -seed[seed < 0].sum() / RSI_PERIOD
        
        rs = np.zeros_like(deltas)
        rs[:] = 100.
        
        for i in range(1, len(deltas)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up * (RSI_PERIOD - 1) + upval) / RSI_PERIOD
            down = (down * (RSI_PERIOD - 1) + downval) / RSI_PERIOD
            rs[i] = 100. - 100. / (1. + up / down)
        
        rsi = rs[-1]
        self.rsi_values.append(rsi)
        return rsi
    
    def calculate_macd(self):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(self.prices) < MACD_SLOW:
            return None, None, None
        
        prices = np.array(list(self.prices))
        
        # Calculate EMAs
        ema_fast = self._ema(prices, MACD_FAST)
        ema_slow = self._ema(prices, MACD_SLOW)
        
        macd = ema_fast - ema_slow
        signal = self._ema(np.array([macd]), MACD_SIGNAL)[0] if len([macd]) > 0 else macd
        histogram = macd - signal
        
        self.macd_values.append(macd)
        self.signal_line.append(signal)
        
        return macd, signal, histogram
    
    def _ema(self, data, period):
        """Calculate Exponential Moving Average"""
        if len(data) == 0:
            return np.array([])
        
        ema = np.zeros(len(data))
        multiplier = 2.0 / (period + 1)
        
        ema[0] = data[0]
        for i in range(1, len(data)):
            ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def is_oversold(self):
        """Check if RSI indicates oversold condition"""
        rsi = self.calculate_rsi()
        return rsi is not None and rsi < RSI_OVERSOLD
    
    def is_overbought(self):
        """Check if RSI indicates overbought condition"""
        rsi = self.calculate_rsi()
        return rsi is not None and rsi > RSI_OVERBOUGHT
    
    def detect_reversal(self):
        """Detect potential reversal patterns"""
        rsi = self.calculate_rsi()
        macd, signal, histogram = self.calculate_macd()
        
        if rsi is None or macd is None:
            return None
        
        reversals = []
        
        # Oversold + MACD bullish crossover = BUY signal
        if self.is_oversold() and histogram is not None and histogram > 0:
            reversals.append({
                'signal': 'BUY',
                'pattern': 'Oversold Reversal',
                'strength': min(rsi, 50),  # Stronger near RSI 30
                'rsi': rsi,
                'macd': macd,
            })
        
        # Overbought + MACD bearish crossover = SELL signal
        if self.is_overbought() and histogram is not None and histogram < 0:
            reversals.append({
                'signal': 'SELL',
                'pattern': 'Overbought Reversal',
                'strength': 100 - rsi,
                'rsi': rsi,
                'macd': macd,
            })
        
        return reversals if reversals else None
    
    def get_support_resistance(self):
        """Identify support and resistance levels"""
        if len(self.prices) < 10:
            return None, None
        
        prices = list(self.prices)
        support = min(prices)
        resistance = max(prices)
        
        return support, resistance


class RiskManager:
    """Manage risk with stop loss, position sizing, and limits"""
    
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.max_loss = initial_capital * (MAX_LOSS_PERCENT / 100)
        self.current_loss = 0
        self.position_size_limit = initial_capital * 0.1  # 10% per position
        self.positions_meta = {}  # Track highest prices for trailing SL
    
    def track_price(self, position_id, current_price):
        """Track price for trailing stop loss"""
        if position_id not in self.positions_meta:
            self.positions_meta[position_id] = {
                'highest_price': current_price,
                'entry_price': current_price
            }
        else:
            self.positions_meta[position_id]['highest_price'] = max(
                self.positions_meta[position_id]['highest_price'], 
                current_price
            )
        return self.positions_meta[position_id]['highest_price']

    def calculate_position_size(self, entry_price, stop_loss_price):
        """Calculate position size based on risk"""
        if entry_price == stop_loss_price:
            return 0
        
        risk_per_share = abs(entry_price - stop_loss_price)
        position_size = self.max_loss / risk_per_share if risk_per_share > 0 else 0
        
        # Limit position size
        max_qty = int(self.position_size_limit / entry_price)
        position_size = min(position_size, max_qty)
        
        return int(position_size)
    
    def calculate_stop_loss(self, entry_price, loss_percent=2):
        """Calculate stop loss price"""
        sl = entry_price * (1 - loss_percent / 100)
        return round(sl, 2)
    
    def calculate_trailing_stop(self, position_id, current_price, trail_percent=1):
        """Calculate trailing stop loss based on highest price reached"""
        highest_price = self.track_price(position_id, current_price)
        entry_price = self.positions_meta[position_id]['entry_price']

        if current_price < entry_price:
            # In loss, initial SL applies
            return entry_price * (1 - 2 / 100)
        
        # In profit, set stop at trail_percent% below highest price
        trailing_sl = highest_price * (1 - trail_percent / 100)
        initial_sl = entry_price * (1 - 2 / 100)
        
        return max(trailing_sl, initial_sl)
    
    def calculate_target(self, entry_price, risk_reward_ratio=1.5):
        """Calculate profit target based on risk"""
        stop_loss = self.calculate_stop_loss(entry_price, 2)
        risk = entry_price - stop_loss
        target = entry_price + (risk * risk_reward_ratio)
        return round(target, 2)
    
    def check_risk_limit(self, current_loss):
        """Check if loss exceeded maximum allowed"""
        self.current_loss = current_loss
        return current_loss <= self.max_loss
    
    def is_max_loss_exceeded(self):
        """Check if max loss limit is exceeded"""
        return self.current_loss > self.max_loss


class OrderExecutor:
    """Execute trades with realistic slippage and brokerage"""
    
    def __init__(self):
        self.orders_history = []
    
    def execute_buy_order(self, symbol, quantity, price):
        """Execute buy order with slippage"""
        slippage = price * SLIPPAGE_PERCENT
        execution_price = price + slippage
        brokerage = execution_price * quantity * BROKERAGE_PERCENT
        total_cost = (execution_price * quantity) + brokerage
        
        order = {
            'symbol': symbol,
            'type': 'BUY',
            'quantity': quantity,
            'order_price': price,
            'execution_price': execution_price,
            'brokerage': brokerage,
            'total_cost': total_cost,
            'timestamp': datetime.now(),
        }
        
        self.orders_history.append(order)
        trading_logger.info(
            f"BUY Order: {symbol} | Qty: {quantity} | Price: ₹{execution_price:.2f} | "
            f"Brokerage: ₹{brokerage:.2f}"
        )
        
        return order
    
    def execute_sell_order(self, symbol, quantity, price):
        """Execute sell order with slippage"""
        slippage = price * SLIPPAGE_PERCENT
        execution_price = price - slippage
        brokerage = execution_price * quantity * BROKERAGE_PERCENT
        total_proceeds = (execution_price * quantity) - brokerage
        
        order = {
            'symbol': symbol,
            'type': 'SELL',
            'quantity': quantity,
            'order_price': price,
            'execution_price': execution_price,
            'brokerage': brokerage,
            'total_proceeds': total_proceeds,
            'timestamp': datetime.now(),
        }
        
        self.orders_history.append(order)
        trading_logger.info(
            f"SELL Order: {symbol} | Qty: {quantity} | Price: ₹{execution_price:.2f} | "
            f"Brokerage: ₹{brokerage:.2f}"
        )
        
        return order
    
    def get_orders_history(self):
        """Get all executed orders"""
        return self.orders_history


class TradingEngine:
    """Main trading engine combining all components"""
    
    def __init__(self, initial_capital):
        self.analyzer = TechnicalAnalyzer()
        self.risk_manager = RiskManager(initial_capital)
        self.executor = OrderExecutor()
        self.active_signals = []
    
    def process_market_data(self, price):
        """Process market data and detect signals"""
        self.analyzer.add_price(price)
        
        reversals = self.analyzer.detect_reversal()
        if reversals:
            self.active_signals = reversals
            for reversal in reversals:
                trading_logger.info(f"Signal detected: {reversal}")
        
        return self.active_signals
    
    def get_trade_recommendation(self, entry_price):
        """Get complete trade setup recommendation"""
        if not self.active_signals:
            return None
        
        signal = self.active_signals[0]
        stop_loss = self.risk_manager.calculate_stop_loss(entry_price, 2)
        target = self.risk_manager.calculate_target(entry_price, 1.5)
        position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss)
        
        return {
            'signal': signal['signal'],
            'entry': entry_price,
            'stop_loss': stop_loss,
            'target': target,
            'position_size': position_size,
            'pattern': signal.get('pattern', ''),
            'risk_reward': (target - entry_price) / (entry_price - stop_loss) if entry_price != stop_loss else 0,
        }
