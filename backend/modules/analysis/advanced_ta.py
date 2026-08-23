"""
Enhanced Technical Analysis Engine
High-performance pure NumPy/Pandas calculations for Institutional Indicators:
- SuperTrend (7, 3)
- VWAP (Volume Weighted Average Price)
- EMA Ribbon (9, 21, 50, 200)
- RSI (14)
- ATR (14)
- Fair Value Gap (FVG)
- Market Regime Analysis
"""

import numpy as np
import pandas as pd

class AdvancedTechnicalEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def calculate_ema(self, series: pd.Series, length: int) -> pd.Series:
        """Calculate Exponential Moving Average (EMA)"""
        return series.ewm(span=length, adjust=False).mean()

    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR)"""
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=length, min_periods=1).mean()

    def calculate_rsi(self, close: pd.Series, length: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)"""
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        avg_gain = gain.rolling(window=length, min_periods=1).mean()
        avg_loss = loss.rolling(window=length, min_periods=1).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def calculate_vwap(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Volume Weighted Average Price (VWAP)"""
        typical_price = (high + low + close) / 3.0
        vol = volume.replace(0, 1.0)
        cum_tp_vol = (typical_price * vol).cumsum()
        cum_vol = vol.cumsum()
        return cum_tp_vol / cum_vol

    def calculate_supertrend(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                             period: int = 7, multiplier: float = 3.0):
        """
        Calculate SuperTrend (Period=7, Multiplier=3.0)
        Returns: direction series (1 = Buy/Green, -1 = Sell/Red), trend line series
        """
        atr = self.calculate_atr(high, low, close, length=period)
        hl2 = (high + low) / 2.0
        
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        n = len(close)
        supertrend = np.zeros(n)
        direction = np.zeros(n)
        
        if n == 0:
            return pd.Series([], dtype=float), pd.Series([], dtype=float)

        supertrend[0] = upper_band.iloc[0]
        direction[0] = 1

        for i in range(1, n):
            c = close.iloc[i]
            prev_c = close.iloc[i-1]
            prev_st = supertrend[i-1]
            prev_dir = direction[i-1]
            
            curr_ub = upper_band.iloc[i]
            curr_lb = lower_band.iloc[i]
            
            if prev_dir == 1:
                # In uptrend
                if c < lower_band.iloc[i]:
                    direction[i] = -1
                    supertrend[i] = curr_ub
                else:
                    direction[i] = 1
                    supertrend[i] = max(curr_lb, prev_st)
            else:
                # In downtrend
                if c > upper_band.iloc[i]:
                    direction[i] = 1
                    supertrend[i] = curr_lb
                else:
                    direction[i] = -1
                    supertrend[i] = min(curr_ub, prev_st)

        return pd.Series(direction, index=close.index), pd.Series(supertrend, index=close.index)

    def apply_indicators(self) -> pd.DataFrame:
        """Add institutional-grade indicators to dataframe"""
        try:
            high = self.df['high']
            low = self.df['low']
            close = self.df['close']
            volume = self.df.get('volume', pd.Series(1000, index=close.index))

            # EMAs
            self.df['EMA_9'] = self.calculate_ema(close, 9)
            self.df['EMA_21'] = self.calculate_ema(close, 21)
            self.df['EMA_50'] = self.calculate_ema(close, 50)
            self.df['EMA_200'] = self.calculate_ema(close, 200)

            # RSI & ATR
            self.df['RSI_14'] = self.calculate_rsi(close, 14)
            self.df['ATR_14'] = self.calculate_atr(high, low, close, 14)

            # VWAP
            self.df['VWAP_D'] = self.calculate_vwap(high, low, close, volume)

            # SuperTrend
            dir_st, val_st = self.calculate_supertrend(high, low, close, period=7, multiplier=3.0)
            self.df['SUPERT_7_3.0'] = dir_st
            self.df['SUPERTd_7_3.0'] = val_st

        except Exception as e:
            print(f"Indicator calculation error: {e}")

        return self.df

    def get_fvg(self):
        """Fair Value Gap (FVG) Validation"""
        if len(self.df) < 3:
            return None
        
        c1, c2, c3 = self.df.iloc[-3], self.df.iloc[-2], self.df.iloc[-1]
        if c1['high'] < c3['low']:
            return {"type": "BULLISH", "gap": round(c3['low'] - c1['high'], 2), "level": round((c1['high'] + c3['low'])/2, 2)}
        if c1['low'] > c3['high']:
            return {"type": "BEARISH", "gap": round(c1['low'] - c3['high'], 2), "level": round((c1['low'] + c3['high'])/2, 2)}
        return None

    def get_levels(self):
        """Prepare Support / Resistance / Breakouts"""
        window = min(20, len(self.df))
        rolling_max = self.df['high'].rolling(window=window).max().iloc[-1]
        rolling_min = self.df['low'].rolling(window=window).min().iloc[-1]
        last_close = self.df['close'].iloc[-1]

        return {
            "resistance": round(float(rolling_max), 2),
            "support": round(float(rolling_min), 2),
            "breakout": bool(last_close >= rolling_max),
            "breakdown": bool(last_close <= rolling_min)
        }

    def get_market_regime(self) -> str:
        """Determine Market Regime (Strong Bullish, Strong Bearish, Sideways)"""
        if self.df is None or len(self.df) < 20:
            return "SIDEWAYS"
            
        last = self.df.iloc[-1]
        close = float(last['close'])
        ema200 = float(last.get('EMA_200', close))
        supertrend = float(last.get('SUPERT_7_3.0', 0))

        if close >= ema200 and supertrend == 1:
            return "STRONG_BULLISH"
        elif close <= ema200 and supertrend == -1:
            return "STRONG_BEARISH"
        else:
            return "SIDEWAYS"
