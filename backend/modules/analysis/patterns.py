import pandas as pd

class CandlestickPatternEngine:
    """
    Detects high-probability candlestick patterns for NSE stocks.
    """
    def __init__(self, df):
        self.df = df

    def detect_hammer(self, i):
        """Bullish Reversal Pattern"""
        row = self.df.iloc[i]
        body = abs(row['close'] - row['open'])
        lower_wick = min(row['close'], row['open']) - row['low']
        upper_wick = row['high'] - max(row['close'], row['open'])
        
        # Hammer criteria: Lower wick > 2x body, tiny upper wick
        return lower_wick > (2 * body) and upper_wick < (0.1 * body)

    def detect_shooting_star(self, i):
        """Bearish Reversal Pattern"""
        row = self.df.iloc[i]
        body = abs(row['close'] - row['open'])
        lower_wick = min(row['close'], row['open']) - row['low']
        upper_wick = row['high'] - max(row['close'], row['open'])
        
        return upper_wick > (2 * body) and lower_wick < (0.1 * body)

    def scan(self):
        """Scan recent candles for patterns"""
        patterns = []
        # Check last 3 candles
        for i in range(len(self.df)-1, len(self.df)-4, -1):
            if self.detect_hammer(i):
                patterns.append({"candle": i, "pattern": "HAMMER", "type": "BULLISH"})
            if self.detect_shooting_star(i):
                patterns.append({"candle": i, "pattern": "SHOOTING_STAR", "type": "BEARISH"})
        return patterns
