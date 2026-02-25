from flask import Blueprint

bp = Blueprint("api", __name__)

@bp.get("/")
def home():
    return {"message": "Calorie Counter API running"}