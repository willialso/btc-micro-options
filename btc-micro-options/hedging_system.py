# hedging_system.py
import time
import json
import asyncio
import random
import aiohttp
from datetime import datetime, timedelta

class CrossPlatformHedging:
    def __init__(self, liquidity_pool_size=1200000):
        self.liquidity = liquidity_pool_size
        self.platforms = {
            "binance": {"url": "wss://stream.binance.com:9443/ws/btcusdt@ticker", "weight": 0.4, "status": "active"},
            "coinbase": {"url": "wss://ws-feed.pro.coinbase.com", "weight": 0.3, "status": "active"},
            "kraken": {"url": "wss://ws.kraken.com", "weight": 0.2, "status": "active"},
            "ftx": {"url": "wss://ftx.com/ws/", "weight": 0.1, "status": "backup"}
        }
        self.hedge_positions = []
        self.hedge_distribution = {}
        self.fallback_triggered = False
        self.last_rebalance = datetime.now()
        self.rebalance_frequency = 15  # seconds
        
    async def connect_to_platforms(self):
        """Establish connections to multiple platforms for price feeds and hedging"""
        active_connections = {}
        
        for platform, config in self.platforms.items():
            if config["status"] == "active":
                try:
                    # Simulate connection to different platforms
                    print(f"Connecting to {platform}...")
                    # In a real implementation, this would establish WebSocket connections
                    active_connections[platform] = True
                except Exception as e:
                    print(f"Failed to connect to {platform}: {e}")
                    self._trigger_fallback(platform)
        
        return active_connections
    
    def _trigger_fallback(self, failed_platform):
        """Activate fallback platform when a primary platform fails"""
        print(f"⚠️ Platform {failed_platform} failed! Triggering fallback mechanism...")
        
        # Find a backup platform to activate
        for platform, config in self.platforms.items():
            if config["status"] == "backup":
                self.platforms[platform]["status"] = "active"
                self.platforms[failed_platform]["status"] = "failed"
                
                # Redistribute weights
                failed_weight = self.platforms[failed_platform]["weight"]
                self.platforms[platform]["weight"] = failed_weight
                
                print(f"✅ Activated {platform} as fallback with weight {failed_weight}")
                self.fallback_triggered = True
                break
        
        # If no backup is available, redistribute among remaining active platforms
        if not self.fallback_triggered:
            active_platforms = [p for p, c in self.platforms.items() 
                              if c["status"] == "active" and p != failed_platform]
            
            if active_platforms:
                failed_weight = self.platforms[failed_platform]["weight"]
                weight_per_platform = failed_weight / len(active_platforms)
                
                for platform in active_platforms:
                    self.platforms[platform]["weight"] += weight_per_platform
                
                print(f"✅ Redistributed weight among remaining {len(active_platforms)} platforms")
                self.platforms[failed_platform]["status"] = "failed"
            else:
                print("❌ CRITICAL: All platforms failed!")
    
    async def distribute_hedges(self, portfolio_delta):
        """Distribute hedging across multiple platforms based on weights"""
        if abs(portfolio_delta) < 0.01:
            return {"status": "skipped", "reason": "delta too small"}
            
        # Calculate hedge amounts for each platform
        self.hedge_distribution = {}
        active_platforms = {p: c for p, c in self.platforms.items() if c["status"] == "active"}
        
        # Normalize weights
        total_weight = sum(c["weight"] for c in active_platforms.values())
        normalized_weights = {p: c["weight"]/total_weight for p, c in active_platforms.items()}
        
        # Distribute hedge positions
        for platform, weight in normalized_weights.items():
            hedge_amount = -portfolio_delta * weight  # Negative to offset delta
            self.hedge_distribution[platform] = {
                "amount": hedge_amount,
                "execution_price": None,
                "status": "pending"
            }
        
        # Simulate executing hedges on each platform
        for platform, hedge in self.hedge_distribution.items():
            try:
                # Simulate slight price differences between platforms (0.1% range)
                price_variation = random.uniform(0.999, 1.001)
                execution_price = self.current_price * price_variation
                
                # In a real implementation, this would execute trades via API
                await asyncio.sleep(0.1)  # Simulate network latency
                
                self.hedge_distribution[platform]["execution_price"] = execution_price
                self.hedge_distribution[platform]["status"] = "executed"
                self.hedge_positions.append({
                    "platform": platform,
                    "amount": hedge["amount"],
                    "price": execution_price,
                    "timestamp": datetime.now(),
                    "type": "perpetual_swap"  # Using perpetual swaps for hedging
                })
                
                print(f"✅ Executed hedge on {platform}: {hedge['amount']:.4f} BTC @ ${execution_price:.2f}")
                
            except Exception as e:
                print(f"❌ Failed to execute hedge on {platform}: {e}")
                self.hedge_distribution[platform]["status"] = "failed"
                self._trigger_fallback(platform)
                
        return self.hedge_distribution
    
    async def check_and_rebalance(self, portfolio_delta):
        """Check if rebalance is needed and execute if necessary"""
        now = datetime.now()
        
        if (now - self.last_rebalance).total_seconds() < self.rebalance_frequency:
            return {"status": "skipped", "reason": "too soon"}
        
        # Calculate current net delta across all platforms
        current_hedge_delta = sum(pos["amount"] for pos in self.hedge_positions)
        net_delta = portfolio_delta + current_hedge_delta
        
        # Rebalance if net delta exceeds threshold
        if abs(net_delta) > 0.1:
            print(f"🔄 Rebalancing hedges. Net delta: {net_delta:.4f}")
            result = await self.distribute_hedges(net_delta)
            self.last_rebalance = now
            return {"status": "rebalanced", "net_delta": net_delta, "result": result}
        
        return {"status": "balanced", "net_delta": net_delta}
    
    def update_liquidity_from_hedges(self):
        """Update platform liquidity based on hedge positions"""
        # Calculate PnL of hedge positions
        hedge_pnl = 0
        for position in self.hedge_positions:
            # In a real implementation, this would calculate actual PnL
            price_change = random.uniform(-0.001, 0.001) * self.current_price
            position_pnl = position["amount"] * price_change
            hedge_pnl += position_pnl
        
        # Update liquidity
        previous_liquidity = self.liquidity
        self.liquidity += hedge_pnl
        
        return {
            "previous_liquidity": previous_liquidity,
            "current_liquidity": self.liquidity,
            "pnl": hedge_pnl
        }
    
    @property
    def current_price(self):
        """Get current BTC price (simulated)"""
        return 40000 + random.uniform(-500, 500)
