from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ChatMessage:
    id: Optional[int]
    user_id: int
    sender: str
    message: str
    created_at: str

    @classmethod
    def from_row(cls, row: tuple) -> "ChatMessage":
        """
        row must come from:
        SELECT * FROM chat_messages
        with columns in this exact order:
        id, user_id, sender, message, created_at
        """
        return cls(
            id=row[0],
            user_id=row[1],
            sender=row[2],
            message=row[3],
            created_at=row[4],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sender": self.sender,
            "message": self.message,
            "created_at": self.created_at,
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()

