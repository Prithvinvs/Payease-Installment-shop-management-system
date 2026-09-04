/**
========================================================================
PayEase Dashboard API & Charts Controller
Asynchronously fetches JSON APIs, draws interactive Chart.js widgets,
manages theme updates, handles loading skeletons, and draws event calendars.
========================================================================
*/

document.addEventListener('DOMContentLoaded', () => {
    // Read user role context passed from Jinja
    const userRole = window.UserRole || 'Staff';
    const isStaff = userRole === 'Staff';
    
    // Date filter state
    let activeFilter = 'this_month';
    let startDate = '';
    let endDate = '';
    
    // Hold Chart.js instances to allow destroying/redrawing on updates
    let charts = {};

    // --- 1. DOM Elements Mapping ---
    const filterButtons = document.querySelectorAll('.filter-btn');
    const applyCustomDateBtn = document.getElementById('applyCustomDateBtn');
    const startDateInput = document.getElementById('startDateInput');
    const endDateInput = document.getElementById('endDateInput');
    
    // Hide financial containers if user is Staff
    if (isStaff) {
        document.querySelectorAll('.financial-kpi').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.financial-chart-box').forEach(el => el.style.display = 'none');
    }

    // --- 2. Chart helper functions ---
    function getThemeColors() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        return {
            textColor: isDark ? '#94a3b8' : '#64748b',
            gridColor: isDark ? '#1e293b' : '#e2e8f0',
            primary: '#2563EB', // Blue
            primaryLight: 'rgba(37, 99, 235, 0.1)',
            success: '#10B981', // Green
            successLight: 'rgba(16, 185, 129, 0.1)',
            warning: '#F59E0B', // Orange
            warningLight: 'rgba(245, 158, 11, 0.1)',
            danger: '#EF4444', // Red
            dangerLight: 'rgba(239, 68, 68, 0.1)',
            cardBg: isDark ? '#131b2e' : '#ffffff'
        };
    }

    function destroyChart(name) {
        if (charts[name]) {
            charts[name].destroy();
            delete charts[name];
        }
    }

    // --- 3. Async API Fetch Loaders ---

    async function fetchDashboardSummary() {
        try {
            const url = `/api/dashboard/summary?filter=${activeFilter}&start_date=${startDate}&end_date=${endDate}`;
            const response = await fetch(url);
            const data = await response.json();
            
            // Customers
            document.getElementById('kpi-cust-total').innerHTML = data.customers.total;
            document.getElementById('kpi-cust-new').innerHTML = data.customers.new_this_month;
            document.getElementById('cust-growth-badge').innerHTML = `<i class="bi bi-arrow-up-right me-1"></i>+${data.customers.growth_pct}%`;
            
            // Sales
            document.getElementById('kpi-sales-today').innerHTML = `₹${data.sales.today.toLocaleString()}`;
            document.getElementById('kpi-sales-month').innerHTML = `₹${data.sales.monthly.toLocaleString()}`;
            
            // Revenue / Dues (If Admin / Super Admin)
            if (!isStaff) {
                document.getElementById('kpi-rev-today').innerHTML = `₹${data.revenue.today.toLocaleString()}`;
                document.getElementById('kpi-rev-month').innerHTML = `₹${data.revenue.monthly.toLocaleString()}`;
                document.getElementById('kpi-rev-outstanding').innerHTML = `₹${data.revenue.outstanding_balance.toLocaleString()}`;
                document.getElementById('kpi-plans-active').innerHTML = data.revenue.pending_count;
                document.getElementById('pending-instalments-badge').innerHTML = `${data.revenue.pending_count}`;
            }
        } catch (error) {
            console.error("Error loading dashboard KPIs: ", error);
        }
    }

    async function loadSalesLineChart() {
        try {
            const response = await fetch('/api/dashboard/sales');
            const data = await response.json();
            const colors = getThemeColors();
            
            const ctx = document.getElementById('monthlySalesLineChart');
            if (!ctx) return;
            
            destroyChart('salesLine');
            
            charts['salesLine'] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Sales (₹)',
                        data: data.values,
                        borderColor: colors.primary,
                        backgroundColor: colors.primaryLight,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointBackgroundColor: colors.primary,
                        pointBorderColor: colors.cardBg,
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { padding: 10, borderRadius: 8 }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }
                        },
                        y: {
                            grid: { color: colors.gridColor },
                            ticks: { 
                                color: colors.textColor, 
                                font: { family: 'Inter', size: 10 },
                                callback: value => '₹' + value.toLocaleString()
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error loading sales line chart: ", error);
        }
    }

    async function loadRevenueBarChart() {
        if (isStaff) return;
        try {
            const response = await fetch('/api/dashboard/revenue');
            const data = await response.json();
            const colors = getThemeColors();
            
            const ctx = document.getElementById('monthlyRevenueBarChart');
            if (!ctx) return;
            
            destroyChart('revenueBar');
            
            charts['revenueBar'] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Collections (₹)',
                        data: data.revenue,
                        backgroundColor: colors.success,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { padding: 10, borderRadius: 8 }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }
                        },
                        y: {
                            grid: { color: colors.gridColor },
                            ticks: { 
                                color: colors.textColor, 
                                font: { family: 'Inter', size: 10 },
                                callback: value => '₹' + value.toLocaleString()
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error loading revenue bar chart: ", error);
        }
    }

    async function loadPaymentStatusPieChart() {
        try {
            const response = await fetch('/api/dashboard/payments-status');
            const data = await response.json();
            const colors = getThemeColors();
            
            const ctx = document.getElementById('paymentStatusPieChart');
            if (!ctx) return;
            
            destroyChart('paymentPie');
            
            charts['paymentPie'] = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [colors.success, colors.primary, colors.danger, colors.textColor],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'bottom',
                            labels: {
                                color: colors.textColor,
                                font: { family: 'Inter', size: 10 },
                                boxWidth: 10,
                                padding: 10
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error loading payment status pie chart: ", error);
        }
    }

    async function loadSalesCategoryDoughnutChart() {
        try {
            const response = await fetch('/api/dashboard/sales-category');
            const data = await response.json();
            const colors = getThemeColors();
            
            const ctx = document.getElementById('salesCategoryDoughnutChart');
            if (!ctx) return;
            
            destroyChart('salesDoughnut');
            
            charts['salesDoughnut'] = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [colors.primary, colors.success, colors.warning, colors.danger, colors.textColor],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: { 
                            position: 'bottom',
                            labels: {
                                color: colors.textColor,
                                font: { family: 'Inter', size: 10 },
                                boxWidth: 10,
                                padding: 10
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error loading sales category doughnut chart: ", error);
        }
    }

    async function loadCustomerGrowthAreaChart() {
        try {
            const response = await fetch('/api/dashboard/customer-growth');
            const data = await response.json();
            const colors = getThemeColors();
            
            const ctx = document.getElementById('customerGrowthAreaChart');
            if (!ctx) return;
            
            destroyChart('custGrowth');
            
            charts['custGrowth'] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Total Registered',
                        data: data.values,
                        borderColor: colors.primary,
                        backgroundColor: colors.primaryLight,
                        fill: true,
                        tension: 0.3,
                        borderWidth: 2,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { padding: 10 }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }
                        },
                        y: {
                            grid: { color: colors.gridColor },
                            ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error loading customer growth area chart: ", error);
        }
    }

    async function loadRevenueExpensesChart() {
        if (isStaff) return;
        try {
            const response = await fetch('/api/dashboard/revenue');
            const data = await response.json();
            const colors = getThemeColors();
            
            const ctx = document.getElementById('revenueExpensesBarChart');
            if (!ctx) return;
            
            destroyChart('revExpBar');
            
            charts['revExpBar'] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Collections (₹)',
                            data: data.revenue,
                            backgroundColor: colors.success,
                            borderRadius: 4
                        },
                        {
                            label: 'Expenses (₹)',
                            data: data.expenses,
                            backgroundColor: colors.danger,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'bottom',
                            labels: {
                                color: colors.textColor,
                                font: { family: 'Inter', size: 10 },
                                boxWidth: 10
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: colors.textColor, font: { family: 'Inter', size: 10 } }
                        },
                        y: {
                            grid: { color: colors.gridColor },
                            ticks: { 
                                color: colors.textColor, 
                                font: { family: 'Inter', size: 10 },
                                callback: value => '₹' + value.toLocaleString()
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error loading revenue vs expenses chart: ", error);
        }
    }

    async function fetchAdvancedAnalytics() {
        try {
            const response = await fetch('/api/dashboard/analytics');
            const data = await response.json();
            
            document.getElementById('anal-most-sold').innerHTML = data.most_sold_product;
            document.getElementById('anal-highest-rev').innerHTML = data.highest_revenue_product;
            document.getElementById('anal-most-active').innerHTML = data.most_active_customer;
            document.getElementById('anal-retention').innerHTML = data.customer_retention_rate;
            document.getElementById('anal-turnover').innerHTML = data.stock_turnover_ratio;
            document.getElementById('anal-avg-sale').innerHTML = data.average_sale_value;
            
            if (!isStaff) {
                document.getElementById('anal-avg-monthly').innerHTML = data.average_monthly_revenue;
                document.getElementById('anal-profit').innerHTML = data.monthly_profit;
            }
        } catch (error) {
            console.error("Error loading advanced analytics: ", error);
        }
    }

    async function fetchNotificationsAlerts() {
        try {
            const response = await fetch('/api/dashboard/notifications');
            const data = await response.json();
            
            const badge = document.getElementById('alerts-count-badge');
            const panel = document.getElementById('alerts-panel-list');
            if (badge) badge.innerText = data.length;
            
            if (!panel) return;
            panel.innerHTML = '';
            
            if (data.length === 0) {
                panel.innerHTML = `<div class="text-center py-4 text-muted text-xs">All clear. No outstanding system alerts!</div>`;
                return;
            }
            
            data.forEach(alert => {
                const borderClass = alert.type === 'danger' ? 'border-danger' : 'border-warning';
                const iconClass = alert.type === 'danger' ? 'bi-exclamation-octagon text-danger' : 'bi-exclamation-triangle text-warning';
                
                panel.innerHTML += `
                    <div class="d-flex align-items-center gap-3 p-2 bg-light border-start border-4 ${borderClass} rounded-2">
                        <i class="bi ${iconClass} fs-5"></i>
                        <div style="flex: 1;">
                            <strong class="text-xs d-block text-dark">${alert.title}</strong>
                            <span class="text-muted" style="font-size: 0.7rem; line-height: 1.2;">${alert.desc}</span>
                        </div>
                        <span class="text-muted text-xs">${alert.time}</span>
                    </div>
                `;
            });
        } catch (error) {
            console.error("Error loading system alerts: ", error);
        }
    }

    async function fetchActivities() {
        try {
            const response = await fetch('/api/dashboard/activities');
            const data = await response.json();
            
            const panel = document.getElementById('activities-panel-list');
            if (!panel) return;
            panel.innerHTML = '';
            
            if (data.length === 0) {
                panel.innerHTML = `<div class="text-center py-4 text-muted text-xs">No logged events found in timeline.</div>`;
                return;
            }
            
            data.forEach(log => {
                panel.innerHTML += `
                    <div class="d-flex gap-3 text-xs mb-1">
                        <div class="d-flex flex-column align-items-center">
                            <span class="d-block rounded-circle bg-primary-light text-primary d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">
                                <i class="bi bi-clock-history" style="font-size: 0.65rem;"></i>
                            </span>
                            <span class="d-block bg-light" style="width: 2px; flex: 1;"></span>
                        </div>
                        <div class="pb-3 border-bottom w-100">
                            <span class="text-muted text-xs d-block float-end">${log.time.split(' ')[1]}</span>
                            <strong class="text-dark">@${log.username}</strong>
                            <p class="text-muted text-xs mb-0 mt-0.5">${log.desc}</p>
                            <span class="text-muted text-xs" style="font-size: 0.65rem;">IP: ${log.ip}</span>
                        </div>
                    </div>
                `;
            });
        } catch (error) {
            console.error("Error loading system audit activity logs: ", error);
        }
    }

    // --- 4. Event Calendar Generator ---
    function drawEventCalendar() {
        const monthYearLabel = document.getElementById('calendar-month-year');
        const container = document.getElementById('calendar-days-container');
        const todayLabel = document.getElementById('calendar-today-str');
        
        if (!container) return;
        
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth();
        const date = now.getDate();
        
        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        if (monthYearLabel) monthYearLabel.innerText = `${monthNames[month]} ${year}`;
        if (todayLabel) todayLabel.innerText = `${date}${getOrdinalIndicator(date)}`;
        
        // Find calendar grids days limits
        const firstDayIndex = new Date(year, month, 1).getDay();
        const lastDay = new Date(year, month + 1, 0).getDate();
        const prevLastDay = new Date(year, month, 0).getDate();
        
        container.innerHTML = '';
        
        // Mock due days of month for visualization (e.g. 5, 10, 15, 20)
        const mockDueDays = [5, 10, 15, 20, 25];
        
        // Previous month days fill
        for (let x = firstDayIndex; x > 0; x--) {
            container.innerHTML += `<div class="calendar-cell inactive-month">${prevLastDay - x + 1}</div>`;
        }
        
        // Current month days
        for (let i = 1; i <= lastDay; i++) {
            let classes = "calendar-cell";
            if (i === date) {
                classes += " active-day";
            } else if (mockDueDays.includes(i)) {
                classes += " due-day";
            }
            container.innerHTML += `<div class="${classes}">${i}</div>`;
        }
        
        // Next month days fill
        const totalCells = firstDayIndex + lastDay;
        const remainingCells = 42 - totalCells; // Standard 6-row calendar
        for (let j = 1; j <= remainingCells; j++) {
            container.innerHTML += `<div class="calendar-cell inactive-month">${j}</div>`;
        }
    }

    function getOrdinalIndicator(d) {
        if (d > 3 && d < 21) return 'th';
        switch (d % 10) {
            case 1:  return "st";
            case 2:  return "nd";
            case 3:  return "rd";
            default: return "th";
        }
    }

    // --- 5. Redraw Logic on Theme Switch ---
    window.addEventListener('themeChanged', () => {
        // Redraw all charts to update gridlines and fonts color
        loadSalesLineChart();
        loadPaymentStatusPieChart();
        loadSalesCategoryDoughnutChart();
        loadCustomerGrowthAreaChart();
        
        if (!isStaff) {
            loadRevenueBarChart();
            loadRevenueExpensesChart();
        }
    });

    // --- 6. Date Filter Buttons listeners ---
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filterVal = btn.getAttribute('data-filter');
            if (filterVal !== 'custom') {
                activeFilter = filterVal;
                startDate = '';
                endDate = '';
                // Reload dashboard data
                fetchDashboardSummary();
            }
        });
    });
    
    if (applyCustomDateBtn && startDateInput && endDateInput) {
        applyCustomDateBtn.addEventListener('click', () => {
            if (startDateInput.value && endDateInput.value) {
                activeFilter = 'custom';
                startDate = startDateInput.value;
                endDate = endDateInput.value;
                fetchDashboardSummary();
            }
        });
    }

    // --- 7. Initialize Data Loaders ---
    fetchDashboardSummary();
    loadSalesLineChart();
    loadPaymentStatusPieChart();
    loadSalesCategoryDoughnutChart();
    loadCustomerGrowthAreaChart();
    fetchAdvancedAnalytics();
    fetchNotificationsAlerts();
    fetchActivities();
    drawEventCalendar();
    
    if (!isStaff) {
        loadRevenueBarChart();
        loadRevenueExpensesChart();
    }
});
