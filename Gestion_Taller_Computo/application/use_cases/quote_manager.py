import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from ...domain.entities.quote import Quote
from ...domain.entities.invoice import Invoice
from ...domain.value_objects.billing_types import QuoteStatus, InvoiceStatus
from ...domain.interfaces.quote_repository import IQuoteRepository
from ...domain.interfaces.invoice_repository import IInvoiceRepository
from ...domain.interfaces.work_order_repository import IWorkOrderRepository
from ...domain.value_objects.work_order_status import WorkOrderStatus


class QuoteManager:
    def __init__(
        self, quote_repo: IQuoteRepository, 
        invoice_repo: IInvoiceRepository = None,
        work_order_repo: IWorkOrderRepository = None
    ):
        self.quote_repo = quote_repo
        self.invoice_repo = invoice_repo
        self.work_order_repo = work_order_repo

    def create_quote_from_diagnostic(
        self,
        work_order_id: uuid.UUID,
        customer_id: uuid.UUID,
        items_summary: str,
        amount: float,
        tax_rate: float = 0.16,
        valid_days: int = 7,
    ) -> Quote:
        """
        Genera un presupuesto basado en el diagnóstico técnico.
        """
        quote_num = f"PRE-{datetime.now().strftime('%y%m%d%H%M%S')}"
        subtotal = round(amount / (1 + tax_rate), 2)
        tax = round(amount - subtotal, 2)
        
        new_quote = Quote(
            quote_number=quote_num,
            customer_id=customer_id,
            work_order_id=work_order_id,
            items_summary=items_summary,
            subtotal=subtotal,
            tax=tax,
            total=amount,
            status=QuoteStatus.DRAFT,
            expiry_date=datetime.utcnow() + timedelta(days=valid_days)
        )
        quote = self.quote_repo.create(new_quote)
        
        # Actualizar estado de orden si existe
        if work_order_id and self.work_order_repo:
            order = self.work_order_repo.findById(work_order_id)
            if order:
                order.status = WorkOrderStatus.AWAITING_APPROVAL
                self.work_order_repo.update(order)
                
        return quote

    def approve_quote(self, quote_id: uuid.UUID, notes: str = None) -> Quote:
        """
        Marca un presupuesto como aprobado por el cliente.
        """
        quote = self.quote_repo.findById(quote_id)
        if not quote:
            raise ValueError("Presupuesto no encontrado.")
        
        if quote.status != QuoteStatus.DRAFT and quote.status != QuoteStatus.SENT:
            raise ValueError(f"No se puede aprobar un presupuesto en estado {quote.status}")
        
        quote.status = QuoteStatus.APPROVED
        quote.approval_date = datetime.utcnow()
        if notes:
            quote.notes = notes
            
        quote = self.quote_repo.update(quote)
        
        # Si tiene orden, pasarla a reparación
        if quote.work_order_id and self.work_order_repo:
            order = self.work_order_repo.findById(quote.work_order_id)
            if order:
                order.status = WorkOrderStatus.IN_REPAIR
                self.work_order_repo.update(order)
                
        return quote

    def convert_to_invoice(self, quote_id: uuid.UUID) -> Invoice:
        """
        Convierte un presupuesto aprobado en una factura final.
        """
        if not self.invoice_repo:
            raise ValueError("Repositorio de facturas no configurado.")
            
        quote = self.quote_repo.findById(quote_id)
        if not quote:
            raise ValueError("Presupuesto no encontrado.")
            
        if quote.status != QuoteStatus.APPROVED:
            raise ValueError("Solo los presupuestos aprobados pueden convertirse en factura.")
            
        # Generar número de factura
        invoice_num = f"FAC-Q{quote.quote_number[4:]}"
        
        new_invoice = Invoice(
            invoice_number=invoice_num,
            customer_id=quote.customer_id,
            work_order_id=quote.work_order_id,
            subtotal=quote.subtotal,
            tax=quote.tax,
            total=quote.total,
            status=InvoiceStatus.PENDING,
            due_date=datetime.utcnow() + timedelta(days=15)
        )
        
        invoice = self.invoice_repo.create(new_invoice)
        
        # Marcar presupuesto como convertido
        quote.status = QuoteStatus.CONVERTED
        quote.conversion_invoice_id = invoice.id
        self.quote_repo.update(quote)
        
        return invoice

    def get_customer_quotes(self, customer_id: uuid.UUID) -> List[Quote]:
        return self.quote_repo.findByCustomerId(customer_id)
        
    def get_work_order_quotes(self, work_order_id: uuid.UUID) -> List[Quote]:
        return self.quote_repo.findByWorkOrderId(work_order_id)
