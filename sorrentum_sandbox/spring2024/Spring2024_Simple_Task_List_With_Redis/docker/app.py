from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import logging
from flask import Flask, request, jsonify, g, session
from redis import Redis
import json
import secrets
import hashlib
import uuid


app = Flask(__name__)

# Connect to Redis
r = Redis(host='redis', port=6379)

# Endpoint for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Check if username or email is already in use
    if r.exists(f'user:username:{username}'):
        return jsonify({'error': 'Username already exists'}), 400
    if r.exists(f'user:email:{email}'):
        return jsonify({'error': 'Email already exists'}), 400
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    # Generate user ID
    user_id = secrets.token_hex(16)
    
    # Create user profile
    profile = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'name': '',
        'bio': ''
    }
    
    r.hmset(f'user:{user_id}', profile)
    r.set(f'user:username:{username}', user_id)
    r.set(f'user:email:{email}', user_id)
    
    return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201

# Endpoint for user authentication
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Find the user by username
    user_id = r.get(f'user:username:{username}')
    if user_id:
        user_data = r.hgetall(f'user:{user_id.decode()}')
        if check_password_hash(user_data[b'password'].decode(), password):
            return jsonify({'message': 'Login successful', 'user_id': user_id.decode()}), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401


# Endpoint to create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    user_id = data.get('user_id')
    task_name = data.get('task_name')
    task_description = data.get('task_description')
    deadline = data.get('deadline')
    category = data.get('category')

    # Check if the user exists
    if not r.exists(f'user:{user_id}'):
        return jsonify({'error': 'User not found'}), 404

    # Generate a unique task ID
    task_id = secrets.token_hex(16)

    # Create task details
    task_details = {
        'task_name': task_name,
        'task_description': task_description,
        'assigned_to': user_id,
        'status': 'pending',
        'deadline': deadline,
        'category': category
    }

    # Store task details in Redis
    r.hmset(f'task:{task_id}', task_details)

    return jsonify({'message': 'Task assigned successfully', 'task_id': task_id, 'task_details': task_details}), 201

# Endpoint to get all tasks
@app.route('/tasks/<user_id>', methods=['GET'])
def get_tasks(user_id):
    # Retrieve all tasks assigned to the specified user_id from Redis
    task_ids = r.keys(f'task:*')
    user_tasks = []

    for task_id in task_ids:
        task_data = r.hgetall(task_id)
        if task_data[b'assigned_to'].decode() == user_id:
            user_tasks.append({
                'task_id': task_id.decode().split(':')[1],
                'task_name': task_data[b'task_name'].decode(),
                'task_description': task_data[b'task_description'].decode(),
                'status': task_data[b'status'].decode(),
                'deadline': task_data[b'deadline'].decode(),
                'category': task_data[b'category'].decode()
            })
    return jsonify({'user_tasks': user_tasks}), 201

@app.route('/tasks/category/<category>', methods=['GET'])
def get_tasks_by_category(category):
    # Retrieve all tasks from Redis
    task_ids = r.keys(f'task:*')
    tasks_in_category = []

    # Iterate through each task and filter by category
    for task_id in task_ids:
        task_data = r.hgetall(task_id)
        if task_data[b'category'].decode() == category:
            tasks_in_category.append({
                'task_id': task_id.decode().split(':')[1],
                'task_name': task_data[b'task_name'].decode(),
                'task_description': task_data[b'task_description'].decode(),
                'status': task_data[b'status'].decode(),
                'deadline': task_data[b'deadline'].decode()
            })

    return jsonify({'tasks_in_category': tasks_in_category}), 200

# Endpoint to get a single task by ID
@app.route('/tasks/<user_id>/<task_name>', methods=['GET'])
def get_user_task_by_name(user_id, task_name):
    # Find the task ID based on the user ID and task name
    task_ids = r.keys(f'task:*')
    for task_id in task_ids:
        task_data = r.hgetall(task_id)
        if (task_data[b'assigned_to'].decode() == user_id) and (task_data[b'task_name'].decode() == task_name):
            return jsonify({
                'task_id': task_id.decode().split(':')[1],
                'task_name': task_data[b'task_name'].decode(),
                'task_description': task_data[b'task_description'].decode(),
                'status': task_data[b'status'].decode(),
                'deadline': task_data[b'deadline'].decode(),
                'category': task_data[b'category'].decode()
            })

    return jsonify({'error': 'Task not found'}), 404

# Endpoint to update a task by ID
@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    task_name = data.get('task_name')
    task_description = data.get('task_description')
    status = data.get('status')

    # Check if the task exists
    if not r.exists(f'task:{task_id}'):
        return jsonify({'error': 'Task not found'}), 404

    # Update task details
    task_details = {
        'task_name': task_name,
        'task_description': task_description,
        'status': status
    }

    r.hmset(f'task:{task_id}', task_details)

    return jsonify({'message': 'Task updated successfully'}), 200

# Endpoint to delete a task by ID
@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    # Check if the task exists
    if not r.exists(f'task:{task_id}'):
        return jsonify({'error': 'Task not found'}), 404

    # Delete the task
    r.delete(f'task:{task_id}')

    return jsonify({'message': 'Task deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
