from flask import Flask
from app.api.auth_routes import register_auth_routes
from app.api.tdee_routes import register_tdee_routes

app = Flask(__name__)


@app.route("/")
def home():
    return "athleticore running"


# Register routes from other files
register_auth_routes(app)
register_tdee_routes(app)


if __name__ == "__main__":
    app.run(debug=True)
