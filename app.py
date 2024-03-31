from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import string
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

users = {}



# MongoDB setup
uri = "mongodb+srv://webAi:1234@cluster0.l8xvws7.mongodb.net/web-Ai?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Get the database
db = client.your_database_name

# Get the collection
users_collection = db.users

# Fetch all documents in the collection
all_users = users_collection.find()

# Iterate over the documents and print them
for user in all_users:
    print(user)

# Fetch only the 'username' and 'email' fields for each user
all_users = users_collection.find({}, {'username': 1, 'email': 1})

# Iterate over the documents and print the 'username' and 'email'
for user in all_users:
    print(user['username'], user['email'])

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = client.your_database_name.users.find_one({'username': username})
        
        if user and user['password'] == password:
            # Store user information in the session
            session['username'] = username
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid username or password", 401
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the home page
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email= request.form['email']
        password = request.form['password']

        if username not in users:
            client.your_database_name.users.insert_one({'username': username, 'name': name, 'email': email, 'password': password, 'chathistory': []})
            print('ilabu')

    return render_template('register.html')

def generate_token(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.json.get('email')
    
        if email in users:
            return redirect(url_for('change_password', email='email'))
  
        else:
            return jsonify({"success": False, "message": "Email not found."}), 404
    
    return render_template('forget_password.html')

@app.route('/change_password',)
def change_password():
    if request.method == 'POST':
        new_password = request.json.get('password')

@app.route('/profile/<username>')
def profile(username):
    # Check if the username in the session matches the requested username
    if 'username' in session and session['username'] == username:
        # Fetch the user's data from the MongoDB database
        user_data = client.your_database_name.users.find_one({'username': username})
        
        # Pass the user's data to the template
        return render_template('profile.html', user=user_data)
    else:
        return "User not found", 404

# New route for AI chat
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    username = session.get('username', 'default_user')
    messages = []
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

@app.route('/admin', methods=['GET', 'POST'])
def print_json_db():
    if request.method == 'POST':
        # Define the expected admin ID and password
        admin_id = 'admin'
        admin_email = 'tawkirarifin200@gmail.com' 
        admin_password = 'password'

        # Get the ID and password from the form data
        provided_id = request.form.get('id')
        provided_password = request.form.get('password')

        # Check if the provided ID and password match the expected values
        if provided_id == admin_id and provided_password == admin_password:
            return redirect(url_for('table'))
            # try:
            #     with open('users.json', 'r') as f:
            #         users = json.load(f)
            #     return jsonify(users)
            # except FileNotFoundError:
            #     return "JSON database file not found", 404
        else:
            return "Invalid ID or password", 401
    return render_template('admin.html')

@app.route('/table', methods=['GET', 'POST'])
def table():
    return render_template('table.html')

if __name__ == '__main__':
    app.run(debug=True)
