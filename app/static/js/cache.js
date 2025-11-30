(function () {
    const loginUrl = "{{ url_for('login') }}";
    const sessionEndpoint = "{{ url_for('session_status') }}";

    function enforceSession() {
        fetch(sessionEndpoint, { cache: 'no-store' })
            .then(r => r.ok ? r.json() : Promise.reject())
            .then(data => {
                if (!data.logged_in) {
                    window.location.replace(loginUrl);
                }
            })
            .catch(() => window.location.replace(loginUrl));
    }

    // Run on load and when user navigates via back button
    enforceSession();
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) enforceSession();
    });

    // Logout button
    window.handleLogout = function() {
        fetch("{{ url_for('logout') }}", { method: 'GET', cache: 'no-store' })
            .finally(() => window.location.replace(loginUrl));
    };
})();