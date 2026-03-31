import reflex as rx
from typing import Dict, List, Any
from ..state.tracking_state import (
    TrackingState, STATUS_LABELS, STATUS_COLORS, STATUS_ICONS, STATUS_PIPELINE
)
from ..components.sidebar import sidebar
from ..components.page_header import page_header

# ── Paleta de alertas ─────────────────────────────────────────────────────────
ALERT_SCHEMA = [
    ("overdue_orders",   "Órdenes Vencidas",        "alarm-clock",     "red",    "La fecha de entrega estimada ha pasado."),
    ("blocked_orders",   "Bloqueadas en Espera",     "octagon-x",       "orange", f"En estado 'En espera' más de 48 horas."),
    ("unassigned_orders","Sin Técnico Asignado",     "user-x",          "amber",  "En reparación/diagnóstico sin responsable."),
]

# ── Alert Banner ──────────────────────────────────────────────────────────────

def alert_banner() -> rx.Component:
    def alert_card(list_attr: str, label: str, icon: str, color: str, desc: str) -> rx.Component:
        count = rx.cond(
            list_attr == "overdue_orders",   TrackingState.overdue_orders.length(),
            rx.cond(
                list_attr == "blocked_orders", TrackingState.blocked_orders.length(),
                TrackingState.unassigned_orders.length(),
            )
        )
        has_alerts = rx.cond(
            list_attr == "overdue_orders",   TrackingState.overdue_orders.length() > 0,
            rx.cond(
                list_attr == "blocked_orders", TrackingState.blocked_orders.length() > 0,
                TrackingState.unassigned_orders.length() > 0,
            )
        )
        return rx.card(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=22, color=rx.color(color, 9)),
                    padding="10px",
                    border_radius="10px",
                    background=rx.color(color, 2),
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(count, size="5", weight="bold", color=rx.color(color, 9)),
                        rx.cond(
                            has_alerts,
                            rx.box(width="8px", height="8px", border_radius="full",
                                   background=rx.color(color, 9),
                                   box_shadow=f"0 0 6px {rx.color(color, 7)}"),
                        ),
                        spacing="2", align_items="center",
                    ),
                    rx.text(label, size="2", weight="bold", color=rx.color("slate", 11)),
                    rx.text(desc, size="1", color=rx.color("slate", 9)),
                    spacing="0",
                ),
                spacing="3", align_items="center",
            ),
            padding="16px 20px",
            border_radius="14px",
            border=rx.cond(
                has_alerts,
                f"1px solid {rx.color(color, 6)}",
                f"1px solid {rx.color('slate', 4)}"
            ),
            background=rx.cond(
                has_alerts,
                rx.color(color, 1),
                rx.color("slate", 1),
            ),
            flex="1",
        )

    return rx.hstack(
        alert_card(*ALERT_SCHEMA[0]),
        alert_card(*ALERT_SCHEMA[1]),
        alert_card(*ALERT_SCHEMA[2]),
        spacing="4", width="100%",
    )

# ── Kanban Card ───────────────────────────────────────────────────────────────

def kanban_card(order: Dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            # Ticket + prioridad
            rx.hstack(
                rx.text(order["ticket"], size="2", weight="bold", color=rx.color("slate", 12)),
                rx.spacer(),
                rx.badge(order["priority"], color_scheme=order["priority_color"],
                         variant="soft", size="1", radius="full"),
            ),
            # Alerta de vencimiento
            rx.cond(
                order["is_overdue"],
                rx.hstack(
                    rx.icon(tag="alarm-clock", size=12, color=rx.color("red", 9)),
                    rx.text("VENCIDA", size="1", weight="bold", color=rx.color("red", 9)),
                    spacing="1",
                ),
            ),
            rx.cond(
                order["is_unassigned"],
                rx.hstack(
                    rx.icon(tag="user-x", size=12, color=rx.color("amber", 9)),
                    rx.text("Sin técnico", size="1", color=rx.color("amber", 9)),
                    spacing="1",
                ),
            ),
            # Device + customer
            rx.hstack(
                rx.icon(tag="laptop", size=12, color=rx.color("slate", 8)),
                rx.text(order["device"], size="1", color=rx.color("slate", 10), no_of_lines=1),
                spacing="1",
            ),
            rx.hstack(
                rx.icon(tag="user", size=12, color=rx.color("slate", 8)),
                rx.text(order["customer"], size="1", color=rx.color("slate", 9), no_of_lines=1),
                spacing="1",
            ),
            # Técnico + fecha
            rx.hstack(
                rx.icon(tag="user-cog", size=12,
                        color=rx.cond(order["is_unassigned"], rx.color("amber", 8), rx.color("slate", 7))),
                rx.text(order["technician"], size="1",
                        color=rx.cond(order["is_unassigned"], rx.color("amber", 9), rx.color("slate", 9)),
                        no_of_lines=1),
                rx.spacer(),
                rx.text(order["due_date"], size="1",
                        color=rx.cond(order["is_overdue"], rx.color("red", 9), rx.color("slate", 8))),
                width="100%", spacing="1",
            ),
            spacing="2",
        ),
        padding="12px",
        border_radius="12px",
        background=rx.cond(
            order["is_overdue"],
            rx.color("red", 1),
            rx.color("slate", 1)
        ),
        border=rx.cond(
            order["is_overdue"],
            f"1px solid {rx.color('red', 5)}",
            f"1px solid {rx.color('slate', 4)}"
        ),
        cursor="pointer",
        _hover={
            "border_color": rx.color("cyan", 6),
            "box_shadow": "0 2px 12px rgba(0,0,0,0.08)",
            "transform": "translateY(-1px)",
        },
        transition="all 0.15s ease",
        on_click=TrackingState.open_detail(order),
        width="100%",
    )

# ── Columna Kanban ────────────────────────────────────────────────────────────

def kanban_column(
    status: str,
    label: str,
    icon_tag: str,
    color: str,
    orders: List[Dict],
) -> rx.Component:
    return rx.box(
        rx.vstack(
            # Header columna
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon_tag, size=14, color=rx.color(color, 9)),
                    padding="6px",
                    border_radius="8px",
                    background=rx.color(color, 2),
                ),
                rx.text(label, size="2", weight="bold", color=rx.color("slate", 11)),
                rx.spacer(),
                rx.badge(orders.length(), color_scheme=color, variant="soft", radius="full"),
                width="100%", spacing="2", align_items="center",
            ),
            rx.divider(color=rx.color(color, 4), margin_y="4px"),
            # Tarjetas
            rx.cond(
                orders.length() >= 1,
                rx.vstack(
                    rx.foreach(orders, kanban_card),
                    spacing="2", width="100%",
                ),
                rx.vstack(
                    rx.icon(tag="inbox", size=28, color=rx.color("slate", 4)),
                    rx.text("Sin órdenes", size="1", color=rx.color("slate", 7)),
                    spacing="2", align_items="center",
                    padding_y="24px", width="100%",
                ),
            ),
            spacing="2", width="100%",
        ),
        min_width="240px",
        max_width="240px",
        height="calc(100vh - 290px)",
        overflow_y="auto",
        padding="14px",
        border_radius="16px",
        background=rx.color("slate", 2),
        border=f"1px solid {rx.color('slate', 4)}",
        border_top=f"3px solid {rx.color(color, 7)}",
        flex_shrink="0",
    )

# ── Tablero Kanban completo ───────────────────────────────────────────────────

def kanban_board() -> rx.Component:
    columns = [
        ("RECEIVED",     "Recibido",       "package",      "gray",   TrackingState.received),
        ("IN_DIAGNOSIS", "Diagnóstico",    "stethoscope",  "amber",  TrackingState.in_diagnosis),
        ("IN_REPAIR",    "En reparación",  "wrench",       "cyan",   TrackingState.in_repair),
        ("ON_HOLD",      "En espera",      "clock",        "orange", TrackingState.on_hold),
        ("COMPLETED",    "Finalizado",     "circle-check", "indigo", TrackingState.completed),
        ("DELIVERED",    "Entregado",      "hand-metal",   "green",  TrackingState.delivered),
    ]
    return rx.box(
        rx.hstack(
            kanban_column(*columns[0]),
            kanban_column(*columns[1]),
            kanban_column(*columns[2]),
            kanban_column(*columns[3]),
            kanban_column(*columns[4]),
            kanban_column(*columns[5]),
            spacing="4",
            align_items="start",
            padding_bottom="24px",
        ),
        overflow_x="auto",
        width="100%",
        padding_bottom="8px",
    )

# ── Panel Lateral de Detalle ──────────────────────────────────────────────────

def detail_tabs() -> rx.Component:
    """Tabs de Info / Comentarios / Incidencias."""
    def tab_btn(label: str, tab: str, icon_tag: str) -> rx.Component:
        is_active = TrackingState.active_tab == tab
        return rx.button(
            rx.icon(tag=icon_tag, size=14),
            rx.text(label, size="2"),
            on_click=TrackingState.set_active_tab(tab),
            variant=rx.cond(is_active, "solid", "ghost"),
            color_scheme=rx.cond(is_active, "cyan", "gray"),
            size="2", flex="1",
        )
    return rx.hstack(
        tab_btn("Detalle",       "info",       "info"),
        tab_btn("Comentarios",   "comments",   "message-square"),
        tab_btn("Incidencias",   "incidents",  "triangle-alert"),
        spacing="2", width="100%",
    )


def info_tab() -> rx.Component:
    o = TrackingState.selected_order
    return rx.vstack(
        # Pipeline
        rx.card(
            rx.vstack(
                rx.text("Flujo del Servicio", size="2", weight="bold", color=rx.color("slate", 10)),
                # Pipeline simplificado con pasos
                rx.hstack(
                    *[
                        rx.vstack(
                            rx.box(
                                rx.icon(tag=STATUS_ICONS[s], size=14),
                                width="30px", height="30px",
                                border_radius="full",
                                display="flex", align_items="center", justify_content="center",
                                background=rx.cond(
                                    o["status"] == s, rx.color(STATUS_COLORS[s], 3),
                                    rx.color("slate", 2)
                                ),
                                border=rx.cond(
                                    o["status"] == s,
                                    f"2px solid {rx.color(STATUS_COLORS[s], 8)}",
                                    "2px solid transparent"
                                ),
                            ),
                            rx.text(STATUS_LABELS[s], size="1", text_align="center",
                                    color=rx.cond(o["status"] == s,
                                                  rx.color(STATUS_COLORS[s], 10),
                                                  rx.color("slate", 8))),
                            spacing="1", align_items="center",
                        )
                        for s in STATUS_PIPELINE
                    ],
                    spacing="2", justify="between", width="100%",
                ),
                spacing="3",
            ),
            padding="14px", width="100%",
        ),
        # Grid info
        rx.grid(
            rx.vstack(rx.text("Cliente", size="1", weight="bold", color=rx.color("slate", 9)),
                      rx.text(o["customer"], size="2"), spacing="0"),
            rx.vstack(rx.text("Equipo", size="1", weight="bold", color=rx.color("slate", 9)),
                      rx.text(o["device"], size="2"), spacing="0"),
            rx.vstack(rx.text("Técnico", size="1", weight="bold", color=rx.color("slate", 9)),
                      rx.text(o["technician"], size="2",
                              color=rx.cond(o["is_unassigned"], rx.color("amber", 9), rx.color("slate", 11))),
                      spacing="0"),
            rx.vstack(rx.text("Prioridad", size="1", weight="bold", color=rx.color("slate", 9)),
                      rx.badge(o["priority"], color_scheme=o["priority_color"], variant="soft", size="1"),
                      spacing="0"),
            rx.vstack(rx.text("Fecha Estimada", size="1", weight="bold", color=rx.color("slate", 9)),
                      rx.text(o["due_date"], size="2",
                              color=rx.cond(o["is_overdue"], rx.color("red", 9), rx.color("slate", 11))),
                      spacing="0"),
            rx.vstack(rx.text("Cotización", size="1", weight="bold", color=rx.color("slate", 9)),
                      rx.text("$", o["price"], size="2", weight="bold", color=rx.color("cyan", 9)),
                      spacing="0"),
            columns="2", spacing="4", width="100%",
        ),
        # Descripción del problema
        rx.card(
            rx.vstack(
                rx.hstack(rx.icon(tag="message-square", size=14, color=rx.color("amber", 9)),
                          rx.text("Problema Reportado", size="2", weight="bold"), spacing="2"),
                rx.text(o["description"], size="2", color=rx.color("slate", 11)),
                spacing="2",
            ),
            padding="14px", width="100%",
        ),
        rx.cond(
            o["repair_notes"] != "",
            rx.card(
                rx.vstack(
                    rx.hstack(rx.icon(tag="wrench", size=14, color=rx.color("cyan", 9)),
                              rx.text("Notas Técnicas", size="2", weight="bold"), spacing="2"),
                    rx.text(o["repair_notes"], size="2", color=rx.color("slate", 11)),
                    spacing="2",
                ),
                padding="14px", width="100%",
            ),
        ),
        spacing="4", width="100%",
    )


def comments_tab() -> rx.Component:
    return rx.vstack(
        # Thread de comentarios
        rx.cond(
            TrackingState.comments.length() >= 1,
            rx.vstack(
                rx.foreach(
                    TrackingState.comments,
                    lambda c: rx.hstack(
                        # Avatar con iniciales
                        rx.box(
                            rx.text(c["initials"], size="2", weight="bold", color="white"),
                            width="34px", height="34px", border_radius="full",
                            background=rx.cond(c["is_internal"],
                                               rx.color("amber", 8), rx.color("blue", 8)),
                            display="flex", align_items="center", justify_content="center",
                            flex_shrink="0",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text(c["author"], size="2", weight="bold"),
                                rx.badge(c["tag_label"], color_scheme=c["tag_color"],
                                         variant="soft", size="1"),
                                rx.spacer(),
                                rx.text(c["date"], size="1", color=rx.color("slate", 8)),
                                width="100%",
                            ),
                            rx.box(
                                rx.text(c["content"], size="2", color=rx.color("slate", 11)),
                                padding="10px 12px",
                                border_radius="0 10px 10px 10px",
                                background=rx.cond(c["is_internal"],
                                                   rx.color("amber", 1), rx.color("blue", 1)),
                                border=rx.cond(c["is_internal"],
                                              f"1px solid {rx.color('amber', 4)}",
                                              f"1px solid {rx.color('blue', 4)}"),
                                width="100%",
                            ),
                            spacing="1", width="100%",
                        ),
                        spacing="2", width="100%", align_items="start",
                    )
                ),
                spacing="3", width="100%",
            ),
            rx.vstack(
                rx.icon(tag="message-square-off", size=32, color=rx.color("slate", 4)),
                rx.text("Sin comentarios aún.", size="2", color=rx.color("slate", 8)),
                spacing="2", align_items="center", padding_y="24px", width="100%",
            ),
        ),
        rx.divider(opacity=0.3),
        # Formulario nuevo comentario
        rx.vstack(
            rx.text_area(
                placeholder="Escribe un comentario o actualización...",
                value=TrackingState.new_comment_text,
                on_change=TrackingState.set_new_comment_text,
                rows="3", width="100%", resize="vertical",
            ),
            rx.hstack(
                rx.checkbox(
                    "Solo interno (no visible al cliente)",
                    checked=TrackingState.new_comment_internal,
                    on_change=TrackingState.toggle_comment_internal,
                    size="1",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon(tag="send", size=14),
                    rx.text("Enviar"),
                    on_click=TrackingState.add_comment,
                    color_scheme="cyan", size="2",
                ),
                width="100%", align_items="center",
            ),
            spacing="2", width="100%",
        ),
        spacing="4", width="100%",
    )


def incidents_tab() -> rx.Component:
    return rx.vstack(
        # Botón agregar incidencia
        rx.hstack(
            rx.text("Incidencias Técnicas", size="2", weight="bold"),
            rx.spacer(),
            rx.button(
                rx.icon(tag="plus", size=14),
                rx.text("Registrar"),
                on_click=TrackingState.toggle_incident_form,
                color_scheme="orange", variant="soft", size="2",
            ),
            width="100%",
        ),
        # Formulario nueva incidencia
        rx.cond(
            TrackingState.show_incident_form,
            rx.card(
                rx.vstack(
                    rx.text("Nuevo Problema Encontrado", size="2", weight="bold",
                            color=rx.color("orange", 10)),
                    rx.text_area(
                        placeholder="Describe detalladamente el problema o falla encontrada...",
                        value=TrackingState.new_problem_text,
                        on_change=TrackingState.set_new_problem_text,
                        rows="3", width="100%",
                    ),
                    rx.hstack(
                        rx.button("Cancelar", on_click=TrackingState.toggle_incident_form,
                                  variant="ghost", color_scheme="gray", size="2"),
                        rx.button("Registrar Incidencia", on_click=TrackingState.add_incident,
                                  color_scheme="orange", size="2"),
                        spacing="2", justify="end", width="100%",
                    ),
                    spacing="3",
                ),
                padding="14px", width="100%",
                border=f"1px solid {rx.color('orange', 5)}",
                background=rx.color("orange", 1),
            ),
        ),
        # Lista de incidencias
        rx.cond(
            TrackingState.incidents.length() >= 1,
            rx.vstack(
                rx.foreach(
                    TrackingState.incidents,
                    lambda i: rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.cond(
                                    i["is_resolved"],
                                    rx.icon(tag="circle-check", size=14, color=rx.color("green", 9)),
                                    rx.icon(tag="triangle-alert", size=14, color=rx.color("red", 9)),
                                ),
                                rx.text("Problema encontrado", size="2", weight="bold"),
                                rx.spacer(),
                                rx.badge(i["status_label"], color_scheme=i["status_color"],
                                         variant="soft", size="1"),
                                rx.text(i["date"], size="1", color=rx.color("slate", 8)),
                                width="100%", spacing="2",
                            ),
                            rx.text(i["problem"], size="2", color=rx.color("slate", 11)),
                            rx.cond(
                                i["is_resolved"],
                                rx.vstack(
                                    rx.divider(opacity=0.3),
                                    rx.hstack(
                                        rx.icon(tag="check-circle", size=12,
                                                color=rx.color("green", 8)),
                                        rx.text("Solución aplicada:", size="1", weight="bold",
                                                color=rx.color("green", 9)),
                                        spacing="1",
                                    ),
                                    rx.text(i["solution"], size="2", color=rx.color("slate", 10)),
                                    rx.text("Resuelto: ", i["resolved_at"], size="1",
                                            color=rx.color("slate", 8)),
                                    spacing="1", width="100%",
                                ),
                                rx.cond(
                                    TrackingState.resolving_incident_id == i["id"],
                                    rx.vstack(
                                        rx.text_area(
                                            placeholder="Describe la solución aplicada...",
                                            value=TrackingState.new_solution_text,
                                            on_change=TrackingState.set_new_solution_text,
                                            rows="2", width="100%",
                                        ),
                                        rx.hstack(
                                            rx.button("Cancelar",
                                                      on_click=TrackingState.cancel_resolve,
                                                      variant="ghost", size="1"),
                                            rx.button("Confirmar Resolución",
                                                      on_click=TrackingState.resolve_incident,
                                                      color_scheme="green", size="1"),
                                            spacing="2", justify="end", width="100%",
                                        ),
                                        spacing="2",
                                    ),
                                    rx.button(
                                        rx.icon(tag="check", size=13),
                                        rx.text("Marcar Resuelto"),
                                        on_click=TrackingState.start_resolving(i["id"]),
                                        color_scheme="green", variant="soft", size="1",
                                    ),
                                ),
                            ),
                            spacing="2",
                        ),
                        padding="12px 14px",
                        border=rx.cond(i["is_resolved"],
                                       f"1px solid {rx.color('green', 4)}",
                                       f"1px solid {rx.color('red', 4)}"),
                        background=rx.cond(i["is_resolved"],
                                           rx.color("green", 1), rx.color("red", 1)),
                        width="100%",
                    )
                ),
                spacing="3", width="100%",
            ),
            rx.vstack(
                rx.icon(tag="shield-check", size=32, color=rx.color("slate", 4)),
                rx.text("Sin incidencias registradas.", size="2", color=rx.color("slate", 8)),
                spacing="2", align_items="center", padding_y="24px", width="100%",
            ),
        ),
        spacing="4", width="100%",
    )


def detail_panel() -> rx.Component:
    return rx.cond(
        TrackingState.show_detail,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.vstack(
                        rx.text(TrackingState.selected_order["ticket"],
                                size="4", weight="bold"),
                        rx.hstack(
                            rx.badge(
                                TrackingState.selected_order["status_label"],
                                color_scheme=TrackingState.selected_order["status_color"],
                                variant="soft",
                            ),
                            rx.cond(
                                TrackingState.selected_order["is_overdue"],
                                rx.badge("⚠ VENCIDA", color_scheme="red", variant="solid"),
                            ),
                            spacing="2",
                        ),
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon(tag="x", size=18),
                        on_click=TrackingState.close_detail,
                        variant="ghost", color_scheme="gray",
                    ),
                    width="100%", align_items="start",
                ),
                # Tabs
                detail_tabs(),
                rx.divider(opacity=0.2),
                # Contenido según tab activo
                rx.box(
                    rx.cond(TrackingState.active_tab == "info",       info_tab()),
                    rx.cond(TrackingState.active_tab == "comments",   comments_tab()),
                    rx.cond(TrackingState.active_tab == "incidents",  incidents_tab()),
                    width="100%",
                ),
                spacing="4", width="100%",
                padding="20px",
            ),
            position="fixed", top="0", right="0",
            width="440px", height="100vh",
            background=rx.color("slate", 1),
            border_left=f"1px solid {rx.color('slate', 4)}",
            box_shadow="-8px 0 40px rgba(0,0,0,0.14)",
            z_index="200",
            overflow_y="auto",
        ),
    )

# ── Header de página ─────────────────────────────────────────────────────────

def tracking_header() -> rx.Component:
    return page_header(
        "Seguimiento de Reparaciones",
        "Dashboard en tiempo real del estado de todos los equipos en servicio.",
        actions=[
            rx.hstack(
                rx.cond(
                    TrackingState.last_refresh != "",
                    rx.text(
                        "Actualizado: ", TrackingState.last_refresh,
                        size="1", color=rx.color("slate", 8),
                    ),
                ),
                rx.input(
                    placeholder="Filtrar por ticket, cliente...",
                    value=TrackingState.kanban_filter,
                    on_change=TrackingState.set_kanban_filter,
                    width="220px", size="2", radius="large",
                ),
                rx.button(
                    rx.cond(
                        TrackingState.is_loading,
                        rx.spinner(size="2"),
                        rx.icon(tag="refresh-cw", size=16),
                    ),
                    rx.text("Actualizar"),
                    on_click=TrackingState.fetch_all_data,
                    variant="soft", color_scheme="gray", radius="large",
                    disabled=TrackingState.is_loading,
                ),
                spacing="3", align_items="center",
            ),
        ],
    )

# ── Página principal ──────────────────────────────────────────────────────────

def tracking_page() -> rx.Component:
    return rx.hstack(
        sidebar("/tracking"),
        rx.box(
            rx.container(
                rx.vstack(
                    tracking_header(),
                    # Alert-strip
                    alert_banner(),
                    # KPI global
                    rx.hstack(
                        rx.card(
                            rx.hstack(
                                rx.icon(tag="activity", size=20, color=rx.color("cyan", 9)),
                                rx.vstack(
                                    rx.text(TrackingState.total_active, size="5", weight="bold"),
                                    rx.text("Órdenes Activas", size="1", color=rx.color("slate", 9)),
                                    spacing="0",
                                ),
                                spacing="3", align_items="center",
                            ),
                            padding="16px 24px",
                        ),
                        rx.cond(
                            TrackingState.alert_count > 0,
                            rx.card(
                                rx.hstack(
                                    rx.box(
                                        rx.icon(tag="bell-ring", size=20, color=rx.color("red", 9)),
                                        padding="8px", border_radius="full",
                                        background=rx.color("red", 2),
                                        animation="pulse 2s infinite",
                                    ),
                                    rx.vstack(
                                        rx.text(TrackingState.alert_count, size="5", weight="bold",
                                                color=rx.color("red", 9)),
                                        rx.text("Alertas Activas", size="1", color=rx.color("slate", 9)),
                                        spacing="0",
                                    ),
                                    spacing="3", align_items="center",
                                ),
                                padding="16px 24px",
                                border=f"1px solid {rx.color('red', 5)}",
                                background=rx.color("red", 1),
                            ),
                        ),
                        spacing="4",
                    ),
                    # Tablero Kanban
                    kanban_board(),
                    spacing="5",
                    padding_bottom="48px",
                    width="100%",
                ),
                size="4",
                padding_x="32px",
            ),
            flex="1",
            overflow_y="auto",
            min_width="0",
        ),
        # Panel detalle lateral
        detail_panel(),
        background_color=rx.color("slate", 2),
        min_height="100vh",
        spacing="0",
        align_items="start",
        width="100%",
    )
