import reflex as rx
from ..state.agenda_state import AgendaState
from ..components.sidebar import sidebar
from ..components.page_header import page_header

# ── Helpers de color ──────────────────────────────────────────────────────────

PRIORITY_COLORS = {
    "Crítica": "red",
    "Alta": "orange",
    "Media": "amber",
    "Baja": "blue",
}

STATUS_COLORS = {
    "RECEIVED": "gray",
    "IN_DIAGNOSIS": "cyan",
    "IN_REPAIR": "indigo",
    "ON_HOLD": "orange",
    "COMPLETED": "green",
    "DELIVERED": "teal",
}

# ── Barra de Notificaciones ───────────────────────────────────────────────────

def notification_bar() -> rx.Component:
    """Banda de alertas para tickets de alta prioridad."""
    return rx.cond(
        AgendaState.notifications.length() >= 1,
        rx.hstack(
            rx.icon(tag="bell-ring", size=18, color=rx.color("amber", 10)),
            rx.text("Alertas activas –", size="2", weight="bold", color=rx.color("amber", 11)),
            rx.foreach(
                AgendaState.notifications,
                lambda n: rx.badge(
                    n["message"],
                    color_scheme="orange",
                    variant="soft",
                    radius="full",
                    size="1",
                )
            ),
            spacing="3",
            padding="10px 20px",
            border_radius="12px",
            background=rx.color("amber", 2),
            border=f"1px solid {rx.color('amber', 4)}",
            width="100%",
            flex_wrap="wrap",
        ),
        rx.box(),  # fallback vacío
    )

# ── Panel de KPIs ─────────────────────────────────────────────────────────────

def stats_panel() -> rx.Component:
    """Métricas rápidas del estado de los tickets."""
    return rx.grid(
        # Alta Prioridad
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text("Alta Prioridad", size="1", color=rx.color("slate", 9), weight="medium"),
                    rx.heading(
                        AgendaState.high_priority_count,
                        size="7", weight="bold", color=rx.color("red", 10)
                    ),
                    spacing="1",
                ),
                rx.spacer(),
                rx.box(
                    rx.icon(tag="triangle-alert", size=22, color=rx.color("red", 9)),
                    padding="10px",
                    border_radius="10px",
                    background=rx.color("red", 2),
                ),
                width="100%",
            ),
            padding="18px",
        ),
        # En Proceso
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text("En Proceso", size="1", color=rx.color("slate", 9), weight="medium"),
                    rx.heading(
                        AgendaState.pending_count,
                        size="7", weight="bold", color=rx.color("cyan", 10)
                    ),
                    spacing="1",
                ),
                rx.spacer(),
                rx.box(
                    rx.icon(tag="wrench", size=22, color=rx.color("cyan", 9)),
                    padding="10px",
                    border_radius="10px",
                    background=rx.color("cyan", 2),
                ),
                width="100%",
            ),
            padding="18px",
        ),
        # Total
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text("Total Tickets", size="1", color=rx.color("slate", 9), weight="medium"),
                    rx.heading(
                        AgendaState.tickets.length(),
                        size="7", weight="bold", color=rx.color("indigo", 10)
                    ),
                    spacing="1",
                ),
                rx.spacer(),
                rx.box(
                    rx.icon(tag="clipboard-list", size=22, color=rx.color("indigo", 9)),
                    padding="10px",
                    border_radius="10px",
                    background=rx.color("indigo", 2),
                ),
                width="100%",
            ),
            padding="18px",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )

# ── Barra de Filtros ──────────────────────────────────────────────────────────

def filter_bar() -> rx.Component:
    """Filtros simples usando select estándar de Reflex."""
    return rx.hstack(
        rx.select(
            ["Todas", "Crítica", "Alta", "Media", "Baja"],
            value=AgendaState.filter_priority,
            on_change=AgendaState.set_filter_priority,
            size="2",
            radius="large",
        ),
        rx.select(
            ["Todas", "RECEIVED", "IN_DIAGNOSIS", "IN_REPAIR",
             "ON_HOLD", "COMPLETED", "DELIVERED"],
            value=AgendaState.filter_status,
            on_change=AgendaState.set_filter_status,
            size="2",
            radius="large",
        ),
        rx.spacer(),
        rx.hstack(
            rx.text("Mostrando:", size="2", color=rx.color("slate", 10)),
            rx.badge(
                AgendaState.filtered_tickets.length(),
                color_scheme="indigo",
                variant="solid",
            ),
            spacing="2",
        ),
        spacing="3",
        width="100%",
        flex_wrap="wrap",
    )

# ── Tarjeta de Ticket ─────────────────────────────────────────────────────────

def ticket_card(ticket: dict) -> rx.Component:
    """Tarjeta individual de ticket con prioridad y estado."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            ticket["ticket_number"],
                            size="1", weight="bold",
                            color=rx.color("slate", 9),
                            letter_spacing="0.5px",
                        ),
                        rx.badge(
                            ticket["priority"],
                            color_scheme=rx.cond(
                                ticket["priority"] == "Crítica", "red",
                                rx.cond(
                                    ticket["priority"] == "Alta", "orange",
                                    rx.cond(
                                        ticket["priority"] == "Media", "amber",
                                        "blue"
                                    )
                                )
                            ),
                            radius="full",
                            variant="soft",
                            size="1",
                        ),
                        spacing="2",
                    ),
                    rx.text(
                        ticket["description"],
                        size="2",
                        weight="medium",
                        color=rx.color("slate", 12),
                    ),
                    spacing="1",
                    flex="1",
                ),
                rx.badge(
                    ticket["status_label"],
                    color_scheme=rx.cond(
                        ticket["status"] == "COMPLETED", "green",
                        rx.cond(
                            ticket["status"] == "IN_REPAIR", "indigo",
                            rx.cond(
                                ticket["status"] == "IN_DIAGNOSIS", "cyan",
                                rx.cond(
                                    ticket["status"] == "ON_HOLD", "orange",
                                    "gray"
                                )
                            )
                        )
                    ),
                    radius="full",
                    variant="soft",
                    size="1",
                ),
                width="100%",
                align_items="start",
            ),
            rx.divider(opacity=0.3),
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="user", size=14, color=rx.color("slate", 9)),
                    rx.text(ticket["technician"], size="1", color=rx.color("slate", 10)),
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.icon(tag="clock", size=14, color=rx.color("slate", 9)),
                    rx.text(ticket["due_date"], size="1", color=rx.color("slate", 10)),
                    spacing="1",
                ),
                width="100%",
            ),
            spacing="3",
        ),
        padding="16px",
        border_radius="14px",
        border=f"1px solid {rx.color('slate', 4)}",
        background=rx.color("white", 1),
        _hover={
            "box_shadow": f"0 4px 20px {rx.color('slate', 4)}",
            "transform": "translateY(-2px)",
            "cursor": "pointer",
        },
        transition="all 0.2s ease",
        width="100%",
    )

# ── Lista de Tickets ──────────────────────────────────────────────────────────

def tickets_list() -> rx.Component:
    """Lista de tickets con encabezado de conteo."""
    return rx.vstack(
        rx.hstack(
            rx.text("Total en sistema:", size="2", color=rx.color("slate", 10)),
            rx.badge(
                AgendaState.tickets.length(),
                color_scheme="indigo",
                variant="solid",
            ),
            spacing="2",
            width="100%",
        ),
        rx.cond(
            AgendaState.is_loading,
            rx.center(
                rx.spinner(size="3", color_scheme="indigo"),
                padding_y="40px",
                width="100%",
            ),
            rx.vstack(
                rx.foreach(
                    AgendaState.filtered_tickets,
                    ticket_card,
                ),
                spacing="3",
                width="100%",
            ),
        ),
        spacing="4",
        width="100%",
    )

# ── Modal Nuevo Ticket ─────────────────────────────────────────────────────────

def new_ticket_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="plus-circle", size=20, color=rx.color("cyan", 9)),
                    rx.heading("Nuevo Ticket de Servicio", size="4"),
                    spacing="2",
                ),
                rx.divider(opacity=0.3),
                rx.vstack(
                    rx.text("Descripción del problema", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Describe el problema o servicio...",
                        value=AgendaState.new_ticket_description,
                        on_change=AgendaState.set_ticket_description,
                        rows="4",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Prioridad", size="2", weight="medium"),
                        rx.select(
                            ["Baja", "Media", "Alta", "Crítica"],
                            value=AgendaState.new_ticket_priority,
                            on_change=AgendaState.set_ticket_priority,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Fecha Límite", size="2", weight="medium"),
                        rx.input(
                            type="datetime-local",
                            value=AgendaState.new_ticket_due_date,
                            on_change=AgendaState.set_ticket_due_date,
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            on_click=AgendaState.close_ticket_modal,
                            variant="soft",
                            color_scheme="gray",
                        )
                    ),
                    rx.button(
                        rx.icon(tag="save", size=16),
                        rx.text("Guardar Ticket"),
                        color_scheme="indigo",
                        variant="solid",
                        radius="large",
                    ),
                    spacing="3",
                    justify="end",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="560px",
        ),
        open=AgendaState.show_ticket_modal,
    )

# ── Página Principal ──────────────────────────────────────────────────────────

def agenda_page() -> rx.Component:
    """Página completa de Agenda y Gestión de Tickets."""
    return rx.hstack(
        sidebar("/agenda"),
        rx.container(
            rx.vstack(
                page_header(
                    "Agenda y Tickets",
                    "Control de tickets de servicio, prioridades y asignación de técnicos.",
                    actions=[
                        rx.button(
                            rx.icon(tag="refresh-cw", size=18),
                            on_click=AgendaState.fetch_tickets,
                            variant="soft",
                            color_scheme="gray",
                            radius="large",
                        ),
                        rx.button(
                            rx.icon(tag="plus", size=18),
                            rx.text("Nuevo Ticket"),
                            on_click=AgendaState.open_ticket_modal,
                            color_scheme="indigo",
                            variant="solid",
                            radius="large",
                        ),
                    ],
                ),
                notification_bar(),
                stats_panel(),
                rx.heading(
                    "Tickets de Servicio",
                    size="5",
                    weight="bold",
                    color=rx.color("slate", 11),
                    margin_top="8px",
                ),
                filter_bar(),
                tickets_list(),
                new_ticket_modal(),
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
