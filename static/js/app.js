// IoT Dashboard JavaScript

class IoTDashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeCharts();
        });

        // Handle visibility change to pause/resume updates
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopRealTimeUpdates();
            } else {
                this.startRealTimeUpdates();
            }
        });
    }

    initializeCharts() {
        // Initialize temperature chart if element exists
        const tempChart = document.getElementById('temperatureChart');
        if (tempChart) {
            this.createTemperatureChart(tempChart);
        }

        // Initialize device chart if element exists
        const deviceChart = document.getElementById('deviceChart');
        if (deviceChart) {
            this.createDeviceChart(deviceChart);
        }
    }

    createTemperatureChart(canvas) {
        const ctx = canvas.getContext('2d');
        this.charts.temperature = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: 'rgb(78, 115, 223)',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }, {
                    label: 'Humidity (%)',
                    data: [],
                    borderColor: 'rgb(28, 200, 138)',
                    backgroundColor: 'rgba(28, 200, 138, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Value'
                        },
                        beginAtZero: false
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    createDeviceChart(canvas) {
        const ctx = canvas.getContext('2d');
        this.charts.device = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['ESP32', 'PICO WH', 'Other'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        'rgb(78, 115, 223)',
                        'rgb(28, 200, 138)',
                        'rgb(54, 185, 204)'
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    updateCharts(sensorData) {
        if (!sensorData || sensorData.length === 0) return;

        // Update temperature chart
        if (this.charts.temperature) {
            const temperatures = [];
            const humidities = [];
            const labels = [];

            // Get last 20 data points
            const recentData = sensorData.slice(0, 20).reverse();
            
            recentData.forEach(data => {
                if (data.temperature !== null) {
                    temperatures.push(data.temperature);
                }
                if (data.humidity !== null) {
                    humidities.push(data.humidity);
                }
                labels.push(this.formatTime(data.timestamp));
            });

            this.charts.temperature.data.labels = labels;
            this.charts.temperature.data.datasets[0].data = temperatures;
            this.charts.temperature.data.datasets[1].data = humidities;
            this.charts.temperature.update('none'); // No animation for real-time updates
        }
    }

    updateDeviceChart(devices) {
        if (!this.charts.device || !devices) return;

        const deviceTypes = { 'ESP32': 0, 'PICO WH': 0, 'Other': 0 };
        
        devices.forEach(device => {
            if (deviceTypes.hasOwnProperty(device.device_type)) {
                deviceTypes[device.device_type]++;
            } else {
                deviceTypes['Other']++;
            }
        });

        this.charts.device.data.datasets[0].data = [
            deviceTypes['ESP32'],
            deviceTypes['PICO WH'],
            deviceTypes['Other']
        ];
        this.charts.device.update();
    }

    updateTable(sensorData) {
        const tbody = document.getElementById('sensor-data-tbody');
        if (!tbody || !sensorData) return;

        tbody.innerHTML = '';
        
        sensorData.slice(0, 10).forEach(data => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td><code>${data.device_id}</code></td>
                <td>${data.temperature !== null ? data.temperature.toFixed(1) : '--'}</td>
                <td>${data.humidity !== null ? data.humidity.toFixed(1) : '--'}</td>
                <td>${data.pressure !== null ? data.pressure.toFixed(1) : '--'}</td>
                <td>${data.light !== null ? data.light.toFixed(1) : '--'}</td>
                <td>
                    ${data.motion 
                        ? '<span class="badge bg-warning">Detected</span>' 
                        : '<span class="badge bg-success">None</span>'}
                </td>
                <td>${this.formatDateTime(data.timestamp)}</td>
            `;
        });
    }

    updateStats(sensorData) {
        if (!sensorData || sensorData.length === 0) return;

        const temperatures = sensorData
            .map(d => d.temperature)
            .filter(t => t !== null);
        
        const humidities = sensorData
            .map(d => d.humidity)
            .filter(h => h !== null);

        // Update temperature stat
        const tempElement = document.getElementById('avg-temperature');
        if (tempElement && temperatures.length > 0) {
            const avgTemp = temperatures.reduce((a, b) => a + b, 0) / temperatures.length;
            tempElement.textContent = `${avgTemp.toFixed(1)}°C`;
        }

        // Update humidity stat
        const humidityElement = document.getElementById('avg-humidity');
        if (humidityElement && humidities.length > 0) {
            const avgHumidity = humidities.reduce((a, b) => a + b, 0) / humidities.length;
            humidityElement.textContent = `${avgHumidity.toFixed(1)}%`;
        }

        // Update data count
        const dataCountElement = document.getElementById('data-count');
        if (dataCountElement) {
            dataCountElement.textContent = sensorData.length;
        }
    }

    async fetchSensorData(limit = 50) {
        try {
            const response = await fetch(`/api/sensor-data?limit=${limit}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching sensor data:', error);
            return [];
        }
    }

    async fetchDevices() {
        try {
            const response = await fetch('/api/devices');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching devices:', error);
            return [];
        }
    }

    async updateDashboard() {
        try {
            const [sensorData, devices] = await Promise.all([
                this.fetchSensorData(50),
                this.fetchDevices()
            ]);

            this.updateCharts(sensorData);
            this.updateTable(sensorData);
            this.updateStats(sensorData);
            this.updateDeviceChart(devices);

            // Update last updated time
            this.updateLastUpdated();
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    startRealTimeUpdates() {
        this.stopRealTimeUpdates(); // Clear any existing interval
        this.updateInterval = setInterval(() => {
            this.updateDashboard();
        }, 5001); // Update every 5 seconds

        // Initial update
        this.updateDashboard();
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatDateTime(timestamp) {
        return new Date(timestamp).toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    updateLastUpdated() {
        const element = document.getElementById('last-updated');
        if (element) {
            element.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }

    // Utility function to show notifications
    showNotification(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5001);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.iotDashboard = new IoTDashboard();
});

// Global utility functions
window.copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        return success;
    }
};

// Export data function
window.exportSensorData = async (format = 'csv') => {
    try {
        const response = await fetch('/api/sensor-data?limit=1000');
        const data = await response.json();
        
        if (format === 'csv') {
            const csv = convertToCSV(data);
            downloadFile(csv, 'sensor_data.csv', 'text/csv');
        } else if (format === 'json') {
            downloadFile(JSON.stringify(data, null, 2), 'sensor_data.json', 'application/json');
        }
    } catch (error) {
        console.error('Error exporting data:', error);
    }
};

function convertToCSV(data) {
    const headers = ['Device ID', 'Temperature', 'Humidity', 'Pressure', 'Light', 'Motion', 'Timestamp'];
    const csvContent = [
        headers.join(','),
        ...data.map(row => [
            row.device_id,
            row.temperature || '',
            row.humidity || '',
            row.pressure || '',
            row.light || '',
            row.motion || '',
            row.timestamp
        ].join(','))
    ].join('\n');
    
    return csvContent;
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
