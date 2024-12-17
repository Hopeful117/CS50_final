import os
import time
import datetime
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session,g
from flask_session import Session

from helper import apology, login_required

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['DATABASE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'duck.db')


app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

Session(app)

def get_db():
  
    if not hasattr(g, '_database'):
        g._database = sqlite3.connect(app.config['DATABASE'])
        g._database.row_factory = sqlite3.Row  # pour accéder aux colonnes par nom
    return g._database

# Fermer la base de données après chaque requête
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def welcome():
    return render_template('welcome.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    db=get_db()
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        elif (request.form.get("password") != request.form.get("confirmation")):
            return apology("password dont match", 400)
        hash = generate_password_hash(request.form.get("password"), method='scrypt', salt_length=16)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       (request.form.get("username"), hash))
            db.commit()
            flash("success", category="success")
            

        except Exception as e:
            print(e)

            return apology("error", 400)

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    db=get_db()

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

