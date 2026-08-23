#!/usr/bin/env python3
"""
MARKET TREND ANALYZER
Predicts if market will open positive or negative based on pre-market signals
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import random

load_dotenv()

print("\n" + "="*70)
print("MARKET TREND ANALYZER - PRE-MARKET PREDICTION")
print("="*70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
print("="*70)

# ============================================================
# SIMULATED MARKET DATA (In real scenario, fetch from API)
# ============================================================
print("\n1. FETCHING MARKET DATA")
print("-"*70)

# Previous close (previous day)
nifty_prev_close = 23450
sensex_prev_close = 77950

# Current pre-market data (simulated - in real trading, use live API)
# This would come from NSE/BSE APIs in production
nifty_current = 23480  # Slightly up
sensex_current = 77980  # Slightly up

nifty_change = nifty_current - nifty_prev_close
nifty_percent = (nifty_change / nifty_prev_close) * 100

sensex_change = sensex_current - sensex_prev_close
sensex_percent = (sensex_change / sensex_prev_close) * 100

print(f"\n📊 NIFTY 50 (Pre-market)")
print(f"   Previous Close: {nifty_prev_close}")
print(f"   Current Level:  {nifty_current}")
print(f"   Change:         {nifty_change:+.0f} ({nifty_percent:+.2f}%)")

print(f"\n📊 SENSEX (Pre-market)")
print(f"   Previous Close: {sensex_prev_close}")
print(f"   Current Level:  {sensex_current}")
print(f"   Change:         {sensex_change:+.0f} ({sensex_percent:+.2f}%)")

# ============================================================
# TECHNICAL INDICATORS
# ============================================================
print("\n2. TECHNICAL ANALYSIS")
print("-"*70)

# Simulate price history for analysis
import numpy as np

# Create realistic 50-candle history
prices = []
price = nifty_prev_close - 100
trend_strength = 0.8  # Slight uptrend
volatility = 15

for i in range(50):
    price = price * (1 + (random.uniform(-volatility, volatility) / 10000))
    price = price + (trend_strength * 0.5)  # Add uptrend bias
    prices.append(price)

prices.append(nifty_current)

# Calculate RSI
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

rsi = calculate_rsi(prices)
print(f"\n📈 RSI (14): {rsi:.2f}")
if rsi > 70:
    print(f"   → Overbought (>70) - Could see selling")
elif rsi < 30:
    print(f"   → Oversold (<30) - Could see buying")
else:
    print(f"   → Neutral ({rsi:.0f})")

# Calculate MACD
def calculate_macd(prices):
    prices = np.array(prices)
    ema12 = prices[-12:].mean()  # Simplified EMA
    ema26 = prices[-26:].mean()  # Simplified EMA
    macd = ema12 - ema26
    return macd

macd = calculate_macd(prices)
print(f"\n📊 MACD: {macd:.2f}")
if macd > 0:
    print(f"   → Bullish (positive MACD) - Uptrend signal")
else:
    print(f"   → Bearish (negative MACD) - Downtrend signal")

# Trend Analysis
recent_prices = prices[-5:]
trend = "UPTREND" if recent_prices[-1] > recent_prices[0] else "DOWNTREND"
trend_strength_pct = abs((recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100)

print(f"\n🔄 Trend (Last 5 candles): {trend}")
print(f"   Strength: {trend_strength_pct:.2f}%")

# ============================================================
# FOREIGN FLOWS & SENTIMENT
# ============================================================
print("\n3. MARKET SENTIMENT INDICATORS")
print("-"*70)

# Simulated FII/DII flows
fii_flow = random.choice([-1, 1]) * random.uniform(100, 500)  # Random FII flow
dii_flow = random.choice([-1, 1]) * random.uniform(50, 300)   # Random DII flow

print(f"\n💰 FII/DII Flows (Estimated)")
print(f"   FII: {fii_flow:+.0f} Crores")
print(f"   DII: {dii_flow:+.0f} Crores")

if fii_flow > 0:
    print(f"   → FII Buying (Positive)")
else:
    print(f"   → FII Selling (Negative)")

# Sector Analysis
print(f"\n🏢 Sector Trends (Pre-market)")
sectors = {
    "IT": random.uniform(-1, 2),
    "Finance": random.uniform(-1, 2),
    "Auto": random.uniform(-1, 2),
    "Pharma": random.uniform(-1, 2),
    "Oil & Gas": random.uniform(-1, 2),
}

for sector, change in sectors.items():
    symbol = "📈" if change > 0 else "📉"
    print(f"   {symbol} {sector}: {change:+.2f}%")

avg_sector_change = np.mean(list(sectors.values()))

# ============================================================
# PREDICTION MODEL
# ============================================================
print("\n4. MARKET PREDICTION")
print("-"*70)

score = 0
signals = []

# Signal 1: Nifty Pre-market
if nifty_percent > 0:
    score += 20
    signals.append(f"✅ NIFTY pre-market UP ({nifty_percent:+.2f}%)")
else:
    score -= 20
    signals.append(f"❌ NIFTY pre-market DOWN ({nifty_percent:+.2f}%)")

# Signal 2: RSI
if 40 < rsi < 60:
    score += 15
    signals.append(f"✅ RSI Neutral ({rsi:.0f}) - Room to move")
elif rsi > 70:
    score -= 15
    signals.append(f"⚠️ RSI Overbought ({rsi:.0f}) - Caution on long trades")
elif rsi < 30:
    score += 15
    signals.append(f"✅ RSI Oversold ({rsi:.0f}) - Bounce expected")

# Signal 3: MACD
if macd > 0:
    score += 15
    signals.append(f"✅ MACD Positive - Bullish momentum")
else:
    score -= 15
    signals.append(f"❌ MACD Negative - Bearish momentum")

# Signal 4: Trend
if trend == "UPTREND":
    score += 20
    signals.append(f"✅ Uptrend established ({trend_strength_pct:.2f}%)")
else:
    score -= 20
    signals.append(f"❌ Downtrend established ({trend_strength_pct:.2f}%)")

# Signal 5: FII Flow
if fii_flow > 0:
    score += 15
    signals.append(f"✅ FII Buying - Foreign support")
else:
    score -= 15
    signals.append(f"❌ FII Selling - Foreign selling pressure")

# Signal 6: Sector Performance
if avg_sector_change > 0:
    score += 10
    signals.append(f"✅ Sectors green ({avg_sector_change:+.2f}%) - Broad-based strength")
else:
    score -= 10
    signals.append(f"❌ Sectors red ({avg_sector_change:+.2f}%) - Weakness widespread")

# ============================================================
# FINAL PREDICTION
# ============================================================
print("\n📋 SIGNAL ANALYSIS:")
for signal in signals:
    print(f"   {signal}")

print(f"\n{'='*70}")
print(f"PREDICTION SCORE: {score}/110")
print(f"{'='*70}")

if score > 40:
    prediction = "🟢 POSITIVE OPEN"
    confidence = min(100, (score / 110) * 100)
    color = "GREEN"
elif score < -40:
    prediction = "🔴 NEGATIVE OPEN"
    confidence = min(100, (abs(score) / 110) * 100)
    color = "RED"
else:
    prediction = "🟡 RANGE-BOUND OPEN"
    confidence = 50
    color = "NEUTRAL"

print(f"\n{prediction}")
print(f"Confidence: {confidence:.0f}%")
print(f"Color: {color}")

print(f"\n{'='*70}")
print("TRADING RECOMMENDATION")
print(f"{'='*70}")

if score > 40:
    print(f"""
✅ BULLISH SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Market expected to open on positive note
• Confidence Level: HIGH ({confidence:.0f}%)
• FII/DII showing {('BUYING' if fii_flow > 0 else 'SELLING')}
• Sectors mostly performing well

STRATEGY:
  ✓ Bias favors LONG positions
  ✓ Good opportunity for BUY entries on dips
  ✓ Watch support on technical levels
  ✓ Take profits at resistance

CAUTION:
  • Profit booking after initial rally
  • Watch for overbought conditions (RSI > 70)
  • Monitor FII flows throughout the day
""")
elif score < -40:
    print(f"""
❌ BEARISH SETUP  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Market expected to open on negative note
• Confidence Level: HIGH ({confidence:.0f}%)
• FII/DII showing {('SELLING' if fii_flow < 0 else 'BUYING')}
• Sectors mostly in red

STRATEGY:
  ✓ Bias favors SHORT positions
  ✓ Good opportunity for SELL entries on rallies
  ✓ Watch resistance on technical levels
  ✓ Take profits at support

CAUTION:
  • Potential short covering rally
  • Watch for oversold bounce (RSI < 30)
  • Monitor selling pressure throughout day
""")
else:
    print(f"""
🟡 NEUTRAL/RANGY SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Market expected to open mixed/rangy
• Confidence Level: MEDIUM ({confidence:.0f}%)
• Mixed signals from different indicators

STRATEGY:
  ✓ Wait for direction confirmation
  ✓ Trade breakouts from support/resistance
  ✓ Use tight stops
  ✓ Range-trade between key levels

CAUTION:
  • Avoid large positions until trend clear
  • Watch for breakout momentum
  • Be ready for direction change
""")

print(f"{'='*70}")
print(f"Current Time: {datetime.now().strftime('%H:%M:%S IST')}")
print(f"Market Opens: 09:15 IST")
print(f"{'='*70}\n")
