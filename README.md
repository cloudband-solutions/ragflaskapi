# Default Flask API

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
export FLASK_APP=wsgi.py
flask run
```

## Run with Gunicorn
```bash
gunicorn wsgi:app
```

## Database commands (Flask-Migrate)

```bash
export FLASK_APP=wsgi.py
flask db init
flask db migrate -m "init"
flask db upgrade
```

## Tests
```bash
pytest
```
