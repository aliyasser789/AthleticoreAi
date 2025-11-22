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
            raise RuntimeError("Failed to create workout - workout was not inserted or could not be retrieved")
        
        # Convert row to Workout model
        workout = Workout.from_row(workout_row)
        
        # Insert all exercises into workout_exercises
        for idx, exercise_dict in enumerate(exercises_data):
            exercise_name = exercise_dict.get("exercise_name")
            sets = exercise_dict.get("sets")
            reps = exercise_dict.get("reps")
            weight_kg = exercise_dict.get("weight_kg", 0.0)
            previous_weight = exercise_dict.get("previous_weight", 0.0)
            order_index = exercise_dict.get("order_index")
            exercise_notes = exercise_dict.get("notes")
            
            # Validate required fields before inserting
            if not exercise_name:
                raise ValueError(f"Exercise {idx + 1}: exercise_name is required")
            if sets is None:
                raise ValueError(f"Exercise {idx + 1}: sets is required")
            if reps is None:
                raise ValueError(f"Exercise {idx + 1}: reps is required")
            if order_index is None:
                raise ValueError(f"Exercise {idx + 1}: order_index is required")
            
            try:
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
            except Exception as e:
                raise RuntimeError(f"Failed to insert exercise {idx + 1} ({exercise_name}): {str(e)}")
        
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
    def get_workouts_for_user(user_id: int) -> List[Dict[str, Any]]:
        """
        Get all workouts for a specific user.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            List of dictionaries, each containing 'workout' and 'exercises' keys
        """
        # Fetch all workouts for this user
        workout_rows = db_helper.fetch_all(
            """
            SELECT * FROM workouts
            WHERE user_id = ?
            ORDER BY date DESC, created_at DESC
            """,
            (user_id,)
        )
        
        if not workout_rows:
            return []
        
        # For each workout, get its exercises
        result = []
        for workout_row in workout_rows:
            workout = Workout.from_row(workout_row)
            
            # Get exercises for this workout
            exercise_rows = db_helper.fetch_all(
                """
                SELECT * FROM workout_exercises
                WHERE workout_id = ?
                ORDER BY order_index ASC
                """,
                (workout.id,)
            )
            
            exercises = [WorkoutExercise.from_row(row) for row in exercise_rows]
            
            result.append({
                "workout": workout.to_dict(),
                "exercises": [ex.to_dict() for ex in exercises]
            })
        
        return result

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

    @staticmethod
    def update_workout_with_exercises(
        workout_id: int,
        user_id: int,
        workout_name: Optional[str] = None,
        notes: Optional[str] = None,
        exercises: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a workout and its exercises.
        
        Args:
            workout_id: The ID of the workout to update
            user_id: The ID of the user (for security - ensures user owns the workout)
            workout_name: Optional new workout name
            notes: Optional new notes
            exercises: Optional list of exercise dictionaries to update/create
        
        Returns:
            Dictionary with 'workout' and 'exercises' keys containing
            serialized Workout and WorkoutExercise objects, or None if not found
        """
        # Verify that the workout exists and belongs to the given user
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
        
        # Update workout fields if provided
        if workout_name is not None or notes is not None:
            fields_to_update = []
            params = []
            
            if workout_name is not None:
                fields_to_update.append("workout_name = ?")
                params.append(workout_name)
            
            if notes is not None:
                fields_to_update.append("notes = ?")
                params.append(notes)
            
            if fields_to_update:
                params.extend([workout_id, user_id])
                set_clause = ", ".join(fields_to_update)
                db_helper.execute_query(
                    f"""
                    UPDATE workouts
                    SET {set_clause}
                    WHERE id = ? AND user_id = ?
                    """,
                    tuple(params)
                )
        
        # Update exercises if provided
        if exercises is not None:
            # Get existing exercise IDs for this workout
            existing_exercise_rows = db_helper.fetch_all(
                """
                SELECT id FROM workout_exercises
                WHERE workout_id = ?
                """,
                (workout_id,)
            )
            existing_exercise_ids = {row[0] for row in existing_exercise_rows}
            
            # Process each exercise in the provided list
            provided_exercise_ids = set()
            for idx, exercise_dict in enumerate(exercises):
                exercise_id = exercise_dict.get("id")
                exercise_name = exercise_dict.get("exercise_name", "").strip()
                
                if not exercise_name:
                    continue  # Skip exercises without names
                
                sets = exercise_dict.get("sets", 0)
                reps = exercise_dict.get("reps", 0)
                weight_kg = exercise_dict.get("weight_kg", 0.0)
                previous_weight = exercise_dict.get("previous_weight", 0.0)
                exercise_notes = exercise_dict.get("notes", "")
                order_index = exercise_dict.get("order_index", idx)
                
                if exercise_id and exercise_id in existing_exercise_ids:
                    # Update existing exercise
                    provided_exercise_ids.add(exercise_id)
                    db_helper.execute_query(
                        """
                        UPDATE workout_exercises
                        SET exercise_name = ?, sets = ?, reps = ?, weight_kg = ?,
                            previous_weight = ?, order_index = ?, notes = ?
                        WHERE id = ? AND workout_id = ?
                        """,
                        (
                            exercise_name, sets, reps, weight_kg,
                            previous_weight, order_index, exercise_notes,
                            exercise_id, workout_id
                        )
                    )
                else:
                    # Insert new exercise
                    db_helper.execute_query(
                        """
                        INSERT INTO workout_exercises (
                            workout_id, exercise_name, sets, reps, weight_kg,
                            previous_weight, order_index, notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            workout_id, exercise_name, sets, reps, weight_kg,
                            previous_weight, order_index, exercise_notes,
                        )
                    )
            
            # Delete exercises that were not in the provided list
            exercises_to_delete = existing_exercise_ids - provided_exercise_ids
            if exercises_to_delete:
                placeholders = ",".join("?" * len(exercises_to_delete))
                db_helper.execute_query(
                    f"""
                    DELETE FROM workout_exercises
                    WHERE id IN ({placeholders}) AND workout_id = ?
                    """,
                    tuple(exercises_to_delete) + (workout_id,)
                )
        
        # Fetch the updated workout
        updated_workout_row = db_helper.fetch_one(
            """
            SELECT * FROM workouts
            WHERE id = ? AND user_id = ?
            """,
            (workout_id, user_id)
        )
        
        workout = Workout.from_row(updated_workout_row)
        
        # Fetch all exercises for this workout
        exercise_rows = db_helper.fetch_all(
            """
            SELECT * FROM workout_exercises
            WHERE workout_id = ?
            ORDER BY order_index ASC
            """,
            (workout_id,)
        )
        
        exercises = [WorkoutExercise.from_row(row) for row in exercise_rows]
        
        # Return clean dictionary
        return {
            "workout": workout.to_dict(),
            "exercises": [ex.to_dict() for ex in exercises]
        }
