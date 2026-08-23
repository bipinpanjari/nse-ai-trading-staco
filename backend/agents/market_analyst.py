from .base_agent import BaseAgent
import pandas as pd
from modules.analysis.advanced_ta import AdvancedTechnicalEngine
from modules.pattern_recognition import PatternRecognitionEngine

class MarketAnalyst(BaseAgent):
    """
    Agent 01: Market Analyst (Institutional Grade)
    Multi-timeframe TA, VWAP, SuperTrend (7,3), EMA Ribbon, and Classical/SMC Pattern Detection.
    """
    def __init__(self):
        super().__init__("Market Analyst", "Institutional Technical & Pattern Analysis")

    def analyze(self, df: pd.DataFrame):
        if df is None or df.empty:
            return {"status": "error", "message": "No data"}

        # 1. Advanced Technical Indicators
        ta_engine = AdvancedTechnicalEngine(df)
        df_analyzed = ta_engine.apply_indicators()
        regime = ta_engine.get_market_regime()
        levels = ta_engine.get_levels()
        fvg = ta_engine.get_fvg()

        # 2. Classical Patterns & Smart Money Concepts Engine
        pattern_engine = PatternRecognitionEngine(df)
        pattern_results = pattern_engine.scan_all_patterns()

        last_row = df_analyzed.iloc[-1]
        cmp = float(last_row['close'])
        vwap_val = float(last_row.get('VWAP_D', cmp))

        supertrend_signal = "BUY" if last_row.get('SUPERT_7_3.0', 0) == 1 else (
            "SELL" if last_row.get('SUPERT_7_3.0', 0) == -1 else "WAIT"
        )

        analysis = {
            "rsi": round(float(last_row.get('RSI_14', 50)), 1),
            "regime": regime,
            "vwap": round(vwap_val, 2),
            "vwap_pos": "ABOVE" if cmp >= vwap_val else "BELOW",
            "supertrend": supertrend_signal,
            "patterns": pattern_results.get("candlestick_patterns", []),
            "classical_patterns": pattern_results.get("classical_patterns", []),
            "smc_patterns": pattern_results.get("smc_patterns", []),
            "best_pattern": pattern_results.get("best_setup"),
            "fvg": fvg,
            "support_resistance": levels,
            "strength_score": self._calculate_strength(last_row, regime, supertrend_signal, cmp, vwap_val)
        }
        
        return analysis

    def _calculate_strength(self, row, regime, supertrend, cmp, vwap):
        score = 50
        if regime == "STRONG_BULLISH": score += 20
        elif regime == "STRONG_BEARISH": score -= 20
        
        if cmp >= vwap: score += 10
        else: score -= 10

        if supertrend == "BUY": score += 15
        elif supertrend == "SELL": score -= 15

        return min(max(score, 5), 98)
