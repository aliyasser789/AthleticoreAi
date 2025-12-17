from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, TypeVar, Type, List, Dict


ModelType = TypeVar("ModelType", bound="BaseModel")


class BaseModel(ABC):
    """
    Shared model contract to enforce serialization and construction helpers.
    """

    @classmethod
    @abstractmethod
    def from_row(cls: Type[ModelType], row: tuple) -> ModelType:
        """Build an instance from a DB row (column order is model-specific)."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Dict:
        """Serialize the model to a dictionary suitable for JSON responses."""
        raise NotImplementedError

    def as_dict(self) -> Dict:
        """
        Polymorphic alias for to_dict so callers can treat all models uniformly.
        """
        return self.to_dict()

    @staticmethod
    def serialize_many(models: Iterable["BaseModel"]) -> List[Dict]:
        """
        Serialize any iterable of BaseModel subclasses without knowing
        their concrete types (simple runtime polymorphism).
        """
        return [model.to_dict() for model in models]

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()
