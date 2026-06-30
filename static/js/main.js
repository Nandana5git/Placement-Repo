// Smart College Placement Management Portal - Client Interactions

document.addEventListener('DOMContentLoaded', function() {
    // 1. Sidebar responsiveness toggler
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            if (sidebar.style.display === 'none' || sidebar.classList.contains('collapsed')) {
                sidebar.style.display = 'flex';
                sidebar.classList.remove('collapsed');
            } else {
                sidebar.style.display = 'none';
                sidebar.classList.add('collapsed');
            }
        });
    }

    // 2. Automatically fade out alert messages after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Check if bootstrap alert exists and dismiss it smoothly
            alert.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 4000);
    });

    // 3. Simple Tooltip triggers if bootstrap tooltips are enabled
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});
