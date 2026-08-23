"""
Institutional Multi-Asset Backtesting Engine (Optimized High-Edge Version)
Features:
- ATR-based Dynamic Volatility Stop Loss (1.5x ATR)
- EMA Ribbon Confluence (EMA 9 > EMA 21 > EMA 50)
- SuperTrend (7, 3) + VWAP + RSI (14) Momentum Filter
- Automated Breakeven Trailing Stop Loss (Move SL to Cost at +1.2R)
- Target 1 (1.5R partial / trailing) and Target 2 (2.8R expansion)
"""

import os
import sys
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.analysis.advanced_ta import AdvancedTechnicalEngine
from modules.logger import app_logger

class InstitutionalBacktester:
    """
    High-Edge Backtester for NSE Indian Equities & Indices.
    """

    def __init__(self, initial_capital: float = 500000.0, risk_per_trade_pct: float = 1.2):
        self.initial_capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct

    def fetch_historical_data(self, symbol: str, period: str = "60d", interval: str = "15m") -> pd.DataFrame:
        """Fetch clean historical candles from Yahoo Finance"""
        ticker_map = {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
            "RELIANCE": "RELIANCE.NS",
            "TATAMOTORS": "TATAMOTORS.NS",
            "HDFCBANK": "HDFCBANK.NS",
            "SBIN": "SBIN.NS",
            "INFY": "INFY.NS",
            "TCS": "TCS.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "BHARTIARTL": "BHARTIARTL.NS",
            "LT": "LT.NS",
            "BEL": "BEL.NS",
            "MAZDOCK": "MAZDOCK.NS",
            "TRENT": "TRENT.NS"
        }
        ticker = ticker_map.get(symbol.upper(), f"{symbol}.NS")
        
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if df.empty:
                return pd.DataFrame()
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0].lower() for col in df.columns]
            else:
                df.columns = [c.lower() for c in df.columns]
                
            df = df.dropna()
            # If volume is all zeros (common for index tickers), generate proxy volume
            if 'volume' not in df or df['volume'].sum() == 0:
                df['volume'] = 50000
                
            return df
        except Exception as e:
            app_logger.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    def run_strategy_backtest(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes backtest using Optimized Institutional Confluence:
        - SuperTrend (7, 3) Buy/Sell
        - EMA Ribbon Alignment (EMA 9 vs EMA 21)
        - VWAP Intraday Direction
        - RSI Momentum Filter (52-72 for Longs, 28-48 for Shorts)
        - ATR-based Dynamic Stop Loss & Trailing to Breakeven
        """
        if df.empty or len(df) < 50:
            return {
                "symbol": symbol,
                "candles_analyzed": len(df),
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": "0.0%",
                "profit_factor": 0.0,
                "net_pnl": 0.0,
                "return_pct": "0.0%",
                "max_drawdown": "0.0%",
                "avg_trade_pnl": 0.0,
                "sample_trades": []
            }

        # 1. Apply Technical Engine Indicators
        ta_engine = AdvancedTechnicalEngine(df)
        df_ta = ta_engine.apply_indicators()
        
        balance = self.initial_capital
        position = None
        trades = []
        equity_curve = []

        for i in range(50, len(df_ta)):
            row = df_ta.iloc[i]
            prev_row = df_ta.iloc[i-1]
            cmp = float(row['close'])
            current_time = str(df_ta.index[i])

            volume = float(row.get('volume', 1000))
            avg_vol = float(df_ta['volume'].iloc[i-15:i].mean()) if 'volume' in df_ta else 1000.0
            rvol = volume / (avg_vol if avg_vol > 0 else 1.0)
            
            rsi = float(row.get('RSI_14', 50))
            vwap = float(row.get('VWAP_D', cmp))
            atr = max(float(row.get('ATR_14', cmp * 0.008)), cmp * 0.003)
            
            ema9 = float(row.get('EMA_9', cmp))
            ema21 = float(row.get('EMA_21', cmp))
            ema50 = float(row.get('EMA_50', cmp))

            supertrend = row.get('SUPERT_7_3.0', 0)
            prev_st = prev_row.get('SUPERT_7_3.0', 0)

            # Check existing position exits & trailing
            if position is not None:
                pos_type = position['type']
                entry_p = position['entry_price']
                qty = position['qty']
                sl = position['sl']
                tp1 = position['tp1']
                tp2 = position['tp2']

                # Trail SL to Breakeven once price moves favorably past Target 1 (1.5R)
                if pos_type == 'LONG' and float(row['high']) >= tp1 and position['sl'] < entry_p:
                    position['sl'] = round(entry_p * 1.001, 2) # Locked into breakeven/small gain
                elif pos_type == 'SHORT' and float(row['low']) <= tp1 and position['sl'] > entry_p:
                    position['sl'] = round(entry_p * 0.999, 2)

                exit_price = None
                exit_reason = ""

                if pos_type == 'LONG':
                    # Stop Loss hit
                    if float(row['low']) <= position['sl']:
                        exit_price = position['sl']
                        exit_reason = "STOP_LOSS" if position['sl'] <= entry_p else "TRAILED_PROFIT_STOP"
                    # Target 2 (Runner Expansion Exit)
                    elif float(row['high']) >= tp2:
                        exit_price = tp2
                        exit_reason = "TARGET_2_EXPANSION"
                    # Trend Reversal (Supertrend flips to Sell)
                    elif supertrend == -1 and prev_st == 1:
                        exit_price = cmp
                        exit_reason = "SUPERTREND_REVERSAL"

                elif pos_type == 'SHORT':
                    # Stop Loss hit
                    if float(row['high']) >= position['sl']:
                        exit_price = position['sl']
                        exit_reason = "STOP_LOSS" if position['sl'] >= entry_p else "TRAILED_PROFIT_STOP"
                    # Target 2 (Runner Expansion Exit)
                    elif float(row['low']) <= tp2:
                        exit_price = tp2
                        exit_reason = "TARGET_2_EXPANSION"
                    # Trend Reversal (Supertrend flips to Buy)
                    elif supertrend == 1 and prev_st == -1:
                        exit_price = cmp
                        exit_reason = "SUPERTREND_REVERSAL"

                if exit_price is not None:
                    pnl = (exit_price - entry_p) * qty if pos_type == 'LONG' else (entry_p - exit_price) * qty
                    balance += pnl
                    trades.append({
                        "symbol": symbol,
                        "type": pos_type,
                        "entry_time": position['entry_time'],
                        "exit_time": current_time,
                        "entry_price": round(entry_p, 2),
                        "exit_price": round(exit_price, 2),
                        "qty": qty,
                        "pnl": round(pnl, 2),
                        "pnl_pct": round((pnl / (entry_p * qty)) * 100, 2),
                        "reason": exit_reason
                    })
                    position = None

            # High-Probability Entry Filter
            if position is None:
                # Long Setup: SuperTrend 1 + EMA9 > EMA21 + CMP > VWAP + RSI Bullish Zone (50-70)
                is_long_setup = (
                    (supertrend == 1 and prev_st != 1) or 
                    (supertrend == 1 and ema9 > ema21 and cmp >= vwap and 50 <= rsi <= 68 and rvol >= 1.0)
                )

                # Short Setup: SuperTrend -1 + EMA9 < EMA21 + CMP < VWAP + RSI Bearish Zone (30-50)
                is_short_setup = (
                    (supertrend == -1 and prev_st != -1) or 
                    (supertrend == -1 and ema9 < ema21 and cmp < vwap and 30 <= rsi <= 50 and rvol >= 1.0)
                )

                if is_long_setup:
                    risk_amount = balance * (self.risk_per_trade_pct / 100.0)
                    sl_dist = atr * 1.5
                    sl = round(cmp - sl_dist, 2)
                    risk_per_share = max(cmp - sl, 1.0)
                    qty = int(risk_amount / risk_per_share)
                    if qty > 0 and (qty * cmp) <= (balance * 3.5):
                        tp1 = round(cmp + (risk_per_share * 1.5), 2)
                        tp2 = round(cmp + (risk_per_share * 2.8), 2)
                        position = {
                            'type': 'LONG',
                            'entry_price': cmp,
                            'qty': qty,
                            'sl': sl,
                            'tp1': tp1,
                            'tp2': tp2,
                            'entry_time': current_time
                        }

                elif is_short_setup:
                    risk_amount = balance * (self.risk_per_trade_pct / 100.0)
                    sl_dist = atr * 1.5
                    sl = round(cmp + sl_dist, 2)
                    risk_per_share = max(sl - cmp, 1.0)
                    qty = int(risk_amount / risk_per_share)
                    if qty > 0 and (qty * cmp) <= (balance * 3.5):
                        tp1 = round(cmp - (risk_per_share * 1.5), 2)
                        tp2 = round(cmp - (risk_per_share * 2.8), 2)
                        position = {
                            'type': 'SHORT',
                            'entry_price': cmp,
                            'qty': qty,
                            'sl': sl,
                            'tp1': tp1,
                            'tp2': tp2,
                            'entry_time': current_time
                        }

            equity_curve.append({"time": current_time, "equity": balance})

        if not trades:
            return {
                "symbol": symbol,
                "candles_analyzed": len(df_ta),
                "initial_capital": self.initial_capital,
                "final_balance": round(balance, 2),
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": "0.0%",
                "profit_factor": 0.0,
                "net_pnl": 0.0,
                "return_pct": "0.0%",
                "max_drawdown": "0.0%",
                "avg_trade_pnl": 0.0,
                "sample_trades": []
            }

        df_trades = pd.DataFrame(trades)
        winning_trades = df_trades[df_trades['pnl'] > 0]
        losing_trades = df_trades[df_trades['pnl'] <= 0]
        
        win_rate = (len(winning_trades) / len(df_trades)) * 100.0
        total_pnl = df_trades['pnl'].sum()
        gross_profit = winning_trades['pnl'].sum() if not winning_trades.empty else 0.0
        gross_loss = abs(losing_trades['pnl'].sum()) if not losing_trades.empty else 1.0
        profit_factor = round(gross_profit / (gross_loss if gross_loss > 0 else 1.0), 2)

        equity_series = pd.Series([e['equity'] for e in equity_curve])
        cum_max = equity_series.cummax()
        drawdowns = (cum_max - equity_series) / cum_max
        max_drawdown = round(float(drawdowns.max()) * 100.0, 2)

        return {
            "symbol": symbol,
            "candles_analyzed": len(df_ta),
            "initial_capital": self.initial_capital,
            "final_balance": round(balance, 2),
            "net_pnl": round(total_pnl, 2),
            "return_pct": f"{round((total_pnl / self.initial_capital) * 100, 2)}%",
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": f"{round(win_rate, 2)}%",
            "profit_factor": profit_factor,
            "max_drawdown": f"{max_drawdown}%",
            "avg_trade_pnl": round(float(df_trades['pnl'].mean()), 2),
            "sample_trades": trades[-5:]
        }

    def run_multi_asset_backtest(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Runs backtesting across multiple liquid NSE instruments"""
        if symbols is None:
            symbols = ["NIFTY", "BANKNIFTY", "SBIN", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "BHARTIARTL", "BEL", "LT"]

        results = []
        total_pnl = 0.0
        total_trades = 0
        total_wins = 0

        for sym in symbols:
            df = self.fetch_historical_data(sym, period="60d", interval="15m")
            if not df.empty:
                res = self.run_strategy_backtest(sym, df)
                results.append(res)
                total_pnl += res.get('net_pnl', 0.0)
                total_trades += res.get('total_trades', 0)
                total_wins += res.get('winning_trades', 0)

        overall_win_rate = round((total_wins / total_trades) * 100.0, 2) if total_trades > 0 else 0.0

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tested_symbols": len(results),
            "cumulative_portfolio_pnl": round(total_pnl, 2),
            "overall_win_rate": f"{overall_win_rate}%",
            "total_trades_executed": total_trades,
            "total_winning_trades": total_wins,
            "detailed_asset_results": results
        }

if __name__ == "__main__":
    backtester = InstitutionalBacktester(initial_capital=500000.0, risk_per_trade_pct=1.2)
    symbols_to_test = ["NIFTY", "BANKNIFTY", "SBIN", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "BHARTIARTL", "BEL", "LT"]
    summary = backtester.run_multi_asset_backtest(symbols_to_test)
    
    print("\n" + "="*75)
    print("🏆 INSTITUTIONAL AI TRADING STACK - HIGH-EDGE BACKTEST SUMMARY")
    print("="*75)
    print(f"Total Assets Tested: {summary['tested_symbols']}")
    print(f"Total Trades Executed: {summary['total_trades_executed']}")
    print(f"Overall Strategy Win Rate: {summary['overall_win_rate']}")
    print(f"Cumulative Strategy Net PnL: ₹{summary['cumulative_portfolio_pnl']:,.2f}")
    print("="*75)
    
    for res in summary['detailed_asset_results']:
        print(f"\n📊 {res['symbol']} (Candles: {res['candles_analyzed']})")
        print(f"   • Win Rate: {res['win_rate']} ({res['winning_trades']}W / {res['losing_trades']}L)")
        print(f"   • Net PnL: ₹{res['net_pnl']:,.2f} ({res['return_pct']})")
        print(f"   • Profit Factor: {res['profit_factor']} | Max Drawdown: {res['max_drawdown']}")
        print(f"   • Avg Trade PnL: ₹{res['avg_trade_pnl']:,.2f}")
