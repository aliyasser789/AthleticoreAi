from app.models.calorie_entry import CalorieLog
from app.db import db_helper
from typing import Optional, List


class Calorie_manager:
    @staticmethod
    #hanadeh men el route haolo add log with these parameters
    def add_log(
        user_id: int,
        description: Optional[str],
        calories: Optional[float],
        protein_g: Optional[float],
        carbs_g: Optional[float],
        fat_g: Optional[float],
        entry_date: Optional[str] = None,
    ) -> CalorieLog:
        # lesa baamel entry date lw log gededa 
        if entry_date is None:
            entry_date = CalorieLog.today_iso()

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
        today = CalorieLog.today_iso()
        return Calorie_manager.get_logs(user_id, today)

    @staticmethod
    def get_today_total_calories(user_id: int) -> float:
        """Calculate total calories consumed today."""
        today = CalorieLog.today_iso()
        row = db_helper.fetch_one(
            """
            SELECT COALESCE(SUM(calories), 0) as total
            FROM calorie_logs
            WHERE user_id = ? AND entry_date = ? AND is_deleted = 0
            """,
            (user_id, today)
        )
        if row and row[0] is not None:
            return float(row[0])
        return 0.0

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
    def delete_log(log_id: int) -> bool:
        """Soft delete a calorie log (set is_deleted = 1)."""
        db_helper.execute_query(
            "UPDATE calorie_logs SET is_deleted = 1 WHERE id = ?",
            (log_id,)
        )
        return True
