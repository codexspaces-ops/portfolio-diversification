from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup(users_collection):
    if request.method == 'POST':
        # Detect if it's a JSON request (API) or form submission
        if request.is_json:
            data = request.get_json()
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            age = data.get('age')
            email = data.get('email')
            password = data.get('password')
            city = data.get('city')
        else:
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            age = request.form.get('age')
            email = request.form.get('email')
            password = request.form.get('password')
            city = request.form.get('city')

        # Validation
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            msg = {"message": "User already exists!"}
            if request.is_json:
                return jsonify(msg), 400
            flash(msg["message"], "warning")
            return render_template('signup.html')

        # Store hashed password
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            "firstname": firstname,
            "lastname": lastname,
            "age": age,
            "email": email,
            "password": hashed_password,
            "city": city
        })

        if request.is_json:
            return jsonify({"message": "Signup successful! Please login."}), 201
        else:
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login.login'))

    return render_template('signup.html')
