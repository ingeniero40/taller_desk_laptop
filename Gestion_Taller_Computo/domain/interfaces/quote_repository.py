from abc import ABC, abstractmethod
import uuid
from typing import List, Optional
from ..entities.quote import Quote

class IQuoteRepository(ABC):
    @abstractmethod
    def create(self, quote: Quote) -> Quote:
        pass

    @abstractmethod
    def findById(self, quote_id: uuid.UUID) -> Optional[Quote]:
        pass

    @abstractmethod
    def findByQuoteNumber(self, quote_number: str) -> Optional[Quote]:
        pass

    @abstractmethod
    def findByWorkOrderId(self, work_order_id: uuid.UUID) -> List[Quote]:
        pass

    @abstractmethod
    def findByCustomerId(self, customer_id: uuid.UUID) -> List[Quote]:
        pass

    @abstractmethod
    def update(self, quote: Quote) -> Quote:
        pass

    @abstractmethod
    def findAll(self) -> List[Quote]:
        pass
