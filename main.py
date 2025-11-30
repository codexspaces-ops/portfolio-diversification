import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, session,request
from flask_session import Session
from flask_login import logout_user
from app.auth.login import login_bp
from app.auth.signup import signup_bp
import pandas as pd
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


@app.route('/importdata', methods=['GET', 'POST'])
def importdata():
    if 'user' not in session:
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        print("✅ Form submitted")
        file = request.files.get('file')
        if not file:
            return render_template('importdata.html', error="No file uploaded.", full_name=session.get('full_name'))
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"📁 File saved at: {filepath}")
        ext = os.path.splitext(filename)[1].lower()
        df = None
        try:
            # --- Handle multiple file formats ---
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif ext == '.csv':
                df = pd.read_csv(filepath)
            elif ext == '.json':
                df = pd.read_json(filepath)
            elif ext in ['.txt', '.tsv']:
                try:
                    df = pd.read_csv(filepath, sep='\t')
                except Exception:
                    df = pd.read_csv(filepath, sep=',')
            else:
                return render_template(
                    'importdata.html',
                    error=f"Unsupported file type: {ext}. Please upload Excel, CSV, JSON, or TXT.",
                    full_name=session.get('full_name')
                )

            print("✅ Columns detected:", df.columns.tolist())
            possible_sector_cols = [col for col in df.columns if 'sector' in col.lower()]
            possible_value_cols = [col for col in df.columns if 'value' in col.lower() or 'amount' in col.lower()]
            if possible_sector_cols and possible_value_cols:
                sector_col = possible_sector_cols[0]
                value_col = possible_value_cols[0]
                summary = df.groupby(sector_col)[value_col].sum().reset_index()
                total = summary[value_col].sum()
                summary['Percentage'] = (summary[value_col] / total * 100).round(2)
                summary = summary.sort_values(by='Percentage', ascending=False)
                print("✅ Summary prepared")
                return render_template(
                    'portfolio_summary.html',
                    tables=summary.to_dict(orient='records'),
                    full_name=session.get('full_name')
                )
            else:
                return render_template(
                    'importdata.html',
                    error="Required columns not found. Please ensure your file has 'Sector' and 'Value' or 'Amount' columns.",
                    full_name=session.get('full_name')
                )
        except Exception as e:
            print("❌ Error reading file:", e)
            return render_template(
                'importdata.html',
                error=f"Error reading file: {e}",
                full_name=session.get('full_name')
            )
    return render_template('importdata.html', full_name=session.get('full_name'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login.login'))
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
