# BTC Micro Options Platform Simulator

This project is a sophisticated Bitcoin micro options trading platform with real-time pricing, dynamic hedging, and simulated Web3 integration. The platform demonstrates 120-second expiry options that automatically exercise at expiry if in-the-money.

## Features

- **Real-time BTC price feed** - Live BTC price simulation with bid/ask spreads
- **120-second expiry options** - Ultra-short expiry options for quick trading
- **Automatic exercise** - Options exercise automatically when in-the-money at expiry
- **Cross-platform hedging** - Delta-gamma hedging across multiple exchanges with fallback mechanisms
- **Dynamic fee adjustment** - Fee rates that adjust based on market conditions and competitor pricing
- **Self-balancing liquidity** - $1.2M liquidity pool that maintains balance through hedging
- **Full Greeks calculation** - Delta, gamma, theta, and vega for effective risk management
- **Simulated Web3 integration** - Simulates on-chain settlement without actual blockchain transactions

## Installation

### Prerequisites

- Python 3.8 or higher
- Flask
- NumPy
- SciPy
- Chart.js (included via CDN)

### Setup

1. Clone the repository:
2. Create a virtual environment:
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate


3. Install dependencies:
pip install flask numpy scipy


4. Run the application:
python app.py


5. Open your browser and navigate to:
http://localhost:5000


## Application Structure

- `app.py` - Main Flask application with API endpoints and simulation logic
- `static/css/style.css` - CSS styles for the platform
- `static/js/app.js` - Frontend JavaScript for the trading interface
- `templates/index.html` - Main HTML template

## Demo Instructions

1. **Create Option**:
- Select option type (Call/Put)
- Choose a strike price (ATM, ITM, OTM)
- Adjust quantity if needed
- Click "Create Option"

2. **Monitor Options**:
- Active options appear in the portfolio section
- Options automatically exercise at expiry if in-the-money
- Watch for notification alerts when options exercise or expire

3. **Observe Hedging**:
- Track delta and gamma exposure in the portfolio section
- View cross-platform hedging distribution in the Advanced tab
- Notice automatic fallback if an exchange fails

4. **Dynamic Fees**:
- See how fees adjust based on market conditions
- Compare fees with competitors in the Fees tab

## Technical Details

### Option Pricing

The platform uses the Black-Scholes model with adjustments for the unique characteristics of cryptocurrency options, including:

- Higher volatility assumptions (70% annualized by default)
- Ultra-short expiry handling (120 seconds)
- Wider bid-ask spreads during volatile periods

### Delta-Gamma Hedging

The hedging system:
- Calculates portfolio-wide Greeks (Delta, Gamma, Theta, Vega)
- Distributes hedges across multiple exchanges based on weight and reliability
- Automatically rebalances to maintain delta neutrality
- Implements fallback mechanisms if exchanges fail

### Web3 Integration (Simulated)

The platform simulates smart contract interactions for:
- Option creation and premium collection
- Automatic exercise at expiry for in-the-money options
- Settlement payments for exercised options

## Customization

The following parameters can be adjusted in the code:

- `initial_liquidity`: Initial liquidity pool size (default: $1,200,000)
- `volatility`: Annualized volatility assumption (default: 0.7 or 70%)
- `risk_free_rate`: Risk-free rate for option pricing (default: 0.03 or 3%)
- `base_fee_rate`: Base fee rate before adjustments (default: 0.0015 or 0.15%)

## Investor Notes

This platform demonstrates several innovative features:

1. **No Liquidity Provider Required**: Self-balancing liquidity through sophisticated hedging
2. **Hybrid Web2/Web3 Architecture**: Combines traditional exchange infrastructure with blockchain settlement
3. **Multi-Platform Hedging**: Reduces risk through diversification and automatic failover
4. **Competitive Fee Structure**: Dynamic fee adjustment to maintain market competitiveness

The platform is designed to be easily integrated with actual Web3 infrastructure for production deployment.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
