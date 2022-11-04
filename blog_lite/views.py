from flask import Blueprint, render_template

home = Blueprint("home", __name__)

@home.route("/", methods=["GET"])
def landing_page():
    return render_template("index.html")