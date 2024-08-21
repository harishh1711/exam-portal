from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = '#Ironman2003'

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="#Ironman2003",
    database="exam_portal"
)
cursor = db.cursor()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):  # Check hashed password
            session['user_id'] = user[0]
            session['role'] = user[4]  # Assuming role is in the 4th column
            print(user)
            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = 'student'  # Default role for registration; can be adjusted

        # Hash password with pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (name, email, hashed_password, role))
        db.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('studentDashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('adminDashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
