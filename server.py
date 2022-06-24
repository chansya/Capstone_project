
from calendar import week
from unittest import result
from flask import Flask, jsonify, render_template, render_template_string, request, flash, session, redirect
from model import connect_to_db, db, User, Habit, Record, Badge
from datetime import datetime, timedelta
import os
import cloudinary.uploader
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key= os.environ['secret_key']

app.jinja_env.undefined = StrictUndefined


CLOUDINARY_KEY = os.environ['CLOUDINARY_KEY']
CLOUDINARY_SECRET = os.environ['CLOUDINARY_SECRET']
CLOUD_NAME = "habittracking"


@app.route("/")
def index():
    """View homepage"""
    if session.get("user_email"):
        return redirect("/progress")
    
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """View login page and process login."""
    error = None
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.get_by_email(email)
        # if login fail, redirect back to login with error message
        if not user or user.password != password:
            error = "Invalid email/password. Please try again."
        
        session["user_email"] = user.email
        session.modified = True
        return redirect("/progress")

    return render_template('login.html', error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Create a new user."""
    if request.method == 'POST':
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
            session.modified = True
            
            # Create badge 1 for sign up
            badge1 = Badge.create(user.user_id, "static/img/1.png", "Welcome", "Register an account")
            db.session.add(badge1)
            db.session.commit()
            flash("You've earned a badge! You can see it under your profile.")
            return redirect("/progress")

    return render_template('signup.html')


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
            Habit.update_curr_streak(habit.habit_id)
            Habit.update_max_streak(habit.habit_id)

        # populate events list for calendar 
        events = [{'title': f"{record.habit.habit_name.capitalize()}",
                'start': f"{record.record_date}"} for record in record_lst]
        daily_habits = Habit.query.filter(Habit.time_period=="daily", Habit.user_id==user.user_id).all()
        weekly_habits = Habit.query.filter(Habit.time_period=="weekly", Habit.user_id==user.user_id).all()
        monthly_habits = Habit.query.filter(Habit.time_period=="monthly", Habit.user_id==user.user_id).all()

        return render_template("progress.html", user=user, habits=habits, events=events,
                                daily_habits=daily_habits,weekly_habits=weekly_habits, monthly_habits=monthly_habits)
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
    reminder = request.json.get("reminder")
    current_streak = 0
    max_streak = 0
    user = User.get_by_email(session.get("user_email"))

    # create new habit object in database
    habit = Habit.create(user.user_id, habit_name, frequency,
                         time_period, current_streak, max_streak,
                         start_date, reminder)
    db.session.add(habit)
    db.session.commit()

    # Reward badges for creating habits

    # Check for any existing badge 2 to avoid duplicate
    badge2 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/2.png").first()
    if Habit.count_habit_by_user(user.user_id) == 1 and badge2 == None:
        # Create badge 2 for first habit
        badge2 = Badge.create(user.user_id, "static/img/2.png", "First Goal", "Create first habit")
        db.session.add(badge2)
        db.session.commit()
        flash("You've created your first habit and earned a badge!")

    # Check for any existing badge 4 to avoid duplicate
    badge4 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/4.png").first()

    if Habit.count_habit_by_user(user.user_id) == 3 and badge4 == None:
        # create badge 4 for third habits
        badge4 = Badge.create(user.user_id, "static/img/4.png", "Multi-tasker", "Create 3 habits")
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


@app.route("/create_record", methods=["POST"])
def create_record():
    """Create a record for a habit and add to database."""
    habit_id = request.form.get("log-habit")
    notes = request.form.get("log-notes")
    record_date = datetime.strptime(
        request.form.get("log-date"),
        '%Y-%m-%d')
    photo = request.files["log-photo"]
    finished = True

    if photo:
        # make API request to save uploaded image to Cloudinary
        result = cloudinary.uploader.upload(photo, 
                                            api_key=CLOUDINARY_KEY,
                                            api_secret=CLOUDINARY_SECRET,
                                            cloud_name=CLOUD_NAME)
        # url for the uploaded image
        img_url = result['secure_url']
    else:
        img_url=""

    # Create new record object
    record = Record.create(habit_id, finished, notes, img_url, record_date)
    db.session.add(record)
    db.session.commit()
    
    # update streak based on record
    # Habit.update_curr_streak(habit_id)
    # Habit.update_max_streak(habit_id)

    # Create badges according to number of records
    user = User.get_by_email(session["user_email"])
    habits = Habit.get_by_user(user.user_id)
    record_count = 0
    for habit in habits:
        record_count +=  Record.count_records_by_habit(habit.habit_id)
    
    # Check for any existing badges to avoid duplicate
    badge3 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/3.png").first()
    badge5 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/5.png").first()
    badge6 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/6.png").first()
                                

    if record_count == 1 and badge3 == None:
        badge3 = Badge.create(user.user_id, "static/img/3.png", "From 0 To 1", "Create first record")
        db.session.add(badge3)
        db.session.commit()
        flash("You've created your first record and earned a badge!")

    if record_count == 5 and badge5 == None:
        badge5 = Badge.create(user.user_id, "static/img/5.png", "5-Star Records", "Create 5 records")
        db.session.add(badge5)
        db.session.commit()
        flash("You've created your 5 records and earned a badge!")
    
    if record_count == 10 and badge6 == None:
        badge6 = Badge.create(user.user_id, "static/img/6.png", "Perfect 10", "Create 10 records")
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
    user = User.get_by_email(session["user_email"])
    badges = Badge.get_by_user(user.user_id)
    return render_template("all_badges.html", user=user, badges=badges)


@app.route("/chart_data.json")
def get_daily_habit_data():
    """Get daily habit data as JSON."""

    # get user
    user = User.get_by_email(session.get("user_email"))
    habits = Habit.get_by_user(user.user_id)
    # get habit id list
    
    daily_habit_dict = {}

    # for loop to go through each habit, make dict of habit
    for habit in habits:
   
        daily_record_data = []
        counted_days=[]
        # list of all records sorted by date
        records = Record.query.filter(Record.habit_id==habit.habit_id).order_by(Record.record_date.desc()).all()

        # loop over records to generate dictionary ro append to json data list
        for record in records:
            if record.record_date not in counted_days:
                # count number of times done
                times_done = Record.query.filter(Record.habit_id==habit.habit_id,
                                                Record.record_date== record.record_date).count()
                # dictionary for each record date
                daily_record_data.append({'date': record.record_date.isoformat(),
                                        'times_done':times_done})
                # to avoid duplicate dates
                counted_days.append(record.record_date)
     

        daily_habit_dict[habit.habit_name] = daily_record_data
     
    return jsonify(daily_habit_dict)

@app.route("/logout")
def process_logout():
    """Log user out and clear the session."""
    del session["user_email"]
    return redirect("/")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
