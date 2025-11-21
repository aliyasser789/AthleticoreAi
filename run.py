from flask import Flask, render_template
from app.api.auth_routes import register_auth_routes
from app.api.tdee_routes import register_tdee_routes
from app.api.food_feed_routes import register_food_feed_routes
from app.api.calories_routes import register_calories_routes


app = Flask(__name__, template_folder="app/templates", static_folder="app/static")


@app.route("/")
def home():
    return "athleticore running"

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/tdee")
def tdee_page():
    return render_template("tdee.html")

@app.route("/calories")
def calories_page():
    return render_template("calories.html")

@app.route("/forgot-password")
def forgot_password_page():
    return render_template("forgot_password.html")



# Register routes from other files
register_auth_routes(app)
register_tdee_routes(app)
register_food_feed_routes(app)
register_calories_routes(app)



if __name__ == "__main__":
    app.run(debug=True)
