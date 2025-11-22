from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class WorkoutExercise:
    id: Optional[int]
    workout_id: int
    exercise_name: str
    sets: Optional[int]
    reps: Optional[int]
    weight_kg: Optional[float]
    previous_weight: Optional[float]
    order_index: int
    notes: Optional[str]

    @classmethod
    def from_row(cls, row: tuple) -> "WorkoutExercise":
        """
        row must come from:
        SELECT * FROM workout_exercises
        with columns in this exact order:
        id, workout_id, exercise_name, sets, reps, weight_kg,
        previous_weight, order_index, notes
        """
        return cls(
            id=row[0],
            workout_id=row[1],
            exercise_name=row[2],
            sets=row[3],
            reps=row[4],
            weight_kg=row[5],
            previous_weight=row[6],
            order_index=row[7],
            notes=row[8],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workout_id": self.workout_id,
            "exercise_name": self.exercise_name,
            "sets": self.sets,
            "reps": self.reps,
            "weight_kg": self.weight_kg,
            "previous_weight": self.previous_weight,
            "order_index": self.order_index,
            "notes": self.notes,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

