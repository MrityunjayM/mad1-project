from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user, confirm_login
import nanoid
import re

from . import db
from .models import User

auth = Blueprint("auth", __name__)

# regex for email validation
email_validation_regex = r"\b[aa-zA-Z0-9.%_+-]+@[a-z0-9-.]+.[a-z|A-Z]{2,}\b"

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Getting data from form
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if not first_name:
            # flash error msg if first name is not given
            flash("First Name is required", "danger")
            return redirect(url_for("auth.signup")), 400
        
        elif not re.fullmatch(email_validation_regex, email):
            # flash error msg if email is not valid
            flash("Invalid email", "danger")
            return redirect(url_for("auth.signup")), 400
        
        elif password1 != password2:
            # flash error msg if password & confirm_password doesn't match
            flash("Password doesn't match", "danger")
            return redirect(url_for("auth.signup")), 400

        else:
            # Generate password hash
            pass_hash = generate_password_hash(password1, 10)
            unique_username=f"{''.join(first_name.lower().split(' '))}-{nanoid.generate(size=6)}"
            # Create new user
            new_user = User(first_name=first_name, last_name=last_name, 
                            email=email, password=pass_hash, username=unique_username)
            # Add user to database
            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully", "success")    
            return redirect(url_for('blogs.home')), 301

    return render_template("signup.html", user=current_user)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get data from form
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate Email
        if not re.fullmatch(email_validation_regex, email):
            flash("Invalid Email", "danger")
            return redirect(url_for("auth.login"))

        # find user from database
        user = User.query.filter_by(email=email).first()

        if not user:
            # flash error message if user not found
            flash("User not found", "danger")
            return redirect(url_for("auth.login"))
        
        # Validate password_hash
        if check_password_hash(user.password, password):
            login_user(user)
            confirm_login()
            flash("Login successful", "success")
            return redirect(url_for("blogs.home"))
        else:
            flash("Incorrect password", "danger")

    return render_template("login.html", user=current_user)

@auth.route("/logout", methods=["GET"])
@login_required
def landing_page():
    logout_user()
    return redirect(url_for("auth.login"))