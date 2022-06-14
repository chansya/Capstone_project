
# from pydoc import render_doc
from unicodedata import name
from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db, User, Habit, Record, Badge
from datetime import datetime
from jinja2 import StrictUndefined


app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

@app.route("/")
def index():
    """View homepage"""
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
    return render_template("progress.html")

@app.route("/create_habit", methods = ["POST"])
def create_habit():
    # get the input from form
    habit_name = request.form.get("habit_name")
    frequency = request.form.get("frequency")
    time_period = request.form.get("time_period")
    start_date  = datetime.strptime(
                     request.form['start_date'],
                     '%Y-%m-%d')
    
    current_streak = 0
    max_streak = 0

    user = User.get_by_email(session.get("user_email"))
    
    habit = Habit.create(user.user_id, habit_name,frequency,time_period,current_streak,max_streak, start_date)
    db.session.add(habit)
    db.session.commit()
    flash("Habit created!")
    # create new habit
    habits = Habit.all_habits()
    
    return render_template("progress.html", habits = habits)

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)