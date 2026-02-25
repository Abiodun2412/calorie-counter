import os
from datetime import datetime, date

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///calorie_counter.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class FoodEntry(db.Model):
    __tablename__ = "food_entries"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    food_name = db.Column(db.String(255), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    entry_date = db.Column(db.Date, default=date.today, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

@app.get("/")
def home():
    return {"message": "Calorie Counter API running"}

@app.post("/api/entries")
def create_entry():
    data = request.get_json(force=True)
    entry = FoodEntry(
        user_id=int(data["user_id"]),
        food_name=str(data["food_name"]).strip(),
        calories=int(data["calories"]),
        entry_date=date.fromisoformat(data.get("entry_date", date.today().isoformat()))
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({"id": entry.id}), 201

@app.get("/api/entries")
def list_entries():
    user_id = request.args.get("user_id", type=int)
    date_str = request.args.get("date", default=date.today().isoformat())
    target_date = date.fromisoformat(date_str)

    entries = FoodEntry.query.filter_by(user_id=user_id, entry_date=target_date).all()
    total = sum(e.calories for e in entries)

    return jsonify({
        "user_id": user_id,
        "date": target_date.isoformat(),
        "total_calories": total,
        "entries": [{"id": e.id, "food_name": e.food_name, "calories": e.calories} for e in entries]
    })