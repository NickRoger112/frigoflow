from flask import Flask, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, query
from datetime import datetime, date
from dotenv import load_dotenv
import requests
import sqlite3
import json
import os

# Load the environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Get the API key from environment variables
API_KEY = os.getenv('SPOONACULAR_API_KEY')
if not API_KEY:
    raise ValueError("SPOONACULAR_API_KEY environment variable not set.")

# Main page, can't visit without logging in
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():     
    rows = query('SELECT id, name, expiration_date, notes FROM items WHERE user_id = ? ORDER BY expiration_date', session['user_id'])
    
    items_with_dates = []
    
    today = date.today()
    
    for item in rows:
        expiration_date_obj = datetime.strptime(item['expiration_date'], '%Y-%m-%d').date()
            
        days_left = (expiration_date_obj - today).days
        
        item_data = {
            "id": item['id'],
            "name": item['name'],
            "expiration_date": item['expiration_date'],
            "notes": item['notes'],
            "days_left": days_left
        }
        
        items_with_dates.append(item_data)
    
    return render_template("index.html", items=items_with_dates)

@app.route('/recipes')
@login_required
def recipes():
    rows = query('SELECT name FROM items WHERE user_id = ?', session['user_id'])
    items = [row['name'] for row in rows]
    
    products = ','.join(items).lower()
    
    cache_dir = 'cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f'{products}.json')
    
    recipes_data = []
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            try:
                recipes_data = json.load(f)
            except json.JSONDecodeError:
                print("Cache file is corrupted. Fetching from API instead.")
                os.remove(cache_file)
                recipes_data = fetch_and_cache_recipes(products, cache_file)    
    else:
        recipes_data = fetch_and_cache_recipes(products, cache_file)
        
    return render_template("recipes.html", recipes=recipes_data, api_key=API_KEY)
        
def fetch_and_cache_recipes(products, cache_file):
    params = {
        'ingredients': products,
        'apiKey': API_KEY,
        'minMissingIngredients': 0,
        'ignorePantry': True
    }

    response = requests.get('https://api.spoonacular.com/recipes/findByIngredients', params=params)
    
    if response.status_code == 200:
        recipes_data = response.json()
        with open(cache_file, 'w') as f:
            json.dump(recipes_data, f)
        return recipes_data
    else:
        print(f'API error: {response.status_code}')
        return []

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        item_name = request.form.get('item-name')
        expiration_date_str = request.form.get('expiration-date')
        notes = request.form.get('notes')
        
        if not item_name:
            flash('Missing item name.', 'danger')
            return redirect(url_for('index'))
        if not expiration_date_str:
            flash('Missing expiration date.', 'danger')
            return redirect(url_for('index'))

        try:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
            if expiration_date < date.today():
                flash('Expiration date must be in the future.', 'danger')
                return redirect(url_for('index'))
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('index'))
        
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO items(name, expiration_date, notes, user_id) VALUES(?, ?, ?, ?)', (item_name, expiration_date_str, notes, session['user_id']))
                conn.commit()
        except sqlite3.Error:
            flash('Failed to add item.', 'danger')
            return redirect(url_for('index'))
        
    flash(f'Added {item_name} to items!', 'success')
    return redirect(url_for('index'))
    
# Delete an item from the database
@app.route('/delete/<int:item_id>')
@login_required
def delete(item_id):
    rows = query('SELECT * FROM items WHERE id = ? AND user_id = ?', item_id, session['user_id'])
    
    if len(rows) != 1:
        flash('Couldn\'t delete item.', 'danger')
        return redirect(url_for('index'))

    try:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM items WHERE id = ? AND user_id = ?', (item_id, session['user_id']))
            conn.commit()
    except sqlite3.Error:
        flash('Couldnt\'t delete item.', 'danger')
        return redirect(url_for('index'))
        
    flash('Successfuly deleted item!', 'success')
    return redirect(url_for('index'))

# Edit an existing item in database
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        expiration_date_str = request.form.get('expiration_date')
        notes = request.form.get('notes')
        
        if not item_name:
            flash('Missing item name.', 'danger')
            return redirect(url_for('index'))
        if not expiration_date_str:
            flash('Missing expiration date.', 'danger')
            return redirect(url_for('index'))

        try:
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
            if expiration_date < date.today():
                flash('Expiration date must be in the future.', 'danger')
                return redirect(url_for('index'))
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('index'))
        
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("UPDATE items SET name = ?, expiration_date = ?, notes = ? WHERE id = ? AND user_id = ?", (item_name, expiration_date_str, notes, item_id, session['user_id']))
                conn.commit()
        except sqlite3.Error:
            flash('Failed to update item.', 'danger')
            return redirect(url_for('index'))
        
        flash('Successfuly changed item.', 'success')
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
            flash('Missing username.', 'danger')
            return redirect(url_for('register'))
        if not password:
            flash('Missing password.', 'danger')
            return redirect(url_for('register'))
        if not password == confirmation:
            flash('Passwords don\'t match.', 'danger')
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)
        
        try:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users(username, password_hash) VALUES(?, ?)', (username, password_hash))
                conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        except sqlite3.Error as e:
            flash(f'Something went wrong {e}.', 'danger')
            return redirect(url_for('register'))
        
        return redirect(url_for('login'))
    else:
        return render_template('register.html')
    
# Log the user in, and redirect to homepage
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username:
            flash('Missing username.', 'danger')
            return redirect(url_for('login'))
        if not password:
            flash('Missing password.', 'danger')
            return redirect(url_for('login'))
        
        rows = query('SELECT * FROM users WHERE username = ?', username)
        
        if len(rows) != 1 or not check_password_hash(rows[0]['password_hash'], password):
            flash('Invalid username and/on password.', 'danger')
            return redirect(url_for('login'))
            
        session.clear()
        session['user_id'] = rows[0]['id']
        
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

# Log the user out, and redirect to homepage
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)