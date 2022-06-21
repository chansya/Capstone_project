"""Script to seed sample database."""

from email import message
import os
from datetime import datetime
from model import User, Habit, Record, Badge, connect_to_db, db
from server import app


os.system("dropdb habits")
os.system("createdb habits")

connect_to_db(app)

db.create_all()


def load_users():
    """Load sample users from data/sample_users.csv into database."""

    for row in open("data/sample_users.csv"):
        name, email, password = row.rstrip().split("|")

        user = User.create(name, email, password)
        db.session.add(user)

    db.session.commit()


def load_habits():
    """Load sample habits from data/sample_habits.csv into database."""

    for row in open("data/sample_habits.csv"):
        row_lst = row.rstrip().split("|")

        user_id, habit_name,frequency,time_period,current_streak,max_streak=row_lst[:-2]
        start_date = datetime.strptime(row_lst[-2], "%Y-%m-%d")
        # parse date if end_date is available, otherwise None
        # if row_lst[-1]!='null':
        #     end_date = datetime.strptime(row_lst[-1], "%Y-%m-%d")
        # else:
        #     end_date = None
        habit = Habit.create(user_id, habit_name,
                            frequency,time_period,
                            current_streak,max_streak,
                            start_date)
        db.session.add(habit)

    db.session.commit()


def load_records():
    """Load sample records from data/sample_records.csv into database."""

    def parse_boolean(str):
        return str == "True"

    for row in open("data/sample_records.csv"):
        row_lst = row.rstrip().split("|")

        habit_id, finished, notes, img_url = row_lst[:-1]

        record_date = datetime.strptime(row_lst[-1], "%Y-%m-%d")

        record = Record.create(habit_id, parse_boolean(finished), notes, img_url, record_date)
        db.session.add(record)

    db.session.commit()


def load_badges():
    """Load sample badges from data/sample_badges.csv into database."""

    for row in open("data/sample_badges.csv"):
        row = row.rstrip()
        user_id, img_url, name, message = row.split("|")

        badge = Badge.create(user_id, img_url, name, message)
        db.session.add(badge)

    db.session.commit()




load_users()
load_habits()
load_records()
load_badges()
