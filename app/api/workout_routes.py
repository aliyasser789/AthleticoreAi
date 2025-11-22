from flask import request, jsonify
from app.services.workout_service import WorkoutService
import traceback
import sqlite3


def register_workout_routes(app):
    @app.route("/api/workouts", methods=["GET"])
    def get_workouts():
        """Get all workouts for a user."""
        try:
            user_id = request.args.get("user_id", type=int)
            
            if not user_id:
                return jsonify({"error": "user_id is required as a query parameter"}), 400
            
            workouts = WorkoutService.get_workouts_for_user(user_id)
            
            return jsonify({
                "workouts": workouts
            }), 200
        except Exception as e:
            print(f"Error getting workouts: {e}")
            traceback.print_exc()
            return jsonify({"error": "An unexpected error occurred"}), 500

    @app.route("/api/workouts", methods=["POST"])
    def create_workout():
        """Create a new workout with exercises."""
        data = request.get_json() or {}
        
        user_id = data.get("user_id")
        workout_name = data.get("workout_name")
        log_date = data.get("log_date")
        notes = data.get("notes")
        exercises = data.get("exercises", [])
        
        # Validate required fields
        missing_fields = []
        if not user_id:
            missing_fields.append("user_id")
        if not workout_name:
            missing_fields.append("workout_name")
        if not log_date:
            missing_fields.append("log_date")
        if not exercises:
            missing_fields.append("exercises")
        
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Validate exercises structure
        if not isinstance(exercises, list) or len(exercises) == 0:
            return jsonify({"error": "At least one exercise is required"}), 400
        
        for i, exercise in enumerate(exercises):
            if not isinstance(exercise, dict):
                return jsonify({"error": f"Exercise {i + 1}: must be an object"}), 400
            exercise_name = exercise.get("exercise_name")
            if not exercise_name or not str(exercise_name).strip():
                return jsonify({"error": f"Exercise {i + 1}: exercise_name is required"}), 400
            sets_value = exercise.get("sets")
            if sets_value is None or (isinstance(sets_value, (int, float)) and sets_value <= 0):
                return jsonify({"error": f"Exercise {i + 1}: sets is required and must be greater than 0"}), 400
            reps_value = exercise.get("reps")
            if reps_value is None or (isinstance(reps_value, (int, float)) and reps_value <= 0):
                return jsonify({"error": f"Exercise {i + 1}: reps is required and must be greater than 0"}), 400
            if exercise.get("order_index") is None:
                return jsonify({"error": f"Exercise {i + 1}: order_index is required"}), 400
        
        try:
            # Convert user_id to int
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid user_id format"}), 400
            
            result = WorkoutService.create_workout_for_users(
                user_id=user_id_int,
                workout_name=workout_name,
                log_date=log_date,
                notes=notes,
                exercises_data=exercises
            )
            
            return jsonify({
                "message": "Workout created successfully",
                **result
            }), 201
        except RuntimeError as e:
            error_msg = str(e)
            print(f"Error creating workout: {error_msg}")
            traceback.print_exc()
            return jsonify({"error": f"Failed to create workout: {error_msg}"}), 500
        except ValueError as e:
            error_msg = str(e)
            print(f"Value error in create_workout: {error_msg}")
            traceback.print_exc()
            return jsonify({"error": f"Invalid input: {error_msg}"}), 400
        except sqlite3.OperationalError as e:
            error_msg = str(e)
            print(f"Database error in create_workout: {error_msg}")
            traceback.print_exc()
            if "no such table" in error_msg.lower():
                return jsonify({"error": "Database tables not initialized. Please run: python app/db/init_db.py"}), 500
            return jsonify({"error": f"Database error: {error_msg}"}), 500
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            print(f"Unexpected error in create_workout ({error_type}): {error_msg}")
            traceback.print_exc()
            # Return the actual error message to help with debugging
            return jsonify({"error": f"An unexpected error occurred: {error_msg} (Type: {error_type})"}), 500

    @app.route("/api/workouts/<int:workout_id>", methods=["GET"])
    def get_workout(workout_id):
        """Get workout details with all exercises."""
        try:
            # GET requests should use query parameters, not JSON body
            user_id = request.args.get("user_id", type=int)
            
            if not user_id:
                return jsonify({"error": "user_id is required as a query parameter"}), 400
            
            result = WorkoutService.get_workout_detail(
                workout_id=workout_id,
                user_id=user_id
            )
            
            if not result:
                return jsonify({"error": "Workout not found or unauthorized"}), 404
            
            return jsonify(result), 200
        except Exception as e:
            print(f"Error getting workout detail: {e}")
            traceback.print_exc()
            return jsonify({"error": "An unexpected error occurred"}), 500

    @app.route("/api/workouts/<int:workout_id>", methods=["DELETE"])
    def delete_workout(workout_id):
        """Delete a workout and its exercises."""
        try:
            # DELETE can use query params or JSON body
            user_id = request.args.get("user_id", type=int)
            if not user_id:
                data = request.get_json() or {}
                user_id = data.get("user_id")
            
            if not user_id:
                return jsonify({"error": "user_id is required"}), 400
            
            deleted = WorkoutService.delete_workout(
                workout_id=workout_id,
                user_id=int(user_id)
            )
            
            if not deleted:
                return jsonify({"error": "Workout not found or unauthorized"}), 404
            
            return jsonify({"message": "Workout deleted successfully"}), 200
        except Exception as e:
            print(f"Error deleting workout: {e}")
            traceback.print_exc()
            return jsonify({"error": "An unexpected error occurred"}), 500

    @app.route("/api/workouts/<int:workout_id>", methods=["PATCH"])
    def update_workout(workout_id):
        """Update a workout's fields (partial update)."""
        data = request.get_json() or {}
        user_id = data.get("user_id")
        workout_name = data.get("workout_name")
        log_date = data.get("log_date")
        notes = data.get("notes")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # At least one field must be provided for update
        if workout_name is None and log_date is None and notes is None:
            return jsonify({"error": "At least one field (workout_name, log_date, notes) must be provided"}), 400
        
        try:
            result = WorkoutService.update_workout(
                workout_id=workout_id,
                user_id=int(user_id),
                workout_name=workout_name,
                log_date=log_date,
                notes=notes
            )
            
            if not result:
                return jsonify({"error": "Workout not found or unauthorized"}), 404
            
            return jsonify({
                "message": "Workout updated successfully",
                "workout": result
            }), 200
        except Exception as e:
            print(f"Error updating workout: {e}")
            traceback.print_exc()
            return jsonify({"error": "An unexpected error occurred"}), 500

