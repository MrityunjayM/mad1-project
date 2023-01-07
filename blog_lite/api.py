from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
import nanoid
from flask_bcrypt import generate_password_hash
from . import db
from .models import Blog, User, Likes, Followers, Comments


user_schema = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'username': fields.String,
    'created_at': fields.String
}


class UserResource(Resource):
    @marshal_with(user_schema)
    def get(self, user_id: int):
        user = User.query.get(user_id)

        return user, 200

    @marshal_with(user_schema)
    def post(self):
        parser = RequestParser()
        parser.add_argument('first_name', type=str)
        parser.add_argument('last_name', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        user_data = parser.parse_args()

        user = User(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password=generate_password_hash(user_data['password'], 12),
            username=f"{user_data['first_name']}-{nanoid.generate(size=8)}"
        )

        db.session.add(user)
        db.session.commit()
        return user, 200


class UserFollowerResource(Resource):
    def post(self, user_id, follower_id):
        if not User.query.get(user_id):
            return abort(404, message='User not found')

        follower = Followers(user_id=user_id, follower_id=follower_id)
        db.session.add(follower)
        db.session.commit()
        return '', 201

    def delete(self, user_id, follower_id):
        follower = Followers.query.filter_by(
            user_id=user_id, follower_id=follower_id).first()

        if not follower:
            return abort(404, message='Invalid follower/user id')
        db.session.delete(follower)
        db.session.commit()
        return '', 200


like_schema = {'blog_id': fields.Integer, 'user_id': fields.Integer}
comment_schema = {
    'blog_id': fields.Integer,
    'user_id': fields.Integer,
    'comment': fields.String,
    'created_at': fields.DateTime
}
blog_schema = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'image_path': fields.String,
    'created_at': fields.DateTime,
    'likes': fields.List(fields.Nested(like_schema)),
    'comments': fields.List(fields.Nested(comment_schema)),
}


class BlogResource(Resource):
    @marshal_with(blog_schema)
    def get(self):
        blogs = Blog.query.join(Likes, Blog.id == Likes.blog_id)\
            .join(Comments, Blog.id == Comments.blog_id)\
            .all()

        print(blogs[0].likes)
        return blogs, 200

    @marshal_with(blog_schema)
    def put(self, blog_id: int):
        blog = Blog.query.get(blog_id)
        if not blog:
            return abort(404, message=f'Blog {blog_id} doesn\'t exists')

        parser = RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('image_path', type=str)

        blog_data = parser.parse_args()

        blog.title = blog_data['title']
        blog.description = blog_data['description']
        blog.image_path = blog_data['image_path']

        db.session.add(blog)
        db.session.commit()

        return blog, 201

    @marshal_with(blog_schema)
    def post(self):
        parser = RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('image_path', type=str)
        parser.add_argument('user_id', type=str)
        blog_data = parser.parse_args()

        blog = Blog(
            title=blog_data['title'],
            description=blog_data['description'],
            user_id=blog_data['user_id'],
            image_path=blog_data['image_path']
        )

        db.session.add(blog)
        db.session.commit()

        return blog, 201

    def delete(self, blog_id):
        '''delete a blog'''
        blog = Blog.query.get(blog_id)

        if not blog:
            return abort(404, message=f'Blog {blog_id} doesn\'t exists')

        db.session.delete(blog)
        db.session.commit()
        return "", 200


class BlogLikeResource(Resource):
    def post(self, blog_id, user_id):
        new_like = Likes(user_id=user_id, blog_id=blog_id)
        # add and commit queries
        db.session.add(new_like)
        db.session.commit()
        return '', 201

    def delete(self, blog_id, user_id):
        like = Likes.query.filter_by(user_id=user_id, blog_id=blog_id).first()

        if not like:
            return abort(404, message=f"User {user_id} haven't liked blog {blog_id}")

        # add and commit queries
        db.session.delete(like)
        db.session.commit()
        return '', 200


class BlogCommentResource(Resource):
    def post(self, blog_id, user_id):
        parser = RequestParser()
        parser.add_argument('comment', type=str)
        req_data = parser.parse_args()
        comment = req_data['comment']

        if not comment:
            return abort(404, message='invalid comment')

        new_comment = Comments(
            comment=comment, user_id=user_id, blog_id=blog_id)

        db.session.add(new_comment)
        db.session.commit()
        return '', 201
