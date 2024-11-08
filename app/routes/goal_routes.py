from flask import Blueprint, request, abort, make_response
from app.models.goal import Goal
from ..db import db
from app.models.task import Task

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

@goals_bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_goal(goal_id)

    return {"goal": goal.to_dict()}, 200

def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except:
        response = {"message": f"goal {goal_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(Goal).where(Goal.id == goal_id)
    goal = db.session.scalar(query)
    
    if not goal:
        response = {"message": "goal not found"}
        abort(make_response(response, 404))
    return goal

@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]

    db.session.commit()

    response_body = {"goal": goal.to_dict()}
    return response_body, 200

@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_goal(goal_id)
    db.session.delete(goal)
    db.session.commit()

    response_body = {"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}
    return response_body

@goals_bp.post("/<goal_id>/tasks")
def create_task_with_goal_id(goal_id):
    goal = validate_goal(goal_id)

    request_body = request.get_json()
    request_body["goal_id"] = goal.id
    
    try:
        new_task = Task.from_dict(request_body)
    
    except KeyError as e:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()
    response_body = {
        "id": goal.id,
        "title": goal.title,
        "tasks": [
            {
                "id": new_task.id,
                "goal_id": new_task.goal_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": new_task.is_complete
            }
        ]
    }

    return response_body, 201

@goals_bp.get("/<goal_id>/tasks")
def get_tasks_by_goal(goal_id):
    goal = validate_goal(goal_id)
    response_body = {
        "id": goal.id,
        "title": goal.title,
        "tasks": [task.to_dict() for task in goal.tasks] 
    }

    return response_body

# def get_tasks_by_goal(goal_id):
#     goal = validate_goal(goal_id)
#     response = [task.to_dict() for task in goal.tasks]
#     print(goal.tasks)
    # return response

