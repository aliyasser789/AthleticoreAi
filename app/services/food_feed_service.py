from app.models.food_feed import FoodFeed
from app.models.food_chat import FoodChat
from app.db import db_helper
from typing import Optional, List
from datetime import date


class FoodFeedService:
    @staticmethod
    def add_food_entry(user_id: int, content: str, entry_date: Optional[str] = None) -> FoodFeed:
        """Add a food entry to the feed."""
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        created_at = FoodFeed.now_iso()
        
        db_helper.execute_query(
            """INSERT INTO food_feed 
               (user_id, content, entry_date, created_at)
               VALUES (?, ?, ?, ?)""",
            (user_id, content, entry_date, created_at)
        )
        
        # Fetch the last inserted entry
        row = db_helper.fetch_one(
            "SELECT * FROM food_feed WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,)
        )
        return FoodFeed.from_row(row)

    @staticmethod
    def update_food_card(
        feed_id: int,
        food_name: str,
        calories: float,
        protein_g: float,
        carbs_g: float,
        fat_g: float
    ) -> FoodFeed:
        """Update a feed entry with AI-generated nutrition information."""
        db_helper.execute_query(
            """UPDATE food_feed 
               SET food_name = ?, calories = ?, protein_g = ?, carbs_g = ?, fat_g = ?
               WHERE id = ?""",
            (food_name, calories, protein_g, carbs_g, fat_g, feed_id)
        )
        
        # Fetch the updated entry
        row = db_helper.fetch_one(
            "SELECT * FROM food_feed WHERE id = ?",
            (feed_id,)
        )
        return FoodFeed.from_row(row)

    @staticmethod
    def get_today_feed(user_id: int, entry_date: Optional[str] = None) -> List[FoodFeed]:
        """Get all food feed entries for today, ordered by creation time."""
        if entry_date is None:
            entry_date = date.today().isoformat()
        
        rows = db_helper.fetch_all(
            "SELECT * FROM food_feed WHERE user_id = ? AND entry_date = ? ORDER BY created_at ASC",
            (user_id, entry_date)
        )
        return [FoodFeed.from_row(row) for row in rows]

    @staticmethod
    def get_feed_by_id(feed_id: int) -> Optional[FoodFeed]:
        """Get a specific feed entry by ID."""
        row = db_helper.fetch_one(
            "SELECT * FROM food_feed WHERE id = ?",
            (feed_id,)
        )
        if row is None:
            return None
        return FoodFeed.from_row(row)

    @staticmethod
    def delete_feed_entry(feed_id: int) -> bool:
        """Delete a feed entry."""
        db_helper.execute_query(
            "DELETE FROM food_feed WHERE id = ?",
            (feed_id,)
        )
        return True

    @staticmethod
    def get_chat_history(food_feed_id: int) -> List[FoodChat]:
        """Get all chat messages for a specific food feed entry, ordered by creation time."""
        rows = db_helper.fetch_all(
            "SELECT * FROM food_chat WHERE food_feed_id = ? ORDER BY created_at ASC",
            (food_feed_id,)
        )
        return [FoodChat.from_row(row) for row in rows]

    @staticmethod
    def save_chat_message(food_feed_id: int, role: str, content: str) -> FoodChat:
        """Save a chat message to the database."""
        created_at = FoodChat.now_iso()
        db_helper.execute_query(
            "INSERT INTO food_chat (food_feed_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (food_feed_id, role, content, created_at)
        )
        
        # Fetch the last inserted message
        row = db_helper.fetch_one(
            "SELECT * FROM food_chat WHERE food_feed_id = ? ORDER BY id DESC LIMIT 1",
            (food_feed_id,)
        )
        return FoodChat.from_row(row)

