import os
import time
import datetime
import sqlite3
import random
from flask import Flask, flash, redirect, render_template, request, session,g, jsonify
from flask_session import Session
from data import lesson1


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
@login_required
def dashboard():
    """Dashboard"""
    return render_template("dashboard.html")


@app.route("/lesson1", methods=["GET", "POST"])
@login_required
def lesson1_page():
    
   

    return render_template("lesson1.html",vocabulary=lesson1)

@app.route("/quizz1", methods=["GET", "POST"])
@login_required
def quizz1():
    db=get_db()
    user_id=session.get("user_id")
    if "score" not in session:
        session["score"] = 0  # Initialisation du score dans la session
        session["test_size"] = 0  # Initialisation du nombre de questions
    score = session["score"]
    test_size = session["test_size"]

    
    
    
    if request.method == "POST":
        selected_answer = request.form.get("choice")  # Récupère la réponse sélectionnée
        question = session.get("question") 

        # Vérifie si la réponse est correcte
        correct_answer = lesson1[question]["translation"]
        
        if selected_answer == correct_answer:
            score += 1  # Incrémente le score
        test_size += 1  # Incrémente le nombre de questions

        session["score"] = score
        session["test_size"] = test_size

        # Si 10 questions ont été posées, on affiche le score final
        if test_size >= 10:
            db.execute("INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",(user_id, "quizz1", session["score"]))
            db.commit()
            session.pop('score', None)  # Reset score or use session.clear() for all session data
            session.pop('test_size', None)  # Reset any other session data
          
            return render_template("dashboard.html", score=score)

    # Si on est en GET (c'est-à-dire qu'on commence un nouveau quiz)
    question = random.choice(list(lesson1.keys()))
    session["question"] = question
    choice2 = random.choice(list(lesson1.keys()))
    choice3 = random.choice(list(lesson1.keys()))
    correct_answer = lesson1[question]["translation"]
    answer2 = lesson1[choice2]["translation"]
    answer3 = lesson1[choice3]["translation"]
    
    # Mélange les réponses pour ne pas afficher la bonne toujours en premier
    answers = [correct_answer, answer2, answer3]
    random.shuffle(answers)

    # Envoie la question et les réponses à la page

    
    
    return render_template("quizz1.html", question=question, answers=answers, score=score)







        


    


    

