import sqlite3
from werkzeug.security import generate_password_hash

username = "admin"
password = "adminpass"
role = 'admin'

with sqlite3.connect("messages.db") as conn:
    c = conn.cursor()
    hashed_pw = generate_password_hash(password)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
    conn.commit()

print("Utilisateur ajouté !")