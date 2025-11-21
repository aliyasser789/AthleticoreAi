from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TdeeProfile:
    id: Optional[int]
    user_id: int
    activity_level: str
    tdee_value: float
    goal_type: str
    goal_offset: int
    goal_calories: float
    created_at: str
    updated_at: Optional[str]

    @classmethod
    def from_row(cls, row: tuple) -> "TdeeProfile":
        """
        row must come from:
        SELECT * FROM tdee_profile
        with columns in this exact order:
        id, user_id, activity_level, tdee_value, goal_type,
        goal_offset, goal_calories, created_at, updated_at
        """
        return cls(
            id=row[0],
            user_id=row[1],
            activity_level=row[2],
            tdee_value=row[3],
            goal_type=row[4],
            goal_offset=row[5],
            goal_calories=row[6],
            created_at=row[7],
            updated_at=row[8],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_level": self.activity_level,
            "tdee_value": self.tdee_value,
            "goal_type": self.goal_type,
            "goal_offset": self.goal_offset,
            "goal_calories": self.goal_calories,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

