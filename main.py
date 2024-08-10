from os import getenv
from flask_restful import Api
from blog_lite import create_app

from blog_lite.api import UserResource, UserFollowerResource, BlogResource, BlogCommentResource, BlogLikeResource

DEBUG = getenv("ENV") not in ["prod", "production"]

app = create_app()

api = Api(app, catch_all_404s=True)
api.add_resource(UserResource, "/api/users", "/api/users/<int:user_id>")
api.add_resource(UserFollowerResource,
                 "/api/users/<int:user_id>/follow/<int:follower_id>")
api.add_resource(BlogResource, "/api/blogs", "/api/blogs/<int:blog_id>")
api.add_resource(BlogCommentResource, "/api/blogs/<int:blog_id>/comment")
api.add_resource(BlogLikeResource,
                 "/api/blogs/<int:blog_id>/like/<int:user_id>")

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=DEBUG)
