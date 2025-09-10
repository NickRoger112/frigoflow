from flask import Flask, redirect, render_template, request, session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, query, execute
from datetime import datetime, date
from dotenv import load_dotenv
import requests
import json
import os
import mysql.connector

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
    rows = query('SELECT id, name, expiration_date, notes FROM items WHERE user_id = %s ORDER BY expiration_date', session['user_id'])
    items_with_dates = []
    
    today = date.today()
    
    for item in rows:
        expiration_date_obj = datetime.strptime(str(item['expiration_date']), '%Y-%m-%d').date()
        days_left = (expiration_date_obj - today).days
        
        item_data = {
            "id": item['id'], "name": item['name'], "expiration_date": str(item['expiration_date']),
            "notes": item['notes'], "days_left": days_left
        }
        
        items_with_dates.append(item_data)
        
    return render_template("index.html", items=items_with_dates)

@app.route('/recipes')
@login_required
def recipes():
    rows = query('SELECT name FROM items WHERE user_id = %s', session['user_id'])
    items = [row['name'] for row in rows]
    
    products = ','.join(items).lower()
    
    cache_dir = 'cache'
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f'{products}.json')
    
    recipes_data = []
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            try: recipes_data = json.load(f)
            except json.JSONDecodeError:
                os.remove(cache_file)
                recipes_data = fetch_and_cache_recipes(products, cache_file)
    else:
        recipes_data = fetch_and_cache_recipes(products, cache_file)
        
    return render_template("recipes.html", recipes=recipes_data, api_key=API_KEY)

def fetch_and_cache_recipes(products, cache_file):
    params = {'ingredients': products, 'apiKey': API_KEY, 'minMissingIngredients': 0, 'ignorePantry': True}
    response = requests.get('https://api.spoonacular.com/recipes/findByIngredients', params=params)
    
    if response.status_code == 200:
        recipes_data = response.json()
        with open(cache_file, 'w') as f: json.dump(recipes_data, f)
        return recipes_data
    else:
        return []

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        item_name = request.form.get('item-name')
        expiration_date_str = request.form.get('expiration-date')
        notes = request.form.get('notes')
        
        if not item_name or not expiration_date_str:
            flash('Missing required fields.', 'danger')
            return redirect(url_for('index'))

        try:
            execute('INSERT INTO items (name, expiration_date, notes, user_id) VALUES (%s, %s, %s, %s)',
                    item_name, expiration_date_str, notes, session['user_id'])
        except mysql.connector.Error:
            flash('Failed to add item.', 'danger')
            return redirect(url_for('index'))
        
        flash(f'Added {item_name} to items!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:item_id>')
@login_required
def delete(item_id):
    rows = query('SELECT id FROM items WHERE id = %s AND user_id = %s', item_id, session['user_id'])
    if len(rows) != 1:
        flash('Item not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('index'))

    try:
        execute('DELETE FROM items WHERE id = %s AND user_id = %s', item_id, session['user_id'])
    except mysql.connector.Error:
        flash('Could not delete item.', 'danger')
        return redirect(url_for('index'))
        
    flash('Successfully deleted item!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        expiration_date_str = request.form.get('expiration_date')
        notes = request.form.get('notes')
        
        if not item_name or not expiration_date_str:
            flash('Missing required fields.', 'danger')
            return redirect(url_for('index'))

        try:
            execute("UPDATE items SET name = %s, expiration_date = %s, notes = %s WHERE id = %s AND user_id = %s",
                    item_name, expiration_date_str, notes, item_id, session['user_id'])
        except mysql.connector.Error:
            flash('Failed to update item.', 'danger')
            return redirect(url_for('index'))
        
        flash('Successfully updated item.', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        
        if not username or not password or not confirmation:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        if password != confirmation:
            flash('Passwords don\'t match.', 'danger')
            return render_template('register.html')
        
        password_hash = generate_password_hash(password)
        
        try:
            execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', username, password_hash)
        except mysql.connector.IntegrityError:
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        except mysql.connector.Error:
            flash('An error occurred during registration.', 'danger')
            return render_template('register.html')
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
    
# Log the user in, and redirect to homepage
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Missing username or password.', 'danger')
            return render_template('login.html')
        
        rows = query('SELECT * FROM users WHERE username = %s', username)
        
        if len(rows) != 1 or not check_password_hash(rows[0]['password_hash'], password):
            flash('Invalid username and/or password.', 'danger')
            return render_template('login.html')
            
        session.clear()
        session['user_id'] = rows[0]['id']
        
        return redirect(url_for('index'))
    return render_template('login.html')

# Log the user out, and redirect to homepage
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)