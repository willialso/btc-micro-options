# option_pricing.py
import numpy as np
import scipy.stats as stats
import math

class MicroOptionPricing:
    def __init__(self, risk_free_rate=0.03, volatility=0.7):
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
    
    def call_price(self, S, K, T):
        """Calculate call option price using Black-Scholes"""
        if T <= 0:
            return max(0, S - K)
            
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * self.volatility**2) * T) / (self.volatility * np.sqrt(T))
        d2 = d1 - self.volatility * np.sqrt(T)
        
        call = S * stats.norm.cdf(d1) - K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(d2)
        return call
    
    def put_price(self, S, K, T):
        """Calculate put option price using Black-Scholes"""
        if T <= 0:
            return max(0, K - S)
            
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * self.volatility**2) * T) / (self.volatility * np.sqrt(T))
        d2 = d1 - self.volatility * np.sqrt(T)
        
        put = K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
        return put
    
    def calculate_greeks(self, S, K, T, option_type='call'):
        """Calculate option Greeks"""
        if T <= 0:
            # At expiry
            if option_type == 'call':
                return {'delta': 1.0 if S > K else 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
            else:
                return {'delta': -1.0 if S < K else 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
        
        d1 = (np.log(S/K) + (self.risk_free_rate + 0.5 * self.volatility**2) * T) / (self.volatility * np.sqrt(T))
        d2 = d1 - self.volatility * np.sqrt(T)
        
        # Calculate common terms
        norm_d1 = stats.norm.cdf(d1)
        norm_prime_d1 = stats.norm.pdf(d1)
        
        # Delta
        if option_type == 'call':
            delta = norm_d1
        else:  # put
            delta = norm_d1 - 1
        
        # Gamma (same for calls and puts)
        gamma = norm_prime_d1 / (S * self.volatility * np.sqrt(T))
        
        # Theta
        if option_type == 'call':
            theta = -S * norm_prime_d1 * self.volatility / (2 * np.sqrt(T)) - self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(d2)
        else:  # put
            theta = -S * norm_prime_d1 * self.volatility / (2 * np.sqrt(T)) + self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * stats.norm.cdf(-d2)
        
        # Vega (same for calls and puts)
        vega = S * np.sqrt(T) * norm_prime_d1
        
        return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}
