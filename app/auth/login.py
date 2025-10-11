from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login(users_collection):
    if request.method == 'POST':
        # Check if request is JSON or form
        if request.is_json:
            data = request.get_json()
            identifier = data.get('identifier')  # support either username or email with a single field
            password = data.get('password')
        else:
            identifier = request.form.get('identifier')  # field named identifier for username/email
            password = request.form.get('password')
        
        # Validate inputs
        if not identifier or not password:
            msg = {"error": "Username/Email and password are required"}
            if request.is_json:
                return jsonify(msg), 400
            flash(msg["error"], "danger")
            return render_template('login.html')

        # Find user by email or username
        user = users_collection.find_one({
            "$or": [
                {"email": identifier},
                {"username": identifier}
            ]
        })

        if user and check_password_hash(user['password'], password):
            session['user'] = user['email']

            if request.is_json:
                return jsonify({"message": "Login successful!", "user": user['email']}), 200

            flash("Login successful!", "success")
            return redirect(url_for('login.dashboard'))
        else:
            msg = {"error": "Invalid username/email or password"}
            if request.is_json:
                return jsonify(msg), 401
            flash(msg["error"], "danger")
            return render_template('login.html')

    return render_template('login.html')

@login_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login.login'))
    return f"Welcome {session['user']}!"
