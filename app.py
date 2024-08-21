from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = '#Ironman2003'

# MySQL Database Connection
db = mysql.connector.connect(
    host="10.160.253.26",
    user="flask_user",
    password="password123",
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


def sanitize_table_name(exam_name):
    # Replace spaces and special characters with underscores
    return re.sub(r'\W+', '_', exam_name.lower())

def create_exam_table(table_name):
    create_table_query = f"""
    CREATE TABLE {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        name VARCHAR(255),
        dob DATE,
        gender VARCHAR(10),
        phone VARCHAR(15),
        email VARCHAR(255),
        address TEXT,
        aadhar_number VARCHAR(20),
        aadhar_image LONGBLOB,
        photo LONGBLOB,
        signature LONGBLOB,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id)
    )
    """
    cursor.execute(create_table_query)
    db.commit()
@app.route('/upload_exam', methods=['GET', 'POST'])
def upload_exam():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        registration_start = request.form['registration_start']
        registration_end = request.form['registration_end']
        exam_date = request.form['exam_date']

        table_name = sanitize_table_name(exam_name)


        cursor.execute("""
            INSERT INTO exams (exam_name, registration_start, registration_end, exam_date)
            VALUES (%s, %s, %s, %s)
        """, (exam_name, registration_start, registration_end, exam_date))
        db.commit()
        create_exam_table(table_name)

        flash('Exam details uploaded successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template('upload_exam.html')

@app.route('/enter_details', methods=['POST'])
def enter_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    exam_id = request.form['exam_id']
    return render_template('enter_details.html', exam_id=exam_id)

# @app.route('/submit_registration', methods=['POST'])
# def submit_registration():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     exam_id = request.form['exam_id']
#     student_id = session['user_id']
#     name = request.form['name']
#     dob = request.form['dob']
#     gender = request.form['gender']
#     phone = request.form['phone']
#     email = request.form['email']
#     address = request.form['address']
#     aadhar_number = request.form['aadhar_number']

#     # Handling file uploads
#     aadhar_image = request.files['aadhar_image'].read()
#     photo = request.files['photo'].read()
#     signature = request.files['signature'].read()

#     cursor.execute("""
#         INSERT INTO exam_registrations 
#         (exam_id, student_id, name, dob, gender, phone, email, address, aadhar_number, aadhar_image, photo, signature)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """, (exam_id, student_id, name, dob, gender, phone, email, address, aadhar_number, aadhar_image, photo, signature))
#     db.commit()

#     flash('Registration successful!')
#     return redirect(url_for('student_dashboard'))
@app.route('/register_exam/<int:exam_id>', methods=['GET', 'POST'])
def register_exam(exam_id):
    if request.method == 'POST':
        table_name_query = "SELECT table_name FROM exams WHERE id = %s"
        cursor.execute(table_name_query, (exam_id,))
        table_name = cursor.fetchone()[0]

        # Process form data
        student_id = session['user_id']
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        aadhar_number = request.form['aadhar_number']
        aadhar_image = request.files['aadhar_image'].read()
        photo = request.files['photo'].read()
        signature = request.files['signature'].read()

        insert_query = f"""
        INSERT INTO {table_name} (student_id, name, dob, gender, phone, email, address, aadhar_number, aadhar_image, photo, signature)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (student_id, name, dob, gender, phone, email, address, aadhar_number, aadhar_image, photo, signature))
        db.commit()

        flash('Registration successful!')
        return redirect(url_for('student_dashboard'))

    # Render registration form for GET requests
    return render_template('register_exam.html', exam_id=exam_id)


@app.route('/view_exams')
def view_exams():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM exams")
    exams = cursor.fetchall()
    return render_template('view_exams.html', exams=exams)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
