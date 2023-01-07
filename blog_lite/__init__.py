from os import getenv, path
from flask import Flask, redirect, flash, render_template, url_for
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

APP_SECRET = getenv("SECRET_KEY") or "thisisasecret"
DB_NAME = "../blog_lite.sqlite3"

db = SQLAlchemy()


def create_app():
    """creates a flask app instance with predefined configurations"""
    app = Flask(__name__)
    # config app secret
    app.config["SECRET_KEY"] = APP_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.app_context().push()

    @app.route('/', methods=['GET'])
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('blogs.home'))
        return render_template('index.html', user=False)

    # blog route blueprint
    from .blogs import blog
    app.register_blueprint(blog, url_prefix="/blogs")

    # auth route blueprint
    from .auth import auth
    app.register_blueprint(auth, url_prefix="/")

    # profile route blueprint
    from .user_profile import profile
    app.register_blueprint(profile, url_prefix="/profile")

    from .models import User

    # register error handler
    @app.errorhandler(Exception)
    def basic_error(error):
        print(error)
        flash("Something went wrong!!", category='danger')
        return redirect('/')

    create_database()

    # login setup
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    return app


def create_database():
    '''initializes tables for all defined modals in application scope'''
    if not path.exists("blog_lite/" + DB_NAME):
        db.create_all()
        print("Database created successfully")
