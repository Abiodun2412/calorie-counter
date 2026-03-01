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
    data = request.get_json()
    person = Person(
        name=data["name"].strip(),
        age=int(data["age"])
    )
    db.session.add(person)
    db.session.commit()
    return jsonify({"id": person.id}), 201


@bp.post("/entries")
def add_entry():
    data = request.get_json()
    entry = FoodEntry(
        person_id=int(data["person_id"]),
        food_name=data["food_name"].strip(),
        calories=int(data["calories"]),
        entry_date=date.fromisoformat(
            data.get("entry_date", date.today().isoformat())
        )
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