from flask import session, redirect, url_for
import sqlite3
import functools

# Add the login required decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# Function for querying data from the database
def query(sql, *args):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, args)
    rows = cur.fetchall()
    conn.close()
    return rows