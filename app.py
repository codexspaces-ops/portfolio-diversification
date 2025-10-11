from flask import Flask,render_template,request,redirect,url_for,flash,jsonify  
from app.auth.login import login_bp
from app.auth.signup import signup_bp
from app.config import users_collection
import secrets
# Create a Flask instance
app = Flask(__name__, template_folder="app/templates")
app.secret_key = secrets.token_hex(10)

app.register_blueprint(login_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})
app.register_blueprint(signup_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})

# Define a route for the home page
@app.route('/')
def home_page():
    return render_template('index.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)