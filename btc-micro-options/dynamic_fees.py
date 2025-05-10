# dynamic_fees.py
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta

class DynamicFeeAdjuster:
    def __init__(self):
        # Base fee parameters
        self.base_fee_rate = 0.0015  # 0.15%
        self.min_fee_rate = 0.0005   # 0.05%
        self.max_fee_rate = 0.0030   # 0.30%
        
        # Competitor fee tracking
        self.competitor_fees = {
            "binance": 0.0010,
            "coinbase": 0.0020,
            "dydx": 0.0010,
            "uniswap": 0.0030,
            "sushiswap": 0.0025
        }
        
        # Market condition tracking
        self.market_volatility = 0.0
        self.trading_volume = 0
        self.last_update = datetime.now()
        self.update_frequency = 60  # seconds
        
        # Fee adjustment history
        self.fee_history = []
        self.current_fee = self.base_fee_rate
        
    def scan_competitor_fees(self):
        """Scan competitor fees from APIs (simulated)"""
        # In a real implementation, this would fetch actual competitor fees
        # Here we simulate small random changes to represent market dynamics
        for platform in self.competitor_fees:
            # Simulate minor fee adjustments from competitors
            adjustment = np.random.normal(0, 0.0001)
            new_fee = max(0.0001, min(0.005, self.competitor_fees[platform] + adjustment))
            self.competitor_fees[platform] = new_fee
            
        return self.competitor_fees
        
    def calculate_volatility_factor(self, recent_prices):
        """Calculate fee adjustment factor based on market volatility"""
        if len(recent_prices) < 10:
            return 1.0
            
        # Calculate recent volatility
        returns = np.diff(recent_prices) / recent_prices[:-1]
        recent_volatility = np.std(returns) * np.sqrt(365 * 24)  # Annualized
        
        # Update stored volatility
        self.market_volatility = recent_volatility
        
        # Higher volatility = higher fees (up to a cap)
        volatility_factor = 1.0 + (recent_volatility - 0.7) * 0.5
        return max(0.8, min(1.5, volatility_factor))
        
    def calculate_volume_factor(self, recent_volume):
        """Calculate fee adjustment factor based on trading volume"""
        # Higher volume = lower fees to reward liquidity
        if recent_volume > 1000000:  # $1M
            return 0.8
        elif recent_volume > 500000:  # $500k
            return 0.9
        elif recent_volume < 100000:  # $100k
            return 1.2
        else:
            return 1.0
    
    def calculate_competitive_factor(self):
        """Calculate fee adjustment to stay competitive"""
        # Get average competitor fee
        avg_competitor_fee = np.mean(list(self.competitor_fees.values()))
        
        # Our target is to be slightly lower than average
        target_fee = avg_competitor_fee * 0.95
        
        # Calculate adjustment factor
        if self.base_fee_rate > 0:
            competitive_factor = target_fee / self.base_fee_rate
        else:
            competitive_factor = 1.0
            
        return max(0.7, min(1.3, competitive_factor))
    
    def update_fee_rate(self, recent_prices=None, recent_volume=0):
        """Update fee rate based on all factors"""
        now = datetime.now()
        
        # Only update at specified frequency
        if (now - self.last_update).total_seconds() < self.update_frequency:
            return self.current_fee
            
        # Scan competitor fees
        self.scan_competitor_fees()
        
        # Calculate adjustment factors
        volatility_factor = self.calculate_volatility_factor(recent_prices if recent_prices else [40000])
        volume_factor = self.calculate_volume_factor(recent_volume)
        competitive_factor = self.calculate_competitive_factor()
        
        # Calculate new fee rate
        combined_factor = (volatility_factor * 0.4) + (volume_factor * 0.3) + (competitive_factor * 0.3)
        new_fee = self.base_fee_rate * combined_factor
        
        # Apply min/max constraints
        new_fee = max(self.min_fee_rate, min(self.max_fee_rate, new_fee))
        
        # Record fee adjustment
        self.fee_history.append({
            "timestamp": now,
            "fee_rate": new_fee,
            "volatility_factor": volatility_factor,
            "volume_factor": volume_factor,
            "competitive_factor": competitive_factor,
            "avg_competitor_fee": np.mean(list(self.competitor_fees.values()))
        })
        
        print(f"💰 Updated fee rate: {new_fee*100:.3f}% (volatility: {volatility_factor:.2f}, volume: {volume_factor:.2f}, competitive: {competitive_factor:.2f})")
        
        self.current_fee = new_fee
        self.last_update = now
        
        return new_fee
