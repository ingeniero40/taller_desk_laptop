from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.supplier import Supplier
import uuid

class ISupplierRepository(ABC):
    """
    Interfaz de repositorio para proveedores.
    """
    
    @abstractmethod
    def create(self, supplier: Supplier) -> Supplier:
        """Registra un nuevo proveedor."""
        pass
    
    @abstractmethod
    def findById(self, supplierId: uuid.UUID) -> Optional[Supplier]:
        """Busca un proveedor por su ID."""
        pass
    
    @abstractmethod
    def findAll(self, only_active: bool = True) -> List[Supplier]:
        """Recupera la lista de proveedores."""
        pass
    
    @abstractmethod
    def update(self, supplier: Supplier) -> Supplier:
        """Actualiza la información de un proveedor."""
        pass
    
    @abstractmethod
    def delete(self, supplierId: uuid.UUID) -> bool:
        """Elimina (o desactiva) un proveedor."""
        pass
