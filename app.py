from flask import Flask, render_template, request, redirect, url_for, session
from routes import init_routes
from db import init_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "votre_clé_secrète"  # Change cette clé pour la sécurité

init_db()         # initialise la base au lancement

def create_default_admin():
    admin_username = "admin"
    admin_password = "admin123"  # CHANGE CE MOT DE PASSE EN PROD !
    admin_role = "admin"

    # Connexion à la base (adapter si tu as un autre chemin)
    conn = sqlite3.connect('database.db')  # adapte le chemin selon ta config
    cursor = conn.cursor()

    # Vérifier si l'admin existe déjà
    cursor.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
    user = cursor.fetchone()

    if not user:
        hashed_password = generate_password_hash(admin_password)
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (admin_username, hashed_password, admin_role))
        conn.commit()
        print("Utilisateur admin par défaut créé")
    else:
        print("Utilisateur admin déjà existant")

    conn.close()

create_default_admin()

init_routes(app)  # enregistre les routes

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
