document.addEventListener("DOMContentLoaded", function () {
    // --- Form and Tab Elements ---
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');

    // --- Button Elements ---
    const loginButton = loginForm.querySelector('button[type="submit"]');
    const signupButton = signupForm.querySelector('button[type="submit"]');

    // --- Signup Form Validity State ---
    const signupValidity = {
        fullName: false,
        username: false,
        email: false,
        password: false
    };

    /**
     * Clears only the live validation hints on the signup form.
     * Server-flashed messages are left alone.
     */
    function clearLiveValidationMessages() {
        // Clear all live validation hints
        document.querySelectorAll('.input-hint').forEach(hint => {
            hint.textContent = '';
            hint.classList.remove('show', 'success', 'error');
        });
        // Hide the password checklist
        const checklist = document.getElementById('passwordChecklist');
        if (checklist) {
            checklist.classList.remove('show');
        }
    }

    /**
     * Toggles the visibility of login/signup forms.
     */
    function showForm(formToShow) {
        clearLiveValidationMessages(); // Clear only live hints on tab switch

        if (formToShow === 'login') {
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
        validateLoginForm();
        validateSignupForm();
    }

    // --- Validation Logic ---

    function validateLoginForm() {
        const identifier = loginForm.querySelector('input[name="identifier"]').value;
        const password = loginForm.querySelector('input[name="password"]').value;
        loginButton.disabled = !(identifier && password);
    }

    function validateSignupForm() {
        const allValid = Object.values(signupValidity).every(Boolean);
        signupButton.disabled = !allValid;
    }

    // --- Event Listeners ---

    loginTab.addEventListener('click', () => showForm('login'));
    signupTab.addEventListener('click', () => showForm('signup'));

    // Add listeners to login form
    loginForm.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', validateLoginForm);
    });

    // --- Signup Form Live Validation ---

    // Full Name
    const fullNameInput = signupForm.querySelector('input[name="full_name"]');
    fullNameInput.addEventListener('input', () => {
        signupValidity.fullName = fullNameInput.value.trim().length > 0;
        validateSignupForm();
    });

    // Username
    const usernameInput = document.getElementById("signupUsername");
    const usernameStatus = document.getElementById("usernameStatus");
    let usernameTimeout = null;
    usernameInput.addEventListener("input", function () {
        clearTimeout(usernameTimeout);
        const username = usernameInput.value.trim();
        signupValidity.username = false; // Invalidate until confirmed
        usernameStatus.textContent = "";
        usernameStatus.classList.remove('show', 'success', 'error');
        if (username.length < 3) {
            validateSignupForm();
            return;
        }
        usernameTimeout = setTimeout(function () {
            fetch(usernameInput.dataset.checkUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username })
            })
            .then(r => r.ok ? r.json() : { available: false })
            .then(data => {
                usernameStatus.classList.add('show');
                if (data.available) {
                    usernameStatus.textContent = "✓ Username available";
                    usernameStatus.classList.add('success');
                    usernameStatus.classList.remove('error');
                    signupValidity.username = true;
                } else {
                    usernameStatus.textContent = "✗ Username already taken";
                    usernameStatus.classList.add('error');
                    usernameStatus.classList.remove('success');
                    signupValidity.username = false;
                }
                validateSignupForm();
            });
        }, 400);
    });

    // Email
    const emailInput = document.getElementById('signupEmail');
    const emailError = document.getElementById('emailError');
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    let emailTimeout = null;
    emailInput.addEventListener('input', function () {
        clearTimeout(emailTimeout);
        const email = emailInput.value.trim();
        signupValidity.email = false; // Invalidate until confirmed
        emailError.textContent = "";
        emailError.classList.remove('show', 'success', 'error');
        if (!email) {
            validateSignupForm();
            return;
        }
        if (!emailRe.test(email)) {
            emailError.textContent = "Please enter a valid email address.";
            emailError.classList.add('show', 'error');
            validateSignupForm();
            return;
        }
        emailTimeout = setTimeout(function () {
            fetch(emailInput.dataset.checkUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email })
            })
            .then(r => r.ok ? r.json() : { available: false }) // Corrected this line
            .then(data => {
                emailError.classList.add('show');
                if (data.available) {
                    emailError.textContent = "✓ Email is available";
                    emailError.classList.add('success');
                    emailError.classList.remove('error');
                    signupValidity.email = true;
                } else {
                    emailError.textContent = "✗ Email is already in use";
                    emailError.classList.add('error');
                    emailError.classList.remove('success');
                    signupValidity.email = false;
                }
                validateSignupForm();
            });
        }, 500);
    });

    // Password
    const passwordInput = document.getElementById('signupPassword');
    const checklist = document.getElementById('passwordChecklist');
    const specItems = {
        length: document.getElementById('length'),
        upper: document.getElementById('upper'),
        lower: document.getElementById('lower'),
        number: document.getElementById('number'),
        special: document.getElementById('special')
    };

    function updateChecklist(value) {
        const validations = {
            length: value.length >= 8,
            upper: /[A-Z]/.test(value),
            lower: /[a-z]/.test(value),
            number: /\d/.test(value),
            special: /[^A-Za-z0-9]/.test(value)
        };
        toggleValid(specItems.length, validations.length, "At least 8 characters");
        toggleValid(specItems.upper, validations.upper, "Uppercase letter");
        toggleValid(specItems.lower, validations.lower, "Lowercase letter");
        toggleValid(specItems.number, validations.number, "Number");
        toggleValid(specItems.special, validations.special, "Special character");
        return Object.values(validations).every(Boolean);
    }

    function toggleValid(el, ok, label) {
        if (!el) return;
        el.classList.toggle('valid', ok);
        el.textContent = `${ok ? '✓' : '✗'} ${label}`;
    }

    passwordInput.addEventListener('focus', () => checklist.classList.add('show'));
    passwordInput.addEventListener('input', () => {
        checklist.classList.add('show');
        signupValidity.password = updateChecklist(passwordInput.value);
        validateSignupForm();
    });
    passwordInput.addEventListener('blur', () => {
        if (!passwordInput.value) checklist.classList.remove('show');
    });

    // --- Initial State ---
    if (window.location.hash === "#signup") {
        showForm('signup');
    } else {
        showForm('login');
    }
});