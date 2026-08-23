"""
Configuration file for SENSEX Options Trading Application
"""
import os
from datetime import time
from pytz import timezone

# Application Settings
APP_NAME = "NSE AI Trading Stack"
APP_VERSION = "2.0.0"
DEBUG = True
TESTING = False

# Server Configuration
HOST = "0.0.0.0"
PORT = 5000
SECRET_KEY = "sensex-trading-pro-secret-key-2024"

# Market Settings
MARKET_TIMEZONE = timezone('Asia/Kolkata')
MARKET_OPEN = time(9, 15)  # 9:15 AM IST
MARKET_CLOSE = time(15, 30)  # 3:30 PM IST
MARKET_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# Underlying Index Settings
UNDERLYING = "SENSEX"
SPOT_PRICE = 75000.00  # Starting spot price
MIN_SPOT_PRICE = 50000.00
MAX_SPOT_PRICE = 100000.00

# Options Settings
STRIKE_INTERVAL = 100
EXPIRY_DAYS = 3  # Default: 3-day contracts
VOLATILITY = 0.25  # 25% IV for simulation
RFR = 0.065  # Risk-free rate (6.5%)

# Paper Trading Settings
INITIAL_CAPITAL = 500000  # Rs.5 Lakhs
TRADE_UNIT = 1  # 1 lot
BROKERAGE_PERCENT = 0.001  # 0.1% brokerage
SLIPPAGE_PERCENT = 0.0005  # 0.05% slippage

# Risk Management Settings
MAX_LOSS_PERCENT = 2  # Max 2% loss per trade
MAX_POSITION_SIZE = 50000  # Max position size in rupees
MARGIN_REQUIREMENT = 0.15  # 15% margin

# Watchlist Configuration (Step 3)
SECTOR_WATCHLIST = {
    "IT": ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
    "BANKING": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
    "FIN_SERVICES": ["BAJFINANCE", "BAJAJFINSV", "CHOLAFIN"],
    "DEF_RE": ["HAL", "BEL", "RVNL", "IRCON"],
    "PHARMA": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB"],
    "AUTO": ["TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO"],
    "ENERGY": ["RELIANCE", "NTPC", "POWERGRID", "ONGC"],
    "INFRA": ["LT", "ADANIPORTS", "GRASIM"],
    "FMCG": ["HUL", "ITC", "NESTLEIND"]
}

# Reversal Pattern Detection
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Data Simulation Settings
TICK_INTERVAL = 1  # Update interval
PRICE_VOLATILITY = 0.002
VOLUME_MULTIPLIER = 100

# Live Data Mode
USE_LIVE_DATA = True  # Set to True to disable all fake/simulated data
FETCH_REAL_TIME_NSE = True

# Logging Settings
LOG_LEVEL = "INFO"
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10485760  # 10 MB
LOG_BACKUP_COUNT = 5

# WebSocket Settings
WEBSOCKET_PING_INTERVAL = 25
WEBSOCKET_PING_TIMEOUT = 5

# Broker Integration Settings (Ready for integration)
BROKER_API = {
    "DHAN": {
        "enabled": False,
        "client_id": "",
        "access_token": "",
        "api_url": "https://api.dhan.co"
    },
    "ZERODHA": {
        "enabled": False,
        "api_key": "",
        "access_token": "",
        "api_url": "https://api.kite.trade"
    }
}

# Alert Settings
ALERT_ENABLED = True
ALERT_PRICE_CHANGE_PERCENT = 2  # Alert on 2% price change
ALERT_VOLUME_MULTIPLIER = 3  # Alert on 3x volume

# Telegram Settings
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Features
FEATURES = {
    "live_options_chain": True,
    "paper_trading": True,
    "live_trading": True,
    "reversal_detection": True,
    "portfolio_tracking": True,
    "risk_management": True,
    "telegram_alerts": True,
    "automated_scheduling": True,
    "websocket_updates": True,
    "market_simulation": True,
    "one_click_trading": True,
    "p_and_l_tracking": True,
}

# Demo Data Settings
DEMO_STRIKES = [
    74700, 74800, 74900, 75000, 75100, 75200, 75300,
    75400, 75500, 75600, 75700, 75800, 75900
]

DEMO_EXPIRATIONS = [
    "1D",  # Weekly
    "2D",  # Weekly
    "3D",  # Monthly
]
