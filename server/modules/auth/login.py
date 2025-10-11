from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login(users_collection):
    if request.method == 'POST':
        # Check if request is JSON or form
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')

        # Validate inputs
        if not email or not password:
            msg = {"error": "Email and password are required"}
            if request.is_json:
                return jsonify(msg), 400
            flash(msg["error"], "danger")
            return render_template('login.html')

        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session['user'] = email

            if request.is_json:
                return jsonify({"message": "Login successful!", "user": email}), 200

            flash("Login successful!", "success")
            return redirect(url_for('login.dashboard'))
        else:
            msg = {"error": "Invalid email or password"}
            if request.is_json:
                return jsonify(msg), 401
            flash(msg["error"], "danger")

    return render_template('login.html')


@login_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login.login'))
    return f"Welcome {session['user']}!"
