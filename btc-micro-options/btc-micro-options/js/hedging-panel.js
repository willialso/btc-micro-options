// static/js/hedging-panel.js
class HedgingPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.exchanges = {
            "binance": { status: "active", weight: 0.4, hedge_delta: 0 },
            "coinbase": { status: "active", weight: 0.3, hedge_delta: 0 },
            "kraken": { status: "active", weight: 0.2, hedge_delta: 0 },
            "ftx": { status: "backup", weight: 0.1, hedge_delta: 0 }
        };
        this.portfolioDelta = 0;
        this.netDelta = 0;
        this.lastRebalance = new Date();
        this.hedgeHistory = [];
        this.init();
    }

    init() {
        // Create initial UI structure
        this.createUIStructure();
        
        // Initial render
        this.render();
    }

    createUIStructure() {
        this.container.innerHTML = `
            <div class="hedging-summary">
                <div class="summary-item">
                    <div class="summary-label">Portfolio Delta</div>
                    <div class="summary-value" id="portfolio-delta">0.0000</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Hedge Delta</div>
                    <div class="summary-value" id="hedge-delta">0.0000</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Net Delta</div>
                    <div class="summary-value" id="net-delta">0.0000</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Last Rebalance</div>
                    <div class="summary-value" id="last-rebalance">Never</div>
                </div>
            </div>
            <h4 class="exchange-title">Exchange Distribution</h4>
            <div class="exchange-grid" id="exchange-grid">
                <!-- Exchange items will be populated here -->
            </div>
            <h4 class="history-title">Recent Hedge Activity</h4>
            <div class="hedge-history" id="hedge-history">
                <!-- Hedge history will be populated here -->
            </div>
        `;
    }

    render() {
        // Update summary values
        document.getElementById('portfolio-delta').textContent = this.portfolioDelta.toFixed(4);
        
        const hedgeDelta = this.calculateTotalHedgeDelta();
        document.getElementById('hedge-delta').textContent = hedgeDelta.toFixed(4);
        
        this.netDelta = this.portfolioDelta + hedgeDelta;
        document.getElementById('net-delta').textContent = this.netDelta.toFixed(4);
        
        document.getElementById('last-rebalance').textContent = this.formatTimeAgo(this.lastRebalance);
        
        // Render exchanges
        this.renderExchanges();
        
        // Render hedge history
        this.renderHedgeHistory();
    }

    renderExchanges() {
        const exchangeGrid = document.getElementById('exchange-grid');
        exchangeGrid.innerHTML = '';
        
        for (const [name, exchange] of Object.entries(this.exchanges)) {
            const statusClass = exchange.status === 'active' ? 'exchange-status-active' : 
                exchange.status === 'failed' ? 'exchange-status-failed' : 'exchange-status-backup';
            
            const exchangeElement = document.createElement('div');
            exchangeElement.className = 'exchange-item';
            exchangeElement.innerHTML = `
                <div class="exchange-name">${name}</div>
                <div class="exchange-status ${statusClass}">
                    ${exchange.status}
                </div>
                <div class="exchange-weight">
                    <div class="weight-label">Weight</div>
                    <div class="weight-bar">
                        <div class="weight-fill" style="width: ${exchange.weight * 100}%"></div>
                    </div>
                    <div class="weight-value">${(exchange.weight * 100).toFixed(0)}%</div>
                </div>
                <div class="exchange-delta">
                    Hedge δ: ${exchange.hedge_delta.toFixed(4)}
                </div>
            `;
            
            exchangeGrid.appendChild(exchangeElement);
        }
    }

    renderHedgeHistory() {
        const historyContainer = document.getElementById('hedge-history');
        historyContainer.innerHTML = '';
        
        if (this.hedgeHistory.length === 0) {
            historyContainer.innerHTML = '<div class="no-history">No recent hedge activity</div>';
            return;
        }
        
        // Show most recent 5 items
        const recentHistory = this.hedgeHistory.slice(-5).reverse();
        
        recentHistory.forEach(item => {
            const historyElement = document.createElement('div');
            historyElement.className = 'history-item';
            historyElement.innerHTML = `
                <div class="history-time">${this.formatTimeAgo(item.timestamp)}</div>
                <div class="history-action">
                    <span class="${item.delta > 0 ? 'positive-delta' : 'negative-delta'}">
                        ${item.delta > 0 ? '+' : ''}${item.delta.toFixed(4)} δ
                    </span>
                    on ${item.exchange}
                </div>
                <div class="history-price">@ $${item.price.toFixed(2)}</div>
            `;
            
            historyContainer.appendChild(historyElement);
        });
    }

    calculateTotalHedgeDelta() {
        let total = 0;
        for (const exchange of Object.values(this.exchanges)) {
            if (exchange.status === 'active' || exchange.status === 'failed') {
                total += exchange.hedge_delta;
            }
        }
        return total;
    }

    updatePortfolioDelta(delta) {
        this.portfolioDelta = delta;
        this.render();
    }

    rebalanceHedges(currentPrice) {
        // Calculate current hedge delta
        const currentHedgeDelta = this.calculateTotalHedgeDelta();
        
        // Calculate needed adjustment
        const netDelta = this.portfolioDelta + currentHedgeDelta;
        
        // Only rebalance if net delta exceeds threshold
        if (Math.abs(netDelta) < 0.05) {
            return false;
        }
        
        // Calculate required hedge adjustment
        const adjustmentNeeded = -netDelta;
        
        // Distribute adjustment across active exchanges
        const activeExchanges = Object.entries(this.exchanges)
            .filter(([_, exchange]) => exchange.status === 'active')
            .map(([name, _]) => name);
        
        if (activeExchanges.length === 0) {
            return false;
        }
        
        const totalWeight = activeExchanges.reduce((sum, name) => sum + this.exchanges[name].weight, 0);
        
        activeExchanges.forEach(name => {
            const exchange = this.exchanges[name];
            const normalizedWeight = exchange.weight / totalWeight;
            const exchangeAdjustment = adjustmentNeeded * normalizedWeight;
            
            // Update exchange hedge delta
            exchange.hedge_delta += exchangeAdjustment;
            
            // Add to hedge history
            this.hedgeHistory.push({
                timestamp: new Date(),
                exchange: name,
                delta: exchangeAdjustment,
                price: currentPrice
            });
        });
        
        // Limit history size to prevent memory issues
        if (this.hedgeHistory.length > 100) {
            this.hedgeHistory = this.hedgeHistory.slice(-100);
        }
        
        // Update last rebalance time
        this.lastRebalance = new Date();
        
        // Update display
        this.render();
        
        return true;
    }

    simulateExchangeFailure() {
        const activeExchanges = Object.entries(this.exchanges)
            .filter(([_, exchange]) => exchange.status === 'active')
            .map(([name, _]) => name);
        
        if (activeExchanges.length <= 1) {
            return false; // Don't fail if only one active exchange remains
        }
        
        // Randomly select an exchange to fail
        const randomIndex = Math.floor(Math.random() * activeExchanges.length);
        const failedExchange = activeExchanges[randomIndex];
        
        this.setExchangeStatus(failedExchange, 'failed');
        
        // Find a backup exchange to activate
        const backupExchanges = Object.entries(this.exchanges)
            .filter(([_, exchange]) => exchange.status === 'backup')
            .map(([name, _]) => name);
        
        if (backupExchanges.length > 0) {
            this.setExchangeStatus(backupExchanges[0], 'active');
            
            // Transfer the hedge delta
            this.exchanges[backupExchanges[0]].hedge_delta = this.exchanges[failedExchange].hedge_delta;
            this.exchanges[failedExchange].hedge_delta = 0;
            
            return true;
        }
        
        return false;
    }

    setExchangeStatus(exchangeName, status) {
        if (this.exchanges[exchangeName]) {
            this.exchanges[exchangeName].status = status;
            this.render();
            return true;
        }
        return false;
    }

    formatTimeAgo(date) {
        if (!date) return 'Never';
        
        const now = new Date();
        const diff = now - date;
        
        if (diff < 1000 * 60) {
            return 'Just now';
        } else if (diff < 1000 * 60 * 60) {
            return `${Math.floor(diff / (1000 * 60))}m ago`;
        } else if (diff < 1000 * 60 * 60 * 24) {
            return `${Math.floor(diff / (1000 * 60 * 60))}h ago`;
        } else {
            return date.toLocaleTimeString();
        }
    }
}

// Export the class for use in other scripts
window.HedgingPanel = HedgingPanel;
