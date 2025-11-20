from app.models.calorie_entry import CalorieLog
from app.db import db_helper
from typing import Optional
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



        