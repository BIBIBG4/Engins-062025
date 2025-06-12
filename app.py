from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db import get_db_connection, init_db
import psycopg2

socketio = SocketIO()




def create_default_admin():
    admin_username = "admin"
    admin_password = "admin123"  # CHANGE CE MOT DE PASSE EN PROD !
    admin_role = "admin"

    # Connexion à la base (adapter si tu as un autre chemin)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier si l'admin existe déjà
    cursor.execute("SELECT * FROM users WHERE username = %s", (admin_username,))
    user = cursor.fetchone()

    if not user:
        hashed_password = generate_password_hash(admin_password)
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                       (admin_username, hashed_password, admin_role))
        conn.commit()
        print("Utilisateur admin par défaut créé")
    else:
        print("Utilisateur admin déjà existant")
    conn.close()


def create_app():
    app = Flask(__name__)
    app.secret_key = "votre_clé_secrète"  # Change cette clé pour la sécurité

    init_db()

    create_default_admin()
    from routes import init_routes
    init_routes(app, socketio)  # enregistre les routes
    socketio.init_app(app)
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)


