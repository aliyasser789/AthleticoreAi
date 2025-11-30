from typing import Optional
from datetime import datetime, date
from app.db import db_helper
from app.models.dashboard import Dashboard
from app.services.tdee_service import TdeeService
from app.services.calorie_tracker import Calorie_manager


class DashboardService:
    @staticmethod
    def get_dashboard_data(user_id: int) -> Dashboard:
        """
        Get dashboard data for a user.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            Dictionary with current_goal, calories_left, next_workout, etc.
        """
        # Get TDEE profile for goal and calorie target
        tdee_profile = TdeeService.get_profile_by_user_id(user_id)
        
        # Default values
        current_goal = "maintaining"
        daily_calorie_target = 2000.0
        goal_calories = 2000.0
        
        if tdee_profile:
            current_goal = tdee_profile.goal_type
            goal_calories = tdee_profile.goal_calories
            daily_calorie_target = goal_calories
        
        # Get calories consumed today
        calories_consumed_today = Calorie_manager.get_today_total_calories(user_id)
        
        # Calculate calories left
        calories_left = max(0, daily_calorie_target - calories_consumed_today)
        
        # Calculate progress percentage (0-100)
        if daily_calorie_target > 0:
            calorie_progress_percent = min(100, (calories_consumed_today / daily_calorie_target) * 100)
        else:
            calorie_progress_percent = 0.0
        
        # Get next workout
        next_workout = DashboardService._get_next_workout(user_id)
        if next_workout is None:
            next_workout = "No upcoming workout"
        
        # Create and return Dashboard model
        return Dashboard(
            current_goal=current_goal,
            daily_calorie_target=daily_calorie_target,
            calories_consumed_today=calories_consumed_today,
            calories_left=calories_left,
            calorie_progress_percent=calorie_progress_percent,
            next_workout=next_workout
        )
    
    @staticmethod
    def _get_next_workout(user_id: int) -> Optional[str]:
        """
        Get the next scheduled workout for a user.
        First tries to find future workouts (including today), 
        then falls back to the most recent past workout.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            Formatted string like "Pull Day - Today" or None if no workout exists
        """
        today = date.today().isoformat()
        
        # Get all workouts for this user to find the next one
        # We'll do the date comparison in Python to handle any date format issues
        all_workouts = db_helper.fetch_all(
            """
            SELECT workout_name, date
            FROM workouts
            WHERE user_id = ?
            ORDER BY date ASC
            """,
            (user_id,)
        )
        
        if not all_workouts:
            print(f"No workouts found for user_id: {user_id}")
            return None
        
        print(f"Found {len(all_workouts)} workout(s) for user_id: {user_id}")
        for w in all_workouts:
            print(f"  - {w[0]} on {w[1]}")
        
        # Find the next workout (including today or future)
        today_obj = date.today()
        next_workout_row = None
        
        for workout_row in all_workouts:
            workout_date_str = workout_row[1]
            try:
                # Parse the date string
                if 'T' in workout_date_str:
                    workout_date_obj = datetime.fromisoformat(workout_date_str).date()
                else:
                    workout_date_obj = datetime.fromisoformat(workout_date_str + 'T00:00:00').date()
                
                # If this workout is today or in the future, use it
                if workout_date_obj >= today_obj:
                    next_workout_row = workout_row
                    break
            except Exception as e:
                print(f"Error parsing workout date '{workout_date_str}': {e}")
                continue
        
        # If no future workout found, use the most recent one (last in list since sorted ASC)
        if next_workout_row is None:
            print(f"No future workouts found, using most recent past workout")
            next_workout_row = all_workouts[-1]  # Last workout (most recent)
        
        row = next_workout_row
        
        if row is None:
            return None
        
        workout_name = row[0]
        workout_date = row[1]
        
        # Format the date nicely
        try:
            # Handle both ISO date strings (YYYY-MM-DD) and datetime strings
            if 'T' in workout_date:
                date_obj = datetime.fromisoformat(workout_date).date()
            else:
                date_obj = datetime.fromisoformat(workout_date + 'T00:00:00').date()
            
            today_obj = date.today()
            
            if date_obj == today_obj:
                return f"{workout_name} - Today"
            else:
                from datetime import timedelta
                tomorrow = today_obj + timedelta(days=1)
                if date_obj == tomorrow:
                    return f"{workout_name} - Tomorrow"
                elif date_obj > today_obj:
                    # Future date - Format as "Month Day" (e.g., "Jan 15")
                    return f"{workout_name} - {date_obj.strftime('%b %d')}"
                else:
                    # Past date - Format as "Month Day" (e.g., "Jan 15")
                    return f"{workout_name} - {date_obj.strftime('%b %d')}"
        except Exception as e:
            # If date parsing fails, just return the name
            print(f"Error parsing workout date '{workout_date}': {e}")
            return workout_name

