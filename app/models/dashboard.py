from dataclasses import dataclass
from typing import Optional


@dataclass
class Dashboard:
    current_goal: str
    daily_calorie_target: float
    calories_consumed_today: float
    calories_left: float
    calorie_progress_percent: float
    next_workout: Optional[str]

    def to_dict(self) -> dict:
        return {
            "current_goal": self.current_goal,
            "daily_calorie_target": self.daily_calorie_target,
            "calories_consumed_today": self.calories_consumed_today,
            "calories_left": self.calories_left,
            "calorie_progress_percent": self.calorie_progress_percent,
            "next_workout": self.next_workout
        }

