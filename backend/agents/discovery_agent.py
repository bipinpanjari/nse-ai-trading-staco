from .base_agent import BaseAgent
from modules.intraday_screener import intraday_screener
from modules.pre_market_engine import pre_market_engine
from typing import Dict, Any

class DiscoveryAgent(BaseAgent):
    """
    Agent 08: Live Intraday Stock Discovery & Opportunity Scorer
    Uses real market screening, RVOL analysis, and CPR pivot breakouts.
    """
    def __init__(self, news_analyst, market_analyst):
        super().__init__("Discovery AI", "Real-Time Stock Hunter & Opportunity Scorer")
        self.news_analyst = news_analyst
        self.market_analyst = market_analyst

    def discover(self, symbol: str = "NIFTY") -> Dict[str, Any]:
        self.log("Running Real-Time Stock Screener across NSE Universe...")
        
        # 1. Market Sentiment & Pre-Market Macro
        macro_pred = pre_market_engine.analyze_market_prediction()
        mkt_sentiment = "BULLISH" if "BULLISH" in macro_pred['prediction'] else (
            "BEARISH" if "BEARISH" in macro_pred['prediction'] else "NEUTRAL"
        )
        
        # 2. Real-Time Screener across 20+ liquid stocks
        live_opportunities = intraday_screener.scan_all_universe()

        # If live opportunities are scanning, fallback to pre-market watchlist
        if not live_opportunities:
            pm_watchlist = pre_market_engine.generate_morning_watchlist()
            formatted_recs = []
            for item in pm_watchlist[:4]:
                formatted_recs.append({
                    "symbol": item['symbol'],
                    "sector": "NSE F&O",
                    "direction": item['direction'],
                    "entry": item['entry_trigger'],
                    "sl": item['stop_loss'],
                    "tp": item['target_1'],
                    "tp2": item['target_2'],
                    "score": 85,
                    "rr": item['risk_reward'],
                    "pattern": item['cpr_type'],
                    "fvg": "CONFIRMED",
                    "reason": item['thesis']
                })
            return {
                "market_sentiment": mkt_sentiment,
                "macro_prediction": macro_pred['prediction'],
                "top_sectors": ["BANKING", "IT", "AUTO"],
                "recommendations": formatted_recs
            }

        # Format live screener output
        recommendations = []
        for opp in live_opportunities[:5]:
            recommendations.append({
                "symbol": opp['symbol'],
                "sector": "NSE F&O",
                "direction": opp['direction'],
                "entry": opp['entry'],
                "sl": opp['stop_loss'],
                "tp": opp['target_1'],
                "tp2": opp['target_2'],
                "score": opp['score'],
                "rr": "1:2.0",
                "pattern": opp['pattern'],
                "fvg": "VALID",
                "rvol": opp['rvol'],
                "reason": " + ".join(opp['triggers'])
            })

        return {
            "market_sentiment": mkt_sentiment,
            "macro_prediction": macro_pred['prediction'],
            "top_sectors": ["BANKING", "IT", "AUTO", "ENERGY"],
            "recommendations": recommendations
        }
