from .base_agent import BaseAgent
from modules.option_chain_engine import option_chain_engine

class StrategyAgent(BaseAgent):
    """
    Agent 07: Master Strategy & Confluence Agent
    Connects Market TA, Macro, News Sentiment, Risk, and Option Strike selection.
    """
    def __init__(self, market_analyst, news_analyst, risk_manager):
        super().__init__("Strategy Agent", "Master Confluence & Option Trade Recommender")
        self.market_analyst = market_analyst
        self.news_analyst = news_analyst
        self.risk_manager = risk_manager

    def generate_signal(self, symbol, df, portfolio_value):
        self.log(f"Generating confluence signal for {symbol}...")
        
        market_data = self.market_analyst.analyze(df)
        news_data = self.news_analyst.analyze(symbol)
        
        market_trend = market_data.get('supertrend', 'WAIT')
        vwap_pos = market_data.get('vwap_pos', 'ABOVE')
        sentiment = news_data.get('sentiment', 'NEUTRAL')
        last_price = float(df.iloc[-1]['close'])

        # Institutional Confluence Trigger
        is_bullish = (market_trend == "BUY") and (vwap_pos == "ABOVE") and (sentiment != "BEARISH")
        is_bearish = (market_trend == "SELL") and (vwap_pos == "BELOW") and (sentiment != "BULLISH")
        
        direction = "NONE"
        if is_bullish: direction = "BUY"
        elif is_bearish: direction = "SELL"
        
        if direction != "NONE":
            # Generate Option Strike Trade Recommendation (CE / PE)
            option_trade = option_chain_engine.recommend_strike_trade(
                symbol=symbol,
                spot_price=last_price,
                direction=direction,
                spot_sl_points=last_price * 0.008
            )

            stop_loss = last_price * 0.992 if direction == "BUY" else last_price * 1.008
            target = last_price * 1.016 if direction == "BUY" else last_price * 0.984
            risk_check = self.risk_manager.validate_trade(portfolio_value, last_price, stop_loss)
            
            return {
                "symbol": symbol,
                "signal": direction,
                "entry": round(last_price, 2),
                "stop_loss": round(stop_loss, 2),
                "target": round(target, 2),
                "quantity": risk_check.get('quantity', 50) if risk_check.get('allowed') else 0,
                "option_trade": option_trade,
                "confidence": market_data.get('strength_score', 80),
                "reason": f"SuperTrend ({market_trend}) + VWAP ({vwap_pos}) + News ({sentiment}) with {market_data.get('regime', 'TRENDING')}"
            }
            
        return {
            "symbol": symbol, 
            "signal": "WAITING",
            "reason": "Scanning for VWAP + SuperTrend + Sentiment confluence...",
            "option_trade": None
        }
