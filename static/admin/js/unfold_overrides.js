(function () {
    localStorage.setItem('theme', 'light');
    document.documentElement.classList.remove('dark');

    function setupDashboardShortcut() {
        document.addEventListener('click', function (e) {
            var el = e.target.closest('.material-symbols-outlined');
            if (el && el.textContent.trim() === 'dock_to_right') {
                e.stopImmediatePropagation();
                e.preventDefault();
                window.location.href = '/admin/';
            }
        }, true);

        document.querySelectorAll('.material-symbols-outlined').forEach(function (el) {
            if (el.textContent.trim() === 'dock_to_right') {
                el.title = 'Dashboard';
                el.style.cursor = 'pointer';
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupDashboardShortcut);
    } else {
        setupDashboardShortcut();
    }
})();