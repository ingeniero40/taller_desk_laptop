import reflex as rx
from ..state.device_state import DeviceState
from ..components.sidebar import sidebar

def device_header() -> rx.Component:
    """Encabezado superior de dispositivos."""
    return rx.flex(
        rx.vstack(
            rx.heading("Catálogo de Dispositivos", size="8", weight="bold", color=rx.color("slate", 12)),
            rx.text("Equipos registrados y su historial técnico.", color=rx.color("slate", 10), size="3"),
            spacing="1",
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon(tag="plus", size=18),
                rx.text("Registrar Dispositivo"),
                on_click=DeviceState.open_add_device_modal,
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
            rx.button(
                rx.icon(tag="refresh-cw", size=18),
                on_click=DeviceState.fetch_all_data,
                variant="soft",
                color_scheme="slate",
                radius="large",
            ),
            spacing="3",
        ),
        width="100%",
        align="center",
        padding_y="24px",
    )

def device_filter_bar() -> rx.Component:
    """Barra de búsqueda para dispositivos."""
    return rx.hstack(
        rx.input(
            rx.input.slot(rx.icon(tag="search", size=18, color=rx.color("slate", 9))),
            placeholder="Buscar por Marca, Modelo o Serial...",
            width="320px",
            variant="soft",
            radius="large",
            value=DeviceState.search_query,
            on_change=DeviceState.set_search_query,
        ),
        spacing="3",
        width="100%",
        margin_bottom="16px",
    )

def device_table() -> rx.Component:
    """Tabla de dispositivos."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Marca"),
                rx.table.column_header_cell("Modelo"),
                rx.table.column_header_cell("Número de Serie"),
                rx.table.column_header_cell("Propietario"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                DeviceState.filtered_devices,
                lambda d: rx.table.row(
                    rx.table.cell(rx.text(d["brand"], weight="medium")),
                    rx.table.cell(rx.text(d["model"])),
                    rx.table.cell(rx.code(d["serial"], variant="ghost")),
                    rx.table.cell(rx.text(d["customer"], color=rx.color("cyan", 11))),
                    rx.table.cell(
                        rx.hstack(
                            rx.icon_button(
                                rx.icon(tag="history", size=16),
                                variant="soft",
                                color_scheme="slate",
                                tooltip="Ver Historial de Órdenes",
                            ),
                            rx.icon_button(
                                rx.icon(tag="edit", size=16),
                                variant="ghost",
                                color_scheme="slate",
                            ),
                            spacing="2",
                        )
                    )
                )
            )
        ),
        width="100%",
        variant="surface",
        border_radius="16px",
    )

def add_device_modal() -> rx.Component:
    """Modal de registro de dispositivo."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Registro de Equipo"),
            rx.dialog.description("Vincula un nuevo dispositivo a un cliente."),
            rx.form(
                rx.vstack(
                    rx.grid(
                        rx.vstack(rx.text("Marca", size="2", weight="medium"), rx.input(name="brand", placeholder="Ej: HP, Dell, Apple...", width="100%")),
                        rx.vstack(rx.text("Modelo", size="2", weight="medium"), rx.input(name="model", placeholder="Ej: MacBook Pro M2", width="100%")),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Número de Serie (S/N)", size="2", weight="medium"), 
                        rx.input(name="serial_number", placeholder="Ej: C02F5X2...", width="100%"),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Asociar Cliente Propietario", size="2", weight="medium"),
                        rx.select(
                            DeviceState.customers.map(lambda c: c["id"]),
                            name="customer_id",
                            placeholder="Selecciona el cliente",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancelar", variant="soft")),
                        rx.button("Registrar", type="submit", variant="solid", color_scheme="cyan"),
                        spacing="3",
                        width="100%",
                        justify="end",
                        padding_top="16px",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=DeviceState.save_device,
            ),
            max_width="450px",
            border_radius="24px",
        ),
        open=DeviceState.show_device_modal,
        on_open_change=DeviceState.set_show_device_modal,
    )

def devices_page() -> rx.Component:
    """Página maestra de gestión de dispositivos."""
    return rx.hstack(
        sidebar("/devices"),
        rx.container(
            rx.vstack(
                device_header(),
                device_filter_bar(),
                device_table(),
                add_device_modal(),
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
