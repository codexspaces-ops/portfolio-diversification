from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from datetime import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login(users_collection):
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        if not identifier or not password:
            flash("Username/Email and password are required", "danger")
            return render_template('login.html')

        user = users_collection.find_one({
            "$or": [
                {"email": identifier},
                {"username": identifier}
            ]
        })

        if user and check_password_hash(user['password'], password):
            session['user'] = user['email']
            # Update last_login field
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            flash("Login successful!", "success")
            return redirect(url_for('login.dashboard'))
        else:
            flash("Invalid username/email or password", "danger")
            return render_template('login.html')

    return render_template('login.html')

@login_bp.route('/dashboard')
def dashboard(users_collection):
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login.login'))
    user = users_collection.find_one({"email": session['user']})
    full_name = user.get("full_name", user.get("username", "User")) if user else "User"
    return f"Welcome {full_name}!"