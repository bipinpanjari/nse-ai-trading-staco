import pandas as pd
import numpy as np
from datetime import datetime
from modules.trading import TechnicalAnalyzer, RiskManager

class Backtester:
    """
    Backtest AI strategies against historical OHLCV data.
    """
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.reset()

    def reset(self):
        self.balance = self.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []

    def run(self, df, strategy_agent):
        """
        Run backtest on a dataframe using a the strategy agent.
        Expected columns: 'open', 'high', 'low', 'close', 'volume'
        """
        self.reset()
        
        # We need at least 50 bars for technical analysis
        if len(df) < 50:
            return {"error": "Insufficient data"}

        for i in range(50, len(df)):
            current_bar = df.iloc[i]
            historical_slice = df.iloc[:i+1] # Feed data up to current time
            
            # Check for exits on existing positions
            self._process_exits(current_bar)
            
            # Ask Strategy Agent for signals
            # Note: In backtesting, we usually pass the historical slice
            symbol = "BACKTEST"
            signal_data = strategy_agent.generate_signal(symbol, historical_slice, self.balance)
            
            if signal_data['signal'] == "BUY" and self.balance > (current_bar['close'] * signal_data['quantity']):
                self._execute_entry(current_bar, signal_data)

            self.equity_curve.append({
                "date": df.index[i],
                "equity": self.get_total_value(current_bar['close'])
            })

        return self.get_results()

    def _execute_entry(self, bar, signal):
        entry_price = bar['close']
        qty = signal['quantity']
        
        if qty <= 0: return

        cost = entry_price * qty
        self.balance -= cost
        
        self.positions.append({
            "entry_date": bar.name,
            "entry_price": entry_price,
            "qty": qty,
            "stop_loss": signal['stop_loss'],
            "target": entry_price * 1.05 # Default 5% target if not specified
        })

    def _process_exits(self, bar):
        high = bar['high']
        low = bar['low']
        close = bar['close']
        
        for pos in self.positions[:]:
            exit_price = None
            reason = ""
            
            if low <= pos['stop_loss']:
                exit_price = pos['stop_loss']
                reason = "STOP_LOSS"
            elif high >= pos['target']:
                exit_price = pos['target']
                reason = "TARGET"
                
            if exit_price:
                pnl = (exit_price - pos['entry_price']) * pos['qty']
                self.balance += (exit_price * pos['qty'])
                self.trades.append({
                    "entry_date": pos['entry_date'],
                    "exit_date": bar.name,
                    "entry_price": pos['entry_price'],
                    "exit_price": exit_price,
                    "qty": pos['qty'],
                    "pnl": pnl,
                    "reason": reason
                })
                self.positions.remove(pos)

    def get_total_value(self, current_price):
        pos_value = sum(pos['qty'] * current_price for pos in self.positions)
        return self.balance + pos_value

    def get_results(self):
        if not self.trades:
            return {"total_trades": 0, "final_balance": self.balance}
            
        df_trades = pd.DataFrame(self.trades)
        win_rate = (len(df_trades[df_trades['pnl'] > 0]) / len(df_trades)) * 100
        total_pnl = df_trades['pnl'].sum()
        
        return {
            "initial_capital": self.initial_capital,
            "final_balance": self.balance,
            "total_trades": len(df_trades),
            "win_rate": f"{round(win_rate, 2)}%",
            "net_profit": round(total_pnl, 2),
            "return_pct": f"{round((total_pnl/self.initial_capital)*100, 2)}%",
            "trades": self.trades
        }
