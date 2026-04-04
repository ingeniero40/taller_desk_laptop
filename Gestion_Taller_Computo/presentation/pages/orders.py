import reflex as rx
from typing import Dict, List, Any
from ..state.order_state import OrderState, STATUS_PIPELINE, STATUS_LABELS, STATUS_COLORS
from ..components.sidebar import sidebar
from ..components.page_header import page_header

# ── Pipeline Visual de Estados ────────────────────────────────────────────────

def status_pipeline_bar() -> rx.Component:
    """Barra horizontal de progreso con los 6 estados del flujo."""
    current_status = OrderState.selected_order["status"]

    def step_node(raw: str, icon: str, label: str, idx: int) -> rx.Component:
        is_active = current_status == raw
        is_done = OrderState.selected_status_index > idx
        color = rx.cond(
            is_done, rx.color("cyan", 9),
            rx.cond(is_active, rx.color("cyan", 9), rx.color("slate", 5))
        )
        bg = rx.cond(
            is_done, rx.color("cyan", 3),
            rx.cond(is_active, rx.color("cyan", 2), rx.color("slate", 2))
        )
        return rx.vstack(
            rx.box(
                rx.icon(tag=icon, size=16, color=color),
                width="36px", height="36px",
                border_radius="full",
                background=bg,
                border=rx.cond(is_active, f"2px solid {rx.color('cyan', 9)}", "2px solid transparent"),
                display="flex", align_items="center", justify_content="center",
            ),
            rx.text(label, size="1", color=rx.cond(is_active, rx.color("cyan", 10), rx.color("slate", 9)),
                    weight=rx.cond(is_active, "bold", "regular"), text_align="center"),
            spacing="1", align_items="center",
        )

    return rx.hstack(
        step_node("RECEIVED",    "package",         "Recibido",     0),
        rx.box(flex="1", height="2px", background=rx.color("slate", 4), margin_top="-18px"),
        step_node("IN_DIAGNOSIS","stethoscope",     "Diagnóstico",  1),
        rx.box(flex="1", height="2px", background=rx.color("slate", 4), margin_top="-18px"),
        step_node("IN_REPAIR",   "wrench",          "En reparación",2),
        rx.box(flex="1", height="2px", background=rx.color("slate", 4), margin_top="-18px"),
        step_node("ON_HOLD",     "clock",           "En espera",    3),
        rx.box(flex="1", height="2px", background=rx.color("slate", 4), margin_top="-18px"),
        step_node("COMPLETED",   "circle-check",    "Finalizado",   4),
        rx.box(flex="1", height="2px", background=rx.color("slate", 4), margin_top="-18px"),
        step_node("DELIVERED",   "hand-metal",      "Entregado",    5),
        width="100%", align_items="center", spacing="0", padding_x="4px",
    )

# ── Tarjeta de Orden ──────────────────────────────────────────────────────────

def order_card(order: Dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(order["ticket"], size="2", weight="bold", color=rx.color("slate", 12)),
                    rx.text(order["date"], size="1", color=rx.color("slate", 9)),
                    spacing="0",
                ),
                rx.spacer(),
                rx.badge(
                    order["priority"],
                    color_scheme=order["priority_color"],
                    variant="soft", radius="full", size="1",
                ),
                rx.badge(
                    order["status_label"],
                    color_scheme=order["status_color"],
                    variant="soft", radius="full", size="1",
                ),
                width="100%", align_items="start",
            ),
            rx.divider(opacity=0.3),
            rx.hstack(
                rx.icon(tag="laptop", size=14, color=rx.color("slate", 9)),
                rx.text(order["device"], size="2", color=rx.color("slate", 11), no_of_lines=1),
                spacing="1", width="100%",
            ),
            rx.hstack(
                rx.icon(tag="user", size=14, color=rx.color("slate", 9)),
                rx.text(order["customer"], size="2", color=rx.color("slate", 11)),
                spacing="1", width="100%",
            ),
            rx.hstack(
                rx.icon(tag="user-cog", size=14, color=rx.color("slate", 9)),
                rx.text(order["technician"], size="1", color=rx.color("slate", 9)),
                rx.spacer(),
                rx.text("$", order["price"], size="2", weight="bold", color=rx.color("cyan", 9)),
                spacing="1", width="100%",
            ),
            rx.hstack(
                rx.button(
                    rx.icon(tag="eye", size=14),
                    rx.text("Detalle"),
                    on_click=OrderState.open_order_detail(order),
                    size="1", variant="soft", color_scheme="indigo", flex="1",
                ),
                rx.button(
                    rx.icon(tag="pencil", size=14),
                    rx.text("Estado"),
                    on_click=OrderState.open_status_modal(order),
                    size="1", variant="soft", color_scheme="gray", flex="1",
                ),
                spacing="2", width="100%",
            ),
            spacing="3",
        ),
        padding="16px",
        border_radius="16px",
        border=f"1px solid {rx.color('slate', 4)}",
        cursor="pointer",
        _hover={"border_color": rx.color("cyan", 6), "box_shadow": "0 4px 20px rgba(0,0,0,0.08)"},
        transition="all 0.15s ease",
        width="100%",
    )

# ── Panel de Detalle Lateral ──────────────────────────────────────────────────

def detail_panel() -> rx.Component:
    return rx.cond(
        OrderState.show_detail_panel,
        rx.box(
            rx.vstack(
                # Header del panel
                rx.hstack(
                    rx.vstack(
                        rx.text(OrderState.selected_order["ticket"], size="4", weight="bold"),
                        rx.text("Detalle de Orden", size="1", color=rx.color("slate", 9)),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon(tag="x", size=18),
                        on_click=OrderState.close_detail_panel,
                        variant="ghost", color_scheme="gray",
                    ),
                    width="100%",
                ),

                rx.divider(opacity=0.3),

                # Pipeline del estado actual
                rx.card(
                    rx.vstack(
                        rx.text("Flujo del Servicio", size="2", weight="bold", color=rx.color("slate", 10)),
                        status_pipeline_bar(),
                        spacing="3",
                    ),
                    padding="16px", width="100%",
                ),

                # Info grid
                rx.grid(
                    rx.vstack(
                        rx.text("Cliente", size="1", color=rx.color("slate", 9), weight="bold"),
                        rx.text(OrderState.selected_order["customer"], size="2"),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Equipo", size="1", color=rx.color("slate", 9), weight="bold"),
                        rx.text(OrderState.selected_order["device"], size="2"),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Técnico", size="1", color=rx.color("slate", 9), weight="bold"),
                        rx.text(OrderState.selected_order["technician"], size="2"),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Cotización", size="1", color=rx.color("slate", 9), weight="bold"),
                        rx.text("$", OrderState.selected_order["price"], size="2", weight="bold",
                                color=rx.color("cyan", 9)),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Entrega Estimada", size="1", color=rx.color("slate", 9), weight="bold"),
                        rx.text(OrderState.selected_order["due_date"], size="2"),
                        spacing="0",
                    ),
                    rx.vstack(
                        rx.text("Entrega Real", size="1", color=rx.color("slate", 9), weight="bold"),
                        rx.text(OrderState.selected_order["actual_delivery"], size="2"),
                        spacing="0",
                    ),
                    columns="2", spacing="4", width="100%",
                ),

                # Descripción del problema
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon(tag="message-square", size=14, color=rx.color("amber", 9)),
                            rx.text("Problema Reportado", size="2", weight="bold"),
                            spacing="2",
                        ),
                        rx.text(
                            OrderState.selected_order["description"],
                            size="2", color=rx.color("slate", 11),
                        ),
                        spacing="2",
                    ),
                    padding="14px", width="100%",
                ),

                # Notas de reparación
                rx.cond(
                    OrderState.selected_order["repair_notes"] != "",
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon(tag="wrench", size=14, color=rx.color("cyan", 9)),
                                rx.text("Notas Técnicas", size="2", weight="bold"),
                                spacing="2",
                            ),
                            rx.text(
                                OrderState.selected_order["repair_notes"],
                                size="2", color=rx.color("slate", 11),
                            ),
                            spacing="2",
                        ),
                        padding="14px", width="100%",
                    ),
                ),

                # Timeline de historial
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="history", size=16, color=rx.color("slate", 9)),
                        rx.text("Historial de Cambios", size="2", weight="bold", color=rx.color("slate", 10)),
                        spacing="2",
                    ),
                    rx.cond(
                        OrderState.order_history.length() >= 1,
                        rx.vstack(
                            rx.foreach(
                                OrderState.order_history,
                                lambda h: rx.hstack(
                                    rx.vstack(
                                        rx.box(
                                            width="10px", height="10px", border_radius="full",
                                            background=rx.color(h["color"], 9),
                                        ),
                                        rx.box(width="2px", flex="1", background=rx.color("slate", 4)),
                                        align_items="center", spacing="0",
                                    ),
                                    rx.card(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.badge(h["to"], color_scheme=h["color"],
                                                         variant="soft", size="1"),
                                                rx.spacer(),
                                                rx.text(h["date"], size="1",
                                                        color=rx.color("slate", 9)),
                                                width="100%",
                                            ),
                                            rx.cond(
                                                h["notes"] != "",
                                                rx.text(h["notes"], size="1",
                                                        color=rx.color("slate", 10)),
                                            ),
                                            spacing="1",
                                        ),
                                        padding="10px 14px",
                                        width="100%",
                                    ),
                                    spacing="2", align_items="start", width="100%",
                                )
                            ),
                            spacing="0", width="100%",
                        ),
                        rx.text("Sin historial registrado.", size="1", color=rx.color("slate", 9)),
                    ),
                    spacing="3", width="100%",
                ),

                spacing="4",
                width="100%",
                height="100vh",
                overflow_y="auto",
                padding="20px",
            ),
            position="fixed",
            top="0",
            right="0",
            width="420px",
            height="100vh",
            background=rx.color("slate", 1),
            border_left=f"1px solid {rx.color('slate', 4)}",
            box_shadow="-8px 0 32px rgba(0,0,0,0.12)",
            z_index="100",
            overflow_y="auto",
        ),
    )

# ── Filtros y Contadores ──────────────────────────────────────────────────────

def filters_bar() -> rx.Component:
    def count_badge(label: str, status: str, color: str) -> rx.Component:
        return rx.button(
            rx.text(label, size="2"),
            variant=rx.cond(OrderState.status_filter == status, "solid", "soft"),
            color_scheme=rx.cond(OrderState.status_filter == status, color, "gray"),
            on_click=OrderState.set_status_filter(status),
            radius="large", size="2",
        )

    return rx.vstack(
        rx.hstack(
            rx.input(
                rx.input.slot(rx.icon(tag="search", size=16)),
                placeholder="Buscar ticket, cliente o equipo...",
                value=OrderState.search_query,
                on_change=OrderState.set_search_query,
                width="280px",
                radius="large",
            ),
            rx.spacer(),
            rx.text(
                OrderState.filtered_orders.length(), " órdenes",
                size="2", color=rx.color("slate", 9),
            ),
            width="100%",
        ),
        rx.hstack(
            count_badge("Todas", "Todas", "gray"),
            count_badge("Recibido", "RECEIVED", "gray"),
            count_badge("Diagnóstico", "IN_DIAGNOSIS", "amber"),
            count_badge("En reparación", "IN_REPAIR", "cyan"),
            count_badge("En espera", "ON_HOLD", "orange"),
            count_badge("Finalizado", "COMPLETED", "indigo"),
            count_badge("Entregado", "DELIVERED", "green"),
            spacing="2", flex_wrap="wrap",
        ),
        spacing="3", width="100%",
    )

# ── Modal de Actualización ────────────────────────────────────────────────────

def status_update_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Actualizar Orden de Trabajo"),
            rx.dialog.description(f"Ticket: {OrderState.selected_order['ticket']}"),
            rx.vstack(
                rx.vstack(
                    rx.text("Nuevo Estado", size="2", weight="medium"),
                    rx.select(
                        [
                            "RECEIVED", "IN_DIAGNOSIS", "IN_REPAIR",
                            "ON_HOLD", "COMPLETED", "DELIVERED"
                        ],
                        on_change=OrderState.set_new_status,
                        value=OrderState.new_status,
                        width="100%", radius="large",
                    ),
                    spacing="1", width="100%",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Horas Estimadas", size="2", weight="medium"),
                        rx.input(
                            type="number", placeholder="0",
                            value=OrderState.new_estimated_hours.to_string(),
                            on_change=OrderState.set_new_estimated_hours,
                            width="100%", radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Horas Reales", size="2", weight="medium"),
                        rx.input(
                            type="number", placeholder="0",
                            value=OrderState.new_actual_hours.to_string(),
                            on_change=OrderState.set_new_actual_hours,
                            width="100%", radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),
                rx.vstack(
                    rx.text("Cotización / Precio", size="2", weight="medium"),
                    rx.input(
                        type="number", placeholder="0.00",
                        value=OrderState.new_price.to_string(),
                        on_change=OrderState.set_new_price,
                        width="100%", radius="large",
                    ),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Notas Técnicas / Resolución", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Ej: Se reemplazó el SSD por uno de 480GB...",
                        on_change=OrderState.set_status_notes,
                        value=OrderState.status_notes,
                        rows="4", width="100%", resize="vertical",
                    ),
                    spacing="1", width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                    rx.button(
                        "Guardar Cambios",
                        on_click=OrderState.update_order_status,
                        color_scheme="indigo",
                    ),
                    spacing="3", width="100%", justify="end",
                ),
                spacing="4", width="100%",
            ),
            max_width="500px",
            border_radius="24px",
        ),
        open=OrderState.show_status_modal,
        on_open_change=OrderState.set_show_status_modal,
    )

# ── Modal Nueva Orden ─────────────────────────────────────────────────────────

def new_order_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nueva Orden de Servicio"),
            rx.dialog.description("Registra el cliente, equipo y falla reportada."),
            rx.vstack(
                rx.grid(
                    rx.vstack(
                        rx.text("Cliente", size="2", weight="medium"),
                        rx.select(
                            OrderState.customer_names,
                            on_change=OrderState.set_selected_customer,
                            placeholder="Seleccionar cliente",
                            width="100%", radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Equipo", size="2", weight="medium"),
                        rx.select(
                            OrderState.device_labels,
                            on_change=OrderState.set_selected_device_label,
                            placeholder="Seleccionar equipo",
                            width="100%", radius="large",
                            disabled=OrderState.customer_devices.length() == 0,
                        ),
                        rx.cond(
                            OrderState.customer_devices.length() == 0,
                            rx.text("El cliente no tiene equipos registrados.",
                                    size="1", color=rx.color("red", 9)),
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Prioridad", size="2", weight="medium"),
                        rx.select(
                            ["Baja", "Media", "Alta", "Crítica"],
                            value=OrderState.new_order_priority,
                            on_change=OrderState.set_new_order_priority,
                            width="100%", radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Técnico Asignado", size="2", weight="medium"),
                        rx.select(
                            OrderState.technician_names,
                            on_change=OrderState.set_selected_technician,
                            placeholder="Sin asignar",
                            width="100%", radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="3", width="100%",
                ),
                rx.vstack(
                    rx.text("Descripción del Problema *", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Describe el fallo o servicio solicitado...",
                        on_change=OrderState.set_order_description,
                        value=OrderState.order_description,
                        rows="4", width="100%", resize="vertical",
                    ),
                    spacing="1", width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                    rx.button(
                        rx.icon(tag="plus", size=16),
                        rx.text("Abrir Orden"),
                        on_click=OrderState.save_new_order,
                        color_scheme="indigo",
                        disabled=OrderState.selected_device_id == "",
                    ),
                    spacing="3", width="100%", justify="end",
                ),
                spacing="4", width="100%",
            ),
            max_width="600px",
            border_radius="24px",
        ),
        open=OrderState.show_order_modal,
        on_open_change=OrderState.set_show_order_modal,
    )

# ── KPIs de Trabajo ───────────────────────────────────────────────────────────

def kpi_strip() -> rx.Component:
    def kpi(label: str, status: str, icon: str, color: str) -> rx.Component:
        return rx.card(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=20, color=rx.color(color, 9)),
                    padding="10px",
                    border_radius="10px",
                    background=rx.color(color, 2),
                ),
                rx.vstack(
                    rx.text(OrderState.status_counts[status], size="5", weight="bold"),
                    rx.text(label, size="1", color=rx.color("slate", 9)),
                    spacing="0",
                ),
                spacing="3", align_items="center",
            ),
            padding="16px", flex="1",
        )

    return rx.hstack(
        kpi("Recibidos",     "RECEIVED",     "package",       "gray"),
        kpi("Diagnóstico",   "IN_DIAGNOSIS", "stethoscope",   "amber"),
        kpi("En reparación", "IN_REPAIR",    "wrench",         "cyan"),
        kpi("En espera",     "ON_HOLD",      "clock",          "orange"),
        kpi("Finalizados",   "COMPLETED",    "circle-check",   "indigo"),
        kpi("Entregados",    "DELIVERED",    "hand-metal",     "green"),
        spacing="3", width="100%",
    )

# ── Página Principal ──────────────────────────────────────────────────────────

def orders_page() -> rx.Component:
    return rx.hstack(
        sidebar("/orders"),
        rx.box(
            rx.container(
                rx.vstack(
                    page_header(
                        "Órdenes de Trabajo",
                        "Seguimiento del ciclo completo de reparaciones: recepción → diagnóstico → reparación → entrega.",
                        actions=[
                            rx.button(
                                rx.icon(tag="plus", size=18),
                                rx.text("Nueva Orden"),
                                on_click=OrderState.open_new_order_modal,
                                color_scheme="indigo",
                                variant="solid",
                                radius="large",
                            ),
                            rx.button(
                                rx.icon(tag="refresh-cw", size=18),
                                on_click=OrderState.fetch_orders,
                                variant="soft",
                                color_scheme="gray",
                                radius="large",
                            ),
                        ],
                    ),

                    # KPIs
                    kpi_strip(),

                    # Filtros
                    rx.card(
                        filters_bar(),
                        padding="20px",
                        border_radius="16px",
                        width="100%",
                    ),

                    # Grid de tarjetas
                    rx.cond(
                        OrderState.is_loading,
                        rx.hstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando órdenes...", size="2", color=rx.color("slate", 9)),
                            spacing="3", justify="center", width="100%", padding="48px",
                        ),
                        rx.cond(
                            OrderState.filtered_orders.length() >= 1,
                            rx.grid(
                                rx.foreach(OrderState.filtered_orders, order_card),
                                columns="3",
                                spacing="4",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.icon(tag="clipboard-x", size=48, color=rx.color("slate", 5)),
                                rx.text("No hay órdenes con los filtros seleccionados.",
                                        size="3", color=rx.color("slate", 9)),
                                spacing="3", align_items="center",
                                padding="64px", width="100%",
                            ),
                        ),
                    ),

                    # Modales
                    status_update_modal(),
                    new_order_modal(),

                    spacing="5",
                    padding_bottom="48px",
                    width="100%",
                ),
                size="4",
                padding_x="40px",
            ),
            flex="1",
            overflow_y="auto",
        ),
        # Panel lateral de detalle
        detail_panel(),
        background_color=rx.color("slate", 2),
        min_height="100vh",
        spacing="0",
        align_items="start",
        width="100%",
    )
