from typing import List, Dict, Optional
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.db import db_helper
from app.services.ai_chat_client import chat_with_ai_coach


class ChatManager:
    @staticmethod
    def save_message(user_id: int, sender: str, message: str) -> ChatMessage:
        """
        Save a chat message to the database.
        
        Args:
            user_id: The ID of the user
            sender: "user" or "ai"
            message: The message content
        
        Returns:
            ChatMessage object
        """
        created_at = ChatMessage.now_iso()
        
        db_helper.execute_query(
            "INSERT INTO chat_messages (user_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
            (user_id, sender, message, created_at)
        )
        
        row = db_helper.fetch_one(
            "SELECT * FROM chat_messages WHERE user_id = ? AND sender = ? AND message = ? AND created_at = ? ORDER BY id DESC LIMIT 1",
            (user_id, sender, message, created_at)
        )
        
        if row is None:
            print("Failed to save message")
            return None
        
        chat_message = ChatMessage.from_row(row)
        return chat_message

    @staticmethod
    def get_chat_history(user_id: int) -> List[ChatMessage]:
        """
        Get all chat messages for a user, ordered by creation time.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            List of ChatMessage objects
        """
        rows = db_helper.fetch_all(
            "SELECT * FROM chat_messages WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,)
        )
        
        if rows is None:
            return []
        
        messages = [ChatMessage.from_row(row) for row in rows]
        return messages

    @staticmethod
    def get_user_info(user_id: int) -> Optional[Dict]:
        """
        Get user information needed for AI chat.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            Dictionary with username, age, gender, height, weight, or None if user not found
        """
        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if row is None:
            print("User not found")
            return None
        
        user = User.from_row(row)
        return {
            "username": user.username,
            "age": user.age,
            "gender": user.gender,
            "height": user.height,
            "weight": user.weight
        }

    @staticmethod
    def send_message(user_id: int, message: str) -> Dict:
        """
        Send a user message, get AI response, and save both to database.
        
        Args:
            user_id: The ID of the user
            message: The user's message
        
        Returns:
            Dictionary with user_message and ai_message ChatMessage objects
        """
        # Get user info
        user_info = ChatManager.get_user_info(user_id)
        if user_info is None:
            print("User not found")
            return None
        
        # Get chat history
        chat_history = ChatManager.get_chat_history(user_id)
        history_formatted = [
            {"role": msg.sender, "content": msg.message}
            for msg in chat_history
        ]
        
        # Save user message first
        user_message_obj = ChatManager.save_message(user_id, "user", message)
        if user_message_obj is None:
            print("Failed to save user message")
            return None
        
        # Call AI coach
        ai_response = chat_with_ai_coach(
            user_name=user_info["username"],
            age=user_info["age"],
            gender=user_info["gender"],
            height=user_info["height"],
            weight=user_info["weight"],
            message=message,
            chat_history=history_formatted
        )
        
        # Save AI response
        ai_message_obj = ChatManager.save_message(user_id, "ai", ai_response)
        if ai_message_obj is None:
            print("Failed to save AI message")
            return None
        
        return {
            "user_message": user_message_obj.to_dict(),
            "ai_message": ai_message_obj.to_dict()
        }

    @staticmethod
    def delete_chat_history(user_id: int) -> bool:
        """
        Delete all chat messages for a user.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            True if successful, False otherwise
        """
        db_helper.execute_query(
            "DELETE FROM chat_messages WHERE user_id = ?",
            (user_id,)
        )
        return True

