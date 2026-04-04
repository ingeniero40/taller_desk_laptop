from typing import List, Optional
from datetime import datetime, timedelta
from ...domain.entities.invoice import Invoice
from ...domain.entities.payment import Payment
from ...domain.value_objects.billing_types import InvoiceStatus, PaymentMethod
from ...domain.interfaces.invoice_repository import IInvoiceRepository
from ...domain.interfaces.payment_repository import IPaymentRepository
import uuid


class BillingManager:
    def __init__(
        self, invoice_repo: IInvoiceRepository, payment_repo: IPaymentRepository
    ):
        self.invoice_repo = invoice_repo
        self.payment_repo = payment_repo

    def create_invoice_from_work_order(
        self,
        work_order_id: uuid.UUID,
        customer_id: uuid.UUID,
        amount: float,
        tax_rate: float = 0.16,
    ) -> Invoice:
        """
        Genera una factura a partir de una orden de trabajo.
        """
        # Validar si ya existe factura para esta orden
        existing = self.invoice_repo.findByWorkOrderId(work_order_id)
        if existing:
            return existing

        invoice_num = f"FAC-{datetime.now().strftime('%y%m%d%H%M%S')}"
        subtotal = round(amount / (1 + tax_rate), 2)
        tax = round(amount - subtotal, 2)

        new_invoice = Invoice(
            invoice_number=invoice_num,
            customer_id=customer_id,
            work_order_id=work_order_id,
            subtotal=subtotal,
            tax=tax,
            total=amount,
            status=InvoiceStatus.PENDING,
            due_date=datetime.utcnow() + timedelta(days=15),
        )
        return self.invoice_repo.create(new_invoice)

    def process_payment(
        self,
        invoice_id: uuid.UUID,
        amount: float,
        method: PaymentMethod,
        reference: str = None,
    ) -> Payment:
        """
        Registra un pago y actualiza el estado de la factura.
        """
        invoice = self.invoice_repo.findById(invoice_id)
        if not invoice:
            raise ValueError("Factura no encontrada.")

        if invoice.status == InvoiceStatus.PAID:
            raise ValueError("Esta factura ya ha sido pagada en su totalidad.")

        # Registrar el pago
        new_payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_method=method,
            transaction_reference=reference,
        )
        payment = self.payment_repo.create(new_payment)

        # Actualizar la factura
        invoice.amount_paid += amount
        if invoice.amount_paid >= invoice.total:
            invoice.status = InvoiceStatus.PAID
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.PARTIAL

        self.invoice_repo.update(invoice)
        return payment

    def get_invoice_details(self, invoice_id: uuid.UUID) -> dict:
        """
        Obtiene el detalle completo de una factura incluyendo sus pagos.
        """
        invoice = self.invoice_repo.findById(invoice_id)
        if not invoice:
            return None

        payments = self.payment_repo.findByInvoiceId(invoice_id)
        return {
            "invoice": invoice,
            "payments": payments,
            "balance_due": round(invoice.total - invoice.amount_paid, 2),
        }
