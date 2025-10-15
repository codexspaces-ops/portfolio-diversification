document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');

    function showForm(form) {
        if (form === 'login') {
            loginForm.style.display = '';
            signupForm.style.display = 'none';
            loginTab.classList.add('active');
            signupTab.classList.remove('active');
        } else {
            loginForm.style.display = 'none';
            signupForm.style.display = '';
            loginTab.classList.remove('active');
            signupTab.classList.add('active');
        }
    }

    loginTab.addEventListener('click', function () {
        showForm('login');
    });
    signupTab.addEventListener('click', function () {
        showForm('signup');
    });

    // Optionally, show signup form if there was a signup error
    if (window.location.hash === "#signup" || (typeof signupForm !== "undefined" && signupForm && signupForm.querySelector("input[name='username']").value)) {
        showForm('signup');
    }
});