from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.invoice import Invoice
import uuid

class IInvoiceRepository(ABC):
    @abstractmethod
    def create(self, invoice: Invoice) -> Invoice:
        pass
    
    @abstractmethod
    def findById(self, invoiceId: uuid.UUID) -> Optional[Invoice]:
        pass
    
    @abstractmethod
    def findByInvoiceNumber(self, invoiceNumber: str) -> Optional[Invoice]:
        pass
    
    @abstractmethod
    def findByCustomerId(self, customerId: uuid.UUID) -> List[Invoice]:
        pass

    @abstractmethod
    def findByWorkOrderId(self, workOrderId: uuid.UUID) -> Optional[Invoice]:
        pass
    
    @abstractmethod
    def update(self, invoice: Invoice) -> Invoice:
        pass
    
    @abstractmethod
    def findAll(self) -> List[Invoice]:
        pass
