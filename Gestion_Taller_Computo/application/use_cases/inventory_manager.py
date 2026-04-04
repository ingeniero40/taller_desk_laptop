from typing import List, Optional
from ...domain.entities.product import Product
from ...domain.entities.supplier import Supplier
from ...domain.interfaces.product_repository import IProductRepository
from ...domain.interfaces.supplier_repository import ISupplierRepository
import uuid


from ...domain.interfaces.inventory_movement_repository import IInventoryMovementRepository
from ...domain.entities.inventory_movement import InventoryMovement

class InventoryManager:
    """
    Caso de uso para la gestión de inventario y proveedores.
    """

    def __init__(
        self, product_repo: IProductRepository, supplier_repo: ISupplierRepository,
        movement_repo: IInventoryMovementRepository = None
    ):
        self.product_repo = product_repo
        self.supplier_repo = supplier_repo
        self.movement_repo = movement_repo

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
        created = self.product_repo.create(new_product)
        
        if stock > 0 and self.movement_repo:
            mov = InventoryMovement(
                product_id=created.id,
                movement_type="IN",
                quantity=stock,
                notes="Stock inicial",
            )
            self.movement_repo.create(mov)
            
        return created

    def adjust_stock(self, product_id: uuid.UUID, quantity: int, reference_id: str = None, notes: str = None, user_id: uuid.UUID = None) -> bool:
        """
        Realiza ajustes manuales de stock (entradas/salidas).
        """
        if quantity == 0:
            return True
            
        success = self.product_repo.update_stock(product_id, quantity)
        if success and self.movement_repo:
            movement_type = "IN" if quantity > 0 else "OUT"
            mov = InventoryMovement(
                product_id=product_id,
                movement_type=movement_type,
                quantity=quantity,
                reference_id=reference_id,
                notes=notes,
                created_by_id=user_id
            )
            self.movement_repo.create(mov)
            
        return success
        
    def consume_part_for_order(self, product_id: uuid.UUID, quantity: int, order_id: uuid.UUID, user_id: uuid.UUID = None) -> bool:
        """
        Consume repuestos para una orden de trabajo.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a consumir debe ser positiva.")
            
        product = self.product_repo.findById(product_id)
        if not product or product.stock < quantity:
            raise ValueError("Stock insuficiente.")
            
        return self.adjust_stock(
            product_id, -quantity, reference_id=str(order_id), notes="Consumido en Orden de Trabajo", user_id=user_id
        )

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

    def get_product_movement_history(self, product_id: uuid.UUID) -> List[InventoryMovement]:
        """
        Recupera el historial de movimientos de un producto específico.
        """
        if not self.movement_repo:
            return []
        return self.movement_repo.findByProductId(product_id)

    def get_all_movements(self) -> List[InventoryMovement]:
        """
        Recupera todos los movimientos del inventario (para reportes).
        """
        if not self.movement_repo:
            return []
        return self.movement_repo.findAll()
