from .base_agent import BaseAgent

class RiskManager(BaseAgent):
    """
    Agent 03: Risk Manager
    Manages position sizing and risk/reward.
    """
    def __init__(self, max_risk_per_trade=0.02):
        super().__init__("Risk Manager", "Calculates position sizing and validates trades")
        self.max_risk_per_trade = max_risk_per_trade

    def validate_trade(self, portfolio_value, entry_price, stop_loss):
        risk_amount = portfolio_value * self.max_risk_per_trade
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return {"allowed": False, "reason": "Stop loss same as entry price"}
            
        quantity = int(risk_amount / risk_per_share)
        
        return {
            "allowed": True,
            "quantity": quantity,
            "risk_amount": risk_amount,
            "risk_reward_ratio": abs(entry_price - stop_loss) / entry_price # Simple placeholder
        }
