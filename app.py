from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
import sqlite3
import os
import random

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ================= EMAIL CONFIG =================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'sgadibavitec24@ced.alliance.edu.in'
app.config['MAIL_PASSWORD'] = 'your_16_digit_app_password_here' # 🔴 IMPORTANT
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

# ================= OTP STORAGE =================
otp_storage = {}

# ================= DATABASE =================
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            date TEXT,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            exercise TEXT,
            sets TEXT,
            reps TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= FRONTEND =================
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# ================= REGISTER =================
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (name, email, phone, role, password)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['name'],
            data['email'],
            data['phone'],
            data['role'],
            data['password']
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully"})

    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists"})
    except Exception as e:
        return jsonify({"message": str(e)})

# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role FROM users WHERE email=? AND password=?
    """, (data['email'], data['password']))

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login successful", "role": user[0]})
    else:
        return jsonify({"message": "Invalid credentials"})

# ================= SEND OTP =================
@app.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        email = data['email']

        otp = str(random.randint(1000, 9999))
        otp_storage[email] = otp

        msg = Message(
            "Gym AI OTP",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f"Your OTP is {otp}"

        mail.send(msg)

        return jsonify({"message": "OTP sent"})

    except Exception as e:
        return jsonify({"message": str(e)})

# ================= VERIFY OTP =================
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()

    email = data['email']
    otp = data['otp']

    if otp_storage.get(email) == otp:
        return jsonify({"message": "OTP verified"})
    else:
        return jsonify({"message": "Invalid OTP"})

# ================= RESET PASSWORD =================
@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET password=? WHERE email=?
    """, (data['new_password'], data['email']))

    conn.commit()
    conn.close()

    return jsonify({"message": "Password updated"})

# ================= ATTENDANCE =================
@app.route('/add_attendance', methods=['POST'])
def add_attendance():
    data = request.get_json()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance (email, date, status)
        VALUES (?, ?, ?)
    """, (data['email'], data['date'], data['status']))

    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance added"})

@app.route('/get_attendance/<email>', methods=['GET'])
def get_attendance(email):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, status FROM attendance WHERE email=?
    """, (email,))

    data = cursor.fetchall()
    conn.close()

    return jsonify([{"date": d[0], "status": d[1]} for d in data])

# ================= WORKOUT =================
@app.route('/add_workout', methods=['POST'])
def add_workout():
    data = request.get_json()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO workouts (email, exercise, sets, reps)
        VALUES (?, ?, ?, ?)
    """, (data['email'], data['exercise'], data['sets'], data['reps']))

    conn.commit()
    conn.close()

    return jsonify({"message": "Workout added"})

@app.route('/get_workout/<email>', methods=['GET'])
def get_workout(email):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT exercise FROM workouts WHERE email=?
    """, (email,))

    data = cursor.fetchall()
    conn.close()

    return jsonify([{"exercise": d[0]} for d in data])

# ================= AI =================
@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    data = request.get_json()
    goal = data['goal']

    if goal == "Weight Loss":
        return jsonify({
            "diet": "Low calorie diet",
            "workout": "Cardio exercises"
        })
    elif goal == "Muscle Gain":
        return jsonify({
            "diet": "High protein diet",
            "workout": "Strength training"
        })
    else:
        return jsonify({
            "diet": "Balanced diet",
            "workout": "General fitness"
        })

# ================= RUN =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)