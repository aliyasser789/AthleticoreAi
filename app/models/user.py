from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    password_hash: str
    created_at: str
    updated_at: Optional[str]
    age: int
    gender: str
    height: int
    weight: int

    @classmethod
    def from_row(cls, row: tuple) -> "User":
        """
        row must come from:
        SELECT * FROM users
        with columns in this exact order:
        id, username, email, password_hash, created_at,
        updated_at, age, gender, height, weight
        """
        return cls(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            created_at=row[4],
            updated_at=row[5],
            age=row[6],
            gender=row[7],
            height=row[8],
            weight=row[9],
        )

    def to_dict(self) -> dict:
        # password_hash is intentionally not exposed here
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "age": self.age,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

    