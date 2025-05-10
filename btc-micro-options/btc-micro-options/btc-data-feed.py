# btc_data_feed.py
import asyncio
import websockets
import json
import datetime
import time
import random
import threading
import numpy as np

class BTCDataFeed:
    def __init__(self, price_callback=None, demo_mode=True):
        self.ws_url = 'wss://ws-feed.pro.coinbase.com'
        self.current_data = {
            'price': 40000, 
            'bid': 39990, 
            'ask': 40010, 
            'time': datetime.datetime.now().isoformat()
        }
        self.price_history = []
        self.max_history_length = 1000
        self.price_callback = price_callback
        self.demo_mode = demo_mode
        
    async def connect(self):
        """Connect to Coinbase Pro WebSocket feed"""
        if self.demo_mode:
            await self.run_demo_simulation()
            return
            
        async with websockets.connect(self.ws_url) as websocket:
            # Subscribe to ticker channel for BTC-USD
            subscribe_message = {
                "type": "subscribe",
                "channels": [{"name": "ticker", "product_ids": ["BTC-USD"]}]
            }
            await websocket.send(json.dumps(subscribe_message))
            
            while True:
                try:
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    if data.get('type') == 'ticker':
                        self.current_data = {
                            'price': float(data.get('price', self.current_data['price'])),
                            'bid': float(data.get('best_bid', self.current_data['bid'])),
                            'ask': float(data.get('best_ask', self.current_data['ask'])),
                            'time': data.get('time', datetime.datetime.now().isoformat()),
                        }
                        
                        # Add to history and trim if needed
                        self.price_history.append(self.current_data.copy())
                        if len(self.price_history) > self.max_history_length:
                            self.price_history.pop(0)
                        
                        # Call callback if provided
                        if self.price_callback:
                            self.price_callback(self.current_data)
                        
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    await asyncio.sleep(5)
                    break
    
    async def run_demo_simulation(self):
        """Run a simulated price feed for demo purposes"""
        price = 40000
        volatility = 0.0004  # Per-second volatility
        
        while True:
            # Generate realistic price movements
            # Use jump diffusion model to simulate occasional large moves
            if random.random() < 0.01:  # 1% chance of a jump
                jump_size = random.normalvariate(0, price * 0.005)
                price += jump_size
                print(f"🚀 Price jump: ${jump_size:.2f}")
            else:
                # Regular price movement
                price_change = random.normalvariate(0, price * volatility)
                price += price_change
            
            # Ensure price stays realistic
            price = max(10000, min(100000, price))
            
            # Calculate bid-ask spread (wider during volatile moves)
            spread = price * 0.0005 * (1 + abs(price_change / price) * 10)
            bid = price - spread / 2
            ask = price + spread / 2
            
            # Update current data
            self.current_data = {
                'price': price,
                'bid': bid,
                'ask': ask,
                'time': datetime.datetime.now().isoformat(),
                'change': price_change
            }
            
            # Add to history and trim if needed
            self.price_history.append(self.current_data.copy())
            if len(self.price_history) > self.max_history_length:
                self.price_history.pop(0)
            
            # Call callback if provided
            if self.price_callback:
                self.price_callback(self.current_data)
            
            # Simulate websocket delay
            await asyncio.sleep(0.5)
    
    def run(self):
        """Run the websocket client in a loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while True:
            try:
                loop.run_until_complete(self.connect())
            except Exception as e:
                print(f"Connection error: {e}")
                time.sleep(5)
