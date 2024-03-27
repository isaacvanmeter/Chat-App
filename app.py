from flask import Flask, render_template, request, redirect, session
from db.db_connection import get_db_connection
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/chat')
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return redirect('/signup')

        cursor.execute("INSERT INTO users (username, full_name) VALUES (%s, %s)", (username, full_name))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/')
    else:
        return render_template('signup.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect('/')

    messages = []
    users = []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT username, full_name FROM users")
    users = cursor.fetchall()

    if request.method == 'POST' and 'load_messages' in request.form:
        cursor.execute("""
            SELECT m.*, u1.full_name as sender_full_name, u2.full_name as receiver_full_name,
            CASE
                WHEN DATE(m.time_sent) = DATE(NOW()) THEN TIME_FORMAT(m.time_sent, '%l:%i %p')
                WHEN YEAR(m.time_sent) = YEAR(NOW()) THEN DATE_FORMAT(m.time_sent, '%M %d')
                ELSE DATE_FORMAT(m.time_sent, '%M %d, %Y')
            END AS formatted_time
            FROM messages m
            JOIN users u1 ON m.sender_username = u1.username
            JOIN users u2 ON m.receiver_username = u2.username
            WHERE m.receiver_username = %s OR m.sender_username = %s
            ORDER BY m.time_sent
        """, (session['username'], session['username']))
        messages = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('chat.html', username=session['username'], messages=messages, users=users)


@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return redirect('/')

    receiver_username = request.form['receiver_username']
    message_text = request.form['message_text']
    sender_username = session['username']

    if message_text and receiver_username:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (sender_username, receiver_username, message_text, time_sent)
            VALUES (%s, %s, %s, NOW())
        """, (sender_username, receiver_username, message_text))
        conn.commit()
        cursor.close()
        conn.close()

    return redirect('/chat')


if __name__ == '__main__':
    app.run(debug=True)
