import reflex as rx
from ..components.sidebar import sidebar
from ..components.page_header import page_header

def support_header() -> rx.Component:
    """Encabezado de la página de soporte."""
    return page_header(
        "Centro de Soporte",
        "¿Necesitas ayuda con el sistema o con una reparación avanzada?"
    )

def faq_section() -> rx.Component:
    """Sección de preguntas frecuentes."""
    return rx.vstack(
        rx.heading("Preguntas Frecuentes", size="5", margin_bottom="4"),
        rx.accordion.root(
            rx.accordion.item(
                header="¿Cómo restauro mi contraseña?",
                content="Contacta al administrador del sistema para que resetee tu perfil desde la sección de Ajustes.",
                value="faq-1",
            ),
            rx.accordion.item(
                header="¿Cómo registro una garantía?",
                content="Crea una nueva órden de trabajo vinculada al mismo equipo y marca el costo como $0 indicando 'Garantía' en las notas.",
                value="faq-2",
            ),
            rx.accordion.item(
                header="¿El sistema funciona sin internet?",
                content="Gravity está diseñado para funcionar en red local, pero requiere conexión para respaldos en la nube si están activados.",
                value="faq-3",
            ),
            width="100%",
            variant="ghost",
        ),
        spacing="4",
        width="100%",
        padding="24px",
        background_color=rx.color("white", 1),
        border_radius="16px",
        border=f"1px solid {rx.color('slate', 4)}",
    )

def contact_card(title: str, description: str, icon: str, button_text: str) -> rx.Component:
    """Tarjeta de contacto de soporte."""
    return rx.vstack(
        rx.icon(tag=icon, size=32, color=rx.color("cyan", 9)),
        rx.text(title, weight="bold", size="4"),
        rx.text(description, size="2", color=rx.color("slate", 10), text_align="center"),
        rx.spacer(),
        rx.button(button_text, variant="soft", color_scheme="cyan", width="100%"),
        spacing="3",
        padding="24px",
        border_radius="16px",
        border=f"1px solid {rx.color('slate', 4)}",
        background_color=rx.color("white", 1),
        align_items="center",
        height="220px",
    )

def support_page() -> rx.Component:
    """Layout principal de la página de soporte."""
    return rx.hstack(
        sidebar("/support"),
        rx.container(
            rx.vstack(
                support_header(),
                rx.grid(
                    contact_card(
                        "Soporte IT Local", 
                        "Problemas con la red, impresoras o el software Gravity.", 
                        "monitor", 
                        "Abrir Ticket"
                    ),
                    contact_card(
                        "Consultoría Técnica", 
                        "Dudas sobre diagramas o microsoldadura avanzada.", 
                        "cpu", 
                        "Contactar Senior"
                    ),
                    contact_card(
                        "Reportar Bug", 
                        "Si encontraste un error en el sistema, infórmalo aquí.", 
                        "bug", 
                        "Enviar Reporte"
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                faq_section(),
                spacing="6",
                padding_bottom="48px",
                width="100%",
            ),
            size="4",
            padding_x="40px",
        ),
        background_color=rx.color("slate", 2),
        min_height="100vh",
        spacing="0",
        align_items="start",
    )
