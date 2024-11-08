from flask import Blueprint, request, abort, make_response
from app.models.goal import Goal
from ..db import db

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@goals_bp.post("")
def create_goal():
    request_body = request.get_json()
    
    try:
        new_goal = Goal.from_dict(request_body)
    except KeyError as error:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_goal)
    db.session.commit()

    return {"goal":new_goal.to_dict()}, 201

@goals_bp.get("")
def get_all_goals():
    query = db.select(Goal)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Goal.title.ilike(f"%({title_param}%"))

    goals = db.session.scalars(query.order_by(Goal.id))
    goals_response = [goal.to_dict() for goal in goals]

    return goals_response