from flask import request, jsonify
from app.services.settings_service import SettingsService


def register_settings_routes(app):
    @app.route("/api/settings", methods=["GET"])
    def get_settings():
        """Get current user's settings."""
        # GET requests use query parameters, not JSON body
        user_id = request.args.get("user_id", type=int)
        
        if not user_id:
            return jsonify({"error": "user_id is required as a query parameter"}), 400
        
        settings = SettingsService.get_user_settings(user_id)
        
        if settings is None:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "message": "Settings retrieved successfully",
            "settings": settings
        }), 200

    @app.route("/api/settings", methods=["POST"])
    def update_settings():
        """Update user settings."""
        data = request.get_json() or {}
        
        user_id = data.get("user_id")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Basic validation
        if username is not None and not username.strip():
            return jsonify({"error": "username cannot be empty"}), 400
        
        if email is not None and not email.strip():
            return jsonify({"error": "email cannot be empty"}), 400
        
        if age is not None and (not isinstance(age, int) or age <= 0):
            return jsonify({"error": "age must be a positive integer"}), 400
        
        if height is not None and (not isinstance(height, int) or height <= 0):
            return jsonify({"error": "height must be a positive integer"}), 400
        
        if weight is not None and (not isinstance(weight, int) or weight <= 0):
            return jsonify({"error": "weight must be a positive integer"}), 400
        
        # Update settings
        updated_settings = SettingsService.update_user_settings(
            user_id=user_id,
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password,
            age=age,
            height=height,
            weight=weight
        )
        
        if updated_settings is None:
            return jsonify({"error": "Failed to update settings. User not found or validation failed."}), 400
        
        return jsonify({
            "message": "Settings updated successfully",
            "settings": updated_settings
        }), 200

