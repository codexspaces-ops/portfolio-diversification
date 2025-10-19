from flask import Flask, render_template, redirect, url_for, session
from app.auth.login import login_bp
from app.auth.signup import signup_bp
from app.config import users_collection
import secrets

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = secrets.token_hex(10)

app.register_blueprint(login_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})
app.register_blueprint(signup_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Ensure user is logged in
    if 'user' not in session:
        return redirect(url_for('login.login'))
    return render_template('dashboard.html',full_name=session.get('full_name'))

@app.route('/importdata')
def importdata():
    # Ensure user is logged in
    if 'user' not in session:
        return redirect(url_for('login.login'))
    return render_template('importdata.html',full_name=session.get('full_name'))

if __name__ == '__main__':
    app.run(debug=True)
