document.addEventListener('DOMContentLoaded', () => _app.init());

window._app = {
    init: function() {
        this.initCookieAlert();
        this.bindCollapse();
    },
    initCookieAlert: function() {
        const test = document.cookie.match(/\bac=1\b/)
            || (location.search && location.search.match('from=app'));
        const removeCookie = () => {
            document.body.classList.remove('cookie-alert-in');
            document.cookie = 'ac=1;path=/';
        };
        if (test) {
            removeCookie()
        } else {
            document.body.classList.add('cookie-alert-in');
        };
        bindEvent('.cookie-alert button', 'click', removeCookie);
    },
    bindCollapse: function() {
        bindEvent('[data-toggle="collapse"]', 'click', (event, target) => {
            event.preventDefault();
            const selector = target.getAttribute('href') || target.dataset.target;
            const collapse = document.querySelector(selector);
            if (collapse.classList.contains('show')) {
                collapse.classList.remove('show');
            } else {
                collapse.classList.add('show');
            }
        });
    }
}

function bindEvent(selector, type, listener) {
    document.body.addEventListener(type, event => {
        const target = event.target.closest(selector);
        if (target) {
            listener(event, target);
        }
    });
}

