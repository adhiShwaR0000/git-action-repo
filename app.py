import os
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE"] = Path(app.instance_path) / "tasks.sqlite3"


def initialize_database():
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def get_tasks(view):
    conditions = {
        "active": "WHERE completed = 0",
        "completed": "WHERE completed = 1",
        "all": "",
    }
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        connection.row_factory = sqlite3.Row
        tasks = connection.execute(
            f"SELECT id, title, completed FROM tasks {conditions[view]} "
            "ORDER BY completed ASC, id DESC"
        ).fetchall()
        counts = connection.execute(
            """
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(completed = 0), 0) AS active,
                   COALESCE(SUM(completed = 1), 0) AS completed
            FROM tasks
            """
        ).fetchone()
    return tasks, counts


@app.route("/")
def index():
    view = request.args.get("view", "all")
    if view not in {"all", "active", "completed"}:
        view = "all"
    tasks, counts = get_tasks(view)
    return render_template("index.html", tasks=tasks, counts=counts, view=view)


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Add a task name before saving.")
        return redirect(url_for("index"))

    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        connection.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        connection.commit()
    flash("Task added.")
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        connection.execute(
            """
            UPDATE tasks
            SET completed = CASE completed WHEN 0 THEN 1 ELSE 0 END
            WHERE id = ?
            """,
            (task_id,),
        )
        connection.commit()
    return redirect(url_for("index", view=request.form.get("view", "all")))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()
    flash("Task deleted.")
    return redirect(url_for("index", view=request.form.get("view", "all")))

initialize_database()

if __name__ == "__main__":    
    app.run(debug=True)
