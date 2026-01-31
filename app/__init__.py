from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

_dotenv_path = find_dotenv(".env", usecwd=True)
if _dotenv_path:
    load_dotenv(_dotenv_path)

_flaskenv_path = find_dotenv(".flaskenv", usecwd=True)
if _flaskenv_path:
    load_dotenv(_flaskenv_path)

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import register_routes
    from app.cli import register_cli

    register_routes(app)
    register_cli(app)

    return app
