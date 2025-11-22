from typing import List, Dict, Any, Optional
from datetime import datetime
from app.db import db_helper
from app.models.workout import Workout
from app.models.workout_exercise import WorkoutExercise


class WorkoutService:
    @staticmethod
    def create_workout_for_users(
        user_id: int,
        workout_name: str,
        log_date: str,
        notes: Optional[str],
        exercises_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create a workout with exercises for a user.
        
        Args:
            user_id: The ID of the user creating the workout
            workout_name: Name of the workout
            log_date: Date of the workout (ISO format string)
            notes: Optional notes for the workout
            exercises_data: List of exercise dictionaries with keys:
                - exercise_name (str)
                - sets (int)
                - reps (int)
                - weight_kg (float, optional, defaults to 0)
                - previous_weight (float, optional, defaults to 0)
                - order_index (int)
                - notes (str, optional)
        
        Returns:
            Dictionary with 'workout' and 'exercises' keys containing
            serialized Workout and WorkoutExercise objects
        
        Raises:
            RuntimeError: If the workout creation fails
        """
        # Generate created_at timestamp
        created_at = Workout.now_iso()
        
        # Insert workout into database
        # Note: Table column is 'date', but method parameter is 'log_date' for clarity
        db_helper.execute_query(
            """
            INSERT INTO workouts (user_id, workout_name, date, notes, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, workout_name, log_date, notes, created_at)
        )
        
        # Fetch the inserted workout row
        workout_row = db_helper.fetch_one(
            """
            SELECT * FROM workouts
            WHERE user_id = ? AND workout_name = ? AND date = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id, workout_name, log_date)
        )
        
        if not workout_row:
            raise RuntimeError("Failed to create workout")
        
        # Convert row to Workout model
        workout = Workout.from_row(workout_row)
        
        # Insert all exercises into workout_exercises
        for exercise_dict in exercises_data:
            exercise_name = exercise_dict.get("exercise_name")
            sets = exercise_dict.get("sets")
            reps = exercise_dict.get("reps")
            weight_kg = exercise_dict.get("weight_kg", 0.0)
            previous_weight = exercise_dict.get("previous_weight", 0.0)
            order_index = exercise_dict.get("order_index")
            exercise_notes = exercise_dict.get("notes")
            
            db_helper.execute_query(
                """
                INSERT INTO workout_exercises (
                    workout_id, exercise_name, sets, reps, weight_kg,
                    previous_weight, order_index, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    workout.id,
                    exercise_name,
                    sets,
                    reps,
                    weight_kg,
                    previous_weight,
                    order_index,
                    exercise_notes,
                )
            )
        
        # Fetch all exercises back for this workout
        exercise_rows = db_helper.fetch_all(
            """
            SELECT * FROM workout_exercises
            WHERE workout_id = ?
            ORDER BY order_index ASC
            """,
            (workout.id,)
        )
        
        # Convert each row to WorkoutExercise model
        exercises = [WorkoutExercise.from_row(row) for row in exercise_rows]
        
        # Return clean dict suitable for JSON response
        return {
            "workout": workout.to_dict(),
            "exercises": [ex.to_dict() for ex in exercises]
        }

    @staticmethod
    def get_workout_detail(workout_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get workout details with all exercises for a specific workout.
        
        Args:
            workout_id: The ID of the workout to retrieve
            user_id: The ID of the user (for security - ensures user owns the workout)
        
        Returns:
            Dictionary with 'workout' and 'exercises' keys containing
            serialized Workout and WorkoutExercise objects, or None if not found
        """
        # Fetch the workout row
        workout_row = db_helper.fetch_one(
            """
            SELECT * FROM workouts
            WHERE id = ? AND user_id = ?
            """,
            (workout_id, user_id)
        )
        
        # If no workout is found, return None
        if not workout_row:
            return None
        
        # Convert the workout DB row → Workout model
        workout = Workout.from_row(workout_row)
        
        # Fetch all exercises belonging to this workout
        exercise_rows = db_helper.fetch_all(
            """
            SELECT * FROM workout_exercises
            WHERE workout_id = ?
            ORDER BY order_index ASC
            """,
            (workout_id,)
        )
        
        # Convert each exercise row → WorkoutExercise model
        exercises = [WorkoutExercise.from_row(row) for row in exercise_rows]
        
        # Return clean dictionary
        return {
            "workout": workout.to_dict(),
            "exercises": [ex.to_dict() for ex in exercises]
        }

    @staticmethod
    def delete_workout(workout_id: int, user_id: int) -> bool:
        """
        Delete a workout and its associated exercises.
        
        Args:
            workout_id: The ID of the workout to delete
            user_id: The ID of the user (for security - ensures user owns the workout)
        
        Returns:
            True if the workout was deleted, False if it didn't exist or doesn't belong to the user
        """
        # Verify that the workout belongs to the given user
        workout_row = db_helper.fetch_one(
            """
            SELECT id
            FROM workouts
            WHERE id = ? AND user_id = ?
            """,
            (workout_id, user_id)
        )
        
        # If no row is found, return False (nothing deleted, unauthorized or non-existent)
        if not workout_row:
            return False
        
        # Delete the workout (ON DELETE CASCADE will automatically delete related workout_exercises)
        db_helper.execute_query(
            """
            DELETE FROM workouts
            WHERE id = ?
            """,
            (workout_id,)
        )
        
        # Return True if deletion happened
        return True

    @staticmethod
    def update_workout(
        workout_id: int,
        user_id: int,
        workout_name: Optional[str] = None,
        log_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a workout's fields (partial update - only provided fields are updated).
        
        Args:
            workout_id: The ID of the workout to update
            user_id: The ID of the user (for security - ensures user owns the workout)
            workout_name: Optional new workout name
            log_date: Optional new log date
            notes: Optional new notes
        
        Returns:
            Dictionary representation of the updated workout, or None if not found/unauthorized
        """
        # Check that the workout exists and belongs to the given user
        workout_row = db_helper.fetch_one(
            """
            SELECT * FROM workouts
            WHERE id = ? AND user_id = ?
            """,
            (workout_id, user_id)
        )
        
        # If no row is found, return None
        if not workout_row:
            return None
        
        # Build list of fields to update (only non-None values)
        fields_to_update = []
        params = []
        
        if workout_name is not None:
            fields_to_update.append("workout_name = ?")
            params.append(workout_name)
        
        if log_date is not None:
            fields_to_update.append("date = ?")
            params.append(log_date)
        
        if notes is not None:
            fields_to_update.append("notes = ?")
            params.append(notes)
        
        # If there are no fields to update, just return the current workout
        if not fields_to_update:
            workout = Workout.from_row(workout_row)
            return workout.to_dict()
        
        # Add workout_id and user_id to params for WHERE clause
        params.extend([workout_id, user_id])
        
        # Build and execute the UPDATE statement
        set_clause = ", ".join(fields_to_update)
        db_helper.execute_query(
            f"""
            UPDATE workouts
            SET {set_clause}
            WHERE id = ? AND user_id = ?
            """,
            tuple(params)
        )
        
        # Fetch the updated workout row
        updated_workout_row = db_helper.fetch_one(
            """
            SELECT * FROM workouts
            WHERE id = ? AND user_id = ?
            """,
            (workout_id, user_id)
        )
        
        # Convert it using Workout.from_row
        workout = Workout.from_row(updated_workout_row)
        
        # Return dict representation
        return workout.to_dict()
