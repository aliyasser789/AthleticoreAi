from flask import request, jsonify
from app.services.food_feed_service import FoodFeedService
from app.services.food_chatbot_client import process_food_entry
from app.db import db_helper
from app.models.user import User


def register_food_feed_routes(app):
    @app.route("/api/food/chat", methods=["POST"])
    def food_chat():
        """Handle chat messages with the food nutrition AI."""
        data = request.get_json() or {}
        
        message = data.get("message")
        username = data.get("username")
        food_feed_id = data.get("food_feed_id")
        chat_history = data.get("history", [])
        
        if not message or not username:
            return jsonify({"error": "message and username are required"}), 400
        
        if not food_feed_id:
            return jsonify({"error": "food_feed_id is required"}), 400
        
        # Get user from database
        user_row = db_helper.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if not user_row:
            return jsonify({"error": "User not found"}), 404
        
        user = User.from_row(user_row)
        
        # Verify food_feed_id belongs to this user
        feed_entry = FoodFeedService.get_feed_by_id(food_feed_id)
        if not feed_entry or feed_entry.user_id != user.id:
            return jsonify({"error": "Food entry not found"}), 404
        
        # Load previous chat history from database
        db_chat_history = FoodFeedService.get_chat_history(food_feed_id)
        db_history_formatted = [
            {"role": chat.role, "content": chat.content}
            for chat in db_chat_history
        ]
        
        # Use frontend history if provided (current session), otherwise use DB history
        if chat_history:
            final_history = chat_history
        else:
            final_history = db_history_formatted
        
        # Call AI chatbot
        reply_text, nutrition_result = process_food_entry(
            message=message,
            chat_history=final_history
        )
        
        # Save user message to database
        FoodFeedService.save_chat_message(food_feed_id, "user", message)
        
        # Save AI response to database
        FoodFeedService.save_chat_message(food_feed_id, "assistant", reply_text)
        
        # If AI returned nutrition data, update the food feed entry
        if nutrition_result and nutrition_result.get("ready_to_save"):
            FoodFeedService.update_food_card(
                feed_id=food_feed_id,
                food_name=nutrition_result["food_name"],
                calories=nutrition_result["calories"],
                protein_g=nutrition_result["protein_g"],
                carbs_g=nutrition_result["carbs_g"],
                fat_g=nutrition_result["fat_g"]
            )
        
        # Prepare response
        response_data = {"reply": reply_text}
        if nutrition_result:
            response_data["nutrition_result"] = nutrition_result
        
        return jsonify(response_data), 200

    @app.route("/api/food/entry", methods=["POST"])
    def create_food_entry():
        """Create a new food entry."""
        data = request.get_json() or {}
        
        username = data.get("username")
        content = data.get("content")
        entry_date = data.get("entry_date")
        
        if not username or not content:
            return jsonify({"error": "username and content are required"}), 400
        
        # Get user from database
        user_row = db_helper.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if not user_row:
            return jsonify({"error": "User not found"}), 404
        
        user = User.from_row(user_row)
        
        # Create food entry
        feed_entry = FoodFeedService.add_food_entry(
            user_id=user.id,
            content=content,
            entry_date=entry_date
        )
        
        return jsonify({
            "message": "Food entry created successfully",
            "feed_entry": feed_entry.to_dict()
        }), 201

    @app.route("/api/food/feed/<int:user_id>", methods=["GET"])
    def get_food_feed(user_id):
        """Get today's food feed for a user."""
        entry_date = request.args.get("date")  # Optional date parameter
        
        feed_entries = FoodFeedService.get_today_feed(user_id, entry_date)
        
        return jsonify({
            "feed": [entry.to_dict() for entry in feed_entries]
        }), 200

    @app.route("/api/food/entry/<int:feed_id>", methods=["GET"])
    def get_food_entry(feed_id):
        """Get a specific food entry with its chat history."""
        feed_entry = FoodFeedService.get_feed_by_id(feed_id)
        
        if not feed_entry:
            return jsonify({"error": "Food entry not found"}), 404
        
        # Get chat history for this entry
        chat_history = FoodFeedService.get_chat_history(feed_id)
        
        return jsonify({
            "feed_entry": feed_entry.to_dict(),
            "chat_history": [chat.to_dict() for chat in chat_history]
        }), 200

    @app.route("/api/food/entry/<int:feed_id>", methods=["DELETE"])
    def delete_food_entry(feed_id):
        """Delete a food entry."""
        feed_entry = FoodFeedService.get_feed_by_id(feed_id)
        
        if not feed_entry:
            return jsonify({"error": "Food entry not found"}), 404
        
        FoodFeedService.delete_feed_entry(feed_id)
        
        return jsonify({
            "message": "Food entry deleted successfully"
        }), 200

