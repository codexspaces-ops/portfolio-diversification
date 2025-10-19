from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime
import re

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup(users_collection):
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            full_name = data.get('full_name')
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            full_name = request.form.get('full_name')
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
            "full_name": full_name,
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

@signup_bp.route('/check_username', methods=['POST'])
def check_username(users_collection):
    username = request.json.get('username', '').strip()
    exists = bool(username) and users_collection.find_one({"username": username}) is not None
    return jsonify({"available": bool(username) and not exists})

@signup_bp.route('/check_email', methods=['POST'])
def check_email(users_collection):
    email = request.json.get('email', '').strip()
    if not email:
        return jsonify({"available": False, "error": "Email is required."})
    
    # A simple regex to ensure we don't query the DB with invalid formats
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return jsonify({"available": False, "error": "Invalid email format."})

    exists = users_collection.find_one({"email": email}) is not None
    return jsonify({"available": not exists})
