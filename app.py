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
    db = get_db()
    user_id = session.get("user_id")
    
    # Initialisation de `copylesson2` en début de fonction
    if "copylesson1" not in session:
        session["copylesson1"] = lesson1.copy()

    copylesson1 = session["copylesson1"]

    # Initialisation des variables de session pour le score et la taille du test
    if "score" not in session:
        session["score"] = 0
    if "test_size" not in session:
        session["test_size"] = 0

    score1 = session["score"]
    test_size = session["test_size"]


    

    if request.method == "POST":
        
        selected_answer = request.form.get("choice")  # Réponse sélectionnée par l'utilisateur
        
        question = session.get("question")  # Question en cours
        if not selected_answer:
            logger.error("User didnt select an answer")
            
            return redirect("/quizz1")


        # Vérifie si la réponse est correcte
        correct_answer = lesson1[question]["translation"]
        if selected_answer.strip().lower() == correct_answer.strip().lower():
            score1 += 1  # Incrémente le score
        test_size += 1  # Incrémente le nombre de questions posées

        session["score"] = score1
        session["test_size"] = test_size

        # Retire la question actuelle de `copylesson2`
        copylesson1.pop(question)

        # Vérifie si 10 questions ont été posées ou s'il n'y a plus de questions
        if test_size >= 10 or not copylesson1:
            db.execute(
                "INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",
                (user_id, "quizz1", score1),
            )
            db.commit()

            session["final_score"] = score1
            session.pop("score")  # Réinitialise le score
            session.pop("test_size")  # Réinitialise le compteur de questions
            session.pop("copylesson1")  # Réinitialise `copylesson2`
            logger.info("session reset sucessful")
            logger.info("Score registered succesful")
            return redirect("/score")

    # Si on est en GET (nouvelle question)
    if not copylesson1:
        logger.warning("Quizz didnt reset properly.")
        return redirect("/score")

    question = random.choice(list(copylesson1.keys()))
    session["question"] = question

    # Génère deux autres choix incorrects aléatoires
    remaining_keys = [key for key in lesson1.keys() if key != question]
    if len(remaining_keys) < 2:
        logger.warning("Quizz didnt reset properly.")
        return redirect("/score")

    other_choices = random.sample(remaining_keys, 2)

    # Réponses possibles, mélangées aléatoirement
    correct_answer = lesson1[question]["translation"]
    answers = [
        correct_answer,
        lesson1[other_choices[0]]["translation"],
        lesson1[other_choices[1]]["translation"],
    ]
    random.shuffle(answers)

    # Affiche la question et les réponses à l'utilisateur
    return render_template("quizz1.html", question=question, answers=answers, score=score1)



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
    db = get_db()
    user_id = session.get("user_id")
    
    # Initialisation de `copylesson2` en début de fonction
    if "copylesson2" not in session:
        session["copylesson2"] = lesson2.copy()

    copylesson2 = session["copylesson2"]

    # Initialisation des variables de session pour le score et la taille du test
    if "score" not in session:
        session["score"] = 0
    if "test_size" not in session:
        session["test_size"] = 0

    score2 = session["score"]
    test_size = session["test_size"]

    if request.method == "POST":
        selected_answer = request.form.get("choice")  # Réponse sélectionnée par l'utilisateur
        question = session.get("question")  # Question en cours

        if not selected_answer:
            logger.error("user didnt select an answer ")
            return redirect("/quizz2")


        # Vérifie si la réponse est correcte
        correct_answer = lesson2[question]["translation"]
        if selected_answer.strip().lower() == correct_answer.strip().lower():
            score2 += 1  # Incrémente le score
        test_size += 1  # Incrémente le nombre de questions posées

        session["score"] = score2
        session["test_size"] = test_size

        # Retire la question actuelle de `copylesson2`
        copylesson2.pop(question)

        # Vérifie si 10 questions ont été posées ou s'il n'y a plus de questions
        if test_size >= 10 or not copylesson2:
            db.execute(
                "INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",
                (user_id, "quizz2", score2),
            )
            db.commit()

            session["final_score"] = score2
            session.pop("score")  # Réinitialise le score
            session.pop("test_size")  # Réinitialise le compteur de questions
            session.pop("copylesson2")  # Réinitialise `copylesson2`
            logger.info("session reset successful")
            logger.info("Score registered successfully")
            return redirect("/score")

    # Si on est en GET (nouvelle question)
    if not copylesson2:
        logger.warning("quizz didnt reset properly")
        return redirect("/score")

    question = random.choice(list(copylesson2.keys()))
    session["question"] = question

    # Génère deux autres choix incorrects aléatoires
    remaining_keys = [key for key in lesson2.keys() if key != question]
    if len(remaining_keys) < 2:
        logger.warning("Quizz didnt reset properly")
        return redirect("/score")

    other_choices = random.sample(remaining_keys, 2)

    # Réponses possibles, mélangées aléatoirement
    correct_answer = lesson2[question]["translation"]
    answers = [
        correct_answer,
        lesson2[other_choices[0]]["translation"],
        lesson2[other_choices[1]]["translation"],
    ]
    random.shuffle(answers)

    # Affiche la question et les réponses à l'utilisateur
    return render_template("quizz2.html", question=question, answers=answers, score=score2)




@app.route("/lesson3", methods=["GET", "POST"])
@login_required
def lesson3_page():
    
   

    return render_template("lesson3.html")

@app.route("/quizz3", methods=["GET", "POST"])
@login_required
def quizz3():
    db = get_db()
    user_id = session.get("user_id")
    if "copylesson3" not in session:
        session["copylesson3"] = lesson3.copy()

    copylesson3 = session["copylesson3"]


    # Initialisation des variables de session pour le score et la taille du test
    if "score" not in session:
        session["score"] = 0
    if "test_size" not in session:
        session["test_size"] = 0

    score3 = session["score"]
    test_size = session["test_size"]


    if request.method == "POST":
        selected_answer = request.form.get("choice")  # Réponse sélectionnée par l'utilisateur
        question = session.get("question")  # Question en cours (la clé correcte)
        if not selected_answer:
            logger.error("user didnt select an answer")
            
            return redirect("/quizz3")


        # Vérifie si la réponse est correcte
        if selected_answer.strip().lower() == question.strip().lower():
            score3 += 1  # Incrémente le score si la réponse est correcte
        test_size += 1  # Incrémente le compteur de questions posées

        session["score"] = score3
        session["test_size"] = test_size
        copylesson3.pop(question)


        # Si 10 questions ont été posées, enregistrer le score final et rediriger
        if test_size >= 10 or not copylesson3:
            try:
                db.execute(
                    "INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",
                    (user_id, "quizz3", score3),
                )
                db.commit()
                logger.info("score registered succesfully")
            
            except Exception as e:
                logger.error(f"Error while recording score: {e}")


            try: 
                session["final_score"] = score3
                session.pop("score")  # Réinitialise le score
                session.pop("test_size")  # Réinitialise le compteur de questions
                session.pop("copylesson3")  # Réinitialise le quiz
                session.pop("question")  # Réinitialise la question en cours
                logger.info("session reset sucessful")
                

                return redirect("/score")
        
            except Exception as e:
                logger.error(f"Error while Resetting session: {e}")


    # Si on est en GET (nouvelle question)
    if not copylesson3:
        logger.warning("Quizz was not reset properly")
        
        
        return redirect("/score")
    question = random.choice(list(copylesson3.keys()))  # La bonne réponse est la clé
    french = lesson3[question]["french_sentence"]  # Phrase en français
    english = lesson3[question]["english_sentence"]  # Phrase en anglais
    session["question"] = question

    # Génère deux autres choix incorrects aléatoires
    remaining_keys = [key for key in lesson3.keys() if key != question]
    if len(remaining_keys) < 2:
        logger.warning("Quizz was not reset properly")
        return redirect("/score")

    other_choices = random.sample(remaining_keys, 2)

    # Réponses possibles, mélangées aléatoirement
    answers = [question, other_choices[0], other_choices[1]]
    random.shuffle(answers)

    # Affiche la question et les réponses à l'utilisateur
    return render_template(
        "quizz3.html",
        question=question,
        answers=answers,
        score=score3,
        french=french,
        english=english,
    )



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
    db = get_db()
    user_id = session.get("user_id")
    
    # Initialisation de `copylesson2` en début de fonction
    if "copylesson4" not in session:
        session["copylesson4"] = lesson4.copy()

    copylesson4 = session["copylesson4"]

    # Initialisation des variables de session pour le score et la taille du test
    if "score" not in session:
        session["score"] = 0
    if "test_size" not in session:
        session["test_size"] = 0

    score4= session["score"]
    test_size = session["test_size"]

    if request.method == "POST":
        selected_answer = request.form.get("choice")  # Réponse sélectionnée par l'utilisateur
        question = session.get("question")  # Question en cours
        if not selected_answer:
            logger.error("user didnt select an answer")
            
            return redirect("/quizz4")

        # Vérifie si la réponse est correcte
        correct_answer = lesson4[question]["translation"]
        if selected_answer.strip().lower() == correct_answer.strip().lower():
            score4 += 1  # Incrémente le score
        test_size += 1  # Incrémente le nombre de questions posées

        session["score"] = score4
        session["test_size"] = test_size

        # Retire la question actuelle de `copylesson2`
        copylesson4.pop(question)

        # Vérifie si 10 questions ont été posées ou s'il n'y a plus de questions
        if test_size >= 10 or not copylesson4:
            db.execute(
                "INSERT INTO quiz_results (user_id, quiz_name, score) VALUES (?, ?, ?)",
                (user_id, "quizz4", score4),
            )
            db.commit()

            session["final_score"] = score4
            session.pop("score")  # Réinitialise le score
            session.pop("test_size")  # Réinitialise le compteur de questions
            session.pop("copylesson4")  # Réinitialise `copylesson2`

            logger.info("Score enregistré dans la base de données avec succès")
            return redirect("/score")

    # Si on est en GET (nouvelle question)
    if not copylesson4:
        logger.warning("Aucune question restante pour ce quiz.")
        return redirect("/score")

    question = random.choice(list(copylesson4.keys()))
    session["question"] = question

    # Génère deux autres choix incorrects aléatoires
    remaining_keys = [key for key in lesson4.keys() if key != question]
    if len(remaining_keys) < 2:
        logger.warning("Pas assez de choix incorrects disponibles.")
        return redirect("/score")

    other_choices = random.sample(remaining_keys, 2)

    # Réponses possibles, mélangées aléatoirement
    correct_answer = lesson4[question]["translation"]
    answers = [
        correct_answer,
        lesson4[other_choices[0]]["translation"],
        lesson4[other_choices[1]]["translation"],
    ]
    random.shuffle(answers)

    # Affiche la question et les réponses à l'utilisateur
    return render_template("quizz4.html", question=question, answers=answers, score=score4)

@app.route("/score", methods=["GET", "POST"])

def score():
         

    score=session["final_score"]
    
   

    return render_template("score.html",score=score)

















        


    


    

