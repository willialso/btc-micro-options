# app.py
from flask import Flask, jsonify, request, render_template, Response, session
import json
import time
import datetime
import threading
import asyncio
import numpy as np
import random
import uuid
from datetime import timedelta
from lovable_integration import (
    lovable_auth_required,
    lovable_login,
    lovable_callback,
    lovable_logout,
    sync_with_lovable
)

# Define the Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')  # Required for session

# In-memory storage for simulation purposes
class SimulationState:
    def __init__(self, initial_liquidity=1200000):
        self.btc_price = 40000
        self.bid_price = 39950
        self.ask_price = 40050
        self.liquidity = initial_liquidity
        self.options = []
        self.hedge_positions = []
        self.fee_rate = 0.0015  # 0.15%
        self.fee_history = []
        self.volatility = 0.7  # Annualized volatility
        self.portfolio_delta = 0
        self.portfolio_gamma = 0
        self.portfolio_theta = 0
        self.portfolio_vega = 0
        self.exchanges = {
            "binance": {"status": "active", "weight": 0.4, "hedge_delta": 0},
            "coinbase": {"status": "active", "weight": 0.3, "hedge_delta": 0},
            "kraken": {"status": "active", "weight": 0.2, "hedge_delta": 0},
            "ftx": {"status": "backup", "weight": 0.1, "hedge_delta": 0}
        }
        self.competitor_fees = {
            "binance": 0.0010,
            "coinbase": 0.0020,
            "dydx": 0.0010,
            "uniswap": 0.0030,
            "sushiswap": 0.0025
        }
        self.price_history = []
        self.transactions = []
        self.last_rebalance = datetime.datetime.now()
        self.last_price_update = datetime.datetime.now()
        
        # Start price simulation thread
        self.should_run = True
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def run_simulation(self):
        """Simulate real-time price and platform behavior"""
        while self.should_run:
            # Update BTC price (small random walk with occasional jumps)
            price_change = np.random.normal(0, self.btc_price * 0.0005)
            
            # Add occasional price jumps (5% chance)
            if random.random() < 0.05:
                jump_size = np.random.normal(0, self.btc_price * 0.002)
                price_change += jump_size
            
            self.btc_price += price_change
            
            # Update bid-ask spread (wider during volatile periods)
            spread_factor = 1 + abs(price_change / self.btc_price) * 10
            spread = max(50, self.btc_price * 0.0005 * spread_factor)
            self.bid_price = self.btc_price - spread/2
            self.ask_price = self.btc_price + spread/2
            
            # Record price history
            self.price_history.append({
                'price': self.btc_price,
                'bid': self.bid_price,
                'ask': self.ask_price,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            # Limit history size
            if len(self.price_history) > 1000:
                self.price_history.pop(0)
            
            # Process option expirations
            self.process_expirations()
            
            # Update Greeks and hedge if needed
            self.update_portfolio_metrics()
            
            if (datetime.datetime.now() - self.last_rebalance).total_seconds() > 10:
                self.rebalance_hedges()
                self.last_rebalance = datetime.datetime.now()
            
            # Dynamically adjust fees (less frequently)
            if random.random() < 0.05:
                self.adjust_fees()
            
            # Occasionally simulate exchange issues (0.2% chance per cycle)
            if random.random() < 0.002:
                self.simulate_exchange_issue()
            
            self.last_price_update = datetime.datetime.now()
            
            # Short sleep to prevent CPU overuse
            time.sleep(0.5)
    
    def create_option(self, option_type, strike_price, expiry_seconds, quantity):
        """Create a new option contract"""
        current_time = datetime.datetime.now()
        expiry_time = current_time + timedelta(seconds=expiry_seconds)
        
        # Calculate option price
        time_to_expiry_years = expiry_seconds / (365 * 24 * 60 * 60)
        option_price = self.calculate_option_price(
            option_type, self.btc_price, strike_price, time_to_expiry_years
        )
        
        # Calculate greeks
        greeks = self.calculate_greeks(
            option_type, self.btc_price, strike_price, time_to_expiry_years
        )
        
        # Apply fee
        premium = option_price * (1 + self.fee_rate)
        fee_amount = option_price * self.fee_rate
        
        option = {
            'id': str(uuid.uuid4())[:8],
            'type': option_type,
            'strike': strike_price,
            'quantity': quantity,
            'premium': premium,
            'fee_amount': fee_amount,
            'creation_time': current_time.isoformat(),
            'expiry_time': expiry_time.isoformat(),
            'status': 'active',
            'entry_price': self.btc_price,
            'greeks': {
                'delta': greeks['delta'] * quantity,
                'gamma': greeks['gamma'] * quantity,
                'theta': greeks['theta'] * quantity,
                'vega': greeks['vega'] * quantity
            }
        }
        
        self.options.append(option)
        
        # Update liquidity
        self.liquidity += premium * quantity
        
        # Log transaction
        self.transactions.append({
            'type': 'create',
            'option_id': option['id'],
            'timestamp': current_time.isoformat(),
            'details': f"{option_type} option, strike ${strike_price}, premium ${premium:.2f}"
        })
        
        # Update portfolio metrics after new option
        self.update_portfolio_metrics()
        
        # Trigger hedge rebalance
        self.rebalance_hedges()
        
        return option
    
    def process_expirations(self):
        """Process expired options"""
        current_time = datetime.datetime.now()
        
        for option in self.options:
            if option['status'] != 'active':
                continue
                
            expiry_time = datetime.datetime.fromisoformat(option['expiry_time'])
            
            if current_time >= expiry_time:
                # Check if ITM
                if option['type'] == 'call':
                    is_itm = self.btc_price > option['strike']
                else:  # put
                    is_itm = self.btc_price < option['strike']
                
                if is_itm:
                    # Calculate payoff
                    if option['type'] == 'call':
                        payoff = max(0, self.btc_price - option['strike']) * option['quantity']
                    else:  # put
                        payoff = max(0, option['strike'] - self.btc_price) * option['quantity']
                    
                    option['status'] = 'exercised'
                    option['settlement_price'] = self.btc_price
                    option['payoff'] = payoff
                    
                    # Update liquidity
                    self.liquidity -= payoff
                    
                    # Log transaction
                    self.transactions.append({
                        'type': 'exercise',
                        'option_id': option['id'],
                        'timestamp': current_time.isoformat(),
                        'details': f"Exercise {option['type']} option, payoff ${payoff:.2f}"
                    })
                else:
                    option['status'] = 'expired'
                    option['settlement_price'] = self.btc_price
                    option['payoff'] = 0
                    
                    # Log transaction
                    self.transactions.append({
                        'type': 'expire',
                        'option_id': option['id'],
                        'timestamp': current_time.isoformat(),
                        'details': f"Option expired worthless"
                    })
    
    def calculate_option_price(self, option_type, S, K, T):
        """Simple Black-Scholes calculation"""
        import math
        from scipy.stats import norm
        
        r = 0.03  # Risk-free rate
        sigma = self.volatility
        
        if T <= 0:
            # At expiry
            if option_type == 'call':
                return max(0, S - K)
            else:  # put
                return max(0, K - S)
        
        d1 = (math.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        if option_type == 'call':
            return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        else:  # put
            return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    def calculate_greeks(self, option_type, S, K, T):
        """Calculate option Greeks"""
        import math
        from scipy.stats import norm
        
        r = 0.03  # Risk-free rate
        sigma = self.volatility
        
        if T <= 0:
            # At expiry
            if option_type == 'call':
                delta = 1.0 if S > K else 0.0
            else:  # put
                delta = -1.0 if S < K else 0.0
            return {'delta': delta, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
        
        d1 = (math.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        # Calculate normal distribution values
        norm_d1 = norm.cdf(d1)
        norm_prime_d1 = norm.pdf(d1)
        
        # Delta
        if option_type == 'call':
            delta = norm_d1
        else:  # put
            delta = norm_d1 - 1
        
        # Gamma (same for calls and puts)
        gamma = norm_prime_d1 / (S * sigma * math.sqrt(T))
        
        # Theta
        if option_type == 'call':
            theta = -S * norm_prime_d1 * sigma / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d2)
        else:  # put
            theta = -S * norm_prime_d1 * sigma / (2 * math.sqrt(T)) + r * K * math.exp(-r * T) * norm.cdf(-d2)
        
        # Vega (same for calls and puts)
        vega = S * math.sqrt(T) * norm_prime_d1
        
        return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}
    
    def update_portfolio_metrics(self):
        """Update portfolio-wide Greeks"""
        portfolio_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
        
        # Loop through active options
        for option in self.options:
            if option['status'] != 'active':
                continue
                
            # Calculate time to expiry
            expiry_time = datetime.datetime.fromisoformat(option['expiry_time'])
            current_time = datetime.datetime.now()
            
            if current_time >= expiry_time:
                continue  # Skip expired options
                
            seconds_to_expiry = (expiry_time - current_time).total_seconds()
            time_to_expiry = seconds_to_expiry / (365 * 24 * 60 * 60)  # Convert to years
            
            # Recalculate Greeks with current price and time
            greeks = self.calculate_greeks(
                option['type'], self.btc_price, option['strike'], time_to_expiry
            )
            
            # Update option Greeks
            option['greeks'] = {
                'delta': greeks['delta'] * option['quantity'],
                'gamma': greeks['gamma'] * option['quantity'],
                'theta': greeks['theta'] * option['quantity'],
                'vega': greeks['vega'] * option['quantity']
            }
            
            # Sum for portfolio metrics
            for greek in portfolio_greeks:
                portfolio_greeks[greek] += option['greeks'][greek]
        
        # Update portfolio metrics
        self.portfolio_delta = portfolio_greeks['delta']
        self.portfolio_gamma = portfolio_greeks['gamma']
        self.portfolio_theta = portfolio_greeks['theta']
        self.portfolio_vega = portfolio_greeks['vega']
    
    def rebalance_hedges(self):
        """Rebalance hedges across exchanges"""
        # Calculate current hedge delta
        current_hedge_delta = sum(exch['hedge_delta'] for name, exch in self.exchanges.items() if exch['status'] == 'active')
        
        # Calculate needed adjustment
        net_delta = self.portfolio_delta + current_hedge_delta
        
        # Only rebalance if net delta exceeds threshold
        if abs(net_delta) < 0.05:
            return
        
        # Calculate required hedge adjustment
        adjustment_needed = -net_delta
        
        # Distribute adjustment across active exchanges
        active_exchanges = [name for name, exch in self.exchanges.items() if exch['status'] == 'active']
        if not active_exchanges:
            return
        
        total_weight = sum(self.exchanges[name]['weight'] for name in active_exchanges)
        
        for name in active_exchanges:
            exchange = self.exchanges[name]
            normalized_weight = exchange['weight'] / total_weight
            exchange_adjustment = adjustment_needed * normalized_weight
            
            # Add new hedge position
            hedge_price = self.btc_price * (1 + np.random.normal(0, 0.0005))  # Slight price variation
            
            self.hedge_positions.append({
                'exchange': name,
                'amount': exchange_adjustment,
                'price': hedge_price,
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            # Update exchange hedge delta
            exchange['hedge_delta'] += exchange_adjustment
        
        # Log transaction
        self.transactions.append({
            'type': 'hedge',
            'timestamp': datetime.datetime.now().isoformat(),
            'details': f"Rebalanced hedges across {len(active_exchanges)} exchanges, net adjustment: {adjustment_needed:.4f}"
        })
    
    def adjust_fees(self):
        """Dynamically adjust fee rate based on competitive positioning"""
        # Calculate average competitor fee
        avg_competitor_fee = sum(self.competitor_fees.values()) / len(self.competitor_fees)
        
        # Add small random changes to competitor fees
        for platform in self.competitor_fees:
            adjustment = np.random.normal(0, 0.0001)
            self.competitor_fees[platform] = max(0.0001, min(0.005, self.competitor_fees[platform] + adjustment))
        
        # Calculate volatility factor from recent price history
        if len(self.price_history) > 10:
            recent_prices = [p['price'] for p in self.price_history[-30:]]
            returns = np.diff(recent_prices) / recent_prices[:-1]
            recent_volatility = np.std(returns) * np.sqrt(365 * 24)  # Annualized
            volatility_factor = 1.0 + (recent_volatility - 0.7) * 0.5
            volatility_factor = max(0.8, min(1.5, volatility_factor))
        else:
            volatility_factor = 1.0
        
        # Adjust fee based on competitive positioning and volatility
        target_fee = avg_competitor_fee * 0.95 * volatility_factor
        
        # Smooth fee changes
        fee_change = (target_fee - self.fee_rate) * 0.3
        new_fee = self.fee_rate + fee_change
        
        # Apply constraints
        new_fee = max(0.0005, min(0.003, new_fee))
        
        # Record fee change
        self.fee_history.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'fee_rate': new_fee,
            'avg_competitor_fee': avg_competitor_fee,
            'volatility_factor': volatility_factor
        })
        
        # Update fee rate
        self.fee_rate = new_fee
    
    def simulate_exchange_issue(self):
        """Occasionally simulate an exchange failure to test fallback system"""
        active_exchanges = [name for name, exch in self.exchanges.items() if exch['status'] == 'active']
        
        if len(active_exchanges) <= 1:
            return  # Don't fail if only one exchange is left
        
        # Randomly select an exchange to fail
        failed_exchange = random.choice(active_exchanges)
        self.exchanges[failed_exchange]['status'] = 'failed'
        
        # Find backup to activate
        for name, exchange in self.exchanges.items():
            if exchange['status'] == 'backup':
                exchange['status'] = 'active'
                
                # Transfer hedge delta from failed exchange
                exchange['hedge_delta'] = self.exchanges[failed_exchange]['hedge_delta']
                self.exchanges[failed_exchange]['hedge_delta'] = 0
                
                # Log event
                self.transactions.append({
                    'type': 'exchange_fallback',
                    'timestamp': datetime.datetime.now().isoformat(),
                    'details': f"Exchange {failed_exchange} failed. Activated {name} as fallback."
                })
                break

# Initialize simulation state
simulation = SimulationState()

# API Routes
@app.route('/lovable/login')
def handle_lovable_login():
    return lovable_login()

@app.route('/lovable/callback')
def handle_lovable_callback():
    return lovable_callback()

@app.route('/lovable/logout')
def handle_lovable_logout():
    return lovable_logout()

@app.route('/')
@lovable_auth_required
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/price', methods=['GET'])
@lovable_auth_required
def get_price():
    """Get current BTC price data"""
    price_data = {
        'price': simulation.btc_price,
        'bid': simulation.bid_price,
        'ask': simulation.ask_price,
        'timestamp': datetime.datetime.now().isoformat(),
        'last_update': simulation.last_price_update.isoformat()
    }
    return jsonify(price_data)

@app.route('/api/price_history', methods=['GET'])
@lovable_auth_required
def get_price_history():
    """Get historical price data"""
    # Limit to 100 most recent points for performance
    history = simulation.price_history[-100:]
    return jsonify(history)

@app.route('/api/status', methods=['GET'])
@lovable_auth_required
def get_status():
    """Get platform status including liquidity and metrics"""
    active_options = sum(1 for o in simulation.options if o['status'] == 'active')
    
    status = {
        'price': simulation.btc_price,
        'liquidity': simulation.liquidity,
        'portfolio_metrics': {
            'delta': simulation.portfolio_delta,
            'gamma': simulation.portfolio_gamma,
            'theta': simulation.portfolio_theta,
            'vega': simulation.portfolio_vega
        },
        'active_options': active_options,
        'total_options': len(simulation.options),
        'fee_rate': simulation.fee_rate,
        'hedging': {
            'exchanges': simulation.exchanges,
            'hedge_positions': len(simulation.hedge_positions)
        },
        'last_rebalance': simulation.last_rebalance.isoformat()
    }
    return jsonify(status)

@app.route('/api/options', methods=['GET'])
@lovable_auth_required
def get_options():
    """Get list of all options"""
    return jsonify(simulation.options)

@app.route('/api/options', methods=['POST'])
@lovable_auth_required
def create_option():
    """Create a new option"""
    data = request.json
    
    option = simulation.create_option(
        data.get('type', 'call'),
        float(data.get('strike', simulation.btc_price)),
        int(data.get('expiry', 120)),
        float(data.get('quantity', 1))
    )
    
    # After creating the option, sync with Lovable
    sync_data = {
        'type': 'option_created',
        'option': option,
        'timestamp': datetime.datetime.now().isoformat()
    }
    sync_with_lovable(sync_data)
    return jsonify(option)

@app.route('/api/metrics', methods=['GET'])
@lovable_auth_required
def get_metrics():
    """Get detailed platform metrics including hedging and fees"""
    # Calculate hedge delta by exchange
    hedge_by_exchange = {}
    for name, exchange in simulation.exchanges.items():
        hedge_by_exchange[name] = exchange['hedge_delta']
    
    # Calculate net delta
    net_delta = simulation.portfolio_delta + sum(exchange['hedge_delta'] for exchange in simulation.exchanges.values())
    
    metrics = {
        'portfolio': {
            'delta': simulation.portfolio_delta,
            'gamma': simulation.portfolio_gamma,
            'theta': simulation.portfolio_theta,
            'vega': simulation.portfolio_vega,
            'net_delta': net_delta
        },
        'fees': {
            'current': simulation.fee_rate,
            'competitors': simulation.competitor_fees,
            'history': simulation.fee_history[-10:]  # Last 10 fee adjustments
        },
        'hedging': {
            'exchanges': simulation.exchanges,
            'by_exchange': hedge_by_exchange,
            'recent_positions': simulation.hedge_positions[-10:]  # Last 10 hedge positions
        },
        'transactions': simulation.transactions[-20:]  # Last 20 transactions
    }
    
    return jsonify(metrics)

@app.route('/api/events', methods=['GET'])
@lovable_auth_required
def get_events():
    """Server-sent events for real-time updates"""
    def generate():
        last_transaction_count = len(simulation.transactions)
        
        while True:
            # Check for new transactions
            current_count = len(simulation.transactions)
            if current_count > last_transaction_count:
                new_transactions = simulation.transactions[last_transaction_count:current_count]
                for tx in new_transactions:
                    yield f"data: {json.dumps({'type': 'transaction', 'data': tx})}\n\n"
                last_transaction_count = current_count
            
            # Send price update every 2 seconds
            price_data = {
                'price': simulation.btc_price,
                'bid': simulation.bid_price,
                'ask': simulation.ask_price
            }
            yield f"data: {json.dumps({'type': 'price', 'data': price_data})}\n\n"
            
            time.sleep(2)
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
