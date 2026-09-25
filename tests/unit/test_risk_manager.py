import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from agents.risk_manager import RiskManager

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.risk_manager = RiskManager(max_risk_per_trade=0.02) # 2% risk

    def test_validate_trade_allowed(self):
        portfolio_value = 100000
        entry_price = 100
        stop_loss = 90

        # Risk amount = 2000
        # Risk per share = 10
        # Quantity = 200

        result = self.risk_manager.validate_trade(portfolio_value, entry_price, stop_loss)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["quantity"], 200)
        self.assertEqual(result["risk_amount"], 2000)

    def test_validate_trade_zero_risk_per_share(self):
        portfolio_value = 100000
        entry_price = 100
        stop_loss = 100

        result = self.risk_manager.validate_trade(portfolio_value, entry_price, stop_loss)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "Stop loss same as entry price")

if __name__ == '__main__':
    unittest.main()
