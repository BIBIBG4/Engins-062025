from flask import render_template, request, redirect, url_for, Flask, session, flash
from db import get_db_connection
from datetime import datetime
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

def init_routes(app):

    @app.route("/", methods=["GET", "POST"])
    def chat():
        if "username" not in session:
            return redirect("/login")
        if request.method == "POST":
            username = session["username"]
            status = request.form["status"]
            message = request.form["message"]
            machine = request.form["machine"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO messages (username, status, message, machine, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (username, status, message, machine, timestamp))
            conn.commit()
            conn.close()
            return redirect("/")

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT username, status, message, machine, timestamp FROM messages ORDER BY id DESC")
        messages = c.fetchall()

        c.execute("SELECT name FROM channels")
        machines = [row["name"] for row in c.fetchall()]
        conn.close()

        return render_template("chat.html", messages=messages, machines=machines, title="Messagerie")


    @app.route("/canaux", methods=["GET", "POST"])
    def manage_channels():
        if "username" not in session:
            return redirect("/login")
        conn = get_db_connection()
        c = conn.cursor()
        if request.method == "POST":
            name = request.form["channel_name"]
            action = request.form["action"]
            if action == "add":
                try:
                    c.execute("INSERT INTO channels (name) VALUES (?)", (name,))
                except Exception:
                    pass
            elif action == "delete":
                c.execute("DELETE FROM channels WHERE name = ?", (name,))
            conn.commit()

        c.execute("SELECT name FROM channels ORDER BY name ASC")
        channel_names = [row["name"] for row in c.fetchall()]
        channels = []
        for name in channel_names:
            c.execute("SELECT message, status FROM messages WHERE machine LIKE ? ORDER BY id DESC LIMIT 1", (name,))
            result = c.fetchone()
            last_message = result["message"] if result else None
            last_status = result["status"] if result else None
            channels.append({"name": name, "last_status": last_status, "last_message": last_message})
        conn.close()

        return render_template("manage_channels.html", channels=channels, title = "Tableau de bord")


    @app.route("/canal/<nom>", methods=["GET", "POST"])
    def canal_messages(nom):
        if "username" not in session:
            return redirect("/login")
        if request.method == "POST":
            username = session["username"]
            status = request.form["status"]
            message = request.form["message"]
            machine = nom
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO messages (username, status, message, machine, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (username, status, message, machine, timestamp))
            conn.commit()
            conn.close()
            return redirect(url_for("canal_messages", nom=nom))

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT username, status, message, machine, timestamp FROM messages WHERE machine LIKE ? ORDER BY id DESC", (nom,))
        messages = c.fetchall()
        conn.close()
        return render_template("canal.html", canal=nom, messages=messages, title = nom)
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            with sqlite3.connect("messages.db") as conn:
                c = conn.cursor()
                c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
                result = c.fetchone()

                if result and check_password_hash(result[0], password):
                    session["username"] = username
                    session["role"] = result[1]
                    return redirect("/")
                else:
                    flash("Nom d'utilisateur ou mot de passe incorrect")
        
        return render_template("login.html", title = "Login")

    @app.route("/logout")
    def logout():
        session.pop("username", None)
        return redirect("/login")
       

    @app.route("/utilisateurs", methods=["GET", "POST"])
    def gestion_utilisateurs():
        with sqlite3.connect("messages.db") as conn:
            if "username" not in session:
                return redirect(url_for("login"))
            
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
            
            # Ajouter un utilisateur
            if request.method == "POST":
                action = request.form.get("action")
                if action == "add":
                    username = request.form["username"]
                    password = request.form["password"]
                    hashed_password = generate_password_hash(password)
                    role = request.form.get("role", "user")
                    try:
                        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
                        conn.commit()
                        flash("Utilisateur ajouté", "success")
                    except sqlite3.IntegrityError:
                        flash("Nom d'utilisateur déjà utilisé", "error")
                elif action == "delete":
                    username = request.form["username"]
                    c.execute("DELETE FROM users WHERE username = ?", (username,))
                    conn.commit()
                    flash(f"Utilisateur {username} supprimé", "success")

            # Affichage des utilisateurs
            c.execute("SELECT username, password, role FROM users")
            utilisateurs = c.fetchall()

        return render_template("utilisateurs.html", utilisateurs=utilisateurs, title = "Utilisateurs")