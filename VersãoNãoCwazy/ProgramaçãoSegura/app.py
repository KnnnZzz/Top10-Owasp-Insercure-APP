#  _  __                 ____________          
# | |/ /                |__  /__  / /         
# | ' /_ __  _ __  _ __    / /   / / ____      
# |  <| '_ \| '_ \| '_ \  / /   / / |_  /      
# | . \ | | | | | | | | |/ /___/ /___/ /       
# |_|\_\_| |_|_| |_|_| |_|____/____/___|     


from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

db_path = 'database.db'

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE,
                      password TEXT,
                      is_admin INTEGER DEFAULT 0)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      sender TEXT,
                      content TEXT,
                      channel_id INTEGER,
                      FOREIGN KEY(channel_id) REFERENCES channels(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS wallets (
                      user_id INTEGER PRIMARY KEY,
                      balance INTEGER DEFAULT 0,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS shop_items (
                      id INTEGER PRIMARY KEY,
                      name TEXT,
                      price INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS purchases (
                      id INTEGER PRIMARY KEY,
                      user_id INTEGER,
                      item_id INTEGER,
                      FOREIGN KEY(user_id) REFERENCES users(id),
                      FOREIGN KEY(item_id) REFERENCES shop_items(id))''')

    cursor.execute("""INSERT OR IGNORE INTO shop_items (name, price) VALUES 
        ('Premium Badge', 100),
        ('Custom Emoji', 50),
        ('Profile Color', 75),
        ('Animated Avatar', 200),
        ('Exclusive Channel', 300)
    """)
    
    cursor.execute("INSERT OR IGNORE INTO channels (name) VALUES ('geral')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES ('admin', 'admin123', 1)")

    conn.commit()
    conn.close()

def init_wallets():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO wallets (user_id, balance)
        SELECT id, 100 FROM users
        WHERE id NOT IN (SELECT user_id FROM wallets)
    ''')
    conn.commit()
    conn.close()

init_db()
init_wallets()

@app.context_processor
def inject_wallet():
    if 'username' in session:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance FROM wallets WHERE user_id = (SELECT id FROM users WHERE username = ?)",
            (session['username'],)
        )
        result = cursor.fetchone()
        conn.close()
        return {'wallet_balance': result[0] if result else 0}
    return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         (username, password))
            cursor.execute("INSERT INTO wallets (user_id, balance) VALUES ((SELECT id FROM users WHERE username = ?), 100)",
                         (username,))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Username already exists")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['is_admin'] = user[3]  # assuming is_admin is at index 3
            return redirect('/channels')
        else:
            return render_template('login.html', error="Credenciais inválidas")
    return render_template('login.html')

@app.route('/channels')
def channels():
    if 'username' not in session:
        return redirect('/login')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM channels")
    channel_list = cursor.fetchall()
    conn.close()
    return render_template('channels.html', channels=channel_list)

@app.route('/chat/<int:channel_id>', methods=['GET', 'POST'])
def chat(channel_id):
    if 'username' not in session:
        return redirect('/login')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if request.method == 'POST':
        content = request.form['message']
        cursor.execute("INSERT INTO messages (sender, content, channel_id) VALUES (?, ?, ?)",
                      (session['username'], content, channel_id))
        conn.commit()
    cursor.execute("SELECT name FROM channels WHERE id = ?", (channel_id,))
    channel_name = cursor.fetchone()
    cursor.execute("SELECT sender, content FROM messages WHERE channel_id = ?", (channel_id,))
    messages = cursor.fetchall()
    cursor.execute("SELECT id, name FROM channels")
    all_channels = cursor.fetchall()
    conn.close()
    return render_template('chat.html', messages=messages, channel_name=channel_name[0], channel_id=channel_id, channels=all_channels)

@app.route('/create_channel', methods=['POST'])
def create_channel():
    if 'username' not in session:
        return redirect('/login')
    name = request.form['channel_name']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO channels (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect('/channels')

@app.route('/wallet')
def wallet():
    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT balance FROM wallets WHERE user_id = (SELECT id FROM users WHERE username = ?)",
            (session['username'],)
        )
        wallet_result = cursor.fetchone()
        balance = wallet_result[0] if wallet_result else 0

        cursor.execute("SELECT * FROM shop_items")
        items = cursor.fetchall()

        cursor.execute("SELECT id, name FROM channels")
        channels = cursor.fetchall()

        cursor.execute('''
            SELECT si.name, si.price, p.id 
            FROM purchases p 
            JOIN shop_items si ON si.id = p.item_id
            WHERE p.user_id = (SELECT id FROM users WHERE username = ?)
        ''', (session['username'],))
        history = cursor.fetchall()

        return render_template('wallet.html', 
                            balance=balance, 
                            items=items,
                            channels=channels,
                            history=history)
    except Exception as e:
        print(f"Error in wallet route: {e}")
        return "An error occurred", 500
    finally:
        conn.close()

@app.route('/add_funds', methods=['POST'])
def add_funds():
    if 'username' not in session:
        return redirect('/login')

    amount = int(request.form['amount'])
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE wallets SET balance = balance + ? 
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
        """, (amount, session['username']))
        conn.commit()
        return redirect('/wallet')
    except Exception as e:
        conn.rollback()
        return redirect('/wallet?error=add_funds_failed')
    finally:
        conn.close()

@app.route('/buy/<int:item_id>')
def buy(item_id):
    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION")

        cursor.execute("SELECT price FROM shop_items WHERE id = ?", (item_id,))
        price = cursor.fetchone()[0]

        cursor.execute(
            "SELECT balance FROM wallets WHERE user_id = (SELECT id FROM users WHERE username = ?)",
            (session['username'],)
        )
        balance = cursor.fetchone()[0]

        cursor.execute(
            "UPDATE wallets SET balance = balance - ? WHERE user_id = (SELECT id FROM users WHERE username = ?)",
            (price, session['username'])
        )
        cursor.execute(
            "INSERT INTO purchases (user_id, item_id) VALUES ((SELECT id FROM users WHERE username = ?), ?)",
            (session['username'], item_id)
        )
        conn.commit()
        return redirect('/wallet')

    except Exception as e:
        conn.rollback()
        print(f"Purchase error: {e}")
        return redirect('/wallet?error=purchase_failed')
    finally:
        conn.close()

@app.route('/admin_panel')
def admin_panel():
    if 'username' not in session or not session.get('is_admin'):
        return "Acesso negado", 403

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List of Users
    cursor.execute("SELECT username, is_admin FROM users")
    users = cursor.fetchall()

    # Buys History
    cursor.execute("""
        SELECT u.username, si.name, si.price
        FROM purchases p
        JOIN users u ON u.id = p.user_id
        JOIN shop_items si ON si.id = p.item_id
    """)
    history = cursor.fetchall()

    conn.close()
    return render_template('admin_panel.html', users=users, history=history)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect('/')

@socketio.on('send_message')
def handle_message(data):
    if 'username' not in session:
        return
    channel_id = data['channel_id']
    content = data['message']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, content, channel_id) VALUES (?, ?, ?)",
                  (session['username'], content, channel_id))
    conn.commit()
    emit('new_message', {'sender': session['username'], 'content': content}, room=f'channel_{channel_id}')
    conn.close()

@socketio.on('join_channel')
def handle_join(data):
    if 'username' in session:
        join_room(f'channel_{data["channel_id"]}')

app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SECURE=False
)

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
