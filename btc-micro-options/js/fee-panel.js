// static/js/fee-panel.js
class FeePanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentFee = 0.0015; // 0.15%
        this.competitorFees = {
            "binance": 0.0010,
            "coinbase": 0.0020,
            "dydx": 0.0010,
            "uniswap": 0.0030,
            "sushiswap": 0.0025
        };
        this.feeHistory = [];
        this.adjustmentFactors = {
            volatility: 1.0,
            volume: 1.0,
            competitive: 1.0
        };
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
            <div class="current-fee">
                <div class="fee-label">Current Platform Fee</div>
                <div class="fee-value" id="current-fee-value">0.15%</div>
                <div class="fee-status" id="fee-status">Competitive</div>
            </div>
            
            <div class="fee-adjustment-factors">
                <div class="factor-title">Fee Adjustment Factors</div>
                <div class="factors-grid">
                    <div class="factor-item">
                        <div class="factor-label">Volatility</div>
                        <div class="factor-gauge">
                            <div class="gauge-fill" id="volatility-gauge" style="width: 50%"></div>
                        </div>
                        <div class="factor-value" id="volatility-factor">1.0×</div>
                    </div>
                    <div class="factor-item">
                        <div class="factor-label">Volume</div>
                        <div class="factor-gauge">
                            <div class="gauge-fill" id="volume-gauge" style="width: 50%"></div>
                        </div>
                        <div class="factor-value" id="volume-factor">1.0×</div>
                    </div>
                    <div class="factor-item">
                        <div class="factor-label">Market Position</div>
                        <div class="factor-gauge">
                            <div class="gauge-fill" id="competitive-gauge" style="width: 50%"></div>
                        </div>
                        <div class="factor-value" id="competitive-factor">1.0×</div>
                    </div>
                </div>
            </div>
            
            <div class="competitor-comparison">
                <div class="comparison-title">Market Comparison</div>
                <div id="fee-comparison" class="fee-comparison">
                    <!-- Fee comparison will be populated here -->
                </div>
            </div>
            
            <div class="fee-history-chart">
                <div class="chart-title">Fee History</div>
                <canvas id="fee-history-canvas" height="150"></canvas>
            </div>
        `;
        
        // Initialize the fee history chart
        this.initFeeHistoryChart();
    }

    render() {
        // Update current fee display
        document.getElementById('current-fee-value').textContent = `${(this.currentFee * 100).toFixed(3)}%`;
        
        // Update fee status
        const avgCompetitorFee = this.calculateAverageCompetitorFee();
        const feeStatus = document.getElementById('fee-status');
        
        if (this.currentFee < avgCompetitorFee) {
            feeStatus.textContent = 'Below Market Average';
            feeStatus.className = 'fee-status fee-competitive';
        } else if (this.currentFee > avgCompetitorFee) {
            feeStatus.textContent = 'Above Market Average';
            feeStatus.className = 'fee-status fee-high';
        } else {
            feeStatus.textContent = 'At Market Average';
            feeStatus.className = 'fee-status fee-average';
        }
        
        // Update adjustment factors
        this.renderAdjustmentFactors();
        
        // Update competitor comparison
        this.renderCompetitorComparison();
        
        // Update fee history chart
        this.updateFeeHistoryChart();
    }

    renderAdjustmentFactors() {
        // Update volatility factor
        const volatilityGauge = document.getElementById('volatility-gauge');
        const volatilityValue = document.getElementById('volatility-factor');
        
        volatilityGauge.style.width = `${(this.adjustmentFactors.volatility / 2) * 100}%`;
        volatilityValue.textContent = `${this.adjustmentFactors.volatility.toFixed(2)}×`;
        
        // Color based on factor value
        if (this.adjustmentFactors.volatility > 1.1) {
            volatilityGauge.style.backgroundColor = '#e74c3c';  // Red for high
        } else if (this.adjustmentFactors.volatility < 0.9) {
            volatilityGauge.style.backgroundColor = '#2ecc71';  // Green for low
        } else {
            volatilityGauge.style.backgroundColor = '#3498db';  // Blue for normal
        }
        
        // Update volume factor
        const volumeGauge = document.getElementById('volume-gauge');
        const volumeValue = document.getElementById('volume-factor');
        
        volumeGauge.style.width = `${(this.adjustmentFactors.volume / 2) * 100}%`;
        volumeValue.textContent = `${this.adjustmentFactors.volume.toFixed(2)}×`;
        
        // Color based on factor value
        if (this.adjustmentFactors.volume > 1.1) {
            volumeGauge.style.backgroundColor = '#e74c3c';  // Red for high
        } else if (this.adjustmentFactors.volume < 0.9) {
            volumeGauge.style.backgroundColor = '#2ecc71';  // Green for low
        } else {
            volumeGauge.style.backgroundColor = '#3498db';  // Blue for normal
        }
        
        // Update competitive factor
        const competitiveGauge = document.getElementById('competitive-gauge');
        const competitiveValue = document.getElementById('competitive-factor');
        
        competitiveGauge.style.width = `${(this.adjustmentFactors.competitive / 2) * 100}%`;
        competitiveValue.textContent = `${this.adjustmentFactors.competitive.toFixed(2)}×`;
        
        // Color based on factor value
        if (this.adjustmentFactors.competitive > 1.1) {
            competitiveGauge.style.backgroundColor = '#e74c3c';  // Red for high
        } else if (this.adjustmentFactors.competitive < 0.9) {
            competitiveGauge.style.backgroundColor = '#2ecc71';  // Green for low
        } else {
            competitiveGauge.style.backgroundColor = '#3498db';  // Blue for normal
        }
    }

    renderCompetitorComparison() {
        const comparisonContainer = document.getElementById('fee-comparison');
        
        // Sort fees from lowest to highest
        const allFees = [
            { name: 'Our Platform', fee: this.currentFee }
        ];
        
        for (const [name, fee] of Object.entries(this.competitorFees)) {
            allFees.push({ name, fee });
        }
        
        allFees.sort((a, b) => a.fee - b.fee);
        
        // Find our platform's position
        const ourPosition = allFees.findIndex(f => f.name === 'Our Platform');
        const percentileBetter = (ourPosition / allFees.length) * 100;
        
        // Generate HTML
        let html = `<div class="fee-comparison-title">Lower than ${percentileBetter.toFixed(0)}% of competitors</div>`;
        
        allFees.forEach(fee => {
            const isOur = fee.name === 'Our Platform';
            const barWidth = (fee.fee / allFees[allFees.length-1].fee) * 100;
            
            html += `
                <div class="fee-bar">
                    <div class="fee-progress" style="width: ${barWidth}%; background-color: ${isOur ? '#3498db' : '#2c3e50'}">
                        ${fee.name}: ${(fee.fee * 100).toFixed(3)}%
                    </div>
                </div>
            `;
        });
        
        comparisonContainer.innerHTML = html;
    }

    initFeeHistoryChart() {
        const ctx = document.getElementById('fee-history-canvas').getContext('2d');
        
        this.feeHistoryChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Fee Rate',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: {
                            display: false
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(3) + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return (context.raw * 100).toFixed(3) + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    updateFeeHistoryChart() {
        if (!this.feeHistoryChart) return;
        
        // Update chart with fee history
        this.feeHistoryChart.data.labels = this.feeHistory.map(entry => 
            new Date(entry.timestamp).toLocaleTimeString());
        
        this.feeHistoryChart.data.datasets[0].data = this.feeHistory.map(entry => 
            entry.feeRate);
        
        this.feeHistoryChart.update();
    }

    calculateAverageCompetitorFee() {
        const fees = Object.values(this.competitorFees);
        return fees.reduce((sum, fee) => sum + fee, 0) / fees.length;
    }

    adjustFee(volatilityFactor, volumeFactor, marketPositionFactor) {
        // Store previous fee for history
        const previousFee = this.currentFee;
        
        // Update adjustment factors
        this.adjustmentFactors = {
            volatility: volatilityFactor,
            volume: volumeFactor,
            competitive: marketPositionFactor
        };
        
        // Calculate base fee (0.15%)
        const baseFee = 0.0015;
        
        // Calculate weighted factors
        const combinedFactor = (
            this.adjustmentFactors.volatility * 0.4 +
            this.adjustmentFactors.volume * 0.3 +
            this.adjustmentFactors.competitive * 0.3
        );
        
        // Calculate new fee
        let newFee = baseFee * combinedFactor;
        
        // Apply constraints (min 0.05%, max 0.30%)
        newFee = Math.max(0.0005, Math.min(0.003, newFee));
        
        // Store in history if changed
        if (newFee !== previousFee) {
            this.feeHistory.push({
                timestamp: new Date(),
                feeRate: newFee,
                previousRate: previousFee,
                factors: { ...this.adjustmentFactors }
            });
            
            // Limit history size
            if (this.feeHistory.length > 50) {
                this.feeHistory = this.feeHistory.slice(-50);
            }
        }
        
        // Update current fee
        this.currentFee = newFee;
        
        // Update display
        this.render();
        
        return newFee;
    }

    simulateCompetitorFeeChange() {
        // Randomly select a competitor to adjust fees
        const competitors = Object.keys(this.competitorFees);
        const randomCompetitor = competitors[Math.floor(Math.random() * competitors.length)];
        
        // Small random adjustment (-0.02% to +0.02%)
        const adjustment = (Math.random() - 0.5) * 0.0004;
        
        // Apply adjustment with constraints
        this.competitorFees[randomCompetitor] = Math.max(
            0.0001, 
            Math.min(0.005, this.competitorFees[randomCompetitor] + adjustment)
        );
        
        // Update display
        this.render();
        
        return {
            competitor: randomCompetitor,
            newFee: this.competitorFees[randomCompetitor]
        };
    }

    simulateMarketConditionsChange() {
        // Simulate changing market conditions that would affect fees
        
        // Volatility (0.7 to 1.3)
        const volatilityFactor = 0.7 + Math.random() * 0.6;
        
        // Volume - higher volume = lower fees (0.7 to 1.3)
        const volumeFactor = 0.7 + Math.random() * 0.6;
        
        // Market position - aim to be 5% cheaper than average (0.85 to 1.1)
        const avgFee = this.calculateAverageCompetitorFee();
        const targetFee = avgFee * 0.95;
        const currentRatio = this.currentFee / targetFee;
        const marketPositionFactor = Math.max(0.85, Math.min(1.1, 1 / currentRatio));
        
        // Adjust fee
        this.adjustFee(volatilityFactor, volumeFactor, marketPositionFactor);
    }
}

// Export the class for use in other scripts
window.FeePanel = FeePanel;
