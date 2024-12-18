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
DATABASE = 'duck.db'


app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

Session(app)

def get_db():
  
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db


# Fermer la base de données après chaque requête
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))



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
            flash("Registration successful ! Please log in", category="success")
            return redirect("/login")
            
        except sqlite3.IntegrityError:
            # Handle duplicate usernames gracefully
            return apology("username already exists", 400)
        except Exception as e:
            # Log the error for debugging and return a generic error response
            print(f"Error during registration: {e}")
            return apology("An error occurred. Please try again.", 500)

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
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
        

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/dashboard")

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

@app.route("/dashboard")
def dashboard():
    """Dashboard"""
    return render_template("dashboard.html")


@app.route("/lesson1", methods=["GET", "POST"])
def lesson1():
    
    vocabulary = {
    "Bonjour": {
        "translation": "Hello",
        "pronunciation": "audio/bonjour.mp3",
        "context": "Used to greet someone during the day."
    },
    "Merci": {
        "translation": "Thank you",
        "pronunciation": "audio/Merci.mp3",
        "context": "Used to express gratitude."
    },
    "Excusez-moi": {
        "translation": "Excuse me",
        "pronunciation": "audio/Excusez.mp3",
        "context": "Used to get someone's attention politely."
    },
    "Oui": {
        "translation": "Yes",
        "pronunciation": "audio/Oui.mp3",
        "context": "Used to affirm something."
    },
    "Non": {
        "translation": "No",
        "pronunciation": "audio/Non.mp3",
        "context": "Used to negate something."
    },
    "S'il vous plaît": {
        "translation": "Please",
        "pronunciation": "audio/sil_vous_plait.mp3",
        "context": "Used to politely ask for something."
    },
    "Au revoir": {
        "translation": "Goodbye",
        "pronunciation": "audio/au_revoir.mp3",
        "context": "Used to say farewell."
    },
    "Comment allez vous ?": {
        "translation": "How are you?",
        "pronunciation": "audio/Comment_.mp3",
        "context": "Used to ask how someone is doing."
    },
    "Je ne sais pas": {
        "translation": "I don't know",
        "pronunciation": "audio/je_ne_sais_pas.mp3",
        "context": "Used to indicate uncertainty."
    },
    "Bienvenue": {
        "translation": "Welcome",
        "pronunciation": "audio/bienvenue.mp3",
        "context": "Used to greet someone arriving at a place."
    }
}


    return render_template("lesson1.html",vocabulary=vocabulary)




@app.route("/quizz1", methods=["GET", "POST"])
def quizz1():

    return render_template("quizz1.html")
    