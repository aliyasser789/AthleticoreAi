from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class FoodFeed:
    id: Optional[int]
    user_id: int
    content: str
    food_name: Optional[str]
    calories: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    entry_date: str
    created_at: str

    @classmethod
    def from_row(cls, row: tuple) -> "FoodFeed":
        """
        row must come from:
        SELECT * FROM food_feed
        with columns in this exact order:
        id, user_id, content, food_name, calories, protein_g, carbs_g, fat_g, entry_date, created_at
        """
        return cls(
            id=row[0],
            user_id=row[1],
            content=row[2],
            food_name=row[3],
            calories=row[4],
            protein_g=row[5],
            carbs_g=row[6],
            fat_g=row[7],
            entry_date=row[8],
            created_at=row[9],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "food_name": self.food_name,
            "calories": self.calories,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "entry_date": self.entry_date,
            "created_at": self.created_at,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

