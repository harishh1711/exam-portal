from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection, sanitize_table_name, create_exam_table
import base64


app = Flask(__name__)
app.secret_key = '#Ironman2003'

def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

app.jinja_env.filters['b64encode'] = b64encode_filter


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):  # Check hashed password
            session['user_id'] = user[0]
            session['role'] = user[4]  # Assuming role is in the 4th column
            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password')

        cursor.close()
        conn.close()
        
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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (name, email, hashed_password, role))
        conn.commit()

        cursor.close()
        conn.close()
        
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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO exams (exam_name, registration_start, registration_end, exam_date)
            VALUES (%s, %s, %s, %s)
        """, (exam_name, registration_start, registration_end, exam_date))
        conn.commit()

        cursor.close()
        conn.close()

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

@app.route('/register_exam/<int:exam_id>', methods=['GET', 'POST'])
def register_exam(exam_id):
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        conn.commit()

        cursor.close()
        conn.close()

        flash('Registration successful!')
        return redirect(url_for('student_dashboard'))

    return render_template('enter_details.html', exam_id=exam_id)

@app.route('/view_exams')
def view_exams():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams")
    exams = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('view_exams.html', exams=exams)

@app.route('/manage_exams', methods=['GET'])
def manage_exams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams")
    exams = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('manage_exams.html', exams=exams)

@app.route('/update_exam/<int:exam_id>', methods=['GET', 'POST'])
def update_exam(exam_id):
    if request.method == 'POST':
        # Debugging print statement to confirm it's entering the POST block
        print("Handling POST request")
        
        # Check if the form data contains 'registration_start'
        if 'registration_start' not in request.form:
            flash('Error: registration_start field is missing!')
            return redirect(url_for('manage_exams'))

        # Extracting data from the form
        registration_start = request.form['registration_start']
        registration_end = request.form['registration_end']
        exam_date = request.form['exam_date']

        # Updating the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE exams SET registration_start=%s, registration_end=%s, exam_date=%s WHERE id=%s",
                       (registration_start, registration_end, exam_date, exam_id))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Exam updated successfully!')
        return redirect(url_for('manage_exams'))

    # Handling the GET request
    print("Handling GET request")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams WHERE id=%s", (exam_id,))
    exam = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('update_exam.html', exam=exam)

@app.route('/delete_exam/<int:exam_id>', methods=['POST'])
def delete_exam(exam_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the table name before deleting the exam record
    cursor.execute("SELECT exam_name FROM exams WHERE id=%s", (exam_id,))
    table_name = cursor.fetchone()[0]
    table_name = sanitize_table_name(table_name)

    # Delete the exam record
    cursor.execute("DELETE FROM exams WHERE id=%s", (exam_id,))
    conn.commit()

    # Drop the corresponding table
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()

    cursor.close()
    conn.close()

    flash('Exam deleted successfully!')
    return redirect(url_for('manage_exams'))

@app.route('/view_registered_students/<int:exam_id>')
def view_registered_students(exam_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the table name for the exam
    cursor.execute("SELECT exam_name FROM exams WHERE id=%s", (exam_id,))
    table_name = cursor.fetchone()[0]
    table_name = sanitize_table_name(table_name)

    cursor.execute(f"SELECT * FROM {table_name}")
    students = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('registered_students.html', students=students)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
