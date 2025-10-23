import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, session
from flask_session import Session
from flask_login import logout_user
from app.auth.login import login_bp
from app.auth.signup import signup_bp
from app.config import users_collection  # MongoDB "user" collection

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = secrets.token_hex(16)

# =========================
# Flask-Session MongoDB config
# =========================
mongo_client = users_collection.database.client
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_MONGODB'] = mongo_client
app.config['SESSION_MONGODB_DB'] = users_collection.database.name
app.config['SESSION_MONGODB_COLLECTION'] = 'sessions'
Session(app)

# =========================
# MongoDB collections
# =========================
user_collection = users_collection
sessions_collection = mongo_client[users_collection.database.name]['sessions']

# Make collections available in blueprints
app.config['USERS_COLLECTION'] = user_collection
app.config['SESSIONS_COLLECTION'] = sessions_collection

# =========================
# Register blueprints
# =========================
app.register_blueprint(login_bp, url_prefix="/auth")
app.register_blueprint(signup_bp, url_prefix="/auth")

# =========================
# Utility functions
# =========================
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

def clear_user_sessions(user_id):
    """Delete all existing sessions for a user"""
    if user_id:
        sessions_collection.delete_many({"user_id": user_id})

def save_user_session(user_id, session_data, expiration_minutes=60):
    """Upsert session for user"""
    if user_id:
        sessions_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "session_data": session_data,
                "expiration": datetime.utcnow() + timedelta(minutes=expiration_minutes)
            }},
            upsert=True
        )

# =========================
# After-request headers
# =========================
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# =========================
# Routes
# =========================
@app.route('/', endpoint='home_page')
def home_page():
    return render_template('index.html')

@app.route('/login', endpoint='login')
def login_redirect():
    # Clear any existing session to prevent auto-login
    session.clear()
    return redirect(url_for('login.login'))

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

@app.route('/session')
def session_status():
    return {"logged_in": bool(session.get('user'))}

@app.route('/logout')
def logout():
    user_id = session.get('user')
    clear_user_sessions(user_id)
    session.clear()
    logout_user()
    resp = redirect(url_for('login.login'))
    resp.set_cookie(key=app.session_cookie_name, value='', expires=0, path='/')
    return resp

# =========================
# Run
# =========================
if __name__ == '__main__':
    app.run(debug=True, port=3000)
