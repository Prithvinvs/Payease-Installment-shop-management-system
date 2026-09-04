/**
========================================================================
PayEase Main Javascript Controller
Handles theme toggling, sidebar toggles, tooltips, and interactive
component initialization.
========================================================================
*/

document.addEventListener('DOMContentLoaded', () => {
    // --- Sidebar Collapse Toggler ---
    const sidebar = document.getElementById('sidebar');
    const sidebarCollapseBtn = document.getElementById('sidebarCollapse');
    
    if (sidebarCollapseBtn && sidebar) {
        sidebarCollapseBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    // --- Light/Dark Theme Controller ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');
    const htmlElement = document.documentElement;
    
    // Check local storage for preference, default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            let activeTheme = htmlElement.getAttribute('data-theme');
            let targetTheme = 'light';
            
            if (activeTheme === 'light') {
                targetTheme = 'dark';
            }
            
            htmlElement.setAttribute('data-theme', targetTheme);
            localStorage.setItem('theme', targetTheme);
            updateThemeIcon(targetTheme);
            
            // Dispatch a custom event to redraw charts if they are present
            window.dispatchEvent(new Event('themeChanged'));
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleIcon) return;
        if (theme === 'dark') {
            themeToggleIcon.className = 'bi bi-sun';
        } else {
            themeToggleIcon.className = 'bi bi-moon-stars';
        }
    }

    // --- Bootstrap Tooltips Initialization ---
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // --- Disabled Feature Placeholders Action ---
    // Safely block default click events on future modules during UI previewing
    document.querySelectorAll('.disabled-feature').forEach((elem) => {
        elem.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Trigger tooltip trigger elements manually if they have a tooltip
            const tooltipInst = bootstrap.Tooltip.getInstance(elem);
            if (tooltipInst) {
                tooltipInst.show();
                setTimeout(() => tooltipInst.hide(), 2500);
            }
        });
    });
});
