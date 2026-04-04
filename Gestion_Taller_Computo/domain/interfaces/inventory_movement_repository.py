from abc import ABC, abstractmethod
import uuid
from typing import List
from ..entities.inventory_movement import InventoryMovement

class IInventoryMovementRepository(ABC):
    @abstractmethod
    def create(self, movement: InventoryMovement) -> InventoryMovement:
        pass

    @abstractmethod
    def findByProductId(self, product_id: uuid.UUID) -> List[InventoryMovement]:
        pass

    @abstractmethod
    def findByReferenceId(self, reference_id: str) -> List[InventoryMovement]:
        pass
