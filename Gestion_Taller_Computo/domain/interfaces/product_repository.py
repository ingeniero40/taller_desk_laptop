from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.product import Product
import uuid


class IProductRepository(ABC):
    """
    Interfaz de repositorio para productos e inventario.
    """

    @abstractmethod
    def create(self, product: Product) -> Product:
        """Agrega un nuevo producto al catálogo."""
        pass

    @abstractmethod
    def findById(self, productId: uuid.UUID) -> Optional[Product]:
        """Busca un producto por su ID."""
        pass

    @abstractmethod
    def findBySku(self, sku: str) -> Optional[Product]:
        """Busca un producto por su código SKU."""
        pass

    @abstractmethod
    def findAll(self) -> List[Product]:
        """Recupera la lista total de productos en inventario."""
        pass

    @abstractmethod
    def findByCategory(self, category: str) -> List[Product]:
        """Recupera productos de una categoría específica."""
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        """Actualiza la información técnica, precios o stock del producto."""
        pass

    @abstractmethod
    def update_stock(self, productId: uuid.UUID, quantity_change: int) -> bool:
        """Incrementa o decrementa el stock actual de un producto."""
        pass

    @abstractmethod
    def delete(self, productId: uuid.UUID) -> bool:
        """Elimina un producto del catálogo."""
        pass
