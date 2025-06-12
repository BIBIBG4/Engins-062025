from flask import render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import emit
import psycopg2
import psycopg2.extras

def init_routes(app, socketio):

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
            c.execute("INSERT INTO messages (username, status, message, machine, timestamp) VALUES (%s, %s, %s, %s, %s)",
                      (username, status, message, machine, timestamp))
            conn.commit()
            conn.close()
            return redirect("/")

        utilisateur = request.args.get('utilisateur')
        recent = request.args.get('recent')

        query = "SELECT username, status, message, machine, timestamp FROM messages WHERE 1=1"
        params = []

        if utilisateur:
            query += " AND username = %s"
            params.append(utilisateur)

        if recent == "1":
            query += " AND timestamp >= NOW() - INTERVAL '1 day'"

        query += " ORDER BY id DESC"

        conn = get_db_connection()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute(query, params)
        messages = c.fetchall()

        c.execute("SELECT name FROM channels")
        machines = [row["name"] for row in c.fetchall()]

        c.execute("SELECT DISTINCT username FROM messages")
        users = [row["username"] for row in c.fetchall()]
        conn.close()

        return render_template("chat.html", messages=messages, machines=machines, users=users, title="Messagerie")

    @app.route("/canaux", methods=["GET", "POST"])
    def manage_channels():
        if "username" not in session:
            return redirect("/login")
        conn = get_db_connection()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if request.method == "POST":
            name = request.form["channel_name"]
            action = request.form["action"]
            if action == "add":
                try:
                    c.execute("INSERT INTO channels (name) VALUES (%s)", (name,))
                except Exception:
                    pass
            elif action == "delete":
                c.execute("DELETE FROM channels WHERE name = %s", (name,))
            conn.commit()

        c.execute("SELECT name FROM channels ORDER BY name ASC")
        channel_names = [row["name"] for row in c.fetchall()]
        channels = []
        for name in channel_names:
            c.execute("SELECT message, status FROM messages WHERE machine LIKE %s ORDER BY id DESC LIMIT 1", (name,))
            result = c.fetchone()
            last_message = result["message"] if result else None
            last_status = result["status"] if result else None
            channels.append({"name": name, "last_status": last_status, "last_message": last_message})
        conn.close()

        return render_template("manage_channels.html", channels=channels, title="Tableau de bord")

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
            c.execute("INSERT INTO messages (username, status, message, machine, timestamp) VALUES (%s, %s, %s, %s, %s)",
                      (username, status, message, machine, timestamp))
            conn.commit()
            conn.close()
            return redirect(url_for("canal_messages", nom=nom))

        conn = get_db_connection()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT username, status, message, machine, timestamp FROM messages WHERE machine LIKE %s ORDER BY id DESC", (nom,))
        messages = c.fetchall()
        conn.close()
        return render_template("canal.html", canal=nom, messages=messages, title=nom)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT password, role FROM users WHERE username = %s", (username,))
            result = c.fetchone()

            if result and check_password_hash(result[0], password):
                session["username"] = username
                session["role"] = result[1]
                return redirect("/")
            else:
                flash("Nom d'utilisateur ou mot de passe incorrect")

        return render_template("login.html", title="Login")

    @app.route("/logout")
    def logout():
        session.pop("username", None)
        return redirect("/login")

    @app.route("/utilisateurs", methods=["GET", "POST"])
    def gestion_utilisateurs():
        if "username" not in session:
            return redirect(url_for("login"))

        conn = get_db_connection()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == "POST":
            action = request.form.get("action")
            if action == "add":
                username = request.form["username"]
                password = request.form["password"]
                hashed_password = generate_password_hash(password)
                role = request.form.get("role", "user")
                try:
                    c.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, role))
                    conn.commit()
                    flash("Utilisateur ajouté", "success")
                except Exception as e:
                    conn.rollback()
                    flash("Nom d'utilisateur déjà utilisé", "error")
            elif action == "delete":
                username = request.form["username"]
                c.execute("DELETE FROM users WHERE username = %s", (username,))
                conn.commit()
                flash(f"Utilisateur {username} supprimé", "success")

        c.execute("SELECT username, password, role FROM users")
        utilisateurs = c.fetchall()

        return render_template("utilisateurs.html", utilisateurs=utilisateurs, title="Utilisateurs")

    @socketio.on('new_message')
    def handle_new_message(data):
        emit('message_received', data, broadcast=True)