from typing import List, Optional
from ...domain.entities.product import Product
from ...domain.entities.supplier import Supplier
from ...domain.interfaces.product_repository import IProductRepository
from ...domain.interfaces.supplier_repository import ISupplierRepository
import uuid


class InventoryManager:
    """
    Caso de uso para la gestión de inventario y proveedores.
    """

    def __init__(
        self, product_repo: IProductRepository, supplier_repo: ISupplierRepository
    ):
        self.product_repo = product_repo
        self.supplier_repo = supplier_repo

    # --- Gestión de Proveedores ---

    def register_supplier(
        self,
        name: str,
        contact: str = None,
        email: str = None,
        phone: str = None,
        address: str = None,
    ) -> Supplier:
        new_supplier = Supplier(
            name=name, contact_name=contact, email=email, phone=phone, address=address
        )
        return self.supplier_repo.create(new_supplier)

    def get_all_suppliers(self, only_active: bool = True) -> List[Supplier]:
        return self.supplier_repo.findAll(only_active)

    # --- Gestión de Productos ---

    def add_product(
        self,
        sku: str,
        name: str,
        cost: float,
        price: float,
        stock: int = 0,
        min_stock: int = 5,
        category: str = "Repuestos",
        supplier_id: uuid.UUID = None,
    ) -> Product:
        """
        Agrega un producto al inventario validando SKU único.
        """
        existing = self.product_repo.findBySku(sku)
        if existing:
            raise ValueError(f"Ya existe un producto con SKU '{sku}'.")

        new_product = Product(
            sku=sku,
            name=name,
            cost_price=cost,
            sale_price=price,
            stock=stock,
            min_stock=min_stock,
            category=category,
            supplier_id=supplier_id,
        )
        return self.product_repo.create(new_product)

    def adjust_stock(self, product_id: uuid.UUID, quantity: int) -> bool:
        """
        Realiza ajustes manuales de stock (entradas/salidas).
        """
        return self.product_repo.update_stock(product_id, quantity)

    def get_low_stock_reports(self) -> List[Product]:
        """
        Lista productos que están por debajo del stock mínimo.
        """
        all_products = self.product_repo.findAll()
        return [p for p in all_products if p.stock <= p.min_stock]

    def get_inventory_valuation(self) -> float:
        """
        Calcula el valor total del inventario a precio de costo.
        """
        all_products = self.product_repo.findAll()
        return sum(p.stock * p.cost_price for p in all_products)
