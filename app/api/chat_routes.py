from flask import request, jsonify
from app.services.chat_manager import ChatManager
from app.models.base import BaseModel


def register_chat_routes(app):
    @app.route("/api/chat/send", methods=["POST"])
    def send_chat_message():
        """Send a chat message and get AI response."""
        data = request.get_json() or {}
        
        user_id = data.get("user_id")
        message = data.get("message")
        
        if not user_id or not message:
            return jsonify({"error": "user_id and message are required"}), 400
        
        result = ChatManager.send_message(user_id, message)
        
        if result is None:
            return jsonify({"error": "Failed to send message"}), 500
        
        return jsonify({
            "message": "Message sent successfully",
            "user_message": result["user_message"],
            "ai_message": result["ai_message"]
        }), 200

    @app.route("/api/chat/history", methods=["GET"])
    def get_chat_history():
        """Get chat history for a user."""
        user_id = request.args.get("user_id", type=int)
        
        if not user_id:
            return jsonify({"error": "user_id is required as a query parameter"}), 400
        
        messages = ChatManager.get_chat_history(user_id)
        
        return jsonify({
            "messages": BaseModel.serialize_many(messages)
        }), 200

    @app.route("/api/chat/history", methods=["DELETE"])
    def delete_chat_history():
        """Delete all chat messages for a user."""
        data = request.get_json() or {}
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        deleted = ChatManager.delete_chat_history(user_id)
        
        if not deleted:
            return jsonify({"error": "Failed to delete chat history"}), 500
        
        return jsonify({
            "message": "Chat history deleted successfully"
        }), 200
