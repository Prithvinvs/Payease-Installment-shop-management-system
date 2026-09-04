/**
========================================================================
PayEase Dashboard Charts Controller
Configures and renders Chart.js elements.
Listens to theme changes to redraw with suitable dark/light grid styles.
========================================================================
*/

document.addEventListener('DOMContentLoaded', () => {
    let trendChart = null;
    let efficiencyChart = null;

    // Helper to extract CSS-variable-based colors for Chart.js
    function getThemeColors() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        return {
            textColor: isDark ? '#94a3b8' : '#64748b',
            gridColor: isDark ? '#1e293b' : '#e2e8f0',
            primary: isDark ? '#6366f1' : '#4f46e5',
            primaryLight: isDark ? 'rgba(99, 102, 241, 0.15)' : 'rgba(79, 70, 229, 0.1)',
            success: isDark ? '#34d399' : '#10b981',
            successLight: isDark ? 'rgba(52, 211, 153, 0.15)' : 'rgba(16, 185, 129, 0.1)',
            cardBg: isDark ? '#131b2e' : '#ffffff'
        };
    }

    function initCharts() {
        const colors = getThemeColors();

        // 1. Collections Trend Line Chart
        const trendCtx = document.getElementById('collectionsTrendChart');
        if (trendCtx) {
            trendChart = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                    datasets: [
                        {
                            label: 'Collected Amount (₹)',
                            data: [82000, 95000, 110000, 105000, 130000, 142000, 158400],
                            borderColor: colors.primary,
                            backgroundColor: colors.primaryLight,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3,
                            pointBackgroundColor: colors.primary,
                            pointBorderColor: colors.cardBg,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Target Amount (₹)',
                            data: [90000, 100000, 110000, 115000, 135000, 145000, 160000],
                            borderColor: colors.textColor,
                            borderDash: [5, 5],
                            backgroundColor: 'transparent',
                            fill: false,
                            tension: 0.1,
                            borderWidth: 1.5,
                            pointRadius: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: colors.textColor,
                                font: { family: 'Inter', size: 12, weight: 500 }
                            }
                        },
                        tooltip: {
                            padding: 12,
                            borderRadius: 8,
                            titleFont: { family: 'Inter', size: 13, weight: 600 },
                            bodyFont: { family: 'Inter', size: 12 }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: colors.textColor,
                                font: { family: 'Inter', size: 11 }
                            }
                        },
                        y: {
                            grid: { color: colors.gridColor },
                            ticks: {
                                color: colors.textColor,
                                font: { family: 'Inter', size: 11 },
                                callback: function(value) {
                                    return '₹' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }

        // 2. Collection Efficiency Doughnut Chart
        const efficiencyCtx = document.getElementById('collectionEfficiencyChart');
        if (efficiencyCtx) {
            efficiencyChart = new Chart(efficiencyCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Collected', 'Remaining Dues'],
                    datasets: [{
                        data: [88.5, 11.5],
                        backgroundColor: [colors.success, colors.gridColor],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '80%',
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            padding: 10,
                            borderRadius: 6,
                            bodyFont: { family: 'Inter', size: 12 }
                        }
                    }
                }
            });
        }
    }

    // Initialize charts on startup
    initCharts();

    // Redraw charts dynamically when user switches theme
    window.addEventListener('themeChanged', () => {
        const colors = getThemeColors();

        if (trendChart) {
            // Update line chart colors
            trendChart.data.datasets[0].borderColor = colors.primary;
            trendChart.data.datasets[0].backgroundColor = colors.primaryLight;
            trendChart.data.datasets[1].borderColor = colors.textColor;
            trendChart.options.plugins.legend.labels.color = colors.textColor;
            trendChart.options.scales.x.ticks.color = colors.textColor;
            trendChart.options.scales.y.ticks.color = colors.textColor;
            trendChart.options.scales.y.grid.color = colors.gridColor;
            trendChart.update();
        }

        if (efficiencyChart) {
            // Update doughnut chart colors
            efficiencyChart.data.datasets[0].backgroundColor = [colors.success, colors.gridColor];
            efficiencyChart.update();
        }
    });
});
