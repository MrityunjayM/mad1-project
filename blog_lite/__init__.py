from os import getenv, path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

APP_SECRET = getenv("SECRET_KEY") or "thisisasecret"
DB_NAME = "blog_lite.sqlite3"

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    # config app secret
    app.config["SECRET_KEY"] = APP_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    db.init_app(app)
    app.app_context().push()

    from .views import home
    from .auth import auth

    app.register_blueprint(home, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    create_database()

    return app

def create_database():
    if not path.exists("blog_lite/" + DB_NAME):
        db.create_all()
        print("Database created successfully")