from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

# Load or create the JSON database
try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
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

if __name__ == '__main__':
    app.run(debug=True)