from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from ..db import db
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
load_dotenv()

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# slack URL
SLACK_API_URL = os.environ.get('SLACK_API_URL')
SLACK_API_TOKEN = os.environ.get('SLACK_API_TOCKEN')

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()
    
    try:
        new_task = Task.from_dict(request_body)
    
    except KeyError as e:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    description_param = request.args.get("description")
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    sort_param = request.args.get("sort")
    if sort_param == "desc":
        query = query.order_by(Task.title.desc())
    else:
        query = query.order_by(Task.title.asc())
    

    tasks = db.session.scalars(query.order_by(Task.title))

    tasks_response = [task.to_dict() for task in tasks]
    return tasks_response


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)

    return {"task": task.to_dict()}, 200

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    response_body = {"task":task.to_dict()}
    return response_body, 200

@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    response_body = {"details": f'Task {task_id} "{task.title}" successfully deleted'}
    return response_body

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_task(task_id)
    
    task.mark_complete()  
    db.session.commit()

    post_to_slack(task)

    return {"task": task.to_dict()}, 200


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_task(task_id)

    task.mark_incomplete()
    db.session.commit()

    return {"task" : task.to_dict()}, 200
    


def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"message": f"task {task_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)
    
    if not task:
        response = {"message": "task not found"}
        abort(make_response(response, 404))
    return task

def post_to_slack(task):
    headers = {
        "Authorization": f"Bearer {SLACK_API_TOKEN}",
        "Content-Type": "application/json",

    }
    if task.completed_at:
        data = {
            "text": f"Task '{task.title}' has been marked complete",
            "channel": "C080MLHBX5W",
        }
    else:
        data = {
            "text": f"Task '{task.title}' has been marked incomplete",
            "channel": "C080MLHBX5W",
        }

    r = requests.post(SLACK_API_URL, headers=headers, json=data)

    return r