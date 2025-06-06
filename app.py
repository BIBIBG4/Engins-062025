from flask import Flask, render_template, request, redirect, url_for, session
from routes import init_routes
from db import init_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "votre_clé_secrète"  # Change cette clé pour la sécurité

init_db()         # initialise la base au lancement
init_routes(app)  # enregistre les routes

if __name__ == "__main__":
    app.run(debug=True)
