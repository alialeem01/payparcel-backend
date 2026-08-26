(function () {
    function pinSidebarOpen() {
        var sidebar = document.getElementById('nav-sidebar');
        if (!sidebar) return;

        sidebar.style.setProperty('transform', 'none', 'important');
        sidebar.style.setProperty('left', '0px', 'important');
        sidebar.style.setProperty('display', 'block', 'important');

        var width = sidebar.offsetWidth || 288;
        document.body.style.setProperty('padding-left', width + 'px', 'important');

        document.querySelectorAll('.material-symbols-outlined').forEach(function (el) {
            var text = el.textContent.trim();
            if (text === 'dock_to_right' || text === 'close') {
                el.style.display = 'none';
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', pinSidebarOpen);
    } else {
        pinSidebarOpen();
    }
    window.addEventListener('resize', pinSidebarOpen);
})();