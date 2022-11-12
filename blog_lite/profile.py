from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import User, Followers

profile = Blueprint("profile", __name__)

@profile.route("/", methods=["GET"])
@login_required
def home():
    q = request.args.get('display')
    dis_followers = q == 'followers'
    dis_followings = q == 'followings'
    followings_users = []
    followers = Followers.query.with_entities(Followers.user_id).filter_by(follower_id = current_user.id).all()
    
    fls = User.query.filter(User.id.in_([x for x, *y in followers])).all()

    if dis_followings:
        following = Followers.query.with_entities(
            Followers.follower_id
        ).filter_by(user_id = current_user.id).all()

        maped_following_ids = {x for x, *y in following }
        followings_users = User.query.filter(User.id.in_(maped_following_ids)).all()

    return render_template("profile.html",
                            dis_followers=dis_followers,
                            dis_followings=dis_followings,
                            followers=fls,
                            followings=followings_users,
                            user=current_user)


@profile.route("/search", methods=["GET"])
@login_required
def search_profile():
    search = request.args.get("u")
    users_query = User.query.filter(User.first_name.like(f"%{search}%") |\
        User.last_name.like(f"%{search}%"))
    print(users_query)
    users = users_query.all()

    return render_template("search_profile.html", query=search, users=users, user=current_user)

@profile.route("/follow/<int:follower_id>", methods=["GET"])
@login_required
def follow(follower_id: int):
    user_id = current_user.id
    flr = Followers(user_id=user_id, follower_id=follower_id)

    db.session.add(flr)
    db.session.commit()

    return redirect('/')

@profile.route("/unfollow/<int:follower_id>", methods=["GET"])
@login_required
def unfollow(follower_id: int):
    user_id = current_user.id
    flr = Followers.query.filter_by(user_id=user_id, follower_id=follower_id).first()

    db.session.delete(flr)
    db.session.commit()

    return redirect(request.referrer or '/')

# @profile.route("/followings", methods=["GET"])
# @login_required
# def followings():
#     followings = Followers.query.filter_by(follower_id=current_user.id).all()
#     return redirect(url_for("."))

# @profile.route("/followers", methods=["GET"])
# @login_required
# def followers():
#     followers = Followers.query.filter_by(user_id = current_user.id).all()
#     return redirect(url_for("."))