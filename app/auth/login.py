from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login(users_collection):
    if request.method == 'POST':
        is_json_request = request.is_json
        
        if is_json_request:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request must be a valid JSON."}), 400
            identifier = data.get('identifier')
            password = data.get('password')
        else:
            identifier = request.form.get('identifier')
            password = request.form.get('password')

        if not identifier or not password:
            if is_json_request:
                return jsonify({"error": "Username/Email and password are required"}), 400
            flash("Username/Email and password are required", "danger")
            return render_template('login.html')

        # Find user by email or username
        user = users_collection.find_one({
            "$or": [
                {"email": identifier},
                {"username": identifier}
            ]
        })

        # Case 1: User does not exist
        if not user:
            if is_json_request:
                return jsonify({"error": "User does not exist."}), 404
            flash("User does not exist. Please check your username/email or sign up.", "danger")
            return render_template('login.html')

        # Case 2: User exists, but password is incorrect
        if not check_password_hash(user['password'], password):
            if is_json_request:
                return jsonify({"error": "Incorrect password."}), 401
            flash("Incorrect password. Please try again.", "danger")
            return render_template('login.html')

        # Case 3: Login successful
        session['user'] = user['email']
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        if is_json_request:
            return jsonify({"message": "Login successful!"}), 200
        
        flash("Login successful!", "success")
        return redirect(url_for('login.dashboard'))

    return render_template('login.html')

@login_bp.route('/dashboard')
def dashboard(users_collection):
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login.login'))
    
    user = users_collection.find_one({"email": session['user']})
    full_name = user.get("full_name", user.get("username", "User")) if user else "User"
    return f"Welcome {full_name}!"