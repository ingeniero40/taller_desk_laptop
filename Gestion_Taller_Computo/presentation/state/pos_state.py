import reflex as rx
from typing import List, Dict, Any, Optional
import uuid
from ...infrastructure.repositories.psycopg_invoice_repository import Psycopg2InvoiceRepository
from ...infrastructure.repositories.psycopg_invoice_item_repository import Psycopg2InvoiceItemRepository
from ...infrastructure.repositories.psycopg_payment_repository import Psycopg2PaymentRepository
from ...infrastructure.repositories.psycopg_product_repository import Psycopg2ProductRepository
from ...infrastructure.repositories.psycopg_inventory_movement_repository import Psycopg2InventoryMovementRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...application.use_cases.pos_manager import POSManager
from ...domain.value_objects.billing_types import PaymentMethod

class POSState(rx.State):
    """
    Estado del Punto de Venta (POS).
    Maneja el carrito, escaneo de códigos y procesamiento de venta.
    """
    
    cart: List[Dict[str, Any]] = []
    search_query: str = ""
    public_customer_id: str = ""
    payment_method: str = "Efectivo"
    received_amount: float = 0.0
    is_processing: bool = False
    show_success_modal: bool = False
    last_invoice_num: str = ""

    @rx.event
    def set_search_query(self, val: str):
        self.search_query = val

    @rx.event
    def set_payment_method(self, val: str):
        self.payment_method = val

    @rx.event
    def set_received_amount(self, val: str):
        try:
            self.received_amount = float(val)
        except ValueError:
            self.received_amount = 0.0
    
    @rx.var
    def total(self) -> float:
        return sum(item["total"] for item in self.cart)

    @rx.var
    def change(self) -> float:
        return max(0.0, self.received_amount - self.total)

    def on_load(self):
        """Prepara el POS."""
        self._ensure_public_customer()

    def _ensure_public_customer(self):
        try:
            repo = Psycopg2UserRepository()
            users = repo.findAll()
            for u in users:
                if u.full_name == "Público General":
                    self.public_customer_id = str(u.id)
                    break
        except Exception as e:
            print(f"Error finding public customer: {e}")

    @rx.event
    def add_to_cart(self, product_data: Dict[str, Any]):
        """Agrega un producto al carrito."""
        # Buscar si ya está
        for item in self.cart:
            if item["id"] == product_data["id"]:
                item["quantity"] += 1
                item["total"] = item["quantity"] * item["price"]
                self.cart = self.cart # Trigger update
                return
        
        # Nuevo item
        self.cart.append({
            "id": product_data["id"],
            "name": product_data["name"],
            "price": product_data["price"],
            "quantity": 1,
            "total": product_data["price"]
        })
        self.cart = self.cart # Trigger update

    @rx.event
    def remove_from_cart(self, product_id: str):
        self.cart = [item for item in self.cart if item["id"] != product_id]

    @rx.event
    def update_quantity(self, product_id: str, qty_str: str):
        try:
            qty = int(qty_str)
            if qty <= 0:
                return self.remove_from_cart(product_id)
            for item in self.cart:
                if item["id"] == product_id:
                    item["quantity"] = qty
                    item["total"] = qty * item["price"]
                    break
            self.cart = self.cart # Trigger update
        except ValueError:
            pass

    @rx.event
    def handle_barcode_scan(self, barcode: str):
        """Busca y agrega producto por código de barras."""
        if not barcode: return
        
        try:
            repo = Psycopg2ProductRepository()
            mgr = POSManager(None, None, repo, None) # Min implementation for search
            product = mgr.find_product_by_barcode(barcode)
            
            if product:
                if product["stock"] > 0:
                    self.add_to_cart(product)
                else:
                    return rx.window_alert(f"Stock insuficiente para {product['name']}")
            else:
                return rx.window_alert("Producto no encontrado.")
                
            self.search_query = "" # Clear input
        except Exception as e:
            print(f"Barcode error: {e}")

    @rx.event
    def finalize_sale(self):
        """Procesa la venta y genera factura."""
        if not self.cart:
            return rx.window_alert("El carrito está vacío.")
        
        if not self.public_customer_id:
            return rx.window_alert("No se encontró el cliente genérico. Verifique configuración.")

        self.is_processing = True
        try:
            # Init Manager
            invoice_repo = Psycopg2InvoiceRepository()
            item_repo = Psycopg2InvoiceItemRepository()
            payment_repo = Psycopg2PaymentRepository()
            product_repo = Psycopg2ProductRepository()
            movement_repo = Psycopg2InventoryMovementRepository()
            
            mgr = POSManager(invoice_repo, item_repo, payment_repo, product_repo, movement_repo)
            
            # Map cart for manager
            items = []
            for item in self.cart:
                items.append({
                    "product_id": item["id"],
                    "quantity": item["quantity"]
                })
            
            # Payment Method
            pm = PaymentMethod.CASH
            if self.payment_method == "Tarjeta": pm = PaymentMethod.CARD
            elif self.payment_method == "Transferencia": pm = PaymentMethod.TRANSFER

            invoice = mgr.process_pos_sale(
                customer_id=uuid.UUID(self.public_customer_id),
                items=items,
                payment_method=pm
            )
            
            self.last_invoice_num = invoice.invoice_number
            self.cart = []
            self.search_query = ""
            self.received_amount = 0.0
            self.show_success_modal = True
            
        except Exception as e:
            return rx.window_alert(f"Error procesando venta: {str(e)}")
        finally:
            self.is_processing = False

    @rx.event
    def close_success(self):
        self.show_success_modal = False
