from flask import request, jsonify
from app.services.auth_manager import Authentication_manager


def register_auth_routes(app):
    @app.route("/api/auth/register", methods=["POST"])
    def register():
        data = request.get_json() or {}

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "username, email and password are required"}), 400

        user = Authentication_manager.register_user(username, email, password)

        if user is None:
            return jsonify({"error": "Username or email already taken"}), 409

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 201

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.get_json() or {}

        identifier = data.get("identifier")
        password = data.get("password")

        if not identifier or not password:
            return jsonify({"error": "identifier and password are required"}), 400

        user = Authentication_manager.login_user(identifier, password)

        if user is None:
            return jsonify({"error": "Invalid username/email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200
