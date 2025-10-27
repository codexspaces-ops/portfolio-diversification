from flask import Flask, render_template, redirect, url_for, session, request
from app.auth.login import login_bp
from app.auth.signup import signup_bp
from app.config import users_collection
import secrets
import os
import pandas as pd

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = secrets.token_hex(10)

app.register_blueprint(login_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})
app.register_blueprint(signup_bp, url_prefix="/auth", url_defaults={'users_collection': users_collection})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login.login'))
    return render_template('dashboard.html', full_name=session.get('full_name'))


@app.route('/importdata', methods=['GET', 'POST'])
def importdata():
    if 'user' not in session:
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        print("✅ Form submitted")
        file = request.files.get('file')
        if not file:
            return render_template('importdata.html', error="No file uploaded.", full_name=session.get('full_name'))
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"📁 File saved at: {filepath}")
        ext = os.path.splitext(filename)[1].lower()
        df = None
        try:
            # --- Handle multiple file formats ---
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif ext == '.csv':
                df = pd.read_csv(filepath)
            elif ext == '.json':
                df = pd.read_json(filepath)
            elif ext in ['.txt', '.tsv']:
                try:
                    df = pd.read_csv(filepath, sep='\t')
                except Exception:
                    df = pd.read_csv(filepath, sep=',')
            else:
                return render_template(
                    'importdata.html',
                    error=f"Unsupported file type: {ext}. Please upload Excel, CSV, JSON, or TXT.",
                    full_name=session.get('full_name')
                )

            print("✅ Columns detected:", df.columns.tolist())
            possible_sector_cols = [col for col in df.columns if 'sector' in col.lower()]
            possible_value_cols = [col for col in df.columns if 'value' in col.lower() or 'amount' in col.lower()]
            if possible_sector_cols and possible_value_cols:
                sector_col = possible_sector_cols[0]
                value_col = possible_value_cols[0]
                summary = df.groupby(sector_col)[value_col].sum().reset_index()
                total = summary[value_col].sum()
                summary['Percentage'] = (summary[value_col] / total * 100).round(2)
                summary = summary.sort_values(by='Percentage', ascending=False)
                print("✅ Summary prepared")
                return render_template(
                    'portfolio_summary.html',
                    tables=summary.to_dict(orient='records'),
                    full_name=session.get('full_name')
                )
            else:
                return render_template(
                    'importdata.html',
                    error="Required columns not found. Please ensure your file has 'Sector' and 'Value' or 'Amount' columns.",
                    full_name=session.get('full_name')
                )
        except Exception as e:
            print("❌ Error reading file:", e)
            return render_template(
                'importdata.html',
                error=f"Error reading file: {e}",
                full_name=session.get('full_name')
            )
    return render_template('importdata.html', full_name=session.get('full_name'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login.login'))
    return render_template('profile.html', full_name=session.get('full_name'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_page'))

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True, port=3000)