# option_pricing.py
import numpy as np
import scipy.stats as stats
import math
import datetime

class MicroOptionPricing:
    def __init__(self, risk_free_rate=0.03, volatility=0.7):
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
    
    def call_price(self, S, K, T):
        """
        Calculate European-style call option price using Black-Scholes
        S: Current price of underlying
        K: Strike price
        T: Time to maturity in years
        """
        if T <= 0:
            # At expiry, call option value is max(0, S-K)
            return max(0, S - K)
        
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * self.volatility**2) * T) / (self.volatility * np.sqrt(T))
        d2 = d1 - self.volatility * np.sqrt(T)
        
        call = S * stats.norm.cdf(d1) - K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(d2)
        return call
    
    def put_price(self, S, K, T):
        """
        Calculate European-style put option price using Black-Scholes
        S: Current price of underlying
        K: Strike price
        T: Time to maturity in years
        """
        if T <= 0:
            # At expiry, put option value is max(0, K-S)
            return max(0, K - S)
        
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * self.volatility**2) * T) / (self.volatility * np.sqrt(T))
        d2 = d1 - self.volatility * np.sqrt(T)
        
        put = K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
        return put
    
    def calculate_greeks(self, S, K, T, option_type='call'):
        """
        Calculate option Greeks for risk management
        S: Current price of underlying
        K: Strike price
        T: Time to maturity in years
        option_type: 'call' or 'put'
        """
        if T <= 0:
            # At expiry
            if option_type == 'call':
                delta = 1.0 if S > K else 0.0
            else:  # put
                delta = -1.0 if S < K else 0.0
            return {'delta': delta, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
            
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * self.volatility**2) * T) / (self.volatility * np.sqrt(T))
        d2 = d1 - self.volatility * np.sqrt(T)
        
        # Calculate Greeks
        norm_d1 = stats.norm.cdf(d1)
        norm_prime_d1 = stats.norm.pdf(d1)
        
        # Delta
        if option_type == 'call':
            delta = norm_d1
        else:
            delta = norm_d1 - 1
            
        # Gamma (same for calls and puts)
        gamma = norm_prime_d1 / (S * self.volatility * np.sqrt(T))
        
        # Theta (time decay)
        if option_type == 'call':
            theta = -S * norm_prime_d1 * self.volatility / (2 * np.sqrt(T)) - self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(d2)
        else:
            theta = -S * norm_prime_d1 * self.volatility / (2 * np.sqrt(T)) + self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(-d2)
        
        # Vega (volatility sensitivity)
        vega = S * np.sqrt(T) * norm_prime_d1
        
        return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}

    def implied_volatility(self, S, K, T, market_price, option_type='call'):
        """
        Calculate implied volatility from market price
        """
        precision = 0.00001
        max_iterations = 100
        
        # Initial guess for volatility
        vol = 0.3
        
        for i in range(max_iterations):
            if option_type == 'call':
                price = self.call_price(S, K, T)
            else:
                price = self.put_price(S, K, T)
            
            diff = market_price - price
            
            if abs(diff) < precision:
                return vol
                
            # Approximate derivative of price with respect to volatility
            self.volatility = vol + 0.001
            if option_type == 'call':
                price_up = self.call_price(S, K, T)
            else:
                price_up = self.put_price(S, K, T)
            
            vega = (price_up - price) / 0.001
            
            # Restore original volatility
            self.volatility = vol
            
            # Update volatility estimate
            if abs(vega) < 0.00001:
                break
            
            vol = vol + diff / vega
            
            # Bounds check
            if vol < 0.01:
                vol = 0.01
            elif vol > 5:
                vol = 5
                
        return vol
