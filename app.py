from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

# Load or create the JSON database
try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

with open('users.json', 'w') as f:
    json.dump(users, f)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username # Store the username in the session
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid username or password", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = {'password': password, 'chathistory': []}
            with open('users.json', 'w') as f:
                json.dump(users, f)
            return redirect(url_for('login'))
        else:
            return "Username already exists", 400
    return render_template('register.html')

@app.route('/profile/<username>')
def profile(username):
    if username in users:
        return render_template('profile.html', username=username, chathistory=users[username]['chathistory'])
    else:
        return "User not found", 404

# New route for AI chat
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
headers = {"Authorization": "Bearer kirebada"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    username = session.get('username', 'default_user')
    if request.method == 'POST':
        message = request.form['message']
        # Process the message using the Hugging Face API
        output = query({"inputs": message})
        # Adjust this line based on the actual structure of the API response
        # For example, if the response is a list and the AI's response is the first element:
        ai_response = output[0] if output else 'AI response not available'

        # Assuming each user has a chat history
        # Use the username from the session
        if username not in users:
            users[username] = {'chathistory': []}
        users[username]['chathistory'].append({'type': 'user', 'text': message})
        users[username]['chathistory'].append({'type': 'ai', 'text': ai_response})
        with open('users.json', 'w') as f:
            json.dump(users, f)
        return redirect(url_for('chat'))
    if username in users:
        messages = users[username]['chathistory']
    return render_template('chat.html', messages=messages)

@app.route('/admin', methods=['GET'])
def print_json_db():
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
        return jsonify(users)
    except FileNotFoundError:
        return "JSON database file not found", 404


if __name__ == '__main__':
    app.run(debug=True)
