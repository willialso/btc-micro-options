# BTC Micro Spot Options Platform

A sophisticated Bitcoin micro spot options trading platform with real-time pricing, dynamic hedging, and automated exercise at expiration.

## Features

- **European-Style Spot Options**: Options on spot BTC price that can only be exercised at expiration (120 seconds)
- **Auto-Exercise at Expiry**: In-the-money options are automatically exercised at expiration, as is standard for European-style options
- **Real-time BTC Price Feed**: Live connection to Coinbase Pro WebSocket for accurate pricing
- **Cross-Platform Hedging**: Delta-gamma hedging across multiple exchanges with automatic failover mechanisms
- **Self-Balancing Liquidity**: $1.2M liquidity pool maintained through sophisticated hedging strategies
- **Dynamic Fee Adjustment**: Fees that automatically adapt based on market conditions and competitor rates

## How It Works

### Option Creation and Pricing

The platform uses the Black-Scholes model to price European-style options on Bitcoin. Traders can create options with:

- Option type: Call or Put
- Strike price: Custom or preset (ATM, ITM, OTM)
- Fixed expiry: 120 seconds
- Custom quantity

### Expiration and Settlement

At expiration (120 seconds after creation):

1. If an option is in-the-money (current BTC price is above the strike for calls, or below the strike for puts), it is **automatically exercised**
2. The payoff is calculated as the intrinsic value: `max(0, price - strike)` for calls or `max(0, strike - price)` for puts
3. The settlement amount is credited to the trader's account
4. Options that expire out-of-the-money expire worthless

As these are European-style options:
- They **cannot** be exercised before expiration
- In-the-money options at expiry are **always** automatically exercised (no contrary instructions allowed)

### Risk Management

The platform calculates real-time Greeks (Delta, Gamma, Theta, Vega) for comprehensive risk management. The liquidity pool is protected through:

- Multi-exchange hedging that distributes risk
- Automatic failover if any exchange experiences issues
- Dynamic rebalancing based on portfolio delta exposure

## Technical Details

- **Framework**: Flask backend with JavaScript frontend
- **Price Feed**: WebSocket connection to major crypto exchanges
- **Option Pricing**: Black-Scholes model adapted for cryptocurrency volatility
- **Hedging**: Cross-platform delta-neutral strategy 
- **Settlement**: Simulated Web3 integration for automatic exercise

## Installation

1. Clone the repository:
