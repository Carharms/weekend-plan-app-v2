# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import mysql.connector
from mysql.connector import Error
import logging # https://docs.python.org/3/library/logging.html

app = Flask(__name__)
app.secret_key = "weekend-task-manager"

# MySQL DB Config
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'weekend_tasks'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    # designated port for MySQL
    'port': int(os.environ.get('DB_PORT', '3306'))
}

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logging.error(f"DB connection error: {e}")
        return None

def init_db():
    """Initialize database with weekend_tasks table"""
    connection = get_db_connection()
    if not connection:
        logging.error("Could not establish database connection")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekend_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event VARCHAR(255) NOT NULL,
                day ENUM('Friday', 'Saturday', 'Sunday') NOT NULL,
                start_time TIME NOT NULL,
                description VARCHAR(500),
                additional_links TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        logging.info("Database initialized successfully")
    except Error as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# -- Main Dashboard --
@app.route("/")
def dashboard():
    """Display all weekend tasks"""
    connection = get_db_connection()
    if not connection:
        flash("Database connection error")
        return render_template("dashboard.html", tasks=[])
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM weekend_tasks ORDER BY FIELD(day, 'Friday', 'Saturday', 'Sunday'), start_time")
        tasks = cursor.fetchall()
        return render_template("dashboard.html", tasks=tasks)
    except Error as e:
        logging.error(f"Error fetching tasks: {e}")
        flash("Error loading tasks")
        return render_template("dashboard.html", tasks=[])
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# -- Add Task --
@app.route("/add", methods=["GET", "POST"])
def add_task():
    """Add a new weekend task"""
    if request.method == "POST":
        event = request.form["event"]
        day = request.form["day"]
        start_time = request.form["start_time"]
        description = request.form.get("description", "")
        additional_links = request.form.get("additional_links", "")
        
        connection = get_db_connection()
        if not connection:
            flash("Database connection error")
            return redirect(url_for("dashboard"))
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO weekend_tasks (event, day, start_time, description, additional_links)
                VALUES (%s, %s, %s, %s, %s)
            """, (event, day, start_time, description, additional_links))
            connection.commit()
            flash("Task added successfully!")
            return redirect(url_for("dashboard"))
        except Error as e:
            logging.error(f"Error adding task: {e}")
            flash("Error adding task")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return render_template("add_task.html")

# -- API Endpoints --
@app.route("/api/tasks", methods=["GET"])
def api_get_tasks():
    """API endpoint to get all weekend tasks"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection error"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM weekend_tasks ORDER BY FIELD(day, 'Friday', 'Saturday', 'Sunday'), start_time")
        tasks = cursor.fetchall()
        
        # convert task start_time to string
        for task in tasks:
            if task['start_time']:
                task['start_time'] = str(task['start_time'])
            if task['created_at']:
                task['created_at'] = task['created_at'].isoformat()
        
        return jsonify({"tasks": tasks})
    except Error as e:
        logging.error(f"API error fetching tasks: {e}")
        return jsonify({"error": "Error fetching tasks"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    """API endpoint to create a new weekend task"""
    data = request.get_json()
    
    # Basic validation
    if not data or not data.get('event') or not data.get('day') or not data.get('start_time'):
        return jsonify({"error": "Missing required fields"}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection error"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO weekend_tasks (event, day, start_time, description, additional_links)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['event'],
            data['day'],
            data['start_time'],
            data.get('description', ''),
            data.get('additional_links', '')
        ))
        connection.commit()
        
        # Get the created task
        cursor.execute("SELECT * FROM weekend_tasks WHERE id = LAST_INSERT_ID()")
        task = cursor.fetchone()
        
        if task['start_time']:
            task['start_time'] = str(task['start_time'])
        if task['created_at']:
            task['created_at'] = task['created_at'].isoformat()
        
        return jsonify({"task": task}), 201
    except Error as e:
        logging.error(f"API error creating task: {e}")
        return jsonify({"error": "Error creating task"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# -- Health Check --
@app.route("/health")
def health_check():
    """Health check endpoint"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"status": "unhealthy"}), 503
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        return jsonify({"status": "healthy"})
    except Error as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy"}), 503
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)