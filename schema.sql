DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS items;

-- Users table
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password_hash TEXT NOT NULL
);

-- Items table
CREATE TABLE items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  expiration_date TEXT NOT NULL,
  user_id INTEGER NOT NULL, notes TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);