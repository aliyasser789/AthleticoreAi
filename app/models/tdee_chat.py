from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TdeeChat:
    id: Optional[int]
    tdee_profile_id: int
    role: str
    content: str
    created_at: str

    @classmethod
    def from_row(cls, row: tuple) -> "TdeeChat":
        """
        row must come from:
        SELECT * FROM tdee_chat
        with columns in this exact order:
        id, tdee_profile_id, role, content, created_at
        """
        return cls(
            id=row[0],
            tdee_profile_id=row[1],
            role=row[2],
            content=row[3],
            created_at=row[4],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tdee_profile_id": self.tdee_profile_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

