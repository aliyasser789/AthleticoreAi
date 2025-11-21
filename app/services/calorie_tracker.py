from app.models.calorie_entry import CalorieLog
from app.db import db_helper
from typing import Optional, List
from datetime import date


class Calorie_manager:
    @staticmethod
    def add_log(
        user_id: int,
        description: Optional[str],
        calories: Optional[float],
        protein_g: Optional[float],
        carbs_g: Optional[float],
        fat_g: Optional[float],
        entry_date: Optional[str] = None,
    ) -> CalorieLog:
        # 1) Default entry_date = today
        if entry_date is None:
            entry_date = date.today().isoformat()

        # 2) Generate created_at timestamp
        created_at = CalorieLog.now_iso()

        # 3) Insert into DB
        db_helper.execute_query(
            """
            INSERT INTO calorie_logs (
                user_id, entry_date, description,
                calories, protein_g, carbs_g, fat_g,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                entry_date,
                description,
                calories,
                protein_g,
                carbs_g,
                fat_g,
                created_at,
            ),
        )

        # 4) Fetch the last inserted row for this user & date
        row = db_helper.fetch_one(
            """
            SELECT *
            FROM calorie_logs
            WHERE user_id = ? AND entry_date = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id, entry_date),
        )

        # 5) Convert DB row -> CalorieLog object
        return CalorieLog.from_row(row)

    @staticmethod
    def get_logs(user_id: int, entry_date: Optional[str] = None) -> List[CalorieLog]:
        """Get all calorie logs for a user, optionally filtered by date."""
        if entry_date:
            rows = db_helper.fetch_all(
                """
                SELECT * FROM calorie_logs
                WHERE user_id = ? AND entry_date = ? AND is_deleted = 0
                ORDER BY created_at DESC
                """,
                (user_id, entry_date)
            )
        else:
            rows = db_helper.fetch_all(
                """
                SELECT * FROM calorie_logs
                WHERE user_id = ? AND is_deleted = 0
                ORDER BY entry_date DESC, created_at DESC
                """,
                (user_id,)
            )
        return [CalorieLog.from_row(row) for row in rows]

    @staticmethod
    def get_today_logs(user_id: int) -> List[CalorieLog]:
        """Get all calorie logs for today."""
        today = date.today().isoformat()
        return Calorie_manager.get_logs(user_id, today)

    @staticmethod
    def get_log_by_id(log_id: int) -> Optional[CalorieLog]:
        """Get a specific calorie log by ID."""
        row = db_helper.fetch_one(
            "SELECT * FROM calorie_logs WHERE id = ? AND is_deleted = 0",
            (log_id,)
        )
        if row is None:
            return None
        return CalorieLog.from_row(row)

    @staticmethod
    def update_log(
        log_id: int,
        description: Optional[str] = None,
        calories: Optional[float] = None,
        protein_g: Optional[float] = None,
        carbs_g: Optional[float] = None,
        fat_g: Optional[float] = None,
    ) -> Optional[CalorieLog]:
        """Update a calorie log entry."""
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if calories is not None:
            updates.append("calories = ?")
            params.append(calories)
        if protein_g is not None:
            updates.append("protein_g = ?")
            params.append(protein_g)
        if carbs_g is not None:
            updates.append("carbs_g = ?")
            params.append(carbs_g)
        if fat_g is not None:
            updates.append("fat_g = ?")
            params.append(fat_g)
        
        if not updates:
            return Calorie_manager.get_log_by_id(log_id)
        
        params.append(log_id)
        query = f"UPDATE calorie_logs SET {', '.join(updates)} WHERE id = ? AND is_deleted = 0"
        
        db_helper.execute_query(query, tuple(params))
        
        return Calorie_manager.get_log_by_id(log_id)

    @staticmethod
    def delete_log(log_id: int) -> bool:
        """Soft delete a calorie log (set is_deleted = 1)."""
        db_helper.execute_query(
            "UPDATE calorie_logs SET is_deleted = 1 WHERE id = ?",
            (log_id,)
        )
        return True
