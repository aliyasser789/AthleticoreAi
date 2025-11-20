from app.models.tdee_profile import TDEEProfile
from app.db import db_helper


class TDEE_manager:
    @staticmethod
    def get_profile(user_id):
        row = db_helper.fetch_one(
            "SELECT * FROM tdee_profiles WHERE user_id = ?",
            (user_id,)
        )
        if row is None:
            print("No TDEE profile found for this user.")
            return None

        profile = TDEEProfile.from_row(row)
        return profile

    @staticmethod
    def save_profile(user_id, age, gender, height_cm, weight_kg,
                     activity_level, tdee_value, goal_type,
                     goal_offset, goal_calories):
        
        
        row = db_helper.fetch_one(
            "SELECT * FROM tdee_profiles WHERE user_id = ?",
            (user_id,)
        )

        if row is None:
            
            created_at = TDEEProfile.now_iso()

            db_helper.execute_query(
                """
                INSERT INTO tdee_profiles (
                    user_id,
                    age,
                    gender,
                    height_cm,
                    weight_kg,
                    activity_level,
                    tdee_value,
                    goal_type,
                    goal_offset,
                    goal_calories,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    age,
                    gender,
                    height_cm,
                    weight_kg,
                    activity_level,
                    tdee_value,
                    goal_type,
                    goal_offset,
                    goal_calories,
                    created_at,
                ),
            )
        else:
            
            db_helper.execute_query(
                """
                UPDATE tdee_profiles
                SET age = ?,
                    gender = ?,
                    height_cm = ?,
                    weight_kg = ?,
                    activity_level = ?,
                    tdee_value = ?,
                    goal_type = ?,
                    goal_offset = ?,
                    goal_calories = ?
                WHERE user_id = ?
                """,
                (
                    age,
                    gender,
                    height_cm,
                    weight_kg,
                    activity_level,
                    tdee_value,
                    goal_type,
                    goal_offset,
                    goal_calories,
                    user_id,
                ),
            )

        
        row = db_helper.fetch_one(
            "SELECT * FROM tdee_profiles WHERE user_id = ?",
            (user_id,)
        )
        new_profile = TDEEProfile.from_row(row)
        return new_profile
