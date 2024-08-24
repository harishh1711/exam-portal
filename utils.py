import mysql.connector
import re

def get_db_connection():
    connection = mysql.connector.connect(
        host="10.160.255.169",
        user="flask_user",
        password="password123",
        database="exam_portal"
    )
    return connection

def sanitize_table_name(exam_name):
    # Replace spaces and special characters with underscores
    return re.sub(r'\W+', '_', exam_name.lower())

def create_exam_table(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
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
    conn.commit()

    cursor.close()
    conn.close()
