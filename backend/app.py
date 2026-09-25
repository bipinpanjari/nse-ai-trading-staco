"""
NSE AI Trading Stack - Unified Flask Application (Institutional Grade Upgrade)
Features:
- Real-Time Market Data & Pre-Market Gap Engine (9:08 AM & 9:15 AM ORB)
- Live Multi-Threaded F&O Screener (VWAP, SuperTrend, RVOL, SMC)
- Small-Cap & Mid-Cap Catalyst Hunter (Quarterly Results & Mega Order Wins)
- Institutional Flow Analyzer (FII/DII Cash, F&O Positioning & Block Deals)
- ATM Options Engine with Greeks & OI Buildup Classifier
- Zerodha Kite & Kite MCP (Model Context Protocol) Integration
"""

import os
import json
import threading
import time
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import pytz

from config import *
from modules.logger import app_logger, log_error
from modules.data import Portfolio
from modules.nse_live_feed import nse_live_feed
from modules.pre_market_engine import pre_market_engine
from modules.option_chain_engine import option_chain_engine
from modules.intraday_screener import intraday_screener
from modules.catalyst_screener import catalyst_screener
from modules.institutional_tracker import institutional_tracker
from modules.kite_connector import kite_connector
from modules.pattern_recognition import PatternRecognitionEngine
from modules.analysis.advanced_ta import AdvancedTechnicalEngine

from agents import (
    MarketAnalyst, NewsAnalyst, RiskManager as AIRiskManager, 
    MacroAnalyst, PortfolioManager, ExecutionAgent, StrategyAgent,
    DiscoveryAgent
)

# Initialize Flask & CORS
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize AI Agents
market_analyst = MarketAnalyst()
news_analyst = NewsAnalyst()
risk_ai = AIRiskManager()
strategy_agent = StrategyAgent(market_analyst, news_analyst, risk_ai)
discovery_ai = DiscoveryAgent(news_analyst, market_analyst)

# Portfolio Tracking
portfolio = Portfolio(INITIAL_CAPITAL)

# Global State
price_history = []
active_symbol = "NIFTY"
current_spot = 24500.00
market_thread = None
market_thread_lock = threading.Lock()

def is_market_open():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    if now.weekday() not in MARKET_DAYS:
        return False
    return MARKET_OPEN <= now.time() <= MARKET_CLOSE

def get_market_status():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    return {
        'is_open': is_market_open(),
        'current_time': now.strftime('%H:%M:%S'),
        'day': now.strftime('%A'),
        'timezone': 'IST'
    }

def broadcast_loop():
    """Real-time simulation and broadcast loop with Live NSE Data & Option Chain"""
    global price_history, current_spot, active_symbol
    app_logger.info("Background broadcasting thread started.")
    
    # Pre-seed history
    if not price_history:
        candles_df = nse_live_feed.get_realtime_candles(active_symbol, interval="5m", period="5d")
        if not candles_df.empty:
            for _, row in candles_df.tail(60).iterrows():
                price_history.append({
                    'time': str(row['time']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row.get('volume', 1000))
                })
                current_spot = float(row['close'])

    loop_count = 0
    while True:
        try:
            status = get_market_status()
            
            # 1. Update Real-Time Price
            tick_move = current_spot * 0.00015 * (1 if loop_count % 3 == 0 else -0.8)
            current_spot = round(current_spot + tick_move, 2)

            price_history.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'open': current_spot * 0.9995,
                'high': current_spot * 1.0005,
                'low': current_spot * 0.999,
                'close': current_spot,
                'volume': 1500
            })
            if len(price_history) > 120:
                price_history.pop(0)

            # 2. Advanced TA & Pattern Analysis
            df = pd.DataFrame(price_history)
            analysis_data = market_analyst.analyze(df)
            
            # 3. Master Strategy Confluence Signal
            signal = strategy_agent.generate_signal(active_symbol, df, portfolio.capital)

            # 4. Generate Live Option Chain for the active underlying
            option_chain_data = option_chain_engine.generate_live_option_chain(
                symbol=active_symbol, spot_price=current_spot, num_strikes=11
            )

            # 5. Broadcast Core Market Update (every 2 seconds)
            socketio.emit('market_update', {
                'symbol': active_symbol,
                'spot_price': current_spot,
                'status': status,
                'analysis': analysis_data,
                'signal': signal,
                'option_chain_summary': {
                    'pcr': option_chain_data['pcr'],
                    'pcr_sentiment': option_chain_data['pcr_sentiment'],
                    'max_pain': option_chain_data['max_pain'],
                    'resistance': option_chain_data['major_resistance'],
                    'support': option_chain_data['major_support']
                }
            })

            # 6. Periodic Screener & Intelligence Updates (every 8s)
            if loop_count % 4 == 0:
                discovery_results = discovery_ai.discover(active_symbol)
                socketio.emit('discovery_update', discovery_results)
                
                # Pre-Market Prediction & Watchlist
                premarket_data = pre_market_engine.analyze_market_prediction()
                socketio.emit('premarket_update', premarket_data)

                # Catalysts & Small-Cap update
                catalyst_data = catalyst_screener.get_all_catalysts()
                socketio.emit('catalyst_update', catalyst_data)

                # Institutional intelligence update
                inst_data = institutional_tracker.get_full_institutional_intelligence()
                socketio.emit('institutional_update', inst_data)

            # 7. Portfolio Update
            summary = portfolio.get_portfolio_summary()
            socketio.emit('portfolio_update', {
                'capital': round(summary['capital'] + summary['total_pnl'], 2),
                'pnl': round(summary['total_pnl'], 2),
                'open_positions': summary['open_positions'],
                'positions': summary['positions']
            })

            loop_count += 1
            socketio.sleep(2)
        except Exception as e:
            app_logger.error(f"Broadcast Loop Error: {e}")
            socketio.sleep(2)

# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify(get_market_status())

@app.route('/api/premarket', methods=['GET'])
def api_premarket():
    prediction = pre_market_engine.analyze_market_prediction()
    watchlist = pre_market_engine.generate_morning_watchlist()
    gaps = intraday_screener.scan_pre_market_gaps()
    return jsonify({
        "status": "success",
        "prediction": prediction,
        "watchlist": watchlist,
        "gaps": gaps
    })

@app.route('/api/screener', methods=['GET'])
def api_screener():
    category = request.args.get('category')
    results = intraday_screener.scan_all_universe(category_filter=category)
    return jsonify({
        "status": "success",
        "count": len(results),
        "results": results
    })

@app.route('/api/screener/gaps', methods=['GET'])
def api_screener_gaps():
    gaps = intraday_screener.scan_pre_market_gaps()
    return jsonify({
        "status": "success",
        "gaps": gaps
    })

@app.route('/api/screener/catalysts', methods=['GET'])
def api_screener_catalysts():
    catalysts = catalyst_screener.get_all_catalysts()
    return jsonify({
        "status": "success",
        "data": catalysts
    })

@app.route('/api/screener/institutional', methods=['GET'])
def api_screener_institutional():
    inst = institutional_tracker.get_full_institutional_intelligence()
    return jsonify({
        "status": "success",
        "data": inst
    })

@app.route('/api/optionchain', methods=['GET'])
def api_optionchain():
    symbol = request.args.get('symbol', active_symbol)
    spot = float(request.args.get('spot', current_spot))
    chain = option_chain_engine.generate_live_option_chain(symbol=symbol, spot_price=spot, num_strikes=15)
    return jsonify({
        "status": "success",
        "data": chain
    })

@app.route('/api/recommend_strike', methods=['GET'])
def api_recommend_strike():
    symbol = request.args.get('symbol', active_symbol)
    spot = float(request.args.get('spot', current_spot))
    direction = request.args.get('direction', 'BUY')
    trade = option_chain_engine.recommend_strike_trade(symbol=symbol, spot_price=spot, direction=direction)
    return jsonify({
        "status": "success",
        "trade": trade
    })

# =============================================================================
# ZERODHA KITE & KITE MCP ENDPOINTS
# =============================================================================

@app.route('/api/kite/status', methods=['GET'])
def api_kite_status():
    return jsonify(kite_connector.get_connection_status())

@app.route('/api/kite/margins', methods=['GET'])
def api_kite_margins():
    return jsonify({"status": "success", "margins": kite_connector.get_margins()})

@app.route('/api/kite/positions', methods=['GET'])
def api_kite_positions():
    return jsonify({"status": "success", "positions": kite_connector.get_positions()})

@app.route('/api/kite/orders', methods=['GET'])
def api_kite_orders():
    return jsonify({"status": "success", "orders": kite_connector.get_orders()})

@app.route('/api/kite/trade', methods=['POST'])
def api_kite_trade():
    data = request.json or {}
    symbol = data.get('symbol', 'NIFTY24OCT24500CE')
    txn_type = data.get('transaction_type', 'BUY')
    qty = int(data.get('quantity', 50))
    product = data.get('product', 'MIS')
    order_type = data.get('order_type', 'MARKET')
    price = float(data.get('price', 0.0))

    res = kite_connector.place_order(
        tradingsymbol=symbol,
        transaction_type=txn_type,
        quantity=qty,
        product=product,
        order_type=order_type,
        price=price
    )
    return jsonify(res)

@app.route('/api/kite/mcp', methods=['GET'])
def api_kite_mcp():
    return jsonify({
        "mcp_version": "1.0",
        "server": "Zerodha Kite MCP Endpoint",
        "tools": kite_connector.get_mcp_tools_manifest()
    })

# =============================================================================
# GENERAL TRADING & NEWS ENDPOINTS
# =============================================================================

@app.route('/api/news', methods=['GET'])
def api_news():
    news_data = news_analyst.analyze("NSE INDIA")
    return jsonify({
        "status": "success",
        "data": news_data
    })

@app.route('/api/global_cues', methods=['GET'])
def api_global_cues():
    cues = nse_live_feed.get_global_cues()
    fii_dii = nse_live_feed.get_fii_dii_data()
    return jsonify({
        "status": "success",
        "global_cues": cues,
        "fii_dii": fii_dii
    })

@app.route('/api/trade/place', methods=['POST'])
def api_place_trade():
    data = request.json or {}
    symbol = data.get('symbol', 'NIFTY 24500 CE')
    qty = int(data.get('qty', 50))
    price = float(data.get('price', 145.0))
    opt_type = data.get('type', 'CE')

    success = portfolio.add_position(symbol, qty, price, option_type=opt_type)
    if 'sl' in data: portfolio.set_stop_loss(f"{symbol}_{opt_type}", float(data['sl']))
    if 'target' in data: portfolio.set_target(f"{symbol}_{opt_type}", float(data['target']))

    return jsonify({
        "status": "success" if success else "error",
        "message": f"Order placed for {symbol} x{qty} @ ₹{price}" if success else "Insufficient margin"
    })

@app.route('/api/trade/close', methods=['POST'])
def api_close_trade():
    data = request.json or {}
    symbol_key = data.get('symbol_key')
    exit_price = float(data.get('exit_price', 0.0))
    success = portfolio.close_position(symbol_key, exit_price)
    return jsonify({
        "status": "success" if success else "error",
        "message": f"Position {symbol_key} closed @ ₹{exit_price}"
    })

# Socket.IO connection
@socketio.on('connect')
def handle_connect():
    global market_thread
    with market_thread_lock:
        if market_thread is None:
            market_thread = socketio.start_background_task(broadcast_loop)
            app_logger.info("Client connected: Background thread started.")

if __name__ == '__main__':
    socketio.start_background_task(broadcast_loop)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
