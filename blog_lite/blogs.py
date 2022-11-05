from flask import Blueprint, request, render_template, \
                    redirect, url_for
from flask_login import login_required, current_user
import os
import nanoid
from . import db
from .models import Blog, Likes

BASE_PATH= os.path.abspath(os.path.curdir)

blog = Blueprint("blogs", __name__)

@blog.route("/", methods=["GET"])
@login_required
def home():
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    liked_posts = list(map(lambda l: l.blog_id, current_user.likes))

    return render_template("index.html", blogs=blogs, likes=liked_posts, user=current_user)

@blog.route("/blogs/create", methods=["GET", "POST"])
@login_required
def blogs():
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

@blog.route("/blog/<int:blog_id>/like/<int:user_id>", methods=["GET"])
@login_required
def like_blog(blog_id: int, user_id: int):
    new_like = Likes(user_id=user_id, blog_id=blog_id)
    
    db.session.add(new_like)
    db.session.commit()
    
    return redirect(url_for("blogs.home") + f"#blog{blog_id}")

@blog.route("/blog/<int:blog_id>/dislike/<int:user_id>", methods=["GET"])
@login_required
def dislike_blog(blog_id: int, user_id: int):
    Likes.query.filter_by(user_id=user_id, blog_id=blog_id).delete()
    db.session.commit()
    
    return redirect(url_for("blogs.home") + f"#blog{blog_id}")