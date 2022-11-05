from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import User

profile = Blueprint("profile", __name__)

@profile.route("/", methods=["GET"])
@login_required
def home():
    return render_template("profile.html", user=current_user)


@profile.route("/search", methods=["GET"])
def search_profile():
    query = request.args.get("u")
    users = User.query.filter
    return render_template("search_profile.html", user=[])