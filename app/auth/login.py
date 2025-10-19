from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login(users_collection):
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request must be a valid JSON."}), 400
            identifier = data.get('identifier')
            password = data.get('password')
        else:
            identifier = request.form.get('identifier')
            password = request.form.get('password')

        if not identifier or not password:
            if request.is_json:
                return jsonify({"error": "Username/Email and password are required"}), 400
            flash("Username/Email and password are required", "danger")
            return render_template('login.html')

        user = users_collection.find_one({
            "$or": [
                {"email": identifier},
                {"username": identifier}
            ]
        })

        if user and check_password_hash(user['password'], password):
            # Store user info in session
            session['user'] = user['email']
            session['full_name'] = user.get('full_name', user.get('username'))
            session['email'] = user.get('email')

            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )

            if request.is_json:
                return jsonify({"message": "Login successful!"}), 200

            flash("Login successful!", "success")
            return redirect(url_for('login.dashboard'))
        else:
            if request.is_json:
                return jsonify({"error": "Invalid username/email or password"}), 401

            flash("Invalid username/email or password", "danger")
            return render_template('login.html')

    # Render login page on GET requests
    return render_template('login.html')


@login_bp.route('/dashboard')
def dashboard(users_collection):
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login.login'))

    user = users_collection.find_one({"email": session['user']})
    full_name = user.get("full_name", user.get("username", "User")) if user else "User"
    email = user.get("email", "user@example.com") if user else "user@example.com"   
    return render_template('dashboard.html', full_name=full_name, email=email)