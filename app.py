from flask import Flask, request, jsonify, render_template, redirect, session, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
@app.route('/')
def home():
    if 'username' in session:
        return render_template('welcome.html', user=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'danger')
        conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# Serve the homepage
@app.route('/')
def welcome():
    return render_template("welcome.html")  # Set this as the home page ✅

@app.route('/quiz')
def quiz(): 
    return render_template("index.html")  # Your questionnaire page
# Handle the POST request for prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get the data from the POST request
    data = request.get_json()
    answers = data.get('answers')

    # Validate the answers
    if not answers or len(answers) != 10:
        return jsonify({"error": "Please provide answers for all 10 questions"}), 400

    # Calculate the score based on the answers
    score = sum(answers)

    # Determine the stage based on the score
    if score < 10:
        stage = "Mild"
        suggestion = "Light self-care, relaxing music, rest and support."
    elif score < 20:
        stage = "Moderate"
        suggestion = "Talk to a therapist, watch motivational videos, connect with others."
    else:
        stage = "Severe"
        suggestion = "Consult a psychiatrist, involve family, follow guided recovery steps."

    # Return the result as JSON
    return jsonify({"score": score, "stage": stage, "suggestion": suggestion})
if __name__ == '__main__':
    app.run(debug=True)
