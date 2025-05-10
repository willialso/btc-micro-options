# main.py
import asyncio
import json
import time
import random
import pandas as pd
import numpy as np
import threading
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response
from threading import Thread

from btc_data_feed import BTCDataFeed
from option_pricing import MicroOptionPricing
from hedging_system import CrossPlatformHedging
from dynamic_fees import DynamicFeeAdjuster
from web3_simulator import Web3Simulator

class BTCMicroOptionsSystem:
    def __init__(self, initial_liquidity=1200000):
        # Initialize components
        self.data_feed = BTCDataFeed(self.on_price_update)
        self.pricing_model = MicroOptionPricing()
        self.hedging_system = CrossPlatformHedging(liquidity_pool_size=initial_liquidity)
        self.fee_adjuster = DynamicFeeAdjuster()
        self.web3_simulator = Web3Simulator()
        
        # Portfolio tracking
        self.options = []
        self.liquidity = initial_liquidity
        self.price_history = []
        self.max_history_length = 1000
        self.portfolio_metrics = {
            'delta': 0,
            'gamma': 0,
            'theta': 0,
            'vega': 0
        }
        self.last_rebalance_time = None
        
        # Performance tracking
        self.platform_stats = {
            'trades': 0,
            'volume': 0,
            'fees_collected': 0,
            'hedging_costs': 0,
            'pnl': 0
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()
        self.is_running = False
    
    async def start(self):
        """Start the entire platform"""
        self.is_running = True
        
        # Connect to exchanges for hedging
        await self.hedging_system.connect_to_platforms()
        
        # Start price feed in a separate thread
        price_thread = Thread(target=self.data_feed.run)
        price_thread.daemon = True
        price_thread.start()
        
        # Run the main simulation loop
        simulation_task = asyncio.create_task(self.simulation_loop())
        
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass
    
    async def simulation_loop(self):
        """Main simulation loop"""
        while self.is_running:
            try:
                # Process expired options
                await self.process_option_expirations()
                
                # Update portfolio metrics
                self.update_portfolio_metrics()
                
                # Rebalance hedges if needed
                await self.hedging_system.check_and_rebalance(self.portfolio_metrics['delta'])
                
                # Update liquidity from hedging
                liquidity_update = self.hedging_system.update_liquidity_from_hedges()
                self.liquidity = liquidity_update["current_liquidity"]
                
                # Dynamic fee adjustment
                if self.price_history:
                    prices = [p['price'] for p in self.price_history[-30:]]
                    volume = self.platform_stats['volume'] or 100000  # Default if no volume yet
                    new_fee = self.fee_adjuster.update_fee_rate(prices, volume)
                
                await asyncio.sleep(1)  # Main loop frequency
                
            except Exception as e:
                print(f"Error in simulation loop: {e}")
                await asyncio.sleep(1)
    
    def on_price_update(self, price_data):
        """Handle price updates from the data feed"""
        with self.lock:
            # Store price history
            self.price_history.append(price_data)
            if len(self.price_history) > self.max_history_length:
                self.price_history.pop(0)
    
    async def create_option(self, option_type, strike_price, expiry_seconds, quantity=1):
        """Create a new option contract"""
        with self.lock:
            current_price = self.data_feed.current_data['price']
            
            # Calculate time to expiry in years
            time_to_expiry = expiry_seconds / (365 * 24 * 60 * 60)
            
            # Calculate option premium
            if option_type == 'call':
                base_premium = self.pricing_model.call_price(current_price, strike_price, time_to_expiry)
            else:  # put
                base_premium = self.pricing_model.put_price(current_price, strike_price, time_to_expiry)
            
            # Apply platform fee
            fee_rate = self.fee_adjuster.current_fee
            premium_with_fee = base_premium * (1 + fee_rate)
            
            # Create option in Web3 simulator
            option = self.web3_simulator.create_option(
                option_type, strike_price, expiry_seconds, premium_with_fee * quantity
            )
            
            # Set additional fields for tracking
            option['quantity'] = quantity
            option['base_premium'] = base_premium
            option['fee_rate'] = fee_rate
            option['fee_amount'] = base_premium * fee_rate * quantity
            option['entry_price'] = current_price
            
            # Calculate Greeks for this option
            greeks = self.pricing_model.calculate_greeks(
                current_price, strike_price, time_to_expiry, option_type)
            
            option['greeks'] = {
                'delta': greeks['delta'] * quantity,
                'gamma': greeks['gamma'] * quantity,
                'theta': greeks['theta'] * quantity,
                'vega': greeks['vega'] * quantity
            }
            
            # Add to options list
            self.options.append(option)
            
            # Update platform stats
            self.platform_stats['trades'] += 1
            self.platform_stats['volume'] += premium_with_fee * quantity
            self.platform_stats['fees_collected'] += option['fee_amount']
            
            # Update portfolio metrics
            self.update_portfolio_metrics()
            
            # Trigger hedging
            hedge_result = await self.hedging_system.check_and_rebalance(self.portfolio_metrics['delta'])
            
            # Log the transaction
            print(f"💎 Created {option_type} option: strike=${strike_price}, premium=${premium_with_fee:.2f}, expiry={expiry_seconds}s")
            
            return option
    
    async def process_option_expirations(self):
        """Check and process expired options"""
        current_price = self.data_feed.current_data['price']
        now = datetime.now()
        
        for option in self.options:
            if option['status'] != 'active':
                continue
                
            expiry_time = datetime.fromisoformat(option['expiry_time'])
            
            # Check if option has expired
            if now >= expiry_time:
                # Exercise option if in-the-money
                result = self.web3_simulator.exercise_option(option['id'], current_price)
                
                if result['exercised']:
                    print(f"💰 Option {option['id']} exercised at ${current_price:.2f}, payoff=${result['payoff']:.2f}")
                    # Update PnL
                    self.platform_stats['pnl'] -= result['payoff']
                else:
                    print(f"⏱️ Option {option['id']} expired worthless")
    
    def update_portfolio_metrics(self):
        """Calculate portfolio-wide Greeks"""
        current_price = self.data_feed.current_data['price']
        portfolio_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
        
        for option in self.options:
            if option['status'] != 'active':
                continue
                
            # Calculate time to expiry
            expiry_time = datetime.fromisoformat(option['expiry_time'])
            now = datetime.now()
            
            if now >= expiry_time:
                continue  # Skip expired options
                
            seconds_to_expiry = (expiry_time - now).total_seconds()
            time_to_expiry = seconds_to_expiry / (365 * 24 * 60 * 60)  # Convert to years
            
            # Calculate current Greeks
            greeks = self.pricing_model.calculate_greeks(
                current_price, option['strike'], time_to_expiry, option['type'])
            
            # Scale by quantity
            for key in greeks:
                portfolio_greeks[key] += greeks[key] * option['quantity']
        
        self.portfolio_metrics = portfolio_greeks
        return portfolio_greeks
    
    def get_platform_status(self):
        """Get overall platform status"""
        current_price = self.data_feed.current_data['price']
        
        return {
            'price': current_price,
            'liquidity': self.liquidity,
            'portfolio_metrics': self.portfolio_metrics,
            'active_options': sum(1 for o in self.options if o['status'] == 'active'),
            'total_options': len(self.options),
            'fee_rate': f"{self.fee_adjuster.current_fee*100:.3f}%",
            'hedging': {
                'platforms': self.hedging_system.platforms,
                'hedge_positions': len(self.hedging_system.hedge_positions)
            },
            'stats': self.platform_stats
        }

# Flask API for frontend
app = Flask(__name__)
options_system = BTCMicroOptionsSystem(initial_liquidity=1200000)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(options_system.get_platform_status())

@app.route('/api/options', methods=['GET'])
def get_options():
    return jsonify(options_system.options)

@app.route('/api/options', methods=['POST'])
def create_option():
    data = request.json
    loop = asyncio.new_event_loop()
    option = loop.run_until_complete(options_system.create_option(
        data.get('type', 'call'),
        float(data.get('strike', options_system.data_feed.current_data['price'])),
        int(data.get('expiry', 120)),  # Default 120 seconds
        float(data.get('quantity', 1))
    ))
    return jsonify(option)

@app.route('/api/price', methods=['GET'])
def get_price():
    return jsonify(options_system.data_feed.current_data)

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    return jsonify({
        'portfolio': options_system.portfolio_metrics,
        'fees': {
            'current': options_system.fee_adjuster.current_fee,
            'competitors': options_system.fee_adjuster.competitor_fees
        },
        'hedging': {
            'platforms': options_system.hedging_system.platforms,
            'positions': options_system.hedging_system.hedge_positions
        }
    })

def run_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(options_system.start())

if __name__ == "__main__":
    # Start the options system in a background thread
    system_thread = Thread(target=run_server)
    system_thread.daemon = True
    system_thread.start()
    
    # Run Flask API
    app.run(debug=True, port=5000)
