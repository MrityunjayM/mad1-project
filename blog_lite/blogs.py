from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import os
import nanoid
from . import db
from .models import User, Blog, Likes, Followers, Comments

BASE_PATH= os.path.abspath(os.path.curdir)

blog = Blueprint("blogs", __name__)

@blog.route("/<string:username>", methods=["GET"])
def display_user(username: str):
    u = User.query.filter_by(username=username).first()
    f = Followers.query.filter_by(user_id=u.id).all()

    return render_template('searched_profile.html', 
                            blogs=u.blogs,
                            followers=f,
                            followings=u.followings,
                            searched_user=u, 
                            user=current_user)

@blog.route("/", methods=["GET"])
@login_required
def home():
    followings = Followers.query.filter_by(follower_id=current_user.id).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    liked_posts = list(map(lambda l: l.blog_id, current_user.likes))

    return render_template("index.html", blogs=blogs, likes=liked_posts, user=current_user)

@blog.route("/blogs/create", methods=["GET", "POST"])
@login_required
def create_blog():
    if request.method == "POST":
        # Get Blog data from form
        title = request.form.get("title")
        description = request.form.get("description")
        image = request.files.get("image")
        
        if title and description:
            new_blog = Blog(title=title, description=description, user_id=current_user.id)

            if image: 
                extname = image.filename.split('.')[-1]
                img_path = f"blog-{nanoid.generate(size=8)}.{extname}"
                image.save(f"{BASE_PATH}/blog_lite/static/images/{img_path}")
                new_blog.image_path = img_path
            
            db.session.add(new_blog)
            db.session.commit()

        return redirect(url_for(".home"))

    return render_template("blog.html", user=current_user)

@blog.route("/blog/<int:blog_id>/edit", methods=["GET", "POST"])
@login_required
def edit_blog(blog_id: int):
    blog = Blog.query.get(blog_id)
    if request.method == "POST":
        # Get Blog data from form
        title = request.form.get("title")
        description = request.form.get("description")
        image = request.files.get("image")

        blog.title = title
        blog.description = description

        if image: 
            extname = image.filename.split('.')[-1]
            img_path = f"blog-{nanoid.generate(size=8)}.{extname}"
            image.save(f"{BASE_PATH}/blog_lite/static/images/{img_path}")
            blog.image_path = img_path
        
        db.session.add(blog)
        db.session.commit()

        return redirect(url_for(".home") + f"#blog{blog_id}")

    return render_template("edit_blog.html", blog=blog, user=current_user)

@blog.route("/blog/<int:blog_id>/delete", methods=["GET"])
@login_required
def delete_blog(blog_id: int):
    blog = Blog.query.get(blog_id)
    if blog.author.id == current_user.id:
        # delete all likes of the blog
        Likes.query.filter_by(blog_id=blog_id).delete()
        db.session.flush()
        # delete blog
        db.session.delete(blog)
        db.session.commit()
        return redirect(url_for('blogs.home'))
    else:
        flash('You can\'t delete others blog', category='danger')
        return redirect(url_for('blogs.home'))

@blog.route("/blog/<int:blog_id>/like/<int:user_id>", methods=["GET"])
@login_required
def like_blog(blog_id: int, user_id: int):
    # create user like
    new_like = Likes(user_id=user_id, blog_id=blog_id)
    # add and commit queries
    db.session.add(new_like)
    db.session.commit()
    
    return redirect(url_for("blogs.home") + f"#blog{blog_id}")

@blog.route("/blog/<int:blog_id>/dislike/<int:user_id>", methods=["GET"])
@login_required
def dislike_blog(blog_id: int, user_id: int):
    Likes.query.filter_by(user_id=user_id, blog_id=blog_id).delete()
    db.session.commit()
    
    return redirect(url_for("blogs.home") + f"#blog{blog_id}")

@blog.route("/blog/<int:blog_id>/comments", methods=["POST"])
@login_required
def add_comment(blog_id: int):
    user_id = current_user.id
    comment = request.form.get('comment')
    new_comment = Comments(comment=comment, user_id=user_id, blog_id=blog_id)

    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('blogs.home') + f"#blog{blog_id}")