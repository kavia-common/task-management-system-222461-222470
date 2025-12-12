from datetime import datetime
from typing import Any, Dict, List

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields, validates, ValidationError


# In-memory store for tasks. For simplicity and preview suitability, we avoid external DBs.
# A future iteration can swap this with SQLite without changing the API.
_TASKS: Dict[int, Dict[str, Any]] = {}
_NEXT_ID: int = 1


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class TaskCreateSchema(Schema):
    title = fields.String(required=True, metadata={"description": "Title for the task"})
    completed = fields.Boolean(
        required=False, load_default=False, metadata={"description": "Completion status"}
    )

    @validates("title")
    def validate_title(self, value: str):
        if not value or not value.strip():
            raise ValidationError("Title is required and cannot be empty.")


class TaskUpdateSchema(Schema):
    title = fields.String(required=False, metadata={"description": "Updated title"})
    completed = fields.Boolean(required=False, metadata={"description": "Updated status"})

    @validates("title")
    def validate_title(self, value: str):
        if value is not None and not value.strip():
            raise ValidationError("Title cannot be empty.")


class TaskResponseSchema(Schema):
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    completed = fields.Boolean(required=True)
    created_at = fields.String(required=True)
    updated_at = fields.String(required=True)


class TaskListResponseSchema(Schema):
    tasks = fields.List(fields.Nested(TaskResponseSchema), required=True)


blp = Blueprint(
    "Tasks",
    "tasks",
    url_prefix="/api/tasks",
    description="Task CRUD routes",
)


@blp.route("")
class TasksCollection(MethodView):
    def _list_tasks(self) -> List[Dict[str, Any]]:
        return list(_TASKS.values())

    # PUBLIC_INTERFACE
    @blp.response(200, TaskListResponseSchema)
    def get(self):
        """
        List tasks
        Returns a JSON array of all tasks.

        Response: { "tasks": [Task, ...] }
        """
        return {"tasks": self._list_tasks()}

    # PUBLIC_INTERFACE
    @blp.arguments(TaskCreateSchema)
    @blp.response(201, TaskResponseSchema)
    def post(self, payload: Dict[str, Any]):
        """
        Create a new task

        Request body:
        - title: string (required)
        - completed: boolean (optional, default false)

        Returns the created task.
        """
        global _NEXT_ID
        task_id = _NEXT_ID
        _NEXT_ID += 1

        now = _now_iso()
        task = {
            "id": task_id,
            "title": payload["title"].strip(),
            "completed": bool(payload.get("completed", False)),
            "created_at": now,
            "updated_at": now,
        }
        _TASKS[task_id] = task
        return task, 201


@blp.route("/<int:task_id>")
class TaskResource(MethodView):
    def _get_or_404(self, task_id: int) -> Dict[str, Any]:
        task = _TASKS.get(task_id)
        if not task:
            abort(404, message=f"Task {task_id} not found")
        return task

    # PUBLIC_INTERFACE
    @blp.response(200, TaskResponseSchema)
    def get(self, task_id: int):
        """
        Retrieve a task by ID
        """
        return self._get_or_404(task_id)

    # PUBLIC_INTERFACE
    @blp.arguments(TaskUpdateSchema)
    @blp.response(200, TaskResponseSchema)
    def put(self, payload: Dict[str, Any], task_id: int):
        """
        Update a task by replacing provided fields.
        Title or completed can be provided. At least one must be present.
        """
        if not payload:
            abort(400, message="Request body cannot be empty.")
        task = self._get_or_404(task_id)

        updated = False
        if "title" in payload and payload["title"] is not None:
            task["title"] = payload["title"].strip()
            updated = True
        if "completed" in payload and payload["completed"] is not None:
            task["completed"] = bool(payload["completed"])
            updated = True

        if not updated:
            abort(400, message="No valid fields to update.")
        task["updated_at"] = _now_iso()
        return task

    # PUBLIC_INTERFACE
    @blp.arguments(TaskUpdateSchema, location="json")
    @blp.response(200, TaskResponseSchema)
    def patch(self, payload: Dict[str, Any], task_id: int):
        """
        Partially update a task (same fields as PUT, but optional).
        """
        task = self._get_or_404(task_id)
        if not payload:
            abort(400, message="Request body cannot be empty.")

        if "title" in payload and payload["title"] is not None:
            if not payload["title"].strip():
                abort(400, message="Title cannot be empty.")
            task["title"] = payload["title"].strip()
        if "completed" in payload and payload["completed"] is not None:
            task["completed"] = bool(payload["completed"])

        task["updated_at"] = _now_iso()
        return task

    # PUBLIC_INTERFACE
    @blp.response(204)
    def delete(self, task_id: int):
        """
        Delete a task by ID
        """
        _ = self._get_or_404(task_id)
        del _TASKS[task_id]
        return "", 204
