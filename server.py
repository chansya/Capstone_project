
from calendar import week
from math import remainder
from unittest import result
from flask import Flask, jsonify, render_template, render_template_string, request, flash, session, redirect
from model import connect_to_db, db, User, Habit, Record, Badge
from datetime import datetime, timedelta
import os
from passlib.hash import argon2
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
            if habit.current_streak==0 and Record.query.filter(Record.habit_id==habit.habit_id).count()>0:
                missed_entries+= f" {habit.habit_name}, "
        # Create flash message reminder
        if missed_entries != "":
            flash(f"There seems to be missed entries for {missed_entries} did you forget to log it?")
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
        print(hashed_pw)

        user = User.get_by_email(email)
        if user:
            error = "Email already exists. Please log in."
            return render_template('login.html', error=error)
        else:
            user = User.create(name, email, hashed_pw)
            db.session.add(user)
            db.session.commit()
            session["user_email"] = user.email
            
            # Create badge 1 for sign up
            badge1 = Badge.create(user.user_id, "static/img/1.png", "Our New Star", "Register an account")
            badge2 = Badge.create(user.user_id, "static/img/2bw.png", "First Step", "Create first habit")
            badge3 = Badge.create(user.user_id, "static/img/3bw.png", "From 0 To 1", "Create first record")
            badge4 = Badge.create(user.user_id, "static/img/4bw.png", "Multi-tasker", "Create 3 habits")
            badge5 = Badge.create(user.user_id, "static/img/5bw.png", "5-Star Records", "Create 5 records")
            badge6 = Badge.create(user.user_id, "static/img/6bw.png", "Perfect 10", "Create 10 records")
            badge7 = Badge.create(user.user_id, "static/img/7bw.png", "Up We go", "Reach 7 streaks")
            badge8 = Badge.create(user.user_id, "static/img/8bw.png", "Unstoppable", "Reach 30 streaks")
            badge9 = Badge.create(user.user_id, "static/img/9bw.png", "Streak Master", "Reach 100 streak")
            
            
            db.session.add(badge1)
            db.session.add(badge2)
            db.session.add(badge3)
            db.session.add(badge4)
            db.session.add(badge5)
            db.session.add(badge6)
            db.session.add(badge7)
            db.session.add(badge8)
            db.session.add(badge9)
            db.session.commit()
            flash("Yay! You've earned a badge for creating an account! Check it under your profile.")
            return redirect("/progress")

    return render_template('signup.html')


@app.route("/progress")
def view_progress():
    """View the progress page."""
    user = User.get_by_email(session["user_email"])
    if user:
        
        habits = user.habits
        # habits = Habit.query.filter(Habit.user_id==user.user_id).order_by(Habit.habit_id.asc()).all()
        
        badges = Badge.query.filter(Badge.user_id==user.user_id).order_by(Badge.img_url).all()
   
        # loop over habit list to populate event list for calendar
        events = []
        habit_colors = ['#c5dedd','#bcd4e6','#fad2e1','#eddcd2','#cddafd',
                '#f0efeb','#dbe7e4','#d6e2e9','#fde2e4','#dfe7fd']
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

        # Get list of daily/weekly/monthly habits to update Overview
        daily_habits = Habit.query.filter(Habit.time_period=="daily", 
                                          Habit.user_id==user.user_id).all()
        weekly_habits = Habit.query.filter(Habit.time_period=="weekly", 
                                           Habit.user_id==user.user_id).all()
        monthly_habits = Habit.query.filter(Habit.time_period=="monthly", 
                                            Habit.user_id==user.user_id).all()
        
        # Get 3 most recent records to update Recent Log
        recent_recs = Record.query.join(Habit).filter(Habit.user_id == user.user_id).order_by(Record.record_date.desc()).limit(3)
        
        return render_template("progress.html", user=user, habits=habits, events=events,
                                daily_habits=daily_habits,weekly_habits=weekly_habits, 
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
    badge2 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/2bw.png").first()
    if Habit.count_habit_by_user(user.user_id) == 1 and badge2 :
        # Create badge 2 for first habit
        badge2.img_url = "static/img/2.png"
        db.session.commit()
        flash("Awesome! You've created your first habit and earned a badge!")

    # Check for any existing badge 4 to avoid duplicate
    badge4 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/4bw.png").first()

    if Habit.count_habit_by_user(user.user_id) == 3 and badge4:
        # create badge 4 for third habits
        badge4.img_url = "static/img/4.png"
        db.session.commit()
        flash("Wow! You've created your three habits and earned a badge!")

    # put information in dictionary to send back as json response
    # habit_to_send = {"habit_id": habit.habit_id,
    #                  "habit_name": habit.habit_name,
    #                  "current_streak": habit.current_streak,
    #                  "max_streak": habit.max_streak,
    #                  "frequency": habit.frequency,
    #                  "time_period": habit.time_period
    #                  }
    
    # return jsonify(habit_to_send)
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
        img_url="static/img/thumbsUp.jpg"

    # Create new record object
    record = Record.create(habit_id, finished, notes, img_url, record_date)
    db.session.add(record)
    db.session.commit()
    

    # Create badges according to number of records
    user = User.get_by_email(session["user_email"])
    habits = Habit.get_by_user(user.user_id)
    record_count = 0
    badge7 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/7bw.png").first()
    badge8 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/8bw.png").first()
    badge9 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/9bw.png").first()
    for habit in habits:
        record_count +=  Record.count_records_by_habit(habit.habit_id)
        Habit.update_curr_streak(habit.habit_id)
        Habit.update_max_streak(habit.habit_id)
        if habit.max_streak == 7 and badge7:
            badge7.img_url = "static/img/7.png"
            db.session.commit()
            flash("Wonderful! You've reached 7 streaks and earned a badge!")
        elif habit.max_streak == 30 and badge8:
            badge7.img_url = "static/img/8.png"
            db.session.commit()
            flash("Dope! You've reached 30 streaks and earned a badge!")

        elif habit.max_streak == 100 and badge9:
            badge7.img_url = "static/img/9.png"
            db.session.commit()
            flash("Is that real!? You've reached 100 streaks and earned a badge!")

        
    
    # Check for any existing badges to avoid duplicate
    badge3 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/3bw.png").first()
    badge5 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/5bw.png").first()
    badge6 = Badge.query.filter(Badge.user_id==user.user_id,
                                 Badge.img_url=="static/img/6bw.png").first()
                                

    if record_count == 1 and badge3:
        badge3.img_url = "static/img/3.png"
        db.session.commit()
        flash("Great! You've created your first record and earned a badge!")

    if record_count == 5 and badge5:
        badge5.img_url = "static/img/5.png"
        db.session.commit()
        flash("Amazing! You've created your 5 records and earned a badge!")
    
    if record_count == 10 and badge6:
        badge6.img_url = "static/img/6.png"
        db.session.commit()
        flash("Spectacular! You've created your 10 records and earned a badge!")

    return redirect("/progress")


@app.route("/all_habits")
def view_habits():
    """View a list of habits for a user."""
    user = User.get_by_email(session.get("user_email"))
    
    habits = user.habits
    badges = Badge.query.filter(Badge.user_id==user.user_id).order_by(Badge.img_url).all()

   
    return render_template("all_habits.html", user=user, habits=habits,badges=badges)

@app.route("/habits")
def react_view_habits():
    """View all habits."""
    user = User.get_by_email(session["user_email"])
    habits = Habit.get_by_user(user.user_id)
    badges = Badge.query.filter(Badge.user_id==user.user_id).order_by(Badge.img_url).all()

    return render_template("habits.html", user=user, habits=habits, badges=badges)


@app.route("/habits.json")
def react_habits_json():
    """Return a list of habits for a user as json."""
    user = User.get_by_email(session.get("user_email"))
    habits = Habit.get_by_user(user.user_id)
    user_habits = user.habits
    habits_to_send =[]
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
    print("&&&&&&&")
    print(habits_to_send)
    return jsonify({"habits": habits_to_send})
    

@app.route("/react/remove_habit/<habit_id>")
def react_remove_habit(habit_id):
    """Remove a habit and all its related records."""
    Record.query.filter_by(habit_id=habit_id).delete()
    habit = Habit.get_by_id(habit_id)
    db.session.delete(habit)
    db.session.commit()
    return jsonify({'status':'success'})
  

@app.route("/react/remove_record/<record_id>")
def react_remove_record(record_id):
    """Remove a records."""
    record = Record.get_by_id(record_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'status':'success'})
  

@app.route("/<habit_id>/remove_habit")
def remove_habit(habit_id):
    """Remove a habit and all its related records."""
    Record.query.filter_by(habit_id=habit_id).delete()
    habit = Habit.get_by_id(habit_id)
    db.session.delete(habit)
    db.session.commit()

    return redirect('/all_habits')


@app.route("/react/<habit_id>/records")
def react_get_records(habit_id):
    user = User.get_by_email(session["user_email"])
    habit = Habit.get_by_id(habit_id)
    records = Record.query.filter(Record.habit_id==habit_id).order_by(Record.record_date.desc()).all()

    records_to_send = []
    for record in records: 
        records_to_send.append( 
            {'habit_name': habit.habit_name,
            'record_id':record.record_id,
            'notes':record.notes,
            'img_url':record.img_url,
            'record_date': record.record_date})

    return jsonify({'records': records_to_send})


@app.route("/<habit_id>/records")
def view_records(habit_id):
    """View all records for a habit."""
    user = User.get_by_email(session["user_email"])
    habits=user.habits
    habit = Habit.get_by_id(habit_id)
    records = Record.get_by_habit(habit_id)
    recordsss = habit.records
    
    return render_template("all_records.html", user=user, habit=habit, habits=habits, records=records)


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
    habits = user.habits
    badges = Badge.get_by_user(user.user_id)
    return render_template("all_badges.html", user=user, badges=badges, habits=habits)


@app.route("/chart_data.json")
def get_chart_data():
    """Get daily habit data as JSON."""

    # get user
    user = User.get_by_email(session.get("user_email"))
    habits = user.habits
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
