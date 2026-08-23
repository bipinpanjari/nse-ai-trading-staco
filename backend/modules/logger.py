"""
Logging module for SENSEX Options Trading Application
"""
import os
import logging
import logging.handlers
from config import LOG_DIR, LOG_LEVEL, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name, log_file=None):
    """
    Setup and configure logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Optional log file name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    import sys
    import io
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(formatter)
    # Set encoding for the stream
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except:
            pass
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        log_file = f"{name}.log"
    
    log_path = os.path.join(LOG_DIR, log_file)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Application logger
app_logger = setup_logger("SENSEX_PRO", "app.log")

# Trading logger
trading_logger = setup_logger("TRADING", "trading.log")

# Data logger
data_logger = setup_logger("DATA", "data.log")

# Error logger
error_logger = setup_logger("ERRORS", "errors.log")

def log_trade(symbol, trade_type, entry_price, quantity, stop_loss, target):
    """Log trade execution"""
    trading_logger.info(
        f"TRADE: {symbol} | TYPE: {trade_type} | ENTRY: Rs{entry_price:.2f} | "
        f"QTY: {quantity} | SL: Rs{stop_loss:.2f} | TARGET: Rs{target:.2f}"
    )

def log_market_data(symbol, price, volume, bid, ask):
    """Log market data updates"""
    data_logger.debug(
        f"DATA: {symbol} | PRICE: Rs{price:.2f} | VOL: {volume} | "
        f"BID: Rs{bid:.2f} | ASK: Rs{ask:.2f}"
    )

def log_error(error_msg, exception=None):
    """Log errors"""
    if exception:
        error_logger.error(f"{error_msg}: {str(exception)}", exc_info=True)
    else:
        error_logger.error(error_msg)

def log_portfolio_update(portfolio_data):
    """Log portfolio changes"""
    trading_logger.info(
        f"PORTFOLIO UPDATE | Capital: Rs{portfolio_data.get('capital', 0):.2f} | "
        f"Positions: {portfolio_data.get('open_positions', 0)} | "
        f"P&L: Rs{portfolio_data.get('pnl', 0):.2f}"
    )
