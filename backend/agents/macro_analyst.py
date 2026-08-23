from .base_agent import BaseAgent

class MacroAnalyst(BaseAgent):
    """
    Agent 04: Macro Analyst
    Tracks global events, interest rates, and inflation.
    Focus: Big picture, economic calendar.
    """
    def __init__(self):
        super().__init__("Macro Analyst", "Tracks global macroeconomic data")

    def get_market_sentiment(self):
        # In a real app, this would fetch from an economic calendar API
        return {
            "global_outlook": "NEUTRAL",
            "us_fed_bias": "HAWKISH",
            "rbi_policy": "NEUTRAL",
            "risk_appetite": "MODERATE"
        }
