
from flask import Flask, jsonify, render_template, render_template_string, request, flash, session, redirect
from model import connect_to_db, db, User, Habit, Record, Badge
from datetime import datetime
import os
import requests
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key= os.environ['secret_key']

app.jinja_env.undefined = StrictUndefined

API_KEY = os.environ['FLATICON_KEY']



@app.route("/")
def index():
    """View homepage"""

    if session.get("user_email"):
        return redirect("/progress")
    else:
        return render_template('index.html')


# @app.route("/login")
# def login():
#     """View login page."""
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.get_by_email(email)
        # if login fail, redirect back to /login
        if not user or user.password != password:
            error = "Invalid email/password. Please try again."
        else:
            # Log in user by storing the user's email in session
            session["user_email"] = user.email
            session.modified = True
            return redirect("/progress")

    return render_template('login.html', error=error)

# @app.route("/process_login", methods=["POST"])
# def process_login():
#     """Verify user's login credentials."""

#     email = request.form.get("email")
#     password = request.form.get("password")

#     user = User.get_by_email(email)
#     # if login fail, redirect back to /login
#     if not user or user.password != password:
#         fail_msg = "The email or password you entered was incorrect."
#         return redirect("/login")
#     else:
#         # Log in user by storing the user's email in session
#         session["user_email"] = user.email
#         session.modified = True
#         return redirect("/progress")


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

    user = User.get_by_email(email)
    if user:
        flash("Email already exists. Please log in.")
        return redirect("/login")
    else:
        user = User.create(name, email, password)
        db.session.add(user)
        db.session.commit()
        session["user_email"] = user.email
        # flash(f"Account created. Welcome, {user.name}!")
        session.modified = True
        
        # Create badge 1 for sign up
        badge1 = Badge.create(user.user_id, "static/img/1.png", "Welcome")
        db.session.add(badge1)
        db.session.commit()
        flash("You've earned a badge! You can see it under your profile.")
        return redirect("/progress")


@app.route("/progress")
def view_progress():
    """View the progress page."""
    user = User.get_by_email(session["user_email"])
    if user:
        habits = Habit.get_by_user(user.user_id)

        # loop over habit list to generate record list
        record_lst = []
        for habit in habits:
            records = Record.get_by_habit(habit.habit_id)
            record_lst += records

        events = [{'title': f"{record.habit.habit_name.capitalize()}",
                'start': f"{record.record_date}"} for record in record_lst]
    
        return render_template("progress.html", user=user, habits=habits, events=events)
    else:
        return redirect('/')


@app.route("/calendar")
def view_calendar():
    """View the calendar page."""

    # get list of habits for user
    user = User.get_by_email(session.get("user_email"))
    habits = Habit.get_by_user(user.user_id)

    # loop over habit list to generate record list
    record_lst = []
    for habit in habits:
        records = Record.get_by_habit(habit.habit_id)
        record_lst += records

    events = [{'title': f"{record.habit.habit_name.capitalize()}",
                'start': f"{record.record_date}"} for record in record_lst]
    
    return render_template("calendar.html", events=events)


@app.route("/create_habit", methods=["POST"])
def create_habit():
    """Create new habit object and add into database."""

    # extract the user input from the request
    habit_name = request.json.get("habit_name").capitalize()
    frequency = request.json.get("frequency")
    time_period = request.json.get("time_period")
    start_date = datetime.strptime(
        request.json.get("start_date"),
        '%Y-%m-%d')
    current_streak = 0
    max_streak = 0
    user = User.get_by_email(session.get("user_email"))

    # create new habit object in database
    habit = Habit.create(user.user_id, habit_name, frequency,
                         time_period, current_streak, max_streak, start_date)
    db.session.add(habit)
    db.session.commit()

    # reward badges for creating habits
    
    if Habit.count_habit_by_user(user.user_id) == 1 and Badge.count_badge_by_user(user.user_id) == 1:
        # create badge 2 for first habit
        badge2 = Badge.create(user.user_id, "static/img/2.png", "First Goal")
        db.session.add(badge2)
        db.session.commit()
        flash("You've created your first habit and earned a badge!")

    # Check for any existing badge 4 to avoid duplicate
    badge4 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/4.png").first()

    if Habit.count_habit_by_user(user.user_id) == 3 and badge4 == None:
        # create badge 4 for third habits
        badge4 = Badge.create(user.user_id, "static/img/4.png", "Multi-tasker")
        db.session.add(badge4)
        db.session.commit()
        flash("You've created your three habits and earned a badge!")

    # put information in dictionary to send back as json response
    habit_to_send = {"habit_id": habit.habit_id,
                     "habit_name": habit.habit_name,
                     "current_streak": habit.current_streak,
                     "max_streak": habit.max_streak,
                     "frequency": habit.frequency,
                     "time_period": habit.time_period,
                     "start_date": habit.start_date,
                     }
    return jsonify(habit_to_send)


@app.route("/create_modal_record")
def create_modal_record():
    """Create a record for a habit and add to database."""
    habit_id = request.args.get("modal-habit")
    notes = request.args.get("modal-notes")
    record_date = datetime.strptime(
        request.args.get("modal-date"),
        '%Y-%m-%d')
    finished = True

    # Create new record object
    record = Record.create(habit_id, finished, notes, record_date)
    db.session.add(record)
    db.session.commit()
    
    # Create badges according to number of records
    user = User.get_by_email(session["user_email"])
    habits = Habit.get_by_user(user.user_id)
    record_count = 0
    for habit in habits:
        record_count +=  Record.count_records_by_habit(habit.habit_id)
    
    # Check for any existing badge 4 to avoid duplicate
    badge3 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/3.png").first()
    badge5 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/5.png").first()
    badge6 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/6.png").first()
                                

    if record_count == 1 and badge3 == None:
        badge3 = Badge.create(user.user_id, "static/img/3.png", "From 0 To 1")
        db.session.add(badge3)
        db.session.commit()
        flash("You've created your first record and earned a badge!")

    if record_count == 5 and badge5 == None:
        badge5 = Badge.create(user.user_id, "static/img/5.png", "5-Star Records")
        db.session.add(badge5)
        db.session.commit()
        flash("You've created your 5 records and earned a badge!")
    
    if record_count == 10 and badge6 == None:
        badge6 = Badge.create(user.user_id, "static/img/6.png", "10/10")
        db.session.add(badge6)
        db.session.commit()
        flash("You've created your 10 records and earned a badge!")


    return redirect("/progress")


@app.route("/all_habits")
def view_habits():
    """View a list of habits for a user."""
    user = User.get_by_email(session.get("user_email"))
    habits = Habit.get_by_user(user.user_id)
    return render_template("all_habits.html", user=user, habits=habits)


@app.route("/<habit_id>/remove_habit")
def remove_habit(habit_id):
    """Remove a habit and all its related records."""
    Record.query.filter_by(habit_id=habit_id).delete()
    habit = Habit.get_by_id(habit_id)
    db.session.delete(habit)
    db.session.commit()

    return redirect('/all_habits')


@app.route("/<habit_id>/records")
def view_records(habit_id):
    """View all records for a habit."""
    user = User.get_by_email(session["user_email"])
    habit = Habit.get_by_id(habit_id)
    records = Record.get_by_habit(habit_id)
    return render_template("all_records.html", user=user, habit=habit, records=records)


@app.route("/<record_id>/remove_record")
def remove_record(record_id):
    """Remove a record."""
    record = Record.get_by_id(record_id)
    habit_id = record.habit.habit_id
    db.session.delete(record)
    db.session.commit()

    return redirect(f"/{habit_id}/records")


@app.route("/all_badges")
def view_badges():
    """View all the badges for a user."""
    user = User.get_by_email(session.get("user_email"))
    badges = Badge.get_by_user(user.user_id)
    return render_template("all_badges.html", user=user, badges=badges)


@app.route("/logout")
def process_logout():
    """Log user out and clear the session."""
    del session["user_email"]
    return redirect("/")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
