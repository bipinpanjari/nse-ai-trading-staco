import pandas as pd
import numpy as np
from modules.patterns import PatternDetector

class MarketScreener:
    """Scan market instruments for specific setups"""
    
    def __init__(self, data_provider):
        self.data_provider = data_provider
        
    def scan_for_breakouts(self, symbols):
        """Scan a list of symbols for volatility breakouts"""
        shortlisted = []
        for symbol in symbols:
            # Fetch historical data (e.g., daily or hourly)
            df = self.data_provider.get_historical_data(symbol)
            if df.empty:
                continue
                
            # Volume condition (Volume > 2x Average)
            avg_volume = df['volume'].tail(20).mean()
            last_volume = df['volume'].iloc[-1]
            
            # RSI condition
            last_rsi = self.calculate_rsi(df['close'])
            
            if last_volume > (avg_volume * 2) and last_rsi < 30:
                shortlisted.append({
                    'symbol': symbol,
                    'last_price': df['close'].iloc[-1],
                    'rsi': last_rsi,
                    'volume_surge': last_volume / avg_volume,
                    'strategy': 'Volume-RSI Breakout'
                })
        return shortlisted

    def scan_orb(self, symbols, timeframe_mins=15):
        """Scan for Opening Range Breakout (ORB)"""
        orb_signals = []
        for symbol in symbols:
            # Fetch 1-min data for the morning session
            df = self.data_provider.get_intraday_data(symbol, "9:15", "9:45")
            if df.empty or len(df) < timeframe_mins:
                continue
            
            # Opening Range High/Low
            opening_range = df.head(timeframe_mins)
            range_high = opening_range['high'].max()
            range_low = opening_range['low'].min()
            
            # Current price
            current_price = self.data_provider.get_ltp(symbol)
            
            if current_price > range_high:
                orb_signals.append({
                    'symbol': symbol,
                    'signal': 'BUY',
                    'price': current_price,
                    'range_high': range_high,
                    'range_low': range_low,
                    'strategy': 'ORB'
                })
            elif current_price < range_low:
                orb_signals.append({
                    'symbol': symbol,
                    'signal': 'SELL',
                    'price': current_price,
                    'range_high': range_high,
                    'range_low': range_low,
                    'strategy': 'ORB'
                })
        return orb_signals

    def scan_high_probability_patterns(self, symbols):
        """Scan for H&S, Double Bottom, etc. (80%+ Accuracy)"""
        top_setups = []
        for symbol in symbols:
            df = self.data_provider.get_historical_data(symbol) # Assumes 15m or 1h candles
            if df.empty: continue
            
            detector = PatternDetector(df)
            setup = detector.get_highest_probability_setup()
            
            if setup:
                setup['symbol'] = symbol
                top_setups.append(setup)
        return top_setups

    def calculate_rsi(self, prices, period=14):
        """Standard RSI calculation"""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)
        
        for i in range(period, len(prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down if down != 0 else 0
            rsi[i] = 100. - 100. / (1. + rs)
            
        return rsi[-1]
