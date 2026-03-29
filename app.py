from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
import sqlite3
import os
import random

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# -------------------------------
# EMAIL CONFIG ⚠️ CHANGE THIS
# -------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

# -------------------------------
# OTP STORAGE
# -------------------------------
otp_storage = {}

# -------------------------------
# DATABASE INIT
# -------------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            role TEXT,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# SERVE FRONTEND
# -------------------------------
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# -------------------------------
# SEND OTP
# -------------------------------
@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data['email']

    otp = str(random.randint(1000, 9999))
    otp_storage[email] = otp

    msg = Message("Gym AI OTP Verification",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[email])

    msg.body = f"Your OTP is: {otp}"

    try:
        mail.send(msg)
        return jsonify({"message": "OTP sent"})
    except Exception as e:
        return jsonify({"error": str(e)})

# -------------------------------
# VERIFY OTP
# -------------------------------
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data['email']
    user_otp = data['otp']

    if otp_storage.get(email) == user_otp:
        return jsonify({"message": "OTP verified"})
    else:
        return jsonify({"message": "Invalid OTP"})
    # -------------------------------
# RESET PASSWORD 🔥
# -------------------------------
@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    new_password = data['new_password']

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET password=? WHERE email=?
    """, (new_password, email))

    conn.commit()
    conn.close()

    return jsonify({"message": "Password updated successfully"})

# -------------------------------
# RUN
# -------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)