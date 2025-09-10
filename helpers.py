from flask import session, redirect, url_for
import mysql.connector
import functools
import os

# Add the login required decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return conn

def query(sql, *args):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute(sql, *args):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, args)
    conn.commit()
    cur.close()
    conn.close()