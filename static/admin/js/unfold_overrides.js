(function () {
    function attachModalDelete() {
        document.querySelectorAll('a[href*="/delete/"]').forEach(function (link) {
            if (link.dataset.modalBound) return;
            link.dataset.modalBound = 'true';
            link.addEventListener('click', function (e) {
                e.preventDefault();
                var href = link.getAttribute('href');
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) return;

                fetch(href, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                }).then(function (resp) { return resp.text(); }).then(function (html) {
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(html, 'text/html');
                    var form = doc.querySelector('form');
                    if (!form) { window.location.href = href; return; }
                    form.style.display = 'none';
                    document.body.appendChild(form);
                    form.submit();
                }).catch(function () {
                    window.location.href = href;
                });
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachModalDelete);
    } else {
        attachModalDelete();
    }
})();