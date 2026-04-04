import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...domain.entities.invoice import Invoice
from ...domain.entities.invoice_item import InvoiceItem
from ...domain.entities.payment import Payment
from ...domain.entities.inventory_movement import InventoryMovement
from ...domain.value_objects.billing_types import InvoiceStatus, PaymentMethod
from ...domain.interfaces.invoice_repository import IInvoiceRepository
from ...domain.interfaces.invoice_item_repository import IInvoiceItemRepository
from ...domain.interfaces.payment_repository import IPaymentRepository
from ...domain.interfaces.product_repository import IProductRepository
from ...domain.interfaces.inventory_movement_repository import IInventoryMovementRepository


class POSManager:
    def __init__(
        self,
        invoice_repo: IInvoiceRepository,
        item_repo: IInvoiceItemRepository,
        payment_repo: IPaymentRepository,
        product_repo: IProductRepository,
        movement_repo: IInventoryMovementRepository
    ):
        self.invoice_repo = invoice_repo
        self.item_repo = item_repo
        self.payment_repo = payment_repo
        self.product_repo = product_repo
        self.movement_repo = movement_repo

    def process_pos_sale(
        self,
        customer_id: uuid.UUID,
        items: List[Dict[str, Any]], # [{"product_id": ..., "quantity": ...}]
        payment_method: PaymentMethod,
        tax_rate: float = 0.16
    ) -> Invoice:
        """
        Procesa una venta rápida del POS:
        1. Crea factura.
        2. Registra items.
        3. Descuenta stock.
        4. Registra movimientos de inventario.
        """
        # 1. Calcular totales
        total_amount = 0.0
        sale_items = []
        
        for item_data in items:
            product = self.product_repo.findById(uuid.UUID(item_data["product_id"]))
            if not product:
                raise ValueError(f"Producto no encontrado: {item_data['product_id']}")
            
            if product.stock < item_data["quantity"]:
                raise ValueError(f"Stock insuficiente para {product.name}. Disponible: {product.stock}")
            
            qty = item_data["quantity"]
            price = product.sale_price
            item_total = price * qty
            total_amount += item_total
            
            sale_items.append({
                "product": product,
                "quantity": qty,
                "unit_price": price,
                "total": item_total
            })

        subtotal = round(total_amount / (1 + tax_rate), 2)
        tax = round(total_amount - subtotal, 2)

        # 2. Crear Factura (Cabecera)
        invoice_num = f"POS-{datetime.now().strftime('%y%m%d%H%M%S')}"
        invoice = Invoice(
            invoice_number=invoice_num,
            customer_id=customer_id,
            subtotal=subtotal,
            tax=tax,
            total=total_amount,
            amount_paid=total_amount, # POS is usually paid instantly
            status=InvoiceStatus.PAID,
            due_date=datetime.utcnow()
        )
        created_invoice = self.invoice_repo.create(invoice)

        # 3. Registrar Items y Actualizar Stock
        for item in sale_items:
            product = item["product"]
            qty = item["quantity"]
            
            # Item de factura
            inv_item = InvoiceItem(
                invoice_id=created_invoice.id,
                product_id=product.id,
                description=product.name,
                quantity=qty,
                unit_price=item["unit_price"],
                subtotal=round(item["total"] / (1 + tax_rate), 2),
                tax=round(item["total"] - round(item["total"] / (1 + tax_rate), 2), 2),
                total=item["total"]
            )
            self.item_repo.create(inv_item)
            
            # Descontar stock
            self.product_repo.update_stock(product.id, -qty)
            
            # Movimiento de inventario
            mov = InventoryMovement(
                product_id=product.id,
                quantity=qty,
                type="OUT",
                reason=f"Venta POS {invoice_num}",
                reference_id=created_invoice.id
            )
            self.movement_repo.create(mov)

        # 4. Registrar Pago automático
        payment = Payment(
            invoice_id=created_invoice.id,
            amount=total_amount,
            payment_method=payment_method,
            transaction_reference=f"POS Auto-{invoice_num}"
        )
        self.payment_repo.create(payment)

        return created_invoice

    def find_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        product = self.product_repo.findByBarcode(barcode)
        if product:
            return {
                "id": str(product.id),
                "name": product.name,
                "price": float(product.sale_price),
                "stock": product.stock,
                "barcode": product.barcode
            }
        return None
