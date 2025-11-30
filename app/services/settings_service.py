from typing import Optional, Dict
from app.models.user import User
from app.db import db_helper
from app.services.auth_manager import Authentication_manager


class SettingsService:
    @staticmethod
    def get_user_settings(user_id: int) -> Optional[Dict]:
        """
        Get user settings (username, email, age, height, weight).
        Password is not included.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            Dictionary with user settings, or None if user not found
        """
        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if row is None:
            print("User not found")
            return None
        
        user = User.from_row(row)
        
        # Return settings without password
        return {
            "username": user.username,
            "email": user.email,
            "age": user.age,
            "height": user.height,
            "weight": user.weight
        }

    @staticmethod
    def update_user_settings(
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        confirm_password: Optional[str] = None,
        age: Optional[int] = None,
        height: Optional[int] = None,
        weight: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Update user settings.
        
        Args:
            user_id: The ID of the user
            username: Optional new username
            email: Optional new email
            password: Optional new password (must provide confirm_password if password is provided)
            confirm_password: Optional confirmation password
            age: Optional new age
            height: Optional new height
            weight: Optional new weight
        
        Returns:
            Dictionary with updated user settings, or None if user not found or validation failed
        """
        # Check if user exists
        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if row is None:
            print("User not found")
            return None
        
        user = User.from_row(row)
        
        # Validate password if provided
        if password:
            if not confirm_password:
                print("confirm_password is required when password is provided")
                return None
            
            if password != confirm_password:
                print("Password and confirm_password do not match")
                return None
        
        # Check if username is being changed and if it's already taken
        if username and username != user.username:
            existing_user = db_helper.fetch_one(
                "SELECT * FROM users WHERE username = ? AND id != ?",
                (username, user_id)
            )
            if existing_user is not None:
                print("Username already taken")
                return None
        
        # Check if email is being changed and if it's already taken
        if email and email != user.email:
            existing_user = db_helper.fetch_one(
                "SELECT * FROM users WHERE email = ? AND id != ?",
                (email, user_id)
            )
            if existing_user is not None:
                print("Email already taken")
                return None
        
        # Build update query dynamically
        fields_to_update = []
        params = []
        
        if username is not None:
            fields_to_update.append("username = ?")
            params.append(username)
        
        if email is not None:
            fields_to_update.append("email = ?")
            params.append(email)
        
        if password is not None:
            hashed_password = Authentication_manager.hash_password(password)
            fields_to_update.append("password_hash = ?")
            params.append(hashed_password)
        
        if age is not None:
            fields_to_update.append("age = ?")
            params.append(age)
        
        if height is not None:
            fields_to_update.append("height = ?")
            params.append(height)
        
        if weight is not None:
            fields_to_update.append("weight = ?")
            params.append(weight)
        
        # Always update updated_at timestamp
        updated_at = User.now_iso()
        fields_to_update.append("updated_at = ?")
        params.append(updated_at)
        
        # If no fields to update, return current settings
        if not fields_to_update:
            return {
                "username": user.username,
                "email": user.email,
                "age": user.age,
                "height": user.height,
                "weight": user.weight
            }
        
        # Add user_id for WHERE clause
        params.append(user_id)
        
        # Build and execute UPDATE query
        set_clause = ", ".join(fields_to_update)
        db_helper.execute_query(
            f"UPDATE users SET {set_clause} WHERE id = ?",
            tuple(params)
        )
        
        # Fetch updated user
        updated_row = db_helper.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if updated_row is None:
            print("Failed to fetch updated user")
            return None
        
        updated_user = User.from_row(updated_row)
        
        # Return updated settings without password
        return {
            "username": updated_user.username,
            "email": updated_user.email,
            "age": updated_user.age,
            "height": updated_user.height,
            "weight": updated_user.weight
        }

