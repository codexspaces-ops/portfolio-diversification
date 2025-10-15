from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup(users_collection):
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
        
        # Validation
        if not email or not password or not username:
            msg = {"error": "Email, username, and password are required"}
            return jsonify(msg), 400

        # Check for existence
        username_exists = users_collection.find_one({"username": username}) is not None
        email_exists = users_collection.find_one({"email": email}) is not None

        if username_exists and email_exists:
            msg = {"error": "Both username and email are already in use."}
            if request.is_json:
                return jsonify(msg), 400
            flash(msg["error"], "warning")
            return render_template('signup.html')
        elif email_exists:
            msg = {"error": "Email already in use."}
            if request.is_json:
                return jsonify(msg), 400
            flash(msg["error"], "warning")
            return render_template('signup.html')
        elif username_exists:
            msg = {"error": "Username already in use."}
            if request.is_json:
                return jsonify(msg), 400
            flash(msg["error"], "warning")
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)
        now = datetime.utcnow()

        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "roles": ["user"],
            "created_at": now,
            "last_login": now,
            "is_active": True
        }

        users_collection.insert_one(user_doc)

        if request.is_json:
            return jsonify({"message": "Signup successful! Please login."}), 201
        else:
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login.login'))

    return render_template('signup.html')
