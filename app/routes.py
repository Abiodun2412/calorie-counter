from datetime import date
from flask import Blueprint, request, jsonify
from . import db
from .models import Person, FoodEntry

bp = Blueprint("api", __name__)

@bp.get("/")
def home():
    return {"message": "Calorie Counter API running"}


    @bp.post("/people")
    def create_person():
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "Name is required"}), 400
            try:
            age = int(data.get("age"))
                if age <= 0:
                except (TypeError, ValueError):
                    return jsonify({"error": "Age must be greater than 0"}), 400
                    person = Person(name=name, age=age)
                    db.session.add(person)
                    db.session.commit()
                    return jsonify({"id": person.id}), 201
        


@bp.post("/entries")
def add_entry():
    data = request.get_json() or {}

    try:
        person_id = int(data.get("person_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Valid person_id is required"}), 400

    person = Person.query.get(person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    food_name = data.get("food_name", "").strip()
    if not food_name:
        return jsonify({"error": "Food name is required"}), 400

    try:
        calories = int(data.get("calories"))
        if calories <= 0:
            return jsonify({"error": "Calories must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Calories must be a valid number"}), 400

    try:
        entry_date = date.fromisoformat(
            data.get("entry_date", date.today().isoformat())
        )
    except ValueError:
        return jsonify({"error": "entry_date must be in YYYY-MM-DD format"}), 400

    entry = FoodEntry(
        person_id=person_id,
        food_name=food_name,
        calories=calories,
        entry_date=entry_date
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"id": entry.id}), 201


@bp.get("/entries")
def list_entries():
    person_id = request.args.get("person_id", type=int)
    entry_date = date.fromisoformat(
        request.args.get("date", date.today().isoformat())
    )

    entries = FoodEntry.query.filter_by(
        person_id=person_id,
        entry_date=entry_date
    ).all()

    total_calories = sum(e.calories for e in entries)

    return jsonify({
        "person_id": person_id,
        "date": entry_date.isoformat(),
        "total_calories": total_calories,
        "entries": [
            {
                "id": e.id,
                "food_name": e.food_name,
                "calories": e.calories
            } for e in entries
        ]
    })