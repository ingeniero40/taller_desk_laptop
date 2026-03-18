from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.payment import Payment
import uuid

class IPaymentRepository(ABC):
    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def findById(self, paymentId: uuid.UUID) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def findByInvoiceId(self, invoiceId: uuid.UUID) -> List[Payment]:
        pass
    
    @abstractmethod
    def findAll(self) -> List[Payment]:
        pass
