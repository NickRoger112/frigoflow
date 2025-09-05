from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysecret'

# Main page, can't visit without logging in
@app.route('/')
def index():
    return render_template("index.html")

# Register user, and redirect to login page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        
        if not username:
            return render_template('register.html', alert='Missing username')
        if not password:
            return render_template('register.html', alert='Missing password')
        if not password == confirmation:
            return render_template('register.html', alert='Passwords don\'t match')
        
        password_hash = generate_password_hash(password)
        
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users(username, password_hash) VALUES(?, ?)', (username, password_hash))
                conn.commit()
        except sqlite3.IntegrityError:
            return render_template('register.html', alert='Username already exists')
        except sqlite3.Error as e:
            return render_template('register.html', alert=f'Something went wrong: {e}')
        
        return redirect('/login')
    else:
        return render_template('register.html')
    
# Log the user in, and redirect to homepage
@app.route('/login', methods=['GET', 'POST'])
def login():

    session.clear()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username:
            return render_template('login.html', alert='Missing username')
        if not password:
            return render_template('login.html', alert='Missing password')
        
        rows = query('SELECT * FROM users WHERE username = ?', username)
        
        if len(rows) != 1 or not check_password_hash(rows[0]['password_hash'], password):
            return render_template('login.html', alert='Invalid username and/or password')
            
        session['user_id'] = rows[0]['id']
        
        return redirect('/')
    else:
        return render_template('login.html')

# Log the user out, and redirect to homepage
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Function for querying data from the database
def query(sql, *args):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, args)
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':
    app.run(debug=True)