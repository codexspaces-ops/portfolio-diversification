document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');

    // Toggle forms without inline styles
    function showForm(form) {
        if (form === 'login') {
            loginForm.classList.remove('is-hidden');
            signupForm.classList.add('is-hidden');
            loginTab.classList.add('active');
            signupTab.classList.remove('active');
        } else {
            loginForm.classList.add('is-hidden');
            signupForm.classList.remove('is-hidden');
            loginTab.classList.remove('active');
            signupTab.classList.add('active');
        }
    }

    loginTab.addEventListener('click', () => showForm('login'));
    signupTab.addEventListener('click', () => showForm('signup'));

    // Username availability check (debounced)
    const usernameInput = document.getElementById("signupUsername");
    const usernameStatus = document.getElementById("usernameStatus");
    let usernameTimeout = null;

    if (usernameInput && usernameStatus) {
        usernameInput.addEventListener("input", function () {
            clearTimeout(usernameTimeout);
            const username = usernameInput.value.trim();

            // Reset hint state
            usernameStatus.textContent = "";
            usernameStatus.classList.remove('show', 'success', 'error');

            if (username.length < 3) return;

            usernameTimeout = setTimeout(function () {
                fetch(usernameInput.dataset.checkUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username })
                })
                .then(r => r.ok ? r.json() : { available: false })
                .then(data => {
                    if (!data) return;
                    usernameStatus.classList.add('show');
                    if (data.available) {
                        usernameStatus.textContent = "✓ Username available";
                        usernameStatus.classList.remove('error');
                        usernameStatus.classList.add('success');
                    } else {
                        usernameStatus.textContent = "✗ Username already taken";
                        usernameStatus.classList.remove('success');
                        usernameStatus.classList.add('error');
                    }
                })
                .catch(() => {
                    usernameStatus.classList.add('show', 'error');
                    usernameStatus.textContent = "Error checking availability";
                });
            }, 400);
        });
    }

    // Email validation (live)
    const emailInput = document.getElementById('signupEmail');
    const emailError = document.getElementById('emailError');
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (emailInput && emailError) {
        emailInput.addEventListener('input', function () {
            const email = emailInput.value.trim();
            if (email && !emailRe.test(email)) {
                emailError.textContent = "Please enter a valid email address.";
                emailError.classList.add('show', 'error');
                emailError.classList.remove('success');
            } else if (email) {
                emailError.textContent = "✓ Looks good";
                emailError.classList.add('show', 'success');
                emailError.classList.remove('error');
            } else {
                emailError.textContent = "";
                emailError.classList.remove('show', 'success', 'error');
            }
        });
    }

    // Password checklist (smooth reveal)
    const passwordInput = document.getElementById('signupPassword');
    const checklist = document.getElementById('passwordChecklist');
    const lengthItem = document.getElementById('length');
    const upperItem = document.getElementById('upper');
    const lowerItem = document.getElementById('lower');
    const numberItem = document.getElementById('number');
    const specialItem = document.getElementById('special');

    function updateChecklist(value) {
        // Length
        toggleValid(lengthItem, value.length >= 8, "At least 8 characters");
        // Uppercase
        toggleValid(upperItem, /[A-Z]/.test(value), "Uppercase letter");
        // Lowercase
        toggleValid(lowerItem, /[a-z]/.test(value), "Lowercase letter");
        // Number
        toggleValid(numberItem, /\d/.test(value), "Number");
        // Special
        toggleValid(specialItem, /[^A-Za-z0-9]/.test(value), "Special character");
    }

    function toggleValid(el, ok, label) {
        if (!el) return;
        if (ok) {
            el.classList.add('valid');
            el.textContent = `✓ ${label}`;
        } else {
            el.classList.remove('valid');
            el.textContent = `✗ ${label}`;
        }
    }

    if (passwordInput && checklist) {
        passwordInput.addEventListener('focus', () => {
            checklist.classList.add('show');
        });
        passwordInput.addEventListener('input', () => {
            checklist.classList.add('show');
            updateChecklist(passwordInput.value);
        });
        passwordInput.addEventListener('blur', () => {
            if (!passwordInput.value) {
                checklist.classList.remove('show');
            }
        });
    }

    // If deep-linking or after signup error, show signup tab
    if (window.location.hash === "#signup") {
        showForm('signup');
    }
});