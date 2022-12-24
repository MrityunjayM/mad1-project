from os import getenv
from blog_lite import create_app

DEBUG = getenv("ENV") not in ["prod", "production"]

app = create_app()

if __name__ == "__main__":
    app.run(debug=DEBUG)
