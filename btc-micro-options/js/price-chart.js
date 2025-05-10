// static/js/price-chart.js
class PriceChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chartInstance = null;
        this.priceData = [];
        this.labels = [];
        this.maxDataPoints = 100;
        this.strikeLines = [];
        this.init();
    }

    init() {
        // Initialize Chart.js with empty data
        this.chartInstance = new Chart(this.ctx, {
            type: 'line',
            data: {
                labels: this.labels,
                datasets: [{
                    label: 'BTC Price',
                    data: this.priceData,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: {
                            display: false,
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#b3b3b3'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 30, 30, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: '#3498db',
                        borderWidth: 1
                    },
                    annotation: {
                        annotations: {}
                    }
                },
                animation: {
                    duration: 300
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
    }

    addPrice(price, timestamp = null) {
        // Add new price data
        this.priceData.push(price);
        this.labels.push(timestamp || new Date().toLocaleTimeString());
        
        // Remove oldest data if we exceed maximum points
        if (this.priceData.length > this.maxDataPoints) {
            this.priceData.shift();
            this.labels.shift();
        }
        
        // Update the chart
        this.chartInstance.update();
    }

    clearData() {
        this.priceData = [];
        this.labels = [];
        this.chartInstance.data.datasets[0].data = this.priceData;
        this.chartInstance.data.labels = this.labels;
        this.chartInstance.update();
    }

    addStrikeLine(strikePrice, label, type) {
        // Add or update strike line for an option
        const color = type === 'call' ? 'rgba(46, 204, 113, 0.8)' : 'rgba(231, 76, 60, 0.8)';
        
        // Create a unique ID for this strike line
        const lineId = `strike-${strikePrice}-${type}`;
        
        // Check if this strike already exists
        const existingLineIndex = this.strikeLines.findIndex(line => line.id === lineId);
        
        // Create annotation config
        const lineConfig = {
            id: lineId,
            type: 'line',
            mode: 'horizontal',
            scaleID: 'y',
            value: strikePrice,
            borderColor: color,
            borderWidth: 1,
            borderDash: [5, 5],
            label: {
                content: `${type.toUpperCase()} $${strikePrice}`,
                display: true,
                position: type === 'call' ? 'start' : 'end',
                backgroundColor: color,
                color: 'white',
                font: {
                    size: 10
                }
            }
        };
        
        // Update strike lines collection
        if (existingLineIndex >= 0) {
            this.strikeLines[existingLineIndex] = lineConfig;
        } else {
            this.strikeLines.push(lineConfig);
        }
        
        // Update chart annotations
        this.updateStrikeLines();
    }

    removeStrikeLine(strikePrice, type) {
        const lineId = `strike-${strikePrice}-${type}`;
        this.strikeLines = this.strikeLines.filter(line => line.id !== lineId);
        this.updateStrikeLines();
    }

    updateStrikeLines() {
        // Update chart annotations
        this.chartInstance.options.plugins.annotation.annotations = {};
        
        this.strikeLines.forEach(line => {
            this.chartInstance.options.plugins.annotation.annotations[line.id] = line;
        });
        
        this.chartInstance.update();
    }

    applyTheme(isDark = true) {
        // Apply light or dark theme
        const textColor = isDark ? '#b3b3b3' : '#333333';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
        
        this.chartInstance.options.scales.y.ticks.color = textColor;
        this.chartInstance.options.scales.x.grid.color = gridColor;
        this.chartInstance.options.scales.y.grid.color = gridColor;
        
        this.chartInstance.update();
    }

    setSimulationMode(enabled) {
        if (enabled) {
            // Start price simulation
            this.simulationTimer = setInterval(() => {
                const lastPrice = this.priceData.length > 0 ? 
                    this.priceData[this.priceData.length - 1] : 
                    40000;
                
                // Simulate small price changes
                const change = (Math.random() - 0.5) * 100;
                const newPrice = lastPrice + change;
                
                this.addPrice(newPrice);
            }, 1000);
        } else {
            // Stop simulation
            if (this.simulationTimer) {
                clearInterval(this.simulationTimer);
                this.simulationTimer = null;
            }
        }
    }

    // Add method to set 3D effect
    set3DEffect(enabled) {
        const chartContainer = this.canvas.parentElement;
        
        if (enabled) {
            chartContainer.style.perspective = '1000px';
            chartContainer.style.transformStyle = 'preserve-3d';
            chartContainer.style.transform = 'rotateX(10deg)';
            this.canvas.style.boxShadow = '0 10px 20px rgba(0,0,0,0.3)';
        } else {
            chartContainer.style.perspective = 'none';
            chartContainer.style.transformStyle = 'flat';
            chartContainer.style.transform = 'none';
            this.canvas.style.boxShadow = 'none';
        }
    }
}

// Export the class for use in other scripts
window.PriceChart = PriceChart;
