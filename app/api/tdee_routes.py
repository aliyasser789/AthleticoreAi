from flask import request, jsonify
from app.services.tdee_manager import TDEE_manager
from app.services.tdee_assistant_service import tdee_assistant_reply

def register_tdee_routes(app):
    @app.route("/api/tdee/profile", methods=["POST"])
    def save_tdee_profile():
        data = request.get_json() or {}

        user_id = data.get("user_id")
        age = data.get("age")
        gender = data.get("gender")
        height_cm = data.get("height_cm")
        weight_kg = data.get("weight_kg")
        activity_level = data.get("activity_level")
        tdee_value = data.get("tdee_value")
        goal_type = data.get("goal_type")
        goal_offset = data.get("goal_offset")
        goal_calories = data.get("goal_calories")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        profile = TDEE_manager.save_profile(
            user_id,
            age,
            gender,
            height_cm,
            weight_kg,
            activity_level,
            tdee_value,
            goal_type,
            goal_offset,
            goal_calories,
        )

        return jsonify({
            "message": "TDEE profile saved",
            "profile": profile.to_dict()
        }), 200

    @app.route("/api/tdee/profile/<int:user_id>", methods=["GET"])
    def get_tdee_profile(user_id):
        profile = TDEE_manager.get_profile(user_id)

        if profile is None:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify({
            "profile": profile.to_dict()
        }), 200
    @app.route("/api/tdee/chat", methods=["POST"])
    def tdee_chat():
        data = request.get_json() or {}

        message = data.get("message")
        username = data.get("username")
        history = data.get("history") or []

        if not message:
            return jsonify({"error": "message is required"}), 400

        assistant_response = tdee_assistant_reply(
            message,
            username=username,
            previous_messages=history if isinstance(history, list) else [],
        )

        return jsonify(assistant_response), 200


