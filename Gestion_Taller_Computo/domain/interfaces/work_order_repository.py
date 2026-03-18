from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.work_order import WorkOrder
from ..value_objects.work_order_status import WorkOrderStatus
import uuid

class IWorkOrderRepository(ABC):
    """
    Interfaz de repositorio de órdenes de trabajo siguiendo Clean Architecture.
    """
    
    @abstractmethod
    def create(self, workOrder: WorkOrder) -> WorkOrder:
        """Crea una nueva orden de trabajo."""
        pass
    
    @abstractmethod
    def findById(self, orderId: uuid.UUID) -> Optional[WorkOrder]:
        """Busca una orden por su ID."""
        pass
    
    @abstractmethod
    def findByTicketNumber(self, ticketNumber: str) -> Optional[WorkOrder]:
        """Busca una orden por su número de ticket único."""
        pass
    
    @abstractmethod
    def findByDeviceId(self, deviceId: uuid.UUID) -> List[WorkOrder]:
        """Recupera el historial de órdenes de un dispositivo."""
        pass
    
    @abstractmethod
    def findByStatus(self, status: WorkOrderStatus) -> List[WorkOrder]:
        """Filtra órdenes por estado (ej. pendientes, completadas)."""
        pass
    
    @abstractmethod
    def update(self, workOrder: WorkOrder) -> WorkOrder:
        """Actualiza el estado, diagnóstico o notas de la orden."""
        pass
    
    @abstractmethod
    def findAll(self) -> List[WorkOrder]:
        """Recupera todas las órdenes registradas."""
        pass
