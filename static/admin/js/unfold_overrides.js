(function () {
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachModalDelete);
    } else {
        attachModalDelete();
    }
})();