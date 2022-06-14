
# from pydoc import render_doc
from unicodedata import name
from flask import Flask, jsonify, render_template, request, flash, session, redirect
from model import connect_to_db, db, User, Habit, Record, Badge
from datetime import datetime
from jinja2 import StrictUndefined


app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

@app.route("/")
def index():
    """View homepage"""

    if session.get("user_email"):
        return redirect("/progress")
    else:
        return render_template('index.html')


@app.route("/login")
def login():
    """View login page."""
    return render_template('login.html')

@app.route("/verify_login",methods=["POST"])
def verify_login():
    """Verify user's login credentials."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.get_by_email(email)
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
        return redirect("/login")
    else:
        # Log in user by storing the user's email in session
        session["user_email"] = user.email
        flash(f"Welcome back, {user.name}!")
        return redirect("/progress")
        
@app.route("/signup")
def signup():
    """View signup page."""
    return render_template('signup.html')

@app.route("/create_account", methods=["POST"])
def create_account():
    """Create a new user."""
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_pw = request.form.get("confirm_pw")
    
    user = User.get_by_email(email)
    if user:
        flash("Email already exists. Please log in.")
        return redirect("/signup")
    else:
        user = User.create(name, email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")
        return redirect("/login")

@app.route("/progress")
def view_progress():
    """View the progress page."""
    user = User.get_by_email(session["user_email"])
    habits = Habit.get_by_user(user.user_id)
    return render_template("progress.html", user=user, habits=habits)


@app.route("/new_habit")
def new_habit():
    return render_template("new_habit.html")


@app.route("/create_habit", methods = ["POST"])
def create_habit():
    """Create new habit object and add into database."""
    
    # extract the input from the request
    habit_name = request.json.get("habit_name")
    frequency = request.json.get("frequency")
    time_period = request.json.get("time_period")
    start_date  = datetime.strptime(
                     request.json.get("start_date"),
                     '%Y-%m-%d')
    
    current_streak = 0
    max_streak = 0
    
    user = User.get_by_email(session.get("user_email"))
    # create new habit object
    habit = Habit.create(user.user_id, habit_name,frequency,time_period,current_streak,max_streak, start_date)
    db.session.add(habit)
    db.session.commit()
    flash("Habit created!")
   
    habits = Habit.get_by_user(user.user_id)

    return {"success": True,
            "status": f"{habit.habit_name} has been added"}


# @app.route("/create_record")
# def create_record():
#     return render_template("/progress")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)