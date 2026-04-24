from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Use /tmp for database on Render (writable location)
DB_PATH = '/tmp/todos.db'

# ========== DATABASE SETUP ==========
def init_database():
    """Creates the database and table if they don't exist"""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    connection.commit()
    connection.close()
    print("✅ Database ready!")

# ========== API ENDPOINTS ==========

@app.route('/')
def home():
    return jsonify({'message': 'Todo API is running!', 'status': 'ok'})

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    """Get all tasks from database"""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    rows = cursor.fetchall()
    
    tasks = []
    for row in rows:
        tasks.append({
            'id': row[0],
            'title': row[1],
            'completed': bool(row[2]),
            'created_at': row[3]
        })
    
    connection.close()
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    data = request.json
    title = data.get('title')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute('INSERT INTO tasks (title) VALUES (?)', (title,))
    connection.commit()
    
    new_id = cursor.lastrowid
    connection.close()
    
    return jsonify({'message': 'Task added!', 'id': new_id}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Mark task as completed or not"""
    data = request.json
    completed = data.get('completed')
    
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
    connection.commit()
    connection.close()
    
    return jsonify({'message': 'Task updated!'})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Remove a task"""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    connection.commit()
    connection.close()
    
    return jsonify({'message': 'Task deleted!'})

@app.route('/tasks/delete-all', methods=['DELETE'])
def delete_all_tasks():
    """Clear all tasks"""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM tasks')
    connection.commit()
    connection.close()
    
    return jsonify({'message': 'All tasks deleted!'})

# ========== START THE SERVER ==========
if __name__ == '__main__':
    init_database()
    print("\n" + "="*50)
    print("🚀 Server is running!")
    print("📍 URL: http://localhost:10000")
    print("📋 Test with: http://localhost:10000/tasks")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=10000, debug=False)
