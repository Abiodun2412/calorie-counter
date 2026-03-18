from datetime import datetime, date
from . import db


class Person(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    daily_calorie_goal = db.Column(db.Integer, nullable=False, default=2000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    food_entries = db.relationship("FoodEntry", backref="person", lazy=True)


class FoodEntry(db.Model):
    __tablename__ = "food_entries"

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)
    food_name = db.Column(db.String(255), nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False, default=0)
    carbs = db.Column(db.Float, nullable=False, default=0)
    fats = db.Column(db.Float, nullable=False, default=0)
    entry_date = db.Column(db.Date, default=date.today, nullable=False)
    entry_time = db.Column(
        db.Time,
        nullable=False,
        default=lambda: datetime.utcnow().time().replace(microsecond=0)
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)