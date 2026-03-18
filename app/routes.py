from datetime import datetime, date, timedelta, time
from flask import Blueprint, request, jsonify
from . import db
from .models import Person, FoodEntry

bp = Blueprint("api", __name__)

VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner", "snack"}


@bp.get("/")
def home():
    return {"message": "Calorie Counter API running"}


@bp.post("/people")
def create_person():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if not email:
        return jsonify({"error": "Email is required"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400

    existing_person = Person.query.filter_by(email=email).first()
    if existing_person:
        return jsonify({"error": "Email already exists"}), 400

    try:
        age = int(data.get("age"))
        if age <= 0:
            return jsonify({"error": "Age must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Age must be a valid number"}), 400

    try:
        daily_calorie_goal = int(data.get("daily_calorie_goal", 2000))
        if daily_calorie_goal <= 0:
            return jsonify({"error": "daily_calorie_goal must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "daily_calorie_goal must be a valid number"}), 400

    weight = data.get("weight")
    height = data.get("height")

    try:
        weight = float(weight) if weight not in (None, "") else None
        if weight is not None and weight <= 0:
            return jsonify({"error": "Weight must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Weight must be a valid number"}), 400

    try:
        height = float(height) if height not in (None, "") else None
        if height is not None and height <= 0:
            return jsonify({"error": "Height must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Height must be a valid number"}), 400

    person = Person(
        name=name,
        email=email,
        password=password,
        weight=weight,
        height=height,
        age=age,
        daily_calorie_goal=daily_calorie_goal
    )
    db.session.add(person)
    db.session.commit()

    return jsonify({
        "id": person.id,
        "name": person.name,
        "email": person.email,
        "weight": person.weight,
        "height": person.height,
        "age": person.age,
        "daily_calorie_goal": person.daily_calorie_goal
    }), 201


@bp.post("/entries")
def add_entry():
    data = request.get_json() or {}

    try:
        person_id = int(data.get("person_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Valid person_id is required"}), 400

    person = db.session.get(Person, person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    food_name = data.get("food_name", "").strip()
    if not food_name:
        return jsonify({"error": "Food name is required"}), 400

    meal_type = data.get("meal_type", "").strip().lower()
    if meal_type not in VALID_MEAL_TYPES:
        return jsonify({
            "error": "meal_type must be breakfast, lunch, dinner, or snack"
        }), 400

    try:
        calories = int(data.get("calories"))
        if calories <= 0:
            return jsonify({"error": "Calories must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Calories must be a valid number"}), 400

    try:
        protein = float(data.get("protein", 0))
        carbs = float(data.get("carbs", 0))
        fats = float(data.get("fats", 0))
        if protein < 0 or carbs < 0 or fats < 0:
            return jsonify({
                "error": "Protein, carbs, and fats cannot be negative"
            }), 400
    except (TypeError, ValueError):
        return jsonify({
            "error": "Protein, carbs, and fats must be valid numbers"
        }), 400

    try:
        entry_date = date.fromisoformat(
            data.get("entry_date", date.today().isoformat())
        )
    except ValueError:
        return jsonify({"error": "entry_date must be in YYYY-MM-DD format"}), 400

    try:
        entry_time_str = data.get("entry_time")
        if entry_time_str:
            entry_time = time.fromisoformat(entry_time_str)
        else:
            entry_time = datetime.utcnow().time().replace(microsecond=0)
    except ValueError:
        return jsonify({"error": "entry_time must be in HH:MM:SS format"}), 400

    entry = FoodEntry(
        person_id=person_id,
        food_name=food_name,
        meal_type=meal_type,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats,
        entry_date=entry_date,
        entry_time=entry_time
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "id": entry.id,
        "person_id": entry.person_id,
        "food_name": entry.food_name,
        "meal_type": entry.meal_type,
        "calories": entry.calories,
        "protein": entry.protein,
        "carbs": entry.carbs,
        "fats": entry.fats,
        "entry_date": entry.entry_date.isoformat(),
        "entry_time": entry.entry_time.isoformat()
    }), 201


@bp.get("/entries")
def list_entries():
    person_id = request.args.get("person_id", type=int)
    if not person_id:
        return jsonify({"error": "person_id is required"}), 400

    person = db.session.get(Person, person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    try:
        entry_date = date.fromisoformat(
            request.args.get("date", date.today().isoformat())
        )
    except ValueError:
        return jsonify({"error": "date must be in YYYY-MM-DD format"}), 400

    entries = FoodEntry.query.filter_by(
        person_id=person_id,
        entry_date=entry_date
    ).order_by(FoodEntry.entry_time.asc(), FoodEntry.created_at.asc()).all()

    total_calories = sum(e.calories for e in entries)
    total_protein = sum(e.protein for e in entries)
    total_carbs = sum(e.carbs for e in entries)
    total_fats = sum(e.fats for e in entries)

    meal_totals = {
        "breakfast": 0,
        "lunch": 0,
        "dinner": 0,
        "snack": 0
    }

    for e in entries:
        meal_totals[e.meal_type] += e.calories

    remaining_calories = person.daily_calorie_goal - total_calories

    return jsonify({
        "person_id": person_id,
        "person_name": person.name,
        "daily_calorie_goal": person.daily_calorie_goal,
        "date": entry_date.isoformat(),
        "total_calories": total_calories,
        "remaining_calories": remaining_calories,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fats": total_fats,
        "meal_totals": meal_totals,
        "entries": [
            {
                "id": e.id,
                "food_name": e.food_name,
                "meal_type": e.meal_type,
                "calories": e.calories,
                "protein": e.protein,
                "carbs": e.carbs,
                "fats": e.fats,
                "entry_time": e.entry_time.isoformat()
            }
            for e in entries
        ]
    })


@bp.get("/history")
def history():
    person_id = request.args.get("person_id", type=int)
    if not person_id:
        return jsonify({"error": "person_id is required"}), 400

    person = db.session.get(Person, person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    entries = FoodEntry.query.filter_by(person_id=person_id).order_by(
        FoodEntry.entry_date.desc(),
        FoodEntry.entry_time.desc(),
        FoodEntry.created_at.desc()
    ).all()

    return jsonify({
        "person_id": person_id,
        "person_name": person.name,
        "entries": [
            {
                "id": e.id,
                "food_name": e.food_name,
                "meal_type": e.meal_type,
                "calories": e.calories,
                "protein": e.protein,
                "carbs": e.carbs,
                "fats": e.fats,
                "entry_date": e.entry_date.isoformat(),
                "entry_time": e.entry_time.isoformat()
            }
            for e in entries
        ]
    })


@bp.get("/weekly-summary")
def weekly_summary():
    person_id = request.args.get("person_id", type=int)
    if not person_id:
        return jsonify({"error": "person_id is required"}), 400

    person = db.session.get(Person, person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    end_date = date.today()
    start_date = end_date - timedelta(days=6)

    entries = FoodEntry.query.filter(
        FoodEntry.person_id == person_id,
        FoodEntry.entry_date >= start_date,
        FoodEntry.entry_date <= end_date
    ).order_by(FoodEntry.entry_date.asc()).all()

    summary = {}
    for i in range(7):
        day = start_date + timedelta(days=i)
        summary[day.isoformat()] = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0
        }

    for e in entries:
        day_key = e.entry_date.isoformat()
        summary[day_key]["calories"] += e.calories
        summary[day_key]["protein"] += e.protein
        summary[day_key]["carbs"] += e.carbs
        summary[day_key]["fats"] += e.fats

    return jsonify({
        "person_id": person_id,
        "person_name": person.name,
        "daily_calorie_goal": person.daily_calorie_goal,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily_totals": summary
    })