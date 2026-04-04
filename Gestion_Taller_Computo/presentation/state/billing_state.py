import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_invoice_repository import Psycopg2InvoiceRepository
from ...infrastructure.repositories.psycopg_payment_repository import Psycopg2PaymentRepository
from ...infrastructure.repositories.psycopg_quote_repository import Psycopg2QuoteRepository
from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...application.use_cases.billing_manager import BillingManager
from ...application.use_cases.quote_manager import QuoteManager

class BillingState(rx.State):
    """
    Estado de Facturación y Cobros.
    Maneja facturas, pagos y estados de cuenta de clientes.
    """
    
    invoices: List[Dict[str, Any]] = []
    quotes: List[Dict[str, Any]] = []
    
    # Modales
    show_invoice_modal: bool = False
    show_quote_modal: bool = False
    is_editing_quote: bool = False
    
    # Campos del formulario de presupuesto
    quote_form: Dict[str, Any] = {
        "id": "",
        "work_order_id": "",
        "customer_id": "",
        "items_summary": "",
        "amount": 0.0,
        "valid_days": 7
    }
    
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

    @rx.event
    def set_search_query(self, val: str):
        self.search_query = val

    @rx.event
    def set_status_filter(self, val: str):
        self.status_filter = val

    @rx.event
    def set_show_payment_modal(self, val: bool):
        self.show_payment_modal = val

    @rx.event
    def set_show_quote_modal(self, val: bool):
        self.show_quote_modal = val

    @rx.event
    def set_payment_method(self, val: str):
        self.payment_method = val

    @rx.event
    def set_payment_reference(self, val: str):
        self.payment_reference = val

    @rx.event
    def fetch_all_docs(self):
        """Obtiene todas las facturas y presupuestos."""
        try:
            invoice_repo = Psycopg2InvoiceRepository()
            payment_repo = Psycopg2PaymentRepository()
            quote_repo = Psycopg2QuoteRepository()
            
            # Invoices
            all_invoices = invoice_repo.findAll()
            self.invoices = [self._invoice_to_dict(inv) for inv in all_invoices]
            
            # Quotes
            all_quotes = quote_repo.findAll()
            self.quotes = [self._quote_to_dict(q) for q in all_quotes]
            
        except Exception as e:
            print(f"Error fetching billing data: {e}")
        finally:
            self.is_loading = False

    def on_load(self):
        """Carga los datos al iniciar."""
        self.is_loading = True
        self.fetch_all_docs()

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
            return self.fetch_all_docs()
            
        except Exception as e:
            return rx.window_alert(f"Error al procesar pago: {str(e)}")

    def _quote_to_dict(self, q: Any) -> Dict[str, Any]:
        return {
            "id": str(q.id),
            "number": q.quote_number,
            "work_order_id": str(q.work_order_id) if q.work_order_id else "N/A",
            "items": q.items_summary,
            "total": float(q.total),
            "status": q.status.value,
            "expiry": q.expiry_date.strftime("%Y-%m-%d") if q.expiry_date else "---",
            "status_color": self._get_quote_color(q.status.value)
        }

    def _get_quote_color(self, status: str) -> str:
        colors = {
            "DRAFT": "gray",
            "SENT": "blue",
            "APPROVED": "green",
            "REJECTED": "red",
            "EXPIRED": "orange",
            "CONVERTED": "indigo"
        }
        return colors.get(status, "slate")

    @rx.event
    def save_quote(self, form_data: Dict[str, Any]):
        """Crea un nuevo presupuesto."""
        try:
            quote_repo = Psycopg2QuoteRepository()
            invoice_repo = Psycopg2InvoiceRepository()
            order_repo = Psycopg2WorkOrderRepository()
            mgr = QuoteManager(quote_repo, invoice_repo, order_repo)
            
            # Extraer y validar
            work_order_id = form_data.get("work_order_id")
            customer_id = form_data.get("customer_id")
            amount = float(form_data.get("amount", 0))
            items = form_data.get("items_summary", "Servicio General")
            
            if not customer_id:
                return rx.window_alert("El cliente es obligatorio.")
                
            mgr.create_quote_from_diagnostic(
                work_order_id=uuid.UUID(work_order_id) if work_order_id else None,
                customer_id=uuid.UUID(customer_id),
                items_summary=items,
                amount=amount
            )
            
            self.show_quote_modal = False
            return self.fetch_all_docs()
        except Exception as e:
            return rx.window_alert(f"Error al crear presupuesto: {str(e)}")

    @rx.event
    def approve_quote(self, quote_id: str):
        """Aprueba digitalmente un presupuesto."""
        try:
            quote_repo = Psycopg2QuoteRepository()
            order_repo = Psycopg2WorkOrderRepository()
            mgr = QuoteManager(quote_repo, work_order_repo=order_repo)
            mgr.approve_quote(uuid.UUID(quote_id))
            return self.fetch_all_docs()
        except Exception as e:
            return rx.window_alert(f"Error al aprobar: {str(e)}")

    @rx.event
    def convert_quote_to_invoice(self, quote_id: str):
        """Convierte presupuesto aprobado a factura."""
        try:
            quote_repo = Psycopg2QuoteRepository()
            invoice_repo = Psycopg2InvoiceRepository()
            mgr = QuoteManager(quote_repo, invoice_repo)
            mgr.convert_to_invoice(uuid.UUID(quote_id))
            return self.fetch_all_docs()
        except Exception as e:
            return rx.window_alert(f"Error al convertir: {str(e)}")
