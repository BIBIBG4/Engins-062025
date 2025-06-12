# import sqlite3

# def init_db():
#     with sqlite3.connect("messages.db") as conn:
#         c = conn.cursor()
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS messages (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 username TEXT NOT NULL,
#                 status TEXT NOT NULL,
#                 message TEXT NOT NULL,
#                 machine TEXT NOT NULL,
#                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
#             )
#         """)
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS channels (
#                 name TEXT PRIMARY KEY
#             )
#         """)

#         # Utilisateurs
#         c.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 username TEXT UNIQUE NOT NULL,
#                 password TEXT NOT NULL,
#                 role TEXT DEFAULT 'user'
#             )
#         """)
#         conn.commit()

# def get_db_connection():
#     conn = sqlite3.connect("messages.db")
#     conn.row_factory = sqlite3.Row
#     return conn

import psycopg2
import os

def get_db_connection():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Table des utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
    """)

    # Table des messages
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            status TEXT,
            message TEXT,
            machine TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Table des machines (canaux)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
