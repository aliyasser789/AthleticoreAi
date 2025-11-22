from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Workout:
    id: Optional[int]
    user_id: int
    workout_name: str
    date: str
    notes: Optional[str]
    created_at: str

    @classmethod
    def from_row(cls, row: tuple) -> "Workout":
        """
        row must come from:
        SELECT * FROM workouts
        with columns in this exact order:
        id, user_id, workout_name, date, notes, created_at
        """
        return cls(
            id=row[0],
            user_id=row[1],
            workout_name=row[2],
            date=row[3],
            notes=row[4],
            created_at=row[5],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "workout_name": self.workout_name,
            "date": self.date,
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

