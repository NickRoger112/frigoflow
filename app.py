from flask import Flask, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from helpers import login_required, query
from datetime import datetime, date

# TODO: Change alerts to use flash

app = Flask(__name__)
app.secret_key = 'mysecret'

# Main page, can't visit without logging in
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        item_name = request.form.get('item-name')
        expiration_date_str = request.form.get('expiration-date')
        notes = request.form.get('notes')
        
        if not item_name:
            return render_template('index.html', alert='Missing item name')
        if not expiration_date_str:
            return render_template('index.html', alert='Missing expiration date')

        try:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
            if expiration_date < date.today():
                return render_template('index.html', alert='Expiration date must be in future')
        except ValueError:
            return render_template('index.html', alert='Invalid date format')
        
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO items(name, expiration_date, notes, user_id) VALUES(?, ?, ?, ?)', (item_name, expiration_date_str, notes, session['user_id']))
                conn.commit()
        except sqlite3.Error:
            return render_template('index.html', alert='Failed to add item')
            
    rows = query('SELECT id, name, expiration_date, notes FROM items WHERE user_id = ?', session['user_id'])
    return render_template("index.html", items=rows)

# Delete an item from the database
@app.route('/delete/<int:item_id>')
@login_required
def delete_item(item_id):
    rows = query('SELECT * FROM items WHERE id = ? AND user_id = ?', item_id, session['user_id'])
    
    if len(rows) != 1:
        return render_template('index.html', alert='Couldn\'t delete item')

    try:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM items WHERE id = ? AND user_id = ?', (item_id, session['user_id']))
            conn.commit()
    except sqlite3.Error:
        return render_template('index.html', alert='Couldn\'t delete item')
        
    return redirect(url_for('index'))

# Edit an existing item in database
@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        expiration_date_str = request.form.get('expiration_date')
        notes = request.form.get('notes')
        
        if not item_name:
            return render_template('index.html', alert='Missing item name')
        if not expiration_date_str:
            return render_template('index.html', alert='Missing expiration date')

        try:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
            if expiration_date < date.today():
                return render_template('index.html', alert='Expiration date must be in future')
        except ValueError:
            return render_template('index.html', alert='Invalid date format')
        
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("UPDATE items SET name = ?, expiration_date = ?, notes = ? WHERE id = ? AND user_id = ?", (item_name, expiration_date_str, notes, item_id, session['user_id']))
                conn.commit()
        except sqlite3.Error:
            return render_template('index.html', alert='Failed to update item')
        
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))
        
    

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
@login_required
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)