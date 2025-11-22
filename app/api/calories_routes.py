from flask import request, jsonify
from app.services.calorie_tracker import Calorie_manager
from app.services.food_chatbot_client import process_food_entry
from app.services.tdee_service import TdeeService
from app.db import db_helper
from app.models.user import User
from datetime import datetime


def register_calories_routes(app):
    @app.route("/api/calories/chat", methods=["POST"])
    def calories_chat():
        """Handle chat messages for calorie logging with AI."""
        try:
            data = request.get_json() or {}
            
            message = data.get("message")
            username = data.get("username")
            chat_history = data.get("history", [])
            
            if not message or not username:
                return jsonify({"error": "message and username are required"}), 400
            
            # Get user from database
            user_row = db_helper.fetch_one(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            if not user_row:
                return jsonify({"error": "User not found"}), 404
            
            user = User.from_row(user_row)
            
            # Use frontend chat history (simplified - no DB chat storage for calories)
            final_history = chat_history if chat_history else []
            
            # Call AI chatbot to process food entry
            reply_text, nutrition_result = process_food_entry(
                message=message,
                chat_history=final_history
            )
            
            # Prepare response
            response_data = {"reply": reply_text}
            
            # If AI returned nutrition data, save to calorie_logs and return it
            if nutrition_result:
                # Check if we have all required fields
                required_fields = ["food_name", "calories", "protein_g", "carbs_g", "fat_g"]
                if all(key in nutrition_result for key in required_fields):
                    try:
                        # Save to calorie_logs table
                        log_entry = Calorie_manager.add_log(
                            user_id=user.id,
                            description=nutrition_result["food_name"],
                            calories=nutrition_result["calories"],
                            protein_g=nutrition_result["protein_g"],
                            carbs_g=nutrition_result["carbs_g"],
                            fat_g=nutrition_result["fat_g"]
                        )
                        
                        # Format response in the expected format
                        current_time = datetime.now().strftime("%I:%M %p")
                        response_data["food_data"] = {
                            "name": nutrition_result["food_name"],
                            "calories": float(nutrition_result["calories"]),
                            "protein": float(nutrition_result["protein_g"]),
                            "carbs": float(nutrition_result["carbs_g"]),
                            "fat": float(nutrition_result["fat_g"]),
                            "time": current_time,
                            "id": log_entry.id  # Include log ID for potential future use
                        }
                    except Exception as e:
                        print(f"Error saving calorie log: {e}")
                        import traceback
                        traceback.print_exc()
                        # Still return reply even if save fails
            
            return jsonify(response_data), 200
        except Exception as e:
            print(f"Error in calories_chat: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    @app.route("/api/calories/log", methods=["POST"])
    def add_calorie_log():
        """Add a new calorie log entry."""
        data = request.get_json() or {}
        
        username = data.get("username")
        description = data.get("description")
        calories = data.get("calories")
        protein_g = data.get("protein_g")
        carbs_g = data.get("carbs_g")
        fat_g = data.get("fat_g")
        entry_date = data.get("entry_date")
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        # Get user from database
        user_row = db_helper.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if not user_row:
            return jsonify({"error": "User not found"}), 404
        
        user = User.from_row(user_row)
        
        try:
            log_entry = Calorie_manager.add_log(
                user_id=user.id,
                description=description,
                calories=float(calories) if calories is not None else None,
                protein_g=float(protein_g) if protein_g is not None else None,
                carbs_g=float(carbs_g) if carbs_g is not None else None,
                fat_g=float(fat_g) if fat_g is not None else None,
                entry_date=entry_date
            )
            
            return jsonify({
                "message": "Calorie log added successfully",
                "log": log_entry.to_dict()
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/calories/logs/<int:user_id>", methods=["GET"])
    def get_calorie_logs(user_id):
        """Get calorie logs for a user, optionally filtered by date."""
        entry_date = request.args.get("date")  # Optional date parameter
        
        try:
            if entry_date:
                logs = Calorie_manager.get_logs(user_id, entry_date)
            else:
                logs = Calorie_manager.get_logs(user_id)
            
            return jsonify({
                "logs": [log.to_dict() for log in logs]
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/calories/logs/<int:user_id>/today", methods=["GET"])
    def get_today_logs(user_id):
        """Get today's calorie logs for a user, including total calories, goal calories, and surplus."""
        try:
            logs = Calorie_manager.get_today_logs(user_id)
            
            # Calculate total calories consumed today
            total_calories = Calorie_manager.get_today_total_calories(user_id)
            
            # Get user's goal calories from TDEE profile
            goal_calories = None
            tdee_profile = TdeeService.get_profile_by_user_id(user_id)
            if tdee_profile:
                goal_calories = tdee_profile.goal_calories
            
            # Calculate surplus: (Total Calories - Goal Calories)
            # If negative (under goal), show 0. If positive (over goal), show the difference.
            surplus = 0.0
            if goal_calories is not None:
                difference = total_calories - goal_calories
                if difference > 0:
                    surplus = difference
            
            return jsonify({
                "logs": [log.to_dict() for log in logs],
                "total_calories": total_calories,
                "goal_calories": goal_calories,
                "surplus": surplus
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/calories/log/<int:log_id>", methods=["GET"])
    def get_calorie_log(log_id):
        """Get a specific calorie log by ID."""
        log = Calorie_manager.get_log_by_id(log_id)
        
        if not log:
            return jsonify({"error": "Log entry not found"}), 404
        
        return jsonify({
            "log": log.to_dict()
        }), 200

    @app.route("/api/calories/log/<int:log_id>", methods=["PUT"])
    def update_calorie_log(log_id):
        """Update a calorie log entry."""
        data = request.get_json() or {}
        
        description = data.get("description")
        calories = data.get("calories")
        protein_g = data.get("protein_g")
        carbs_g = data.get("carbs_g")
        fat_g = data.get("fat_g")
        
        try:
            updated_log = Calorie_manager.update_log(
                log_id=log_id,
                description=description,
                calories=float(calories) if calories is not None else None,
                protein_g=float(protein_g) if protein_g is not None else None,
                carbs_g=float(carbs_g) if carbs_g is not None else None,
                fat_g=float(fat_g) if fat_g is not None else None,
            )
            
            if not updated_log:
                return jsonify({"error": "Log entry not found"}), 404
            
            return jsonify({
                "message": "Log updated successfully",
                "log": updated_log.to_dict()
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/calories/log/<int:log_id>", methods=["DELETE"])
    def delete_calorie_log(log_id):
        """Delete a calorie log entry."""
        log = Calorie_manager.get_log_by_id(log_id)
        
        if not log:
            return jsonify({"error": "Log entry not found"}), 404
        
        Calorie_manager.delete_log(log_id)
        
        return jsonify({
            "message": "Log deleted successfully"
        }), 200

