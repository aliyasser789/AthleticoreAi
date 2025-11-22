from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date, date

@dataclass
class CalorieLog:# name of the class is CalorieLog
    #data fields of the class
    id: Optional[int]
    user_id: int
    entry_date: str
    created_at: str
    # Optional fields mumken yethato aw la'
    description: Optional[str] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    is_deleted: int = 0      # 0 = active, 1 = deleted
    @classmethod
    def from_row(cls, row: tuple) -> "CalorieLog":
        """
        method that creates a CalorieLog object from a database row
        """
        return cls(
            id=row[0],
            user_id=row[1],
            entry_date=row[2],
            created_at=row[8],  # created_at is at index 8 in DB
            description=row[3],
            calories=row[4],
            protein_g=row[5],
            carbs_g=row[6],
            fat_g=row[7],
            is_deleted=row[9],
        )
    def to_dict(self) -> dict:
       #retuns object of class by json format
        return {
            "id": self.id,
            "user_id": self.user_id,
            "entry_date": self.entry_date,
            "description": self.description,
            "calories": self.calories,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "created_at": self.created_at,
            "is_deleted": self.is_deleted,
        }
    @staticmethod
    #for timestamp
    def now_iso() -> str:
        return datetime.utcnow().isoformat()
    
    @staticmethod
    #for today's date
    def today_iso() -> str:
        return date.today().isoformat()
