import numpy as np
import pandas as pd
from scipy.signal import find_peaks

class PatternDetector:
    """Detect high-probability price patterns in SENSEX market data"""
    
    def __init__(self, data_frame):
        self.df = data_frame
        self.prices = data_frame['close'].values
        self.highs = data_frame['high'].values
        self.lows = data_frame['low'].values
        
    def find_pivots(self, window=5):
        """Find local highs and lows (pivots) for pattern detection"""
        # peaks: local maxima, troughs: local minima
        peaks, _ = find_peaks(self.highs, distance=window)
        troughs, _ = find_peaks(-self.lows, distance=window)
        
        pivots = []
        for p in peaks: pivots.append({'index': p, 'price': self.highs[p], 'type': 'high'})
        for t in troughs: pivots.append({'index': t, 'price': self.lows[t], 'type': 'low'})
        
        # Sort by index
        pivots.sort(key=lambda x: x['index'])
        return pivots

    def detect_head_and_shoulders(self):
        """Detect Head & Shoulders (83-89% Success)"""
        pivots = self.find_pivots()
        if len(pivots) < 5: return None
        
        # Look at last 5 pivots: L-Shoulder (H), Head (H), R-Shoulder (H)
        highs = [p for p in pivots if p['type'] == 'high'][-3:]
        if len(highs) < 3: return None
        
        s1, head, s2 = highs[0], highs[1], highs[2]
        
        # Conditions: Head > Shoulders, Shoulders roughly equal
        if head['price'] > s1['price'] and head['price'] > s2['price']:
            shoulder_diff = abs(s1['price'] - s2['price']) / s1['price']
            if shoulder_diff < 0.05: # 5% tolerance
                return {'pattern': 'Head & Shoulders', 'confidence': 0.85, 'type': 'Bearish Reversal'}
        return None

    def detect_double_bottom(self):
        """Detect Double Bottom (88% Success)"""
        pivots = self.find_pivots()
        lows = [p for p in pivots if p['type'] == 'low'][-2:]
        if len(lows) < 2: return None
        
        l1, l2 = lows[0], lows[1]
        diff = abs(l1['price'] - l2['price']) / l1['price']
        
        if diff < 0.01: # 1% tolerance for "equal" bottoms
            return {'pattern': 'Double Bottom', 'confidence': 0.88, 'type': 'Bullish Reversal'}
        return None

    def detect_flag_pennant(self):
        """Detect Flag/Pennant (85% Success) - Best for Day Trading"""
        if len(self.prices) < 20: return None
        
        # Look for a vertical "pole" (sharp move) followed by consolidation
        recent_move = (self.prices[-1] - self.prices[-20]) / self.prices[-20]
        if abs(recent_move) > 0.02: # 2% move in 20 periods
            # Check for low volatility consolidation (flag)
            consolidation = self.prices[-5:]
            std_dev = np.std(consolidation) / np.mean(consolidation)
            if std_dev < 0.005: 
                return {'pattern': 'Flag/Pennant', 'confidence': 0.85, 'type': 'Continuation'}
        return None

    def get_highest_probability_setup(self):
        """Analyze all patterns and return the best one"""
        patterns = [
            self.detect_head_and_shoulders(),
            self.detect_double_bottom(),
            self.detect_flag_pennant()
        ]
        
        # Filter None and sort by confidence
        valid_patterns = [p for p in patterns if p]
        if not valid_patterns: return None
        
        return max(valid_patterns, key=lambda x: x['confidence'])
