from flask import Flask, render_template, redirect, url_for, session
from functools import wraps
from datetime import timedelta
from app.auth.login import login_bp
from app.auth.signup import signup_bp
from app.config import users_collection
import secrets

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = secrets.token_hex(32)

# Keep sessions persistent for a reasonable time so users don't have to login every time.
# Adjust lifetime as needed (e.g., hours=8, days=14).
app.permanent_session_lifetime = timedelta(days=14)

# Recommended cookie hardening (adjust depending on your deployment)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # or 'Strict' if you need stronger CSRF protection
    SESSION_COOKIE_SECURE=True  # enable in production when using HTTPS
)

app.register_blueprint(login_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})
app.register_blueprint(signup_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})

# Prevent browser caching for protected responses so "back" won't show protected pages from cache
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def login_required(view):
    """Decorator to protect routes that require an authenticated user."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user' not in session:
            # Not logged in, redirect to blueprint login endpoint
            return redirect(url_for('login.login'))
        return view(*args, **kwargs)
    return wrapped_view

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/login')
def login():
    # If already logged in, send to dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear all session data so the user stays logged out even if they press back.
    session.clear()
    # After clearing the session, redirect to the public home page.
    return redirect(url_for('home_page'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', full_name=session.get('full_name'))

@app.route('/importdata')
@login_required
def importdata():
    return render_template('importdata.html', full_name=session.get('full_name'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', full_name=session.get('full_name'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)
