# Taskboard

A small Flask task tracker backed by SQLite.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Tasks are stored in `instance/tasks.sqlite3`.

GitHub Actions workflows are intentionally not included, so you can practice
creating them yourself.

Need to teach and practice for GitHub actions.