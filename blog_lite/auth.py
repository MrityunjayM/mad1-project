from flask import Blueprint, request, render_template, redirect, url_for
from .models import User
from . import db

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        valid_form = email and first_name and last_name and (password1 == password2)

        if valid_form:
            new_user = User(first_name=first_name, last_name=last_name, email=email)
            db.session.add(new_user)
            db.session.commit()
        else:
            return redirect("/signup")
        
        return redirect('/'), 301

    return render_template("signup.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@auth.route("/logout", methods=["GET"])
def landing_page():
    return redirect("/login")