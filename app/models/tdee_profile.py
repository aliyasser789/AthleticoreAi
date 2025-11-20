from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TDEEProfile:
    id: Optional[int]
    user_id: int
    age: Optional[int]
    gender: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    activity_level: Optional[str]
    tdee_value: Optional[float]
    goal_type: Optional[str]
    goal_offset: Optional[int]
    goal_calories: Optional[float]
    created_at: Optional[str]

    @classmethod
    def from_row(cls, row: tuple) -> "TDEEProfile":
        """
        Converts a DB row tuple into a TDEEProfile object.
        Order must match SELECT * column order exactly.
        """
        return cls(
            id=row[0],
            user_id=row[1],
            age=row[2],
            gender=row[3],
            height_cm=row[4],
            weight_kg=row[5],
            activity_level=row[6],
            tdee_value=row[7],
            goal_type=row[8],
            goal_offset=row[9],
            goal_calories=row[10],
            created_at=row[11],
        )

    def to_dict(self) -> dict:
        """
        Convert the object to a JSON-friendly dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "activity_level": self.activity_level,
            "tdee_value": self.tdee_value,
            "goal_type": self.goal_type,
            "goal_offset": self.goal_offset,
            "goal_calories": self.goal_calories,
            "created_at": self.created_at,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()