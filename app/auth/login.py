from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.security import check_password_hash
from datetime import datetime
from bson.objectid import ObjectId

login_bp = Blueprint('login', __name__)

# Helper: Save session in MongoDB
def save_user_session(user_id):
    sessions_collection = current_app.config['SESSIONS_COLLECTION']
    session_data = {
        "user_id": user_id,
        "full_name": session.get("full_name"),
        "email": session.get("email"),
        "last_updated": datetime.utcnow()
    }
    # Upsert: update if exists, else insert
    sessions_collection.update_one(
        {"user_id": user_id},
        {"$set": session_data},
        upsert=True
    )

# =========================
# LOGIN ROUTE
# =========================
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    users_collection = current_app.config['USERS_COLLECTION']

    if request.method == 'POST':
        is_json = request.is_json
        if is_json:
            data = request.get_json() or {}
            identifier = data.get('identifier')
            password = data.get('password')
        else:
            identifier = request.form.get('identifier')
            password = request.form.get('password')

        if not identifier or not password:
            msg = "Username/Email and password are required"
            if is_json:
                return jsonify({"error": msg}), 400
            flash(msg, "danger")
            return render_template('login.html')

        user = users_collection.find_one({
            "$or": [{"email": identifier}, {"username": identifier}]
        })

        if not user or not check_password_hash(user['password'], password):
            msg = "Invalid username/email or password."
            if is_json:
                return jsonify({"error": msg}), 401
            flash(msg, "danger")
            return render_template('login.html')

        # ✅ Successful login
        session.clear()
        session['user'] = str(user['_id'])
        session['full_name'] = user.get('full_name', user.get('username', 'User'))
        session['email'] = user.get('email')

        # Save session in MongoDB
        save_user_session(session['user'])

        # Update last_login timestamp
        users_collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        if is_json:
            return jsonify({"message": "Login successful!"}), 200

        flash("Login successful!", "success")
        return redirect(url_for('login.dashboard'))

    return render_template('login.html')

# =========================
# DASHBOARD ROUTE
# =========================
@login_bp.route('/dashboard')
def dashboard():
    users_collection = current_app.config['USERS_COLLECTION']

    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login.login'))

    user = users_collection.find_one({"_id": ObjectId(session['user'])})
    full_name = user.get("full_name", user.get("username", "User")) if user else "User"
    email = user.get("email", "user@example.com") if user else "user@example.com"

    return render_template('dashboard.html', full_name=full_name, email=email)
