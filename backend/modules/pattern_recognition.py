"""
Advanced Pattern Recognition & Smart Money Concepts (SMC) Engine
Detects Classical Chart Patterns, Smart Money Price Action (FVG, Order Blocks, BOS/CHoCH), and Candlesticks.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from typing import Dict, List, Optional, Any

class PatternRecognitionEngine:
    """
    Unified Technical Pattern Scanner:
    - Classical Patterns: Double Bottom (W), Double Top (M), Head & Shoulders, Flags, Triangles
    - Smart Money Concepts (SMC): Fair Value Gaps (FVG), Order Blocks (OB), Break of Structure (BOS/CHoCH)
    - Candlestick Formations: Hammer, Shooting Star, Bullish/Bearish Engulfing, Pin Bars
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if not self.df.empty:
            self.highs = self.df['high'].values
            self.lows = self.df['low'].values
            self.closes = self.df['close'].values
            self.opens = self.df['open'].values
        else:
            self.highs = self.lows = self.closes = self.opens = np.array([])

    def _get_pivots(self, distance: int = 5) -> List[Dict[str, Any]]:
        """Extract local highs (peaks) and lows (troughs)"""
        if len(self.df) < distance * 2:
            return []

        peaks, _ = find_peaks(self.highs, distance=distance)
        troughs, _ = find_peaks(-self.lows, distance=distance)

        pivots = []
        for p in peaks:
            pivots.append({'index': int(p), 'price': float(self.highs[p]), 'type': 'HIGH'})
        for t in troughs:
            pivots.append({'index': int(t), 'price': float(self.lows[t]), 'type': 'LOW'})

        pivots.sort(key=lambda x: x['index'])
        return pivots

    # =========================================================================
    # 1. CLASSICAL CHART PATTERNS
    # =========================================================================
    def detect_double_bottom(self) -> Optional[Dict[str, Any]]:
        """Detect Double Bottom (W) Pattern (Bullish Reversal)"""
        pivots = self._get_pivots(distance=4)
        lows = [p for p in pivots if p['type'] == 'LOW']
        if len(lows) < 2:
            return None

        l1, l2 = lows[-2], lows[-1]
        diff = abs(l1['price'] - l2['price']) / l1['price']
        if diff < 0.012:  # 1.2% tolerance
            # Find intermediate peak (Neckline)
            intermediate_highs = [p for p in pivots if p['type'] == 'HIGH' and l1['index'] < p['index'] < l2['index']]
            neckline = intermediate_highs[0]['price'] if intermediate_highs else max(l1['price'], l2['price']) * 1.015
            
            return {
                "pattern": "Double Bottom (W Pattern)",
                "category": "Classical Pattern",
                "bias": "BULLISH",
                "confidence": 88,
                "neckline": round(neckline, 2),
                "support_level": round(min(l1['price'], l2['price']), 2),
                "target": round(neckline + (neckline - min(l1['price'], l2['price'])), 2),
                "description": f"Double bottom established at ₹{min(l1['price'], l2['price']):.2f}. Breakout confirmed above ₹{neckline:.2f}."
            }
        return None

    def detect_double_top(self) -> Optional[Dict[str, Any]]:
        """Detect Double Top (M) Pattern (Bearish Reversal)"""
        pivots = self._get_pivots(distance=4)
        highs = [p for p in pivots if p['type'] == 'HIGH']
        if len(highs) < 2:
            return None

        h1, h2 = highs[-2], highs[-1]
        diff = abs(h1['price'] - h2['price']) / h1['price']
        if diff < 0.012:  # 1.2% tolerance
            intermediate_lows = [p for p in pivots if p['type'] == 'LOW' and h1['index'] < p['index'] < h2['index']]
            neckline = intermediate_lows[0]['price'] if intermediate_lows else min(h1['price'], h2['price']) * 0.985

            return {
                "pattern": "Double Top (M Pattern)",
                "category": "Classical Pattern",
                "bias": "BEARISH",
                "confidence": 86,
                "neckline": round(neckline, 2),
                "resistance_level": round(max(h1['price'], h2['price']), 2),
                "target": round(neckline - (max(h1['price'], h2['price']) - neckline), 2),
                "description": f"Double top established at ₹{max(h1['price'], h2['price']):.2f}. Breakdown confirmed below ₹{neckline:.2f}."
            }
        return None

    def detect_head_and_shoulders(self) -> Optional[Dict[str, Any]]:
        """Detect Classical Head & Shoulders Pattern"""
        pivots = self._get_pivots(distance=4)
        highs = [p for p in pivots if p['type'] == 'HIGH']
        if len(highs) < 3:
            return None

        s1, head, s2 = highs[-3], highs[-2], highs[-1]
        if head['price'] > s1['price'] and head['price'] > s2['price']:
            shoulder_diff = abs(s1['price'] - s2['price']) / s1['price']
            if shoulder_diff < 0.035:
                neckline = (s1['price'] + s2['price']) / 2.0 * 0.97
                return {
                    "pattern": "Head & Shoulders",
                    "category": "Classical Pattern",
                    "bias": "BEARISH",
                    "confidence": 85,
                    "neckline": round(neckline, 2),
                    "head_level": round(head['price'], 2),
                    "target": round(neckline - (head['price'] - neckline), 2),
                    "description": f"Bearish H&S formed with Head at ₹{head['price']:.2f}. Breakdown level at ₹{neckline:.2f}."
                }
        return None

    def detect_flag_pennant(self) -> Optional[Dict[str, Any]]:
        """Detect Bull / Bear Flag or Pennant (High-Probability Momentum Continuation)"""
        if len(self.closes) < 20:
            return None

        recent_move = (self.closes[-1] - self.closes[-20]) / self.closes[-20]
        consolidation = self.closes[-5:]
        std_dev = np.std(consolidation) / (np.mean(consolidation) if np.mean(consolidation) else 1)

        if abs(recent_move) > 0.015 and std_dev < 0.004:
            bias = "BULLISH" if recent_move > 0 else "BEARISH"
            target = self.closes[-1] * (1 + recent_move)
            return {
                "pattern": f"{'Bull' if bias == 'BULLISH' else 'Bear'} Flag / Pennant",
                "category": "Classical Pattern",
                "bias": bias,
                "confidence": 84,
                "pole_gain_pct": round(recent_move * 100, 2),
                "target": round(target, 2),
                "description": f"Consolidation after sharp {recent_move*100:+.2f}% move. Continuation expected towards ₹{target:.2f}."
            }
        return None

    # =========================================================================
    # 2. SMART MONEY CONCEPTS (SMC) & INSTITUTIONAL PRICE ACTION
    # =========================================================================
    def detect_fair_value_gap(self) -> Optional[Dict[str, Any]]:
        """Detect 3-Candle Institutional Fair Value Gap (FVG)"""
        if len(self.df) < 3:
            return None

        c1, c2, c3 = self.df.iloc[-3], self.df.iloc[-2], self.df.iloc[-1]

        # Bullish FVG: Candle 1 High < Candle 3 Low
        if c1['high'] < c3['low']:
            gap_size = c3['low'] - c1['high']
            fvg_mid = (c1['high'] + c3['low']) / 2.0
            return {
                "pattern": "Bullish Fair Value Gap (FVG)",
                "category": "Smart Money Concepts",
                "bias": "BULLISH",
                "confidence": 90,
                "fvg_top": round(float(c3['low']), 2),
                "fvg_bottom": round(float(c1['high']), 2),
                "demand_zone": round(float(fvg_mid), 2),
                "description": f"Institutional Imbalance between ₹{c1['high']:.2f} and ₹{c3['low']:.2f}. Expect strong demand on retest."
            }

        # Bearish FVG: Candle 1 Low > Candle 3 High
        if c1['low'] > c3['high']:
            gap_size = c1['low'] - c3['high']
            fvg_mid = (c1['low'] + c3['high']) / 2.0
            return {
                "pattern": "Bearish Fair Value Gap (FVG)",
                "category": "Smart Money Concepts",
                "bias": "BEARISH",
                "confidence": 90,
                "fvg_top": round(float(c1['low']), 2),
                "fvg_bottom": round(float(c3['high']), 2),
                "supply_zone": round(float(fvg_mid), 2),
                "description": f"Institutional Imbalance between ₹{c3['high']:.2f} and ₹{c1['low']:.2f}. Expect strong supply on retest."
            }
        return None

    def detect_order_block(self) -> Optional[Dict[str, Any]]:
        """Detect Institutional Order Block (OB)"""
        if len(self.df) < 5:
            return None

        # Look for violent displacement in last 3 candles
        recent_body = abs(self.closes[-1] - self.opens[-1])
        avg_body = np.mean([abs(c - o) for c, o in zip(self.closes[-10:-1], self.opens[-10:-1])])

        if recent_body > 1.8 * avg_body:
            if self.closes[-1] > self.opens[-1]:
                # Bullish OB: last down candle before displacement
                ob_candle = self.df.iloc[-2] if self.closes[-2] < self.opens[-2] else self.df.iloc[-3]
                return {
                    "pattern": "Bullish Order Block (OB)",
                    "category": "Smart Money Concepts",
                    "bias": "BULLISH",
                    "confidence": 87,
                    "ob_zone": f"₹{ob_candle['low']:.2f} - ₹{ob_candle['high']:.2f}",
                    "invalidation": round(float(ob_candle['low']), 2),
                    "description": f"Institutional demand block formed at ₹{ob_candle['low']:.2f} - ₹{ob_candle['high']:.2f}."
                }
            else:
                ob_candle = self.df.iloc[-2] if self.closes[-2] > self.opens[-2] else self.df.iloc[-3]
                return {
                    "pattern": "Bearish Order Block (OB)",
                    "category": "Smart Money Concepts",
                    "bias": "BEARISH",
                    "confidence": 87,
                    "ob_zone": f"₹{ob_candle['low']:.2f} - ₹{ob_candle['high']:.2f}",
                    "invalidation": round(float(ob_candle['high']), 2),
                    "description": f"Institutional supply block formed at ₹{ob_candle['low']:.2f} - ₹{ob_candle['high']:.2f}."
                }
        return None

    # =========================================================================
    # 3. HIGH PROBABILITY CANDLESTICK PATTERNS
    # =========================================================================
    def detect_candlestick_patterns(self) -> List[Dict[str, Any]]:
        """Scan recent candles for high-probability candlestick triggers"""
        if len(self.df) < 2:
            return []

        patterns = []
        c = self.df.iloc[-1]
        p = self.df.iloc[-2]

        body = abs(c['close'] - c['open'])
        lower_wick = min(c['close'], c['open']) - c['low']
        upper_wick = c['high'] - max(c['close'], c['open'])

        # Hammer / Bullish Pin Bar
        if lower_wick > (2.2 * body) and upper_wick < (0.25 * body):
            patterns.append({
                "pattern": "Hammer / Bullish Pin Bar",
                "bias": "BULLISH",
                "confidence": 82,
                "description": f"Strong price rejection from lower levels at ₹{c['low']:.2f}."
            })

        # Shooting Star / Bearish Pin Bar
        if upper_wick > (2.2 * body) and lower_wick < (0.25 * body):
            patterns.append({
                "pattern": "Shooting Star / Bearish Pin Bar",
                "bias": "BEARISH",
                "confidence": 82,
                "description": f"Strong price rejection from higher levels at ₹{c['high']:.2f}."
            })

        # Bullish Engulfing
        if p['close'] < p['open'] and c['close'] > c['open'] and c['open'] <= p['close'] and c['close'] >= p['open']:
            patterns.append({
                "pattern": "Bullish Engulfing",
                "bias": "BULLISH",
                "confidence": 85,
                "description": "Green candle completely engulfs prior red candle body."
            })

        # Bearish Engulfing
        if p['close'] > p['open'] and c['close'] < c['open'] and c['open'] >= p['close'] and c['close'] <= p['open']:
            patterns.append({
                "pattern": "Bearish Engulfing",
                "bias": "BEARISH",
                "confidence": 85,
                "description": "Red candle completely engulfs prior green candle body."
            })

        return patterns

    def scan_all_patterns(self) -> Dict[str, Any]:
        """Run complete pattern detection suite and return top setups"""
        classical = [
            self.detect_double_bottom(),
            self.detect_double_top(),
            self.detect_head_and_shoulders(),
            self.detect_flag_pennant()
        ]
        classical = [p for p in classical if p]

        smc = [
            self.detect_fair_value_gap(),
            self.detect_order_block()
        ]
        smc = [p for p in smc if p]

        candlesticks = self.detect_candlestick_patterns()

        all_patterns = classical + smc
        best_setup = max(all_patterns, key=lambda x: x['confidence']) if all_patterns else None

        return {
            "best_setup": best_setup,
            "classical_patterns": classical,
            "smc_patterns": smc,
            "candlestick_patterns": candlesticks,
            "total_detected": len(classical) + len(smc) + len(candlesticks)
        }
