"""
PROG8850 Assignment 3 - Flask Web Application
A user registration web application with MySQL database integration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'loginappuser'),
    'password': os.getenv('MYSQL_PASSWORD', 'LoginAppDbPwd@2025'),
    'database': os.getenv('MYSQL_DB', 'loginapp'),
    'port': int(os.getenv('MYSQL_PORT', '3306'))
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """Initialize the database and create tables if they don't exist"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Create users table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_created_at (created_at)
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            
            # Insert sample data if table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            if count == 0:
                sample_users = [
                    ('testuser1', 'password123'),
                    ('testuser2', 'password456'),
                    ('admin', 'admin123')
                ]
                
                insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.executemany(insert_query, sample_users)
                connection.commit()
                logger.info("Sample users inserted successfully")
            
            cursor.close()
            connection.close()
            logger.info("Database initialized successfully")
            
    except Error as e:
        logger.error(f"Error initializing database: {e}")

@app.route('/')
def index():
    """Main page with registration form"""
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle registration form submission"""
    try:
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('index'))
        
        # Connect to database
        connection = get_db_connection()
        if not connection:
            flash('Database connection error', 'error')
            return redirect(url_for('index'))
        
        cursor = connection.cursor()
        
        # Insert user data into database
        insert_query = "INSERT INTO users (username, password, created_at) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, password, datetime.now()))
        connection.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        flash(f'User registered successfully! User ID: {user_id}', 'success')
        logger.info(f"User '{username}' registered successfully with ID: {user_id}")
        
        return redirect(url_for('success', user_id=user_id))
        
    except mysql.connector.IntegrityError as e:
        if "Duplicate entry" in str(e):
            flash('Username already exists. Please choose a different username.', 'error')
        else:
            flash('Database error occurred', 'error')
        logger.error(f"Database integrity error: {e}")
        return redirect(url_for('index'))
        
    except Error as e:
        flash('An error occurred while processing your request', 'error')
        logger.error(f"Database error: {e}")
        return redirect(url_for('index'))

@app.route('/success/<int:user_id>')
def success(user_id):
    """Success page after registration"""
    return render_template('registration_success.html', user_id=user_id)

@app.route('/api/users', methods=['GET'])
def get_users():
    """API endpoint to get all users (for testing purposes)"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection error'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Convert datetime objects to strings for JSON serialization
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
        
        return jsonify({'users': users})
        
    except Error as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
