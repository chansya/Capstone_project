
from calendar import week
import json
from math import remainder
from unittest import result
from flask import Flask, jsonify, render_template, request, flash, session, redirect
from model import connect_to_db, db, User, Habit, Record, Badge
from datetime import datetime, timedelta
import os
import requests
from passlib.hash import argon2
import cloudinary.uploader
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = os.environ['secret_key']
app.jinja_env.undefined = StrictUndefined


CLOUDINARY_KEY = os.environ['CLOUDINARY_KEY']
CLOUDINARY_SECRET = os.environ['CLOUDINARY_SECRET']
CLOUD_NAME = "habittracking"


@app.route("/")
def index():
    """View homepage."""

    if session.get("user_email"):
        return redirect("/progress")

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """View login page and process login."""

    error = None

    if request.method == 'POST':
        email = request.form.get("email")
        attempt_pw = request.form.get("password")

        user = User.get_by_email(email)
        # if login fail, redirect back to login with error message
        if not user:
            error = "Invalid email. Please try again."
            return render_template('login.html', error=error)
        else:
            hashed_pw = user.password
            pw_matched = argon2.verify(attempt_pw, hashed_pw)
            if not pw_matched:
                error = "Invalid password. Please try again."
                return render_template('login.html', error=error)

        session["user_email"] = user.email

        # Check for missed entries
        user = User.get_by_email(session["user_email"])
        habits = user.habits

        missed_entries = ""
        for habit in habits:
            Habit.update_curr_streak(habit.habit_id)
            if habit.current_streak == 0 and Record.query.filter(Record.habit_id == habit.habit_id).count() > 0:
                missed_entries += f" {habit.habit_name}, "
        # Create flash message reminder
        if missed_entries != "":
            flash(
                f"Welcome back! There seems to be missed entries for {missed_entries} remember to log it if you haven't yet!")
        else:
            flash(f"Welcome back {user.name}! How is it going?")
        return redirect("/progress")

    return render_template('login.html', error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Create a new user."""

    if request.method == 'POST':
        error = None
        name = request.form.get("name").capitalize()
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_pw = argon2.hash(password)

        user = User.get_by_email(email)
        if user:
            error = "Email already exists. Please log in."
            return render_template('login.html', error=error)
        else:
            user = User.create(name, email, hashed_pw)
            db.session.add(user)
            db.session.commit()
            session["user_email"] = user.email

            # Create potential badges for users
            badge_names = ["Our New Star", "First Step", "From 0 To 1", "Multi-tasker",
                           "5-Star Records", "Perfect 10", "Up We go", "Unstoppable", "Streak Master"]
            badge_msg = ["Register an account", "Create first habit", "Create first record", "Create 3 habits",
                         "Create 5 records", "Create 10 records", "Reach 7 streaks", "Reach 30 streaks", "Reach 100 streak"]

            for i in range(1, 10):
                badge = Badge.create(
                    user.user_id, f"static/img/Badges_img/{i}bw.png", badge_names[i-1], badge_msg[i-1])
                db.session.add(badge)
                db.session.commit()

            # Activate badge 1
            badge1 = Badge.query.filter(Badge.user_id == user.user_id,
                                        Badge.img_url == "static/img/Badges_img/1bw.png").first()
            badge1.img_url = "static/img/Badges_img/1.png"
            db.session.commit()
            flash(
                "Yay! You've earned a badge for creating an account! Check it out under your profile.")
            return redirect("/progress")

    return render_template('signup.html')


@app.route("/progress")
def view_progress():
    """View the progress page."""

    user = User.get_by_email(session["user_email"])
    if user:

        habits = user.habits

        badges = Badge.query.filter(
            Badge.user_id == user.user_id).order_by(Badge.img_url).all()

        # Populate event list from the records for calendar
        events = []  
        habit_colors = ['#c5dedd', '#bcd4e6', '#fad2e1', '#eddcd2', '#cddafd',
                        '#f0efeb', '#dbe7e4', '#d6e2e9', '#fde2e4', '#dfe7fd']
        for i, habit in enumerate(habits):
            records = Record.get_by_habit(habit.habit_id)
            for record in records:
                events.append({
                    'id': f"{record.habit.habit_id}",
                    'title': f"{record.habit.habit_name}",
                    'start': f"{record.record_date}",
                    'color': habit_colors[i]})

            Habit.update_curr_streak(habit.habit_id)
            Habit.update_max_streak(habit.habit_id)

        # Populate lists of daily/weekly/monthly habits to update Overview
        daily_habits = Habit.query.filter(Habit.time_period == "daily",
                                          Habit.user_id == user.user_id).all()
        weekly_habits = Habit.query.filter(Habit.time_period == "weekly",
                                           Habit.user_id == user.user_id).all()
        monthly_habits = Habit.query.filter(Habit.time_period == "monthly",
                                            Habit.user_id == user.user_id).all()

        # Get 3 most recent records to update Recent Log
        recent_recs = Record.query.join(Habit).filter(
            Habit.user_id == user.user_id).order_by(Record.record_date.desc()).limit(3)

        return render_template("progress.html", user=user, habits=habits, events=events,
                               daily_habits=daily_habits, weekly_habits=weekly_habits,
                               monthly_habits=monthly_habits, recent_recs=recent_recs, badges=badges)
    else:
        return redirect('/')


@app.route("/create_habit", methods=["POST"])
def create_habit():
    """Create new habit object and update database."""

    # Extract the user inputs from the post request
    habit_name = request.form.get("habit_name").capitalize()
    frequency = request.form.get("frequency")
    time_period = request.form.get("time_period")
    # start_date = datetime.strptime(request.json.get("start_date"),
    #                                '%Y-%m-%d')
    reminder = request.form.get("reminder")
    current_streak = 0
    max_streak = 0
    user = User.get_by_email(session.get("user_email"))

    # create new habit object in database
    habit = Habit.create(user.user_id, habit_name, frequency,
                         time_period, current_streak, max_streak, reminder)
    db.session.add(habit)
    db.session.commit()

    # Reward badges for creating habits

    # Check for any existing badge 2 to avoid duplicate
    badge2 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/2bw.png").first()
    if Habit.count_habit_by_user(user.user_id) == 1 and badge2:
        # Activate badge 2 for first habit
        badge2.img_url = "static/img/Badges_img/2.png"
        db.session.commit()
        flash("Awesome! You've created your first habit and earned a badge!")

    # Check for any existing badge 4 to avoid duplicate
    badge4 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/4bw.png").first()

    if Habit.count_habit_by_user(user.user_id) == 3 and badge4:
        # Activate badge 4 for third habits
        badge4.img_url = "static/img/Badges_img/4.png"
        db.session.commit()
        flash("Wow! You've created your three habits and earned a badge!")

    return redirect("/progress")


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
        img_url = "static/img/Record_img/thumbsUp.jpg"

    # Create new record object
    record = Record.create(habit_id, finished, notes, img_url, record_date)
    db.session.add(record)
    db.session.commit()

    # Create badges according to number of records
    user = User.get_by_email(session["user_email"])
    habits = Habit.get_by_user(user.user_id)
    record_count = 0
    badge7 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/7bw.png").first()
    badge8 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/8bw.png").first()
    badge9 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/9bw.png").first()
    for habit in habits:
        record_count += Record.count_records_by_habit(habit.habit_id)
        Habit.update_curr_streak(habit.habit_id)
        Habit.update_max_streak(habit.habit_id)
        if habit.max_streak == 7 and badge7:
            badge7.img_url = "static/img/Badges_img/7.png"
            db.session.commit()
            flash("Wonderful! You've reached 7 streaks and earned a badge!")
        elif habit.max_streak == 30 and badge8:
            badge7.img_url = "static/img/Badges_img/8.png"
            db.session.commit()
            flash("Dope! You've reached 30 streaks and earned a badge!")

        elif habit.max_streak == 100 and badge9:
            badge7.img_url = "static/img/Badges_img/9.png"
            db.session.commit()
            flash("Is that real!? You've reached 100 streaks and earned a badge!")

    # Check for any existing badges to avoid duplicate
    badge3 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/3bw.png").first()
    badge5 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/5bw.png").first()
    badge6 = Badge.query.filter(Badge.user_id == user.user_id,
                                Badge.img_url == "static/img/Badges_img/6bw.png").first()

    # Activate badges
    if record_count == 1 and badge3:
        badge3.img_url = "static/img/Badges_img/3.png"
        db.session.commit()
        flash("Nice! You've created your first record and earned a badge!")

    if record_count == 5 and badge5:
        badge5.img_url = "static/img/Badges_img/5.png"
        db.session.commit()
        flash("Amazing! You've created your 5 records and earned a badge!")

    if record_count == 10 and badge6:
        badge6.img_url = "static/img/Badges_img/6.png"
        db.session.commit()
        flash("Spectacular! You've created your 10 records and earned a badge!")

    return redirect("/progress")


@app.route("/manage")
def view_profile():
    """View the user's profile."""
     
    user = User.get_by_email(session["user_email"])
    habits = user.habits
    badges = Badge.query.filter(
        Badge.user_id == user.user_id).order_by(Badge.img_url).all()
    return render_template("profile.html", user=user, habits=habits, badges=badges)


@app.route("/change_pw", methods=['POST'])
def change_password():
    """Change user's password. """
    user = User.get_by_email(session["user_email"])
    new_pw = request.json['new_pw']
    hashed_pw = argon2.hash(new_pw)
    user.password = hashed_pw
    db.session.commit()

    return jsonify({'status': 'success'})


@app.route("/records")
def view_habits():
    """View all records."""

    user = User.get_by_email(session["user_email"])
    habits = Habit.get_by_user(user.user_id)
    badges = Badge.query.filter(
        Badge.user_id == user.user_id).order_by(Badge.img_url).all()

    return render_template("records.html", user=user, habits=habits, badges=badges)


@app.route("/habits.json")
def get_all_habits():
    """Return a list of all habits as JSON."""

    user = User.get_by_email(session.get("user_email"))
    habits = Habit.get_by_user(user.user_id)
    habits_to_send = []
    for habit in habits:
        habits_to_send.append(
            {"habit_id": habit.habit_id,
             "habit_name": habit.habit_name,
             "frequency": habit.frequency,
             "time_period": habit.time_period,
             "current_streak": habit.current_streak,
             "max_streak": habit.max_streak,
             "reminder": habit.reminder
             })

    return jsonify({"habits": habits_to_send})


@app.route("/records.json")
def get_all_records():
    """Return a list of all records as JSON."""

    user = User.get_by_email(session.get("user_email"))

    user_recs = Record.query.join(Habit).filter(
        Habit.user_id == user.user_id).order_by(Record.record_date.desc()).all()
    records_to_send = []
    for record in user_recs:
        records_to_send.append(
            {'habit_name': record.habit.habit_name,
             'record_id': record.record_id,
             'notes': record.notes,
             'img_url': record.img_url,
             'record_date': datetime.strftime(record.record_date, '%Y-%m-%d')})

    return jsonify({"records": records_to_send})


@app.route("/remove_habit/<habit_id>")
def remove_habit(habit_id):
    """Remove a habit and all its related records."""

    Record.query.filter_by(habit_id=habit_id).delete()
    habit = Habit.get_by_id(habit_id)
    db.session.delete(habit)
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route("/remove_record/<record_id>")
def remove_record(record_id):
    """Remove a records."""

    record = Record.get_by_id(record_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route("/<habit_id>/records")
def get_habit_records(habit_id):
    """Return a list of records for a habit as JSON. """

    habit = Habit.get_by_id(habit_id)
    records = Record.query.filter(Record.habit_id == habit_id).order_by(
        Record.record_date.desc()).all()

    records_to_send = []
    for record in records:
        records_to_send.append(
            {'habit_name': habit.habit_name,
             'record_id': record.record_id,
             'notes': record.notes,
             'img_url': record.img_url,
             'record_date': datetime.strftime(record.record_date, '%Y-%m-%d')})

    return jsonify({'records': records_to_send})


@app.route("/chart_data.json")
def get_chart_data():
    """Get record data for chart as JSON."""

    user = User.get_by_email(session.get("user_email"))
    habits = user.habits
    
    # make a dictionary with habit name as key and record data list as value
    habit_dict = {}

    for habit in habits:

        record_list = []
        counted_days = []
        records = Record.query.filter(Record.habit_id == habit.habit_id).order_by(
            Record.record_date.desc()).all()

        # loop over records to populate the record data list
        for record in records:
            if record.record_date not in counted_days:
                # count number of times done
                times_done = Record.query.filter(Record.habit_id == habit.habit_id,
                                                 Record.record_date == record.record_date).count()
                # dictionary for each record date
                record_list.append({'date': record.record_date.isoformat(),
                                          'times_done': times_done})
                # to avoid duplicate dates
                counted_days.append(record.record_date)

        habit_dict[habit.habit_name] = record_list

    return jsonify(habit_dict)


@app.route("/api/quotes")
def get_quotes():
    """Return daily quote from API call."""

    url = 'https://zenquotes.io/api/today'
    headers = {'content-type': 'application/json'}
    res_obj = requests.get(url, headers=headers)
    quotes = res_obj.json()

    return jsonify(quotes)


@app.route("/logout")
def process_logout():
    """Log user out and clear the session."""

    del session["user_email"]
    return redirect("/")


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
