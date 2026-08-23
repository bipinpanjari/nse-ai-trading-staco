"""
Pre-Market Intelligence & Morning Watchlist Engine
Executes pre-open analysis (8:30 AM - 9:15 AM)
Computes CPR, Camarilla Pivots, Gap Analysis, and generates high-probability morning watchlists.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

from modules.nse_live_feed import nse_live_feed
from modules.logger import app_logger

class PreMarketEngine:
    """
    Analyzes Indian Market Pre-Session:
    1. Global Macro Bias & Sentiment (Gift Nifty, US, Asia, Crude, DXY)
    2. FII / DII Flow Momentum
    3. CPR & Camarilla Pivot Calculations (Trending vs Sideways Day Forecast)
    4. Top High-Conviction Long & Short Intraday Watchlist with precise triggers
    """

    def __init__(self):
        self.watchlist_symbols = [
            "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
            "TATAMOTORS", "SBIN", "BAJFINANCE", "BHARTIARTL", "LT"
        ]

    def calculate_pivots(self, high: float, low: float, close: float) -> Dict[str, Any]:
        """
        Calculate Standard Pivots, Central Pivot Range (CPR), and Camarilla Levels
        """
        pivot = (high + low + close) / 3.0
        bc = (high + low) / 2.0
        tc = (pivot - bc) + pivot
        range_val = high - low

        # CPR Width Classification
        cpr_width = abs(tc - bc)
        cpr_width_pct = (cpr_width / pivot) * 100 if pivot else 0.0
        cpr_type = "NARROW (Trending Day Expected)" if cpr_width_pct < 0.3 else (
            "WIDE (Sideways / Range-Bound Expected)" if cpr_width_pct > 0.6 else "AVERAGE"
        )

        # Camarilla Pivots
        h4 = close + (range_val * 1.1 / 2.0)  # Breakout Buy
        h3 = close + (range_val * 1.1 / 4.0)  # Reversal Resistance
        l3 = close - (range_val * 1.1 / 4.0)  # Reversal Support
        l4 = close - (range_val * 1.1 / 2.0)  # Breakdown Sell

        # Traditional Supports & Resistances
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)

        return {
            "pivot": round(pivot, 2),
            "tc": round(tc, 2),
            "bc": round(bc, 2),
            "cpr_width_pct": round(cpr_width_pct, 3),
            "cpr_type": cpr_type,
            "camarilla": {
                "h4_breakout_buy": round(h4, 2),
                "h3_resistance": round(h3, 2),
                "l3_support": round(l3, 2),
                "l4_breakdown_sell": round(l4, 2)
            },
            "levels": {
                "r1": round(r1, 2),
                "r2": round(r2, 2),
                "s1": round(s1, 2),
                "s2": round(s2, 2)
            }
        }

    def analyze_market_prediction(self) -> Dict[str, Any]:
        """
        Predict market opening direction & trend bias
        """
        global_data = nse_live_feed.get_global_cues()
        fii_dii = nse_live_feed.get_fii_dii_data()

        macro_score = global_data.get("macro_score", 0)
        fii_flow = fii_dii.get("fii_net_crores", 0)
        dii_flow = fii_dii.get("dii_net_crores", 0)

        total_score = macro_score
        reasons = []

        if macro_score > 20:
            reasons.append(f"Global cues positive (Macro Score: +{macro_score})")
        elif macro_score < -20:
            reasons.append(f"Global cues weak/negative (Macro Score: {macro_score})")
        else:
            reasons.append("Global cues mixed/neutral")

        if fii_flow > 0:
            total_score += 20
            reasons.append(f"FII Net Buyers (+₹{fii_flow:.1f} Cr)")
        else:
            total_score -= 20
            reasons.append(f"FII Net Sellers (₹{fii_flow:.1f} Cr)")

        if dii_flow > 0:
            total_score += 15
            reasons.append(f"DII Domestic Support (+₹{dii_flow:.1f} Cr)")

        # Index Nifty Pivot Analysis
        nifty_df = nse_live_feed.get_realtime_candles("NIFTY", interval="1d", period="10d")
        nifty_pivots = {}
        if not nifty_df.empty and len(nifty_df) >= 2:
            prev_row = nifty_df.iloc[-2]
            nifty_pivots = self.calculate_pivots(
                float(prev_row['high']), float(prev_row['low']), float(prev_row['close'])
            )

        if total_score >= 25:
            bias = "🟢 BULLISH OPEN"
            action = "Buy on Dips above CPR / Trade H4 Breakouts"
        elif total_score <= -25:
            bias = "🔴 BEARISH OPEN"
            action = "Sell on Rallies below CPR / Trade L4 Breakdowns"
        else:
            bias = "🟡 RANGE-BOUND OPEN"
            action = "Trade between H3 and L3 Camarilla Reversals"

        return {
            "prediction": bias,
            "confidence_score": min(100, max(10, int(abs(total_score) * 1.2))),
            "recommended_action": action,
            "reasons": reasons,
            "global_cues": global_data.get("cues", {}),
            "fii_dii": fii_dii,
            "nifty_pivots": nifty_pivots,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_morning_watchlist(self) -> List[Dict[str, Any]]:
        """
        Generate high-probability pre-market stock setups with exact Entry, SL, and Target
        """
        watchlist = []
        for symbol in self.watchlist_symbols:
            try:
                df = nse_live_feed.get_realtime_candles(symbol, interval="1d", period="10d")
                if df.empty or len(df) < 2:
                    continue

                prev_day = df.iloc[-2]
                curr_price = float(df.iloc[-1]['close'])
                high = float(prev_day['high'])
                low = float(prev_day['low'])
                close = float(prev_day['close'])

                pivots = self.calculate_pivots(high, low, close)
                h4 = pivots['camarilla']['h4_breakout_buy']
                l4 = pivots['camarilla']['l4_breakdown_sell']

                # Bias determination
                if curr_price >= pivots['pivot']:
                    direction = "LONG"
                    entry = round(max(curr_price, h4), 2)
                    sl = round(entry * 0.992, 2)  # 0.8% risk
                    risk = entry - sl
                    tp1 = round(entry + (risk * 1.5), 2)
                    tp2 = round(entry + (risk * 2.5), 2)
                    thesis = f"Bullish above Pivot (₹{pivots['pivot']}). Trigger above H4 (₹{h4})."
                else:
                    direction = "SHORT"
                    entry = round(min(curr_price, l4), 2)
                    sl = round(entry * 1.008, 2)  # 0.8% risk
                    risk = sl - entry
                    tp1 = round(entry - (risk * 1.5), 2)
                    tp2 = round(entry - (risk * 2.5), 2)
                    thesis = f"Bearish below Pivot (₹{pivots['pivot']}). Trigger below L4 (₹{l4})."

                watchlist.append({
                    "symbol": symbol,
                    "direction": direction,
                    "cmp": round(curr_price, 2),
                    "entry_trigger": entry,
                    "stop_loss": sl,
                    "target_1": tp1,
                    "target_2": tp2,
                    "risk_reward": "1:2.0",
                    "cpr_type": pivots['cpr_type'],
                    "thesis": thesis,
                    "pivots": pivots
                })
            except Exception as e:
                app_logger.warning(f"Error generating watchlist for {symbol}: {e}")

        return watchlist

# Singleton instance
pre_market_engine = PreMarketEngine()
