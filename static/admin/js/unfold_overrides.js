document.addEventListener('DOMContentLoaded', function () {
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
});

/* Normalize row heights so readonly text and input boxes align consistently */
.flex.flex-col.gap-1 {
    min-height: 42px;
    justify-content: center;
}