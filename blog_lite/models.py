from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    username: str = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    blogs = db.relationship("Blog", backref="author")
    likes = db.relationship("Likes", backref="user")
    followings = db.relationship("Followers", backref="follower")

class Blog(db.Model):
    __tablename__ = "blog"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    image_path = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    likes = db.relationship("Likes", backref="blog")

class Followers(db.Model):
    __tablename__ = "followers"
    follower_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)

# class Followings(db.Model):
#     __tablename__ = "followings"
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Likes(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.id"), nullable=False)