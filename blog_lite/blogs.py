import os
import nanoid
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Blog, Likes, Followers, Comments

BASE_PATH = os.path.abspath(os.path.curdir)

blog = Blueprint("blogs", __name__)


@blog.route("/", methods=["GET"])
@login_required
def home():
    # filter blogs by user_id who current_user have followed
    blogs = Blog.query.join(Followers, Blog.user_id == Followers.follower_id)\
        .filter(Followers.user_id == current_user.id)\
        .order_by(Blog.created_at.desc()).all()
    # make a list of blog.id which user have liked
    liked_posts = list(map(lambda l: l.blog_id, current_user.likes))

    return render_template("blog_feed.html", blogs=blogs, likes=liked_posts, user=current_user)


@blog.route("/create", methods=["GET", "POST"])
@login_required
def create_blog():
    if request.method == "POST":
        # Get Blog data from form
        title = request.form.get("title")
        description = request.form.get("description")
        image = request.files.get("image")

        if title and description:
            new_blog = Blog(title=title, description=description,
                            user_id=current_user.id)

            if image:
                extname = image.filename.split('.')[-1]
                img_path = f"blog-{nanoid.generate(size=8)}.{extname}"
                image.save(f"{BASE_PATH}/blog_lite/static/images/{img_path}")
                new_blog.image_path = img_path

            db.session.add(new_blog)
            db.session.commit()

        return redirect(url_for(".home"))

    return render_template("blog.html", user=current_user)


@blog.route("/<int:blog_id>/edit", methods=["GET", "POST"])
@login_required
def edit_blog(blog_id: int):
    _blog = Blog.query.get(blog_id)
    # return back to blog with error message if current_user is not author
    if _blog.author.id != current_user.id:
        flash("You're not allowed to edit others blog", category='danger')
        return redirect(url_for(".home"))
    if request.method == "POST":
        # Get Blog data from form
        title = request.form.get("title")
        description = request.form.get("description")
        image = request.files.get("image")

        _blog.title = title
        _blog.description = description

        if image:
            extname = image.filename.split('.')[-1]
            img_path = f"blog-{nanoid.generate(size=8)}.{extname}"
            image.save(f"{BASE_PATH}/blog_lite/static/images/{img_path}")
            _blog.image_path = img_path

        db.session.add(_blog)
        db.session.commit()

        return redirect(url_for(".home") + f"#blog{blog_id}")

    return render_template("edit_blog.html", blog=_blog, user=current_user)


@blog.route("/<int:blog_id>/delete", methods=["GET"])
@login_required
def delete_blog(blog_id: int):
    _blog = Blog.query.get(blog_id)
    if _blog.author.id == current_user.id:
        # delete all likes of the blog
        Likes.query.filter_by(blog_id=blog_id).delete()
        db.session.flush()
        # delete blog
        db.session.delete(_blog)
        db.session.commit()
        return redirect(url_for('blogs.home'))
    else:
        flash('You can\'t delete others blog', category='danger')
        return redirect(url_for('blogs.home'))


@blog.route("/<int:blog_id>/like/<int:user_id>", methods=["GET"])
@login_required
def like_blog(blog_id: int, user_id: int):
    # create user like
    new_like = Likes(user_id=user_id, blog_id=blog_id)
    # add and commit queries
    db.session.add(new_like)
    db.session.commit()

    return redirect(url_for("blogs.home") + f"#blog{blog_id}")


@blog.route("/<int:blog_id>/dislike/<int:user_id>", methods=["GET"])
@login_required
def dislike_blog(blog_id: int, user_id: int):
    Likes.query.filter_by(user_id=user_id, blog_id=blog_id).delete()
    db.session.commit()

    return redirect(url_for("blogs.home") + f"#blog{blog_id}")


@blog.route("/<int:blog_id>/comments", methods=["POST"])
@login_required
def add_comment(blog_id: int):
    user_id = current_user.id
    comment = request.form.get('comment')

    if not comment:
        flash("Can't post an empty comment")
        return redirect(url_for("blogs.home"))
    new_comment = Comments(comment=comment, user_id=user_id, blog_id=blog_id)

    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('blogs.home') + f"#blog{blog_id}")
