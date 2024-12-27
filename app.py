import os
import time
import datetime
import sqlite3
import random
from flask import Flask, flash, redirect, render_template, request, session,g, jsonify
from flask_session import Session
from data import lesson1,lesson2,lesson3,lesson4
from logging_config import setup_logger


from helper import apology, login_required

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
logger = setup_logger()
logger.info("Application started correctly")

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
            logger.info("User registered sucessfully")
            return redirect("/success")
            
        except sqlite3.IntegrityError:
            # Handle duplicate usernames gracefully
            return apology("username already exists", 400)
        except Exception as e:
            # Log the error for debugging and return a generic error response
          
            logger.error(f"error while registering : {e}")
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
            logger.error("User failed to login")
            return apology("invalid username and/or password", 403)
            

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        logger.info("User login sucessfully")
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
    logger.info("user logout")
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
        session["score"] = 0  # Initialisation uniquement si la clé n'existe pas
    if "test_size" not in session:
        session["test_size"] = 0
    
   
    score = session["score"]
    test_size = session["test_size"]

    
    
    
    if request.method == "POST":
        selected_answer = request.form.get("choice")  # Récupère la réponse sélectionnée
        question = session.get("question") 

        # Vérifie si la réponse est correcte
        correct_answer = lesson1[question]["translation"]
        
        if selected_answer.strip().lower() == correct_answer.strip().lower():
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

            logger.info("score registered in the database successfully")
          
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


@app.route("/about")
def about():

    return render_template("about.html")


@app.route("/account",methods=["GET", "POST"])
@login_required

def account():


    return render_template("account.html")

@app.route("/pswd_change", methods=["GET", "POST"])
@login_required
def pswd_change():
    db=get_db()
    user_id = db.execute("SELECT id FROM users WHERE id=?", (session["user_id"],)).fetchone()

    if request.method == "POST":
        if not request.form.get("password"):
            return apology("must provide password", 403)
        if not request.form.get("confirmation"):
            return apology("must confirm password", 403)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 403)

        old = db.execute("SELECT hash FROM users WHERE id = ?", (user_id["id"],)).fetchone()

        hash = generate_password_hash(request.form.get("password"), method='scrypt', salt_length=16)
        

        if check_password_hash(old["hash"], request.form.get("password")):
            return apology("Do not reuse password", 403)

        try:
            db.execute("UPDATE users SET hash = ? WHERE id = ?", (hash, user_id["id"],))
            db.commit()
            logout()
            logger.info("user password changed successfully")
            return redirect("/success")
            
            

        except Exception as e:
            print(f"Exception: {e}")
            logger.error(f"error while changing password : {e}")
            return apology("Error", 403)

    return render_template("change_pswd.html")


@app.route ("/scoreboard")
@login_required
def scoreboard():
    db=get_db()
    user_id = db.execute("SELECT id FROM users WHERE id=?", (session["user_id"],)).fetchone()

    scoreboard=db.execute("SELECT quiz_name,score,date FROM quiz_results WHERE user_id = ?",(user_id["id"],)).fetchall()

    return render_template("scoreboard.html",scoreboard=scoreboard)


@app.route("/delete_account", methods=["GET","POST"])
@login_required
def delete_account():
    db=get_db()
    user_id = db.execute("SELECT id FROM users WHERE id=?", (session["user_id"],)).fetchone()
    psw= db.execute("SELECT hash FROM users WHERE id = ?", (user_id["id"],)).fetchone()

    if request.method == "POST":
        if not request.form.get("password"):
            return apology("must provide password", 403)
        if not request.form.get("confirmation"):
            return apology("must confirm password", 403)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 403)
        
        if not check_password_hash(psw["hash"],request.form.get("password")):
            return apology("password dont match",403)
        
        try:
            db.execute("DELETE FROM quiz_results WHERE user_id=?",(session["user_id"],))
            db.commit()
            db.execute("DELETE FROM users WHERE id=?",(session["user_id"],))
            db.commit()
            session.clear()
            logger.info("User account deleted sucessfully")
            return redirect("/success")
        
        except:
            logger.error ("Failed to delete account")
            return apology("account was not deleted",400)


        




    


    return render_template("delete.html")


@app.route("/lesson2", methods=["GET", "POST"])
@login_required
def lesson2_page():
    
   

    return render_template("lesson2.html",vocabulary=lesson2)



@app.route("/quizz2", methods=["GET", "POST"])
@login_required
def quizz2():
    db=get_db()
    user_id=session.get("user_id")
    
    if "score" not in session:
        session["score"] = 0  # Initialisation uniquement si la clé n'existe pas
    if "test_size" not in session:
        session["test_size"] = 0
    score2 = session["score"]
    test_size = session["test_size"]

    
    
    
    if request.method == "POST":
        selected_answer = request.form.get("choice")  # Récupère la réponse sélectionnée
        question = session.get("question") 

        # Vérifie si la réponse est correcte
        correct_answer = lesson2[question]["translation"]
        
        if selected_answer.strip().lower() == correct_answer.strip().lower():
            score2 += 1  # Incrémente le score
        test_size += 1  # Incrémente le nombre de questions

        session["score"] = score2
        session["test_size"] = test_size

        # Si 10 questions ont été posées, on affiche le score final
        if test_size >= 10:
            db.execute("INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",(user_id, "quizz2", session["score"]))
            db.commit()
            session.pop('score', None)  # Reset score or use session.clear() for all session data
            session.pop('test_size', None)  # Reset any other session data
            logger.info("score registered in the database successfully")
          
            return render_template("dashboard.html", score=score2)

    # Si on est en GET (c'est-à-dire qu'on commence un nouveau quiz)
    question = random.choice(list(lesson2.keys()))
    session["question"] = question
    choice2 = random.choice(list(lesson2.keys()))
    choice3 = random.choice(list(lesson2.keys()))
    correct_answer = lesson2[question]["translation"]
    answer2 = lesson2[choice2]["translation"]
    answer3 = lesson2[choice3]["translation"]
    
    # Mélange les réponses pour ne pas afficher la bonne toujours en premier
    answers = [correct_answer, answer2, answer3]
    random.shuffle(answers)

    # Envoie la question et les réponses à la page

    
    
    return render_template("quizz2.html", question=question, answers=answers, score=score2)



@app.route("/lesson3", methods=["GET", "POST"])
@login_required
def lesson3_page():
    
   

    return render_template("lesson3.html")

@app.route("/quizz3", methods=["GET","POST"])
@login_required
def quizz3():
    db=get_db()
    user_id=session.get("user_id")
    
    if "score" not in session:
        session["score"] = 0  # Initialisation uniquement si la clé n'existe pas
    if "test_size" not in session:
        session["test_size"] = 0

    score3 = session["score"]
    test_size = session["test_size"]

    
    
    
    if request.method == "POST":
        
        selected_answer = request.form.get("choice")  # Récupère la réponse sélectionnée
        question = session.get("question") 

        # Vérifie si la réponse est correcte
        correct_answer = question
       
       
        
        if selected_answer.strip().lower() == correct_answer.strip().lower():
           
            score3=score3+1  # Incrémente le score
        test_size += 1  # Incrémente le nombre de questions

        session["score"] = score3
    
        session["test_size"] = test_size
        

        # Si 10 questions ont été posées, on affiche le score final
        if test_size >= 10:
            db.execute("INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",(user_id, "quizz3", session["score"]))
            db.commit()
            session.pop('score', None)  # Reset score or use session.clear() for all session data
            session.pop('test_size', None)  # Reset any other session data
            logger.info("score registered in the database successfully")
          
            return render_template("dashboard.html", score=score3)

    # Si on est en GET (c'est-à-dire qu'on commence un nouveau quiz)
    question = random.choice(list(lesson3.keys()))
    french= lesson3[question]["french_sentence"]
    english=lesson3[question]["english_sentence"]
    session["question"] = question
    choice2 = random.choice(list(lesson3.keys()))
    choice3 = random.choice(list(lesson3.keys()))
    correct_answer = question
    answer2 = choice2
    answer3 = choice3
    
    # Mélange les réponses pour ne pas afficher la bonne toujours en premier
    answers = [correct_answer, answer2, answer3]
    random.shuffle(answers)

    # Envoie la question et les réponses à la page


    return render_template("quizz3.html" ,question=question, answers=answers, score=score3,french=french,english=english)



@app.route("/lesson4", methods=["GET", "POST"])
@login_required
def lesson4_page():
    
   

    return render_template("lesson4.html",vocabulary=lesson4)


@app.route("/success", methods=["GET", "POST"])

def success():
    
   

    return render_template("success.html")



@app.route("/quizz4", methods=["GET", "POST"])
@login_required
def quizz4():
    db=get_db()
    user_id=session.get("user_id")
    
    if "score" not in session:
        session["score"] = 0  # Initialisation uniquement si la clé n'existe pas
    if "test_size" not in session:
        session["test_size"] = 0
    score4 = session["score"]
    test_size = session["test_size"]

    
    
    
    if request.method == "POST":
        selected_answer = request.form.get("choice")  # Récupère la réponse sélectionnée
        question = session.get("question") 

        # Vérifie si la réponse est correcte
        correct_answer = lesson4[question]["translation"]
        
        if selected_answer.strip().lower() == correct_answer.strip().lower():
            score4 += 1  # Incrémente le score
        test_size += 1  # Incrémente le nombre de questions

        session["score"] = score4
        session["test_size"] = test_size

        # Si 10 questions ont été posées, on affiche le score final
        if test_size >= 10:
            db.execute("INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",(user_id, "quizz4", session["score"]))
            db.commit()
            session.pop('score', None)  # Reset score or use session.clear() for all session data
            session.pop('test_size', None)  # Reset any other session data
            logger.info("score registered in the database successfully")
          
            return render_template("dashboard.html", score=score4)

    # Si on est en GET (c'est-à-dire qu'on commence un nouveau quiz)
    question = random.choice(list(lesson4.keys()))
    session["question"] = question
    choice2 = random.choice(list(lesson4.keys()))
    choice3 = random.choice(list(lesson4.keys()))
    correct_answer = lesson4[question]["translation"]
    answer2 = lesson4[choice2]["translation"]
    answer3 = lesson4[choice3]["translation"]
    
    # Mélange les réponses pour ne pas afficher la bonne toujours en premier
    answers = [correct_answer, answer2, answer3]
    random.shuffle(answers)

    # Envoie la question et les réponses à la page

    
    
    return render_template("quizz4.html", question=question, answers=answers, score=score4)













        


    


    

