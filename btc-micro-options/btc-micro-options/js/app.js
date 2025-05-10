<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BTC Micro Options Platform</title>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div class="container">
    <header>
      <div class="platform-title">BTC Micro Options Platform</div>
      <div class="platform-status">
        <div class="status-indicator"></div>
        <span>Live Trading</span>
      </div>
    </header>
    
    <div class="main-content">
      <div class="price-section">
        <div class="price-display">
          <div class="current-price">
            <span id="current-price">$40,000.00</span>
            <span id="price-change" class="price-change price-up"><i class="fas fa-caret-up"></i> $200.00</span>
          </div>
          <div class="bid-ask">
            <div class="bid">Bid: <span id="bid-price">$39,950.00</span></div>
            <div class="ask">Ask: <span id="ask-price">$40,050.00</span></div>
          </div>
        </div>
        
        <div class="price-chart">
          <h3 class="section-title">Price Chart</h3>
          <div class="chart-3d-container">
            <div class="chart-3d">
              <canvas id="price-chart-canvas"></canvas>
            </div>
          </div>
        </div>
        
        <div class="portfolio-section">
          <h3 class="section-title">Active Options</h3>
          <div id="active-options" class="active-options">
            <div class="no-options">No active options</div>
          </div>
          
          <div class="greeks-display">
            <div class="greeks-title">Portfolio Greeks</div>
            <div class="greeks-grid">
              <div class="greek-item">
                <div class="greek-label">Delta (δ)</div>
                <div class="greek-value" id="delta-total">0.0000</div>
              </div>
              <div class="greek-item">
                <div class="greek-label">Gamma (γ)</div>
                <div class="greek-value" id="gamma-total">0.000000</div>
              </div>
              <div class="greek-item">
                <div class="greek-label">Theta (θ)</div>
                <div class="greek-value" id="theta-total">0.0000</div>
              </div>
              <div class="greek-item">
                <div class="greek-label">Vega (ν)</div>
                <div class="greek-value" id="vega-total">0.0000</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="advanced-section">
          <h3 class="section-title">Advanced Features</h3>
          
          <div class="tabs">
            <div class="tab active" data-tab="hedging-tab">Cross-Platform Hedging</div>
            <div class="tab" data-tab="fees-tab">Dynamic Fees</div>
            <div class="tab" data-tab="liquidity-tab">Liquidity</div>
          </div>
          
          <div id="hedging-tab" class="tab-content active">
            <div id="exchanges-container" class="exchange-grid">
              <!-- Exchange items will be populated by JS -->
            </div>
          </div>
          
          <div id="fees-tab" class="tab-content">
            <div id="fee-comparison" class="fee-comparison">
              <!-- Fee comparison will be populated by JS -->
            </div>
          </div>
          
          <div id="liquidity-tab" class="tab-content">
            <div class="liquidity-panel">
              <div>
                <div>Total Liquidity</div>
                <div id="liquidity-value" class="premium-amount">$1,200,000.00</div>
              </div>
              <div>
                <div>Balance Status</div>
                <div class="premium-amount" style="color: #2ecc71;">Self-Balancing</div>
              </div>
            </div>
            <div class="liquidity-chart">
              <canvas id="liquidity-chart-canvas"></canvas>
            </div>
          </div>
        </div>
      </div>
      
      <div class="control-section">
        <h3 class="section-title">Create Option</h3>
        
        <div class="option-form">
          <div class="option-type-toggle">
            <div id="option-type-call" class="option-type-btn active-call">CALL</div>
            <div id="option-type-put" class="option-type-btn">PUT</div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Strike Price</label>
            <div class="strike-preset">
              <div class="preset-btn" data-preset="atm">ATM</div>
              <div class="preset-btn" data-preset="itm-call">ITM Call</div>
              <div class="preset-btn" data-preset="otm-call">OTM Call</div>
              <div class="preset-btn" data-preset="itm-put">ITM Put</div>
              <div class="preset-btn" data-preset="otm-put">OTM Put</div>
            </div>
            <input type="number" id="strike-price" class="form-control" placeholder="Strike Price" value="40000">
          </div>
          
          <div class="form-group">
            <label class="form-label">Expiry</label>
            <input type="text" class="form-control" value="120 seconds" disabled>
          </div>
          
          <div class="form-group">
            <label class="form-label">Quantity</label>
            <input type="number" id="option-quantity" class="form-control" placeholder="Quantity" value="1" min="0.1" step="0.1">
          </div>
          
          <div class="premium-display">
            <div>Total Premium</div>
            <div id="premium-amount" class="premium-amount">$0.00</div>
          </div>
          
          <button id="create-option" class="btn btn-primary btn-block">Create Option</button>
        </div>
        
        <div style="margin-top: 20px;">
          <h3 class="section-title">Platform Features</h3>
          <ul style="padding-left: 20px; margin-top: 10px; color: var(--text-secondary);">
            <li>120-second micro options</li>
            <li>Self-balancing liquidity ($1.2M)</li>
            <li>Multi-platform hedging with fallbacks</li>
            <li>Dynamic fee adjustment</li>
            <li>Automatic option exercise at expiry</li>
            <li>Real-time price feed</li>
          </ul>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background-color: rgba(255, 255, 255, 0.05); border-radius: 4px;">
          <div style="font-weight: 500; margin-bottom: 5px;">Trading Simulation</div>
          <div style="font-size: 14px; color: var(--text-secondary);">
            This platform simulates Web3 smart contract integration with automatic option exercise at expiry.
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <div id="notification-container" class="notification-container"></div>
  
  <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
