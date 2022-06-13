""" Models for habit building app. """

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    # A list of habits objects
    habits = db.relationship("Habit", back_populates="user")
    # A list of badge objects
    badges = db.relationship("Badge", back_populates="user")

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"


class Habit(db.Model):
    """A habit."""

    __tablename__ = "habits"

    habit_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    habit_name = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    frequency = db.Column(db.Integer, nullable= False)
    time_period = db.Column(db.String, nullable=False)
    current_streak = db.Column(db.Integer, nullable=False)
    max_streak = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    
    # The user to which a habit belongs
    user = db.relationship("User", back_populates="habits")
    # A ist of records for this habit
    records = db.relationship("Record", back_populates="habit")


    def __repr__(self):
        return f"<Habit habit_id={self.habit_id} habit_name={self.habit_name}>"


class Record(db.Model):
    """A record."""

    __tablename__ = "habits"

    record_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    finished = db.Column(db.Boolean, nullable=False, default= False)
    record_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.habit_id"))
    
    # The habit to which a record belongs
    habit = db.relationship("Habit", back_populates="records")

    def __repr__(self):
        return f"<Record record_id={self.habit_id} finished={self.finished}>"

class Badge(db.Model):
    """A badge."""

    __tablename__ = "badges"

    badge_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    img_url = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    
    # The user to which a badge belongs
    user = db.relationship("User", back_populates="badges")


    def __repr__(self):
        return f"<Badge badge_id={self.badge_id} img_url={self.img_url}>"


def connect_to_db(flask_app, db_uri="postgresql:///database_name", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)