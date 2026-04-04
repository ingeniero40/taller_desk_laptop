import os
from typing import Dict, Any, Optional

class NotificationService:
    """
    Servicio centralizado para el envío de notificaciones (Contexto 12).
    Soporta WhatsApp Business API y Email (SMTP/SendGrid).
    """

    def __init__(self):
        self.wa_token = os.getenv("WHATSAPP_API_TOKEN")
        self.smtp_host = os.getenv("SMTP_HOST")
        self.enabled = True

    def send_whatsapp(self, phone: str, template: str, params: Dict[str, Any]) -> bool:
        """
        Envía un mensaje de WhatsApp al cliente.
        (Integración Stub - Preparado para API Business).
        """
        print(f"📱 NOTIF [WA]: Enviando '{template}' a {phone} con {params}")
        # Lógica de requests.post(wa_api_url, headers=headers, json=payload)
        return True

    def send_email(self, email: str, subject: str, body: str) -> bool:
        """
        Envía un correo electrónico profesional.
        (Integración Stub).
        """
        print(f"📧 NOTIF [Email]: Enviando a {email} - Subj: {subject}")
        # Lógica de smtplib o postmark/sendgrid
        return True

    def notify_order_status_change(self, customer_name: str, phone: str, ticket: str, new_status: str):
        """
        Notificación automática ante cambios de estado en el taller.
        """
        msg = f"Hola {customer_name}, tu equipo con ticket {ticket} ha cambiado a estado: {new_status}."
        self.send_whatsapp(phone, "status_template", {"ticket": ticket, "status": new_status})
        return True
