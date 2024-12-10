from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from cryptography.fernet import Fernet
import mysql.connector

# app = Flask(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'Rajdeep_Bose_Jindabad12'

# Serve static files explicitly
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

encryption_key = b'f-d7jAw7RPY5HJvxIet0E3O6jDDbPGb69ca9nVrUVQM='
cipher = Fernet(encryption_key)

# MySQL Database Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ankit2602@",
    database="college_users"
)
cursor = db.cursor(dictionary=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        if not data['first_name'] or not data['last_name'] or not data['username'] or not data['email'] or not data['password']:
            return jsonify({"status": "error", "message": "Mandatory fields are required."})
        
        if data['password'] != data['confirm_password']:
            return jsonify({"status": "error", "message": "Password and Confirm Password must be the same."})
        
        encrypted_password = cipher.encrypt(data['password'].encode('utf-8'))
        cursor.execute("""
            INSERT INTO users (first_name, last_name, username, email, password, phone_number) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['first_name'], data['last_name'], data['username'], data['email'], encrypted_password, data['phone_number']))
        db.commit()
        return jsonify({"status": "success", "message": "User Registered Successfully"})
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET'])
def login():
    if request.method == 'POST':
        data = request.form
        if not data['username_email'] or not data['password']:
            return jsonify({"status": "error", "message": "Username/Email and Password are required."})
        
        cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (data['username_email'], data['username_email']))
        user = cursor.fetchone()
        if user and cipher.decrypt(user['password'].encode('utf-8')).decode('utf-8') == data['password']:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            return jsonify({"status": "success", "message": "Login Successful"})
        return jsonify({"status": "error", "message": "Invalid Credentials"})
    return render_template("login.html")

@app.route('/home', methods=['GET'])
def home():
    if 'username' in session:
        return render_template("home.html", username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        data = request.form
        if not data['email']:
            return jsonify({"status": "error", "message": "Email is required."})
        
        cursor.execute("SELECT * FROM users WHERE email=%s", (data['email'],))
        user = cursor.fetchone()
        if user:
            decrypted_password = cipher.decrypt(user['password'].encode('utf-8')).decode('utf-8')
            return jsonify({"status": "success", "message": f"Your password is: {decrypted_password}"})
        return jsonify({"status": "error", "message": "Email not found"})
    return render_template("forget_password.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login', logout='true'))

if __name__ == '__main__':
    app.run(debug=True)
