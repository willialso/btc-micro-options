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
