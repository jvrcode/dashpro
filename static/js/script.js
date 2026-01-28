// Atlanta Plant Performance Dashboard - JavaScript

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateDateTime();
    loadData();
    
    // Update date/time every minute
    setInterval(updateDateTime, 60000);
});

// Update current date and time
function updateDateTime() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    document.getElementById('current-date').textContent = now.toLocaleDateString('en-US', options);
}

// Load performance data
async function loadData() {
    const shiftFilter = document.getElementById('shift-filter').value;
    
    try {
        // Fetch performance data
        const response = await fetch(`/api/performance-data?shift=${shiftFilter}`);
        const data = await response.json();
        
        // Update KPIs
        updateKPIs(data.plant_average);
        
        // Update top and bottom performers
        updatePerformers(data.top_performers, data.bottom_performers);
        
        // Update operators table
        updateOperatorsTable(data.all_operators);
        
        // Update shift breakdown
        updateShiftBreakdown(data.shift_averages);
        
        // Load charts
        loadCharts();
        
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load performance data. Please try again.');
    }
}

// Update KPI cards
function updateKPIs(plantAvg) {
    document.getElementById('avg-productivity').textContent = `${plantAvg.productivity}%`;
    document.getElementById('avg-quality').textContent = `${plantAvg.quality_rate}%`;
    document.getElementById('avg-setup').textContent = `${plantAvg.avg_setup_time} min`;
    document.getElementById('avg-score').textContent = plantAvg.performance_score;
    
    // Color code based on targets
    const productivityEl = document.getElementById('avg-productivity');
    productivityEl.style.color = plantAvg.productivity >= 90 ? 'var(--success-color)' : 'var(--danger-color)';
    
    const qualityEl = document.getElementById('avg-quality');
    qualityEl.style.color = plantAvg.quality_rate >= 98 ? 'var(--success-color)' : 'var(--warning-color)';
    
    const setupEl = document.getElementById('avg-setup');
    setupEl.style.color = plantAvg.avg_setup_time <= 3 ? 'var(--success-color)' : 'var(--warning-color)';
}

// Update performers lists
function updatePerformers(topPerformers, bottomPerformers) {
    // Top performers
    const topList = document.getElementById('top-performers-list');
    topList.innerHTML = topPerformers.map((performer, index) => `
        <div class="performer-item">
            <div class="performer-rank">#${index + 1}</div>
            <div class="performer-info">
                <h4>${performer.operator}</h4>
                <div class="performer-details">
                    ${performer.shift} | ${performer.line} | 
                    Productivity: ${performer.productivity}% | 
                    Quality: ${performer.quality_rate.toFixed(1)}%
                </div>
            </div>
            <div class="performer-score">${performer.performance_score}</div>
        </div>
    `).join('');
    
    // Bottom performers
    const bottomList = document.getElementById('bottom-performers-list');
    bottomList.innerHTML = bottomPerformers.reverse().map((performer, index) => `
        <div class="performer-item">
            <div class="performer-rank">#${bottomPerformers.length - index}</div>
            <div class="performer-info">
                <h4>${performer.operator}</h4>
                <div class="performer-details">
                    ${performer.shift} | ${performer.line} | 
                    Productivity: ${performer.productivity}% | 
                    Quality: ${performer.quality_rate.toFixed(1)}%
                </div>
            </div>
            <div class="performer-score">${performer.performance_score}</div>
        </div>
    `).join('');
}

// Update operators table
function updateOperatorsTable(operators) {
    const tbody = document.getElementById('operators-tbody');
    
    tbody.innerHTML = operators.map((op, index) => {
        const rankClass = index < 5 ? 'rank-top' : 
                         index >= operators.length - 5 ? 'rank-bottom' : 'rank-middle';
        
        const productivityClass = op.productivity >= 90 ? 'metric-good' : 
                                 op.productivity >= 85 ? 'metric-warning' : 'metric-bad';
        
        const qualityClass = op.quality_rate >= 98 ? 'metric-good' : 
                            op.quality_rate >= 95 ? 'metric-warning' : 'metric-bad';
        
        const setupClass = op.avg_setup_time <= 3 ? 'metric-good' : 
                          op.avg_setup_time <= 3.5 ? 'metric-warning' : 'metric-bad';
        
        return `
            <tr>
                <td><span class="rank-badge ${rankClass}">${index + 1}</span></td>
                <td><strong>${op.operator}</strong></td>
                <td>${op.shift}</td>
                <td>${op.line}</td>
                <td class="${productivityClass}">${op.productivity}%</td>
                <td class="${qualityClass}">${op.quality_rate.toFixed(1)}%</td>
                <td class="${setupClass}">${op.avg_setup_time.toFixed(2)}</td>
                <td>${op.jobs_completed}</td>
                <td>${op.downtime_minutes}</td>
                <td><strong>${op.performance_score}</strong></td>
            </tr>
        `;
    }).join('');
}

// Update shift breakdown
function updateShiftBreakdown(shiftAverages) {
    const shiftGrid = document.getElementById('shift-breakdown');
    
    const shifts = ['1st Shift', '2nd Shift', '3rd Shift'];
    
    shiftGrid.innerHTML = shifts.map(shift => {
        const data = shiftAverages[shift];
        if (!data) return '';
        
        return `
            <div class="shift-card">
                <h4>🕐 ${shift}</h4>
                <div class="shift-metrics">
                    <div class="shift-metric">
                        <span class="shift-metric-label">Productivity</span>
                        <span class="shift-metric-value">${data.productivity.toFixed(1)}%</span>
                    </div>
                    <div class="shift-metric">
                        <span class="shift-metric-label">Quality Rate</span>
                        <span class="shift-metric-value">${data.quality_rate.toFixed(1)}%</span>
                    </div>
                    <div class="shift-metric">
                        <span class="shift-metric-label">Avg Setup Time</span>
                        <span class="shift-metric-value">${data.avg_setup_time.toFixed(2)} min</span>
                    </div>
                    <div class="shift-metric">
                        <span class="shift-metric-label">Performance Score</span>
                        <span class="shift-metric-value">${data.performance_score.toFixed(1)}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Load charts
async function loadCharts() {
    try {
        const response = await fetch('/api/charts');
        const data = await response.json();
        
        // Render productivity chart
        Plotly.newPlot('productivity-chart', data.productivity_chart.data, data.productivity_chart.layout, {
            responsive: true,
            displayModeBar: false
        });
        
        // Render performance chart
        Plotly.newPlot('performance-chart', data.performance_chart.data, data.performance_chart.layout, {
            responsive: true,
            displayModeBar: false
        });
        
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

// Show error message
function showError(message) {
    alert(message);
}

// Export functions for global access
window.loadData = loadData;
