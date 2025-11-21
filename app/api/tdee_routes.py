from flask import request, jsonify
from app.services.tdee_service import TdeeService
from app.services.chatgpt_client import chat_with_coach
from app.db import db_helper
from app.models.user import User


def register_tdee_routes(app):
    @app.route("/api/tdee/chat", methods=["POST"])
    def tdee_chat():
        """Handle chat messages with the TDEE coach."""
        data = request.get_json() or {}
        
        message = data.get("message")
        username = data.get("username")
        chat_history = data.get("history", [])
        stats = data.get("stats", {})
        
        if not message or not username:
            return jsonify({"error": "message and username are required"}), 400
        
        # Get user from database to get their stats
        user_row = db_helper.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if not user_row:
            return jsonify({"error": "User not found"}), 404
        
        user = User.from_row(user_row)
        
        # Get stats from form or use user's database stats
        age = stats.get("age") or user.age
        gender = stats.get("gender") or user.gender
        height = stats.get("height_cm") or user.height
        weight = stats.get("weight_kg") or user.weight
        
        # Get or create TDEE profile to get profile_id for chat history
        profile_id = TdeeService.get_or_create_profile_id(user.id)
        profile = TdeeService.get_profile_by_user_id(user.id)
        
        # Load previous chat history from database
        db_chat_history = TdeeService.get_chat_history(profile.id)
        db_history_formatted = [
            {"role": chat.role, "content": chat.content}
            for chat in db_chat_history
        ]
        
        # Use frontend history if provided (current session), otherwise use DB history
        # Frontend history is more up-to-date for the current session
        if chat_history:
            # Frontend is maintaining current session, use it
            final_history = chat_history
        else:
            # No frontend history, use DB history
            final_history = db_history_formatted
        
        # Call AI coach
        reply_text, tdee_result = chat_with_coach(
            user_name=user.username,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            message=message,
            chat_history=final_history
        )
        
        # Save user message to database
        TdeeService.save_chat_message(profile.id, "user", message)
        
        # Save AI response to database
        TdeeService.save_chat_message(profile.id, "assistant", reply_text)
        
        # Prepare response
        response_data = {"reply": reply_text}
        if tdee_result:
            response_data["tdee_result"] = tdee_result
        
        return jsonify(response_data), 200

    @app.route("/api/tdee/profile", methods=["POST"])
    def save_tdee_profile():
        """Save or update TDEE profile."""
        data = request.get_json() or {}
        
        user_id = data.get("user_id")
        activity_level = data.get("activity_level")
        tdee_value = data.get("tdee_value")
        goal_type = data.get("goal_type")
        goal_offset = data.get("goal_offset")
        goal_calories = data.get("goal_calories")
        
        # Validate all required fields
        missing_fields = []
        if not user_id:
            missing_fields.append("user_id")
        if not activity_level:
            missing_fields.append("activity_level")
        if tdee_value is None:
            missing_fields.append("tdee_value")
        if not goal_type:
            missing_fields.append("goal_type")
        if goal_offset is None:
            missing_fields.append("goal_offset")
        if goal_calories is None:
            missing_fields.append("goal_calories")
        
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        try:
            profile = TdeeService.save_profile(
                user_id=user_id,
                activity_level=activity_level,
                tdee_value=float(tdee_value),
                goal_type=goal_type,
                goal_offset=int(goal_offset),
                goal_calories=float(goal_calories)
            )
            
            return jsonify({
                "message": "TDEE profile saved successfully",
                "profile": profile.to_dict()
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/tdee/profile/<int:user_id>", methods=["GET"])
    def get_tdee_profile(user_id):
        """Get TDEE profile for a user."""
        profile = TdeeService.get_profile_by_user_id(user_id)
        
        if not profile:
            return jsonify({"error": "Profile not found"}), 404
        
        # Also get user stats for the frontend
        user_row = db_helper.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        if not user_row:
            return jsonify({"error": "User not found"}), 404
        
        user = User.from_row(user_row)
        
        return jsonify({
            "profile": {
                **profile.to_dict(),
                "age": user.age,
                "gender": user.gender,
                "height_cm": user.height,
                "weight_kg": user.weight
            }
        }), 200

