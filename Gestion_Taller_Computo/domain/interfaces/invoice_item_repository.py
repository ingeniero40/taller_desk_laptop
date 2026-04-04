from abc import ABC, abstractmethod
import uuid
from typing import List, Optional
from ..entities.invoice_item import InvoiceItem


class IInvoiceItemRepository(ABC):
    @abstractmethod
    def create(self, item: InvoiceItem) -> InvoiceItem:
        pass

    @abstractmethod
    def findByInvoiceId(self, invoice_id: uuid.UUID) -> List[InvoiceItem]:
        pass

    @abstractmethod
    def delete(self, item_id: uuid.UUID) -> bool:
        pass
