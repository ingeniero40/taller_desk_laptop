import reflex as rx
from ..state.order_state import OrderState
from ..components.sidebar import sidebar
from ..components.page_header import page_header

def order_header() -> rx.Component:
    """Encabezado superior de órdenes de trabajo."""
    return page_header(
        "Órdenes de Trabajo",
        "Seguimiento en tiempo real de reparaciones y diagnósticos.",
        actions=[
            rx.button(
                rx.icon(tag="plus", size=18),
                rx.text("Nueva Orden"),
                on_click=OrderState.open_new_order_modal,
                color_scheme="cyan",
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
        ]
    )

def order_table() -> rx.Component:
    """Tabla de órdenes de trabajo."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Ticket"),
                rx.table.column_header_cell("Fecha"),
                rx.table.column_header_cell("Descripción Falla"),
                rx.table.column_header_cell("Monto Quoted"),
                rx.table.column_header_cell("Estado Actual"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                OrderState.filtered_orders,
                lambda o: rx.table.row(
                    rx.table.cell(rx.text(o["ticket"], weight="bold")),
                    rx.table.cell(rx.text(o["date"])),
                    rx.table.cell(rx.text(o["description"], overflow="hidden", white_space="nowrap", text_overflow="ellipsis", width="200px")),
                    rx.table.cell(rx.text(f"${o['price']}", weight="bold")),
                    rx.table.cell(
                        rx.badge(
                            o["status"],
                            color_scheme=o["status_color"],
                            variant="soft",
                        )
                    ),
                    rx.table.cell(
                        rx.hstack(
                            rx.icon_button(
                                rx.icon(tag="clipboard-check", size=16),
                                variant="soft",
                                color_scheme="cyan",
                                on_click=lambda: OrderState.open_status_modal(o),
                            ),
                            rx.icon_button(
                                rx.icon(tag="pencil", size=16),
                                variant="ghost",
                                color_scheme="gray",
                            ),
                            spacing="2",
                        )
                    )
                )
            )
        )
    )

def status_update_modal() -> rx.Component:
    """Modal para actualizar el avance técnico de una orden."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Actualización de Órden"),
            rx.dialog.description(f"Ticket: {OrderState.selected_order['ticket']}"),
            rx.vstack(
                rx.vstack(
                    rx.text("Nuevo Estado", size="2", weight="medium"),
                    rx.select(
                        ["RECEIVED", "IN_DIAGNOSIS", "IN_REPAIR", "COMPLETED", "DELIVERED", "CANCELLED"],
                        on_change=OrderState.set_new_status,
                        value=OrderState.new_status,
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Presupuesto / Cotización Quoted", size="2", weight="medium"),
                    rx.input(
                         type="number", 
                         value=OrderState.new_price.to_string(),
                         on_change=OrderState.set_new_price,
                         width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Notas Técnicas / Resolución", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Ej: Se cambio disco duro por SDD 480GB SATA...",
                        on_change=OrderState.set_status_notes,
                        value=OrderState.status_notes,
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancelar", variant="soft")),
                    rx.button("Guardar Cambios", on_click=OrderState.update_order_status, color_scheme="cyan"),
                    spacing="3",
                    width="100%",
                    justify="end",
                    padding_top="16px",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="450px",
            border_radius="24px",
        ),
        open=OrderState.show_status_modal,
        on_open_change=OrderState.set_show_status_modal,
    )

def new_order_modal() -> rx.Component:
    """Modal para la apertura de una nueva orden de servicio."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Apertura de Órden de Servicio"),
            rx.dialog.description("Vincule un cliente y su equipo para iniciar el proceso."),
            rx.vstack(
                rx.vstack(
                    rx.text("Cliente", size="2", weight="medium"),
                    rx.select(
                        OrderState.customer_ids,
                        on_change=OrderState.set_selected_customer,
                        value=OrderState.selected_customer_id,
                        placeholder="Seleccione un cliente",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Equipo / Dispositivo", size="2", weight="medium"),
                    rx.select(
                        OrderState.device_ids,
                        on_change=OrderState.set_selected_device_id,
                        value=OrderState.selected_device_id,
                        placeholder="Seleccione el equipo",
                        width="100%",
                        disabled=OrderState.customer_devices.length() == 0,
                    ),
                    rx.cond(
                        OrderState.customer_devices.length() == 0,
                        rx.text("Este cliente no tiene equipos registrados.", size="1", color=rx.color("red", 9)),
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Descripción del Problema / Falla", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Ej: No enciende, pantalla quebrada, limpieza...",
                        on_change=OrderState.set_order_description,
                        value=OrderState.order_description,
                        width="100%",
                        height="100px",
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancelar", variant="soft")),
                    rx.button(
                        "Abrir Orden", 
                        on_click=OrderState.save_new_order, 
                        color_scheme="cyan",
                        disabled=OrderState.selected_device_id == "",
                    ),
                    spacing="3",
                    width="100%",
                    justify="end",
                    padding_top="16px",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="450px",
            border_radius="24px",
        ),
        open=OrderState.show_order_modal,
        on_open_change=OrderState.set_show_order_modal,
    )

def orders_page() -> rx.Component:
    """Layout principal de la página de órdenes."""
    return rx.hstack(
        sidebar("/orders"),
        rx.container(
            rx.vstack(
                order_header(),
                order_table(),
                status_update_modal(),
                new_order_modal(),
                spacing="5",
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
