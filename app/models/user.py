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
    updated_at: Optional[str] = None

    @classmethod  # this means this method belongs to the class
    def from_row(cls, row: tuple) -> "User":
        return cls(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            created_at=row[4],
            updated_at=row[5],
        )

    def to_dict(self) -> dict:
       
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()


    