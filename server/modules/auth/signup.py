from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime

signup_bp = Blueprint('signup', __name__)

def extract_age(age):
    if isinstance(age, dict) and '$numberInt' in age:
        return int(age['$numberInt'])
    elif isinstance(age, (int, float, str)) and age is not None:
        try:
            return int(age)
        except ValueError:
            return None
    return None

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup(users_collection):
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username   = data.get('username')
            email      = data.get('email')
            password   = data.get('password')
            age        = data.get('age')
            gender     = data.get('gender')
            first_name = data.get('first_name')
            last_name  = data.get('last_name')
            phone      = data.get('phone')
            street     = data.get('street')
            city       = data.get('city')
            state      = data.get('state')
            zip_code   = data.get('zip')
        else:
            username   = request.form.get('username')
            email      = request.form.get('email')
            password   = request.form.get('password')
            age        = request.form.get('age')
            gender     = request.form.get('gender')
            first_name = request.form.get('first_name')
            last_name  = request.form.get('last_name')
            phone      = request.form.get('phone')
            street     = request.form.get('street')
            city       = request.form.get('city')
            state      = request.form.get('state')
            zip_code   = request.form.get('zip')
        
        # Validation
        if not email or not password or not username:
            return jsonify({"error": "Email, username, and password are required"}), 400

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

        # Extract age robustly
        age_value = extract_age(age)

        hashed_password = generate_password_hash(password)
        now = datetime.utcnow()

        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "age": age_value,
            "gender": gender,
            "roles": ["user"],
            "created_at": now,
            "last_login": now,
            "is_active": True,
            "profile": {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "address": {
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip_code
                }
            }
        }

        users_collection.insert_one(user_doc)

        if request.is_json:
            return jsonify({"message": "Signup successful! Please login."}), 201
        else:
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login.login'))

    return render_template('signup.html')
