import reflex as rx
import uuid
from datetime import datetime
from ..components.sidebar import sidebar
from ..state.portal_state import PortalState

def info_stat(label: str, value: str, icon: str, color: str = "indigo"):
    return rx.flex(
        rx.hstack(
            rx.icon(tag=icon, size=18, color=rx.color(color, 9)),
            rx.vstack(
                rx.text(label, size="1", weight="bold", color=rx.color("slate", 9)),
                rx.text(value, size="2", weight="medium", color=rx.color("slate", 12)),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
            align="center",
        ),
        padding="12px",
        background=rx.color(color, 2),
        border_radius="12px",
        width="100%",
    )

def status_badge(status: str):
    colors = {
        "RECEIVED": "gray",
        "IN_DIAGNOSIS": "amber",
        "IN_REPAIR": "indigo",
        "ON_HOLD": "orange",
        "COMPLETED": "green",
        "DELIVERED": "blue",
    }
    labels = {
        "RECEIVED": "Recibido",
        "IN_DIAGNOSIS": "En Diagnóstico",
        "IN_REPAIR": "En Reparación",
        "ON_HOLD": "En Espera",
        "COMPLETED": "Listo para Entrega",
        "DELIVERED": "Entregado",
    }
    color = colors.get(status, "gray")
    label = labels.get(status, status)
    
    return rx.badge(
        label,
        color_scheme=color,
        variant="surface",
        radius="full",
        padding_x="12px",
    )

def portal_view():
    """Vista principal del Portal del Cliente."""
    return rx.vstack(
        # Hero Section / Search
        rx.box(
            rx.vstack(
                rx.heading("Portal de Servicios", size="8", weight="bold"),
                rx.text("Consulta el estado de tu equipo y aprueba presupuestos en tiempo real.", color=rx.color("slate", 11)),
                rx.hstack(
                    rx.input(
                        placeholder="Ingresa tu número de ticket (ej. T-1234)...",
                        size="3",
                        width="300px",
                        on_change=PortalState.set_search_ticket,
                        value=PortalState.search_ticket,
                    ),
                    rx.button(
                        "Buscar Equipo",
                        on_click=PortalState.search_order,
                        loading=PortalState.is_searching,
                        size="3",
                        color_scheme="indigo",
                    ),
                    spacing="3",
                    margin_top="16px",
                ),
                align="center",
                spacing="4",
                padding_y="60px",
                width="100%",
            ),
            width="100%",
            background=f"linear-gradient(135deg, {rx.color('indigo', 1)} 0%, {rx.color('blue', 1)} 100%)",
            border_bottom=f"1px solid {rx.color('slate', 3)}",
        ),

        # Result Section
        rx.cond(
            PortalState.order_found,
            rx.container(
                rx.vstack(
                    rx.flex(
                        rx.heading(f"Ticket: {PortalState.order_details['ticket_number']}", size="6"),
                        status_badge(PortalState.order_details["status"]),
                        justify="between",
                        align="center",
                        width="100%",
                        padding_bottom="16px",
                    ),
                    
                    rx.grid(
                        info_stat("Cliente", PortalState.order_details["customer_name"], "user"),
                        info_stat("Equipo", PortalState.order_details["equipment"], "laptop"),
                        info_stat("Ingreso", PortalState.order_details["created_at"], "calendar"),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),

                    rx.divider(margin_y="24px"),

                    # Sección de Presupuesto
                    rx.cond(
                        PortalState.has_quote,
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon(tag="receipt-text", size=24, color=rx.color("indigo", 9)),
                                    rx.heading("Presupuesto de Servicio", size="5"),
                                    spacing="3",
                                ),
                                rx.text("Se requiere tu aprobación para proceder con la reparación detallada en el diagnóstico.", size="2"),
                                rx.flex(
                                    rx.text("Total estimado:", size="2", weight="bold"),
                                    rx.heading(f"${PortalState.order_details['quoted_price']}", size="7", color=rx.color("indigo", 11)),
                                    justify="between",
                                    align="center",
                                    width="100%",
                                    padding_top="12px",
                                ),
                                
                                rx.cond(
                                    PortalState.is_approved,
                                    rx.badge("Aprobado por el cliente", color_scheme="green", variant="soft", width="100%", padding="8px"),
                                    rx.hstack(
                                        rx.button(
                                            "Rechazar", 
                                            variant="soft", 
                                            color_scheme="red", 
                                            width="100%",
                                            on_click=PortalState.reject_quote
                                        ),
                                        rx.button(
                                            "Aprobar Reparación", 
                                            color_scheme="green", 
                                            width="100%",
                                            on_click=PortalState.approve_quote
                                        ),
                                        width="100%",
                                        spacing="3",
                                    )
                                ),
                                spacing="4",
                                width="100%",
                            ),
                            padding="24px",
                            background=rx.color("white", 1),
                            border=f"1px solid {rx.color('indigo', 4)}",
                            box_shadow="lg",
                            width="100%",
                        ),
                    ),

                    # Timeline / History (Historial de Servicios)
                    rx.vstack(
                        rx.heading("Historial del Servicio", size="4", margin_top="32px"),
                        rx.vstack(
                            rx.foreach(
                                PortalState.order_comments,
                                lambda comment: rx.flex(
                                    rx.vstack(
                                        rx.text(comment["date"], size="1", color=rx.color("slate", 9)),
                                        rx.text(comment["content"], size="2", color=rx.color("slate", 11)),
                                        align_items="start",
                                        spacing="1",
                                    ),
                                    padding="12px",
                                    border_left=f"3px solid {rx.color('indigo', 6)}",
                                    background=rx.color("slate", 2),
                                    border_radius="0 8px 8px 0",
                                    margin_left="10px",
                                    width="100%",
                                )
                            ),
                            spacing="3",
                            width="100%",
                            padding_top="16px",
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    
                    padding_y="40px",
                    width="100%",
                ),
                size="3",
            ),
            rx.cond(
                PortalState.has_searched,
                rx.center(
                    rx.vstack(
                        rx.icon(tag="search-code", size=48, color=rx.color("slate", 5)),
                        rx.text("No encontramos ningún equipo con ese número de ticket.", color=rx.color("slate", 9)),
                        rx.text("Por favor, verifica el código que te entregaron en mostrador.", size="1"),
                        align="center",
                        padding_y="100px",
                    )
                )
            )
        ),
        
        width="100%",
        min_height="100vh",
        background_color=rx.color("slate", 1),
    )

def portal_page():
    return rx.flex(
        sidebar(active_page="/portal"),
        rx.box(
            portal_view(),
            flex="1",
            overflow_y="auto",
        ),
        width="100%",
        height="100vh",
    )
