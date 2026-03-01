from datetime import datetime, date
from . import db

class Person(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    food_entries = db.relationship("FoodEntry", backref="person", lazy=True)


class FoodEntry(db.Model):
    __tablename__ = "food_entries"

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)
    food_name = db.Column(db.String(255), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    entry_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)