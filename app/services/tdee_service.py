from app.models.tdee_profile import TdeeProfile
from app.models.tdee_chat import TdeeChat
from app.db import db_helper
from typing import Optional, List


class TdeeService:
    @staticmethod
    def get_profile_by_user_id(user_id: int) -> Optional[TdeeProfile]:
        """Get TDEE profile for a user."""
        row = db_helper.fetch_one(
            "SELECT * FROM tdee_profile WHERE user_id = ?",
            (user_id,)
        )
        if row is None:
            return None
        return TdeeProfile.from_row(row)

    @staticmethod
    def save_profile(
        user_id: int,
        activity_level: str,
        tdee_value: float,
        goal_type: str,
        goal_offset: int,
        goal_calories: float
    ) -> TdeeProfile:
        """Save or update TDEE profile for a user."""
        from app.models.tdee_profile import TdeeProfile
        
        # Check if profile exists
        existing = TdeeService.get_profile_by_user_id(user_id)
        
        if existing:
            # Update existing profile
            updated_at = TdeeProfile.now_iso()
            db_helper.execute_query(
                """UPDATE tdee_profile 
                   SET activity_level = ?, tdee_value = ?, goal_type = ?, 
                       goal_offset = ?, goal_calories = ?, updated_at = ?
                   WHERE user_id = ?""",
                (activity_level, tdee_value, goal_type, goal_offset, goal_calories, updated_at, user_id)
            )
        else:
            # Create new profile
            created_at = TdeeProfile.now_iso()
            db_helper.execute_query(
                """INSERT INTO tdee_profile 
                   (user_id, activity_level, tdee_value, goal_type, goal_offset, goal_calories, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, activity_level, tdee_value, goal_type, goal_offset, goal_calories, created_at)
            )
        
        # Return the updated/new profile
        return TdeeService.get_profile_by_user_id(user_id)

    @staticmethod
    def get_chat_history(tdee_profile_id: int) -> List[TdeeChat]:
        """Get all chat messages for a TDEE profile, ordered by creation time."""
        rows = db_helper.fetch_all(
            "SELECT * FROM tdee_chat WHERE tdee_profile_id = ? ORDER BY created_at ASC",
            (tdee_profile_id,)
        )
        return [TdeeChat.from_row(row) for row in rows]

    @staticmethod
    def save_chat_message(tdee_profile_id: int, role: str, content: str) -> TdeeChat:
        """Save a chat message to the database."""
        created_at = TdeeChat.now_iso()
        db_helper.execute_query(
            "INSERT INTO tdee_chat (tdee_profile_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (tdee_profile_id, role, content, created_at)
        )
        
        # Fetch the last inserted message
        row = db_helper.fetch_one(
            "SELECT * FROM tdee_chat WHERE tdee_profile_id = ? ORDER BY id DESC LIMIT 1",
            (tdee_profile_id,)
        )
        return TdeeChat.from_row(row)

    @staticmethod
    def get_or_create_profile_id(user_id: int) -> int:
        """Get existing profile ID or create a minimal profile and return its ID."""
        profile = TdeeService.get_profile_by_user_id(user_id)
        if profile:
            return profile.id
        
        # Create minimal profile with defaults (will be updated when user saves)
        # Reuse save_profile to avoid code duplication
        profile = TdeeService.save_profile(
            user_id=user_id,
            activity_level="sedentary",
            tdee_value=2000.0,
            goal_type="maintain",
            goal_offset=0,
            goal_calories=2000.0
        )
        return profile.id

