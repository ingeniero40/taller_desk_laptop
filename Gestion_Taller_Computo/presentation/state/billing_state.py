import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_invoice_repository import Psycopg2InvoiceRepository
from ...infrastructure.repositories.psycopg_payment_repository import Psycopg2PaymentRepository
from ...application.use_cases.billing_manager import BillingManager

class BillingState(rx.State):
    """
    Estado de Facturación y Cobros.
    Maneja facturas, pagos y estados de cuenta de clientes.
    """
    
    invoices: List[Dict[str, Any]] = []
    
    # Búsqueda
    search_query: str = ""
    status_filter: str = "Todas"
    
    # Detalle de Factura / Procesar Pago
    selected_invoice: Dict[str, Any] = {}
    show_payment_modal: bool = False
    payment_amount: float = 0.0
    payment_method: str = "Efectivo"
    payment_reference: str = ""
    
    is_loading: bool = True

    def on_load(self):
        """Carga las facturas al iniciar."""
        self.is_loading = True
        self.fetch_invoices()

    @rx.event
    def fetch_invoices(self):
        """Obtiene todas las facturas desde el repositorio."""
        try:
            invoice_repo = Psycopg2InvoiceRepository()
            payment_repo = Psycopg2PaymentRepository()
            mgr = BillingManager(invoice_repo, payment_repo)
            
            # Nota: El repositorio debería tener un findAll.
            # Según test_billing_management.py, se usa billing_mgr.get_invoice_details()
            # Asumamos que invoice_repo maneja la persistencia básica.
            all_invoices = invoice_repo.findAll()
            self.invoices = [self._invoice_to_dict(inv) for inv in all_invoices]
            
        except Exception as e:
            print(f"Error fetching invoices: {e}")
        finally:
            self.is_loading = False

    def _invoice_to_dict(self, inv: Any) -> Dict[str, Any]:
        """Convierte entidad de dominio a diccionario para el frontend."""
        return {
            "id": str(inv.id),
            "invoice_number": inv.invoice_number,
            "customer_id": str(inv.customer_id),
            "total": float(inv.total),
            "status": inv.status.value,
            "date": inv.created_at.strftime("%Y-%m-%d"),
            "status_color": self._get_status_color(inv.status.value)
        }

    def _get_status_color(self, status: str) -> str:
        colors = {
            "PENDING": "amber",
            "PAID": "green",
            "PARTIAL": "cyan",
            "CANCELLED": "red"
        }
        return colors.get(status, "gray")

    @rx.var
    def filtered_invoices(self) -> List[Dict[str, Any]]:
        invoices = self.invoices
        if self.search_query:
            q = self.search_query.lower()
            invoices = [i for i in invoices if q in i["invoice_number"].lower()]
        
        if self.status_filter != "Todas":
            invoices = [i for i in invoices if i["status"] == self.status_filter]
            
        return invoices

    @rx.event
    def open_payment_modal(self, invoice: Dict[str, Any]):
        self.selected_invoice = invoice
        # Deberíamos obtener el balance real
        invoice_repo = Psycopg2InvoiceRepository()
        payment_repo = Psycopg2PaymentRepository()
        mgr = BillingManager(invoice_repo, payment_repo)
        details = mgr.get_invoice_details(uuid.UUID(invoice["id"]))
        
        self.payment_amount = details["balance_due"]
        self.show_payment_modal = True

    @rx.event
    def set_payment_amount(self, value: str):
        try:
            self.payment_amount = float(value) if value else 0.0
        except ValueError:
            self.payment_amount = 0.0

    @rx.event
    def process_payment(self):
        """Registra un pago para la factura seleccionada."""
        try:
            invoice_repo = Psycopg2InvoiceRepository()
            payment_repo = Psycopg2PaymentRepository()
            mgr = BillingManager(invoice_repo, payment_repo)
            
            from ...domain.value_objects.billing_types import PaymentMethod
            
            method = PaymentMethod.CASH
            if self.payment_method == "Tarjeta": method = PaymentMethod.CARD
            elif self.payment_method == "Transferencia": method = PaymentMethod.TRANSFER
            
            mgr.process_payment(
                invoice_id=uuid.UUID(self.selected_invoice["id"]),
                amount=self.payment_amount,
                method=method,
                reference=self.payment_reference
            )
            
            self.show_payment_modal = False
            return self.fetch_invoices()
            
        except Exception as e:
            return rx.window_alert(f"Error al procesar pago: {str(e)}")
