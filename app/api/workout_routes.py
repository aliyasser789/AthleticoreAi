from flask import request, jsonify
from app.services.workout_service import WorkoutService


def register_workout_routes(app):
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
        for i, exercise in enumerate(exercises):
            if not exercise.get("exercise_name"):
                return jsonify({"error": f"Exercise {i + 1}: exercise_name is required"}), 400
            if exercise.get("sets") is None:
                return jsonify({"error": f"Exercise {i + 1}: sets is required"}), 400
            if exercise.get("reps") is None:
                return jsonify({"error": f"Exercise {i + 1}: reps is required"}), 400
            if exercise.get("order_index") is None:
                return jsonify({"error": f"Exercise {i + 1}: order_index is required"}), 400
        
        try:
            result = WorkoutService.create_workout_for_users(
                user_id=int(user_id),
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
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/workouts/<int:workout_id>", methods=["GET"])
    def get_workout(workout_id):
        """Get workout details with all exercises."""
        data = request.get_json() or {}
        user_id = data.get("user_id")
        
        # Also check query parameters for user_id (flexibility)
        if not user_id:
            user_id = request.args.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        try:
            result = WorkoutService.get_workout_detail(
                workout_id=workout_id,
                user_id=int(user_id)
            )
            
            if not result:
                return jsonify({"error": "Workout not found"}), 404
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/workouts/<int:workout_id>", methods=["DELETE"])
    def delete_workout(workout_id):
        """Delete a workout and its exercises."""
        data = request.get_json() or {}
        user_id = data.get("user_id")
        
        # Also check query parameters for user_id (flexibility)
        if not user_id:
            user_id = request.args.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        try:
            deleted = WorkoutService.delete_workout(
                workout_id=workout_id,
                user_id=int(user_id)
            )
            
            if not deleted:
                return jsonify({"error": "Workout not found or unauthorized"}), 404
            
            return jsonify({"message": "Workout deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
            return jsonify({"error": str(e)}), 500

