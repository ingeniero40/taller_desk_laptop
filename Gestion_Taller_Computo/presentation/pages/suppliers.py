import reflex as rx
from ..state.supplier_state import SupplierState
from ..components.sidebar import sidebar

def supplier_header() -> rx.Component:
    """Encabezado superior de proveedores."""
    return rx.flex(
        rx.vstack(
            rx.heading("Catálogo de Proveedores", size="8", weight="bold", color=rx.color("slate", 12)),
            rx.text("Directorio de socios comerciales y fuentes de suministro.", color=rx.color("slate", 10), size="3"),
            spacing="1",
        ),
        rx.spacer(),
        rx.hstack(
            #rx.label(rx.switch(checked=SupplierState.show_inactive, on_change=SupplierState.toggle_inactive_filter), "Mostrar Inactivos"),
            rx.button(
                rx.icon(tag="plus", size=18),
                rx.text("Nuevo Proveedor"),
                on_click=SupplierState.open_add_supplier_modal,
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
            rx.button(
                rx.icon(tag="refresh-cw", size=18),
                on_click=SupplierState.fetch_all_data,
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

def supplier_filter_bar() -> rx.Component:
    """Barra de búsqueda para proveedores."""
    return rx.hstack(
        rx.input(
            rx.input.slot(rx.icon(tag="search", size=18, color=rx.color("slate", 9))),
            placeholder="Buscar por Empresa, Contacto o Email...",
            width="320px",
            variant="soft",
            radius="large",
            value=SupplierState.search_query,
            on_change=SupplierState.set_search_query,
        ),
        rx.spacer(),
        rx.hstack(
            rx.text("Ver Inactivos", size="2", color=rx.color("slate", 10)),
            rx.switch(checked=SupplierState.show_inactive, on_change=SupplierState.set_show_inactive),
            spacing="2",
            align="center",
        ),
        spacing="3",
        width="100%",
        margin_bottom="16px",
    )

def supplier_table() -> rx.Component:
    """Tabla de proveedores registrada."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Empresa"),
                rx.table.column_header_cell("Contacto"),
                rx.table.column_header_cell("Email / Teléfono"),
                rx.table.column_header_cell("Dirección"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                SupplierState.filtered_suppliers,
                lambda s: rx.table.row(
                    rx.table.cell(rx.text(s["name"], weight="bold")),
                    rx.table.cell(rx.text(s["contact"])),
                    rx.table.cell(
                        rx.vstack(
                            rx.text(s["email"], size="1", color=rx.color("slate", 11)),
                            rx.text(s["phone"], size="1", weight="medium"),
                            spacing="0",
                        )
                    ),
                    rx.table.cell(rx.text(s["address"], size="2", overflow="hidden", white_space="nowrap", text_overflow="ellipsis", width="150px")),
                    rx.table.cell(
                        rx.badge(
                            "Activo" if s["is_active"] else "Inactivo",
                            color_scheme=s["status_color"],
                            variant="soft",
                        )
                    ),
                    rx.table.cell(
                        rx.hstack(
                            rx.icon_button(
                                rx.icon(tag="toggle-left" if not s["is_active"] else "toggle-right", size=16),
                                variant="soft",
                                color_scheme="slate",
                                on_click=lambda: SupplierState.toggle_supplier_status(s["id"]),
                            ),
                            rx.icon_button(
                                rx.icon(tag="edit", size=16),
                                variant="ghost",
                                color_scheme="slate",
                                on_click=lambda: SupplierState.open_edit_supplier_modal(s),
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

def add_supplier_modal() -> rx.Component:
    """Modal de registro/edición de proveedor."""
    return rx.dialog.root(
        rx.dialog.content(
             rx.dialog.title("Configuración de Proveedor"),
             rx.dialog.description("Ingresa los datos del nuevo socio comercial."),
             rx.form(
                 rx.vstack(
                    rx.vstack(rx.text("Razón Social / Nombre Empresa", size="2", weight="medium"), rx.input(name="name", value=SupplierState.supplier_form["name"], placeholder="Ej: Repuestos Global S.A.", width="100%")),
                    rx.grid(
                        rx.vstack(rx.text("Persona de Contacto", size="2", weight="medium"), rx.input(name="contact_name", value=SupplierState.supplier_form["contact_name"], placeholder="Ej: Juan Perez", width="100%")),
                        rx.vstack(rx.text("Teléfono Principal", size="2", weight="medium"), rx.input(name="phone", value=SupplierState.supplier_form["phone"], placeholder="+52 555-...", width="100%")),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.vstack(rx.text("Correo Electrónico Vtas", size="2", weight="medium"), rx.input(name="email", value=SupplierState.supplier_form["email"], placeholder="contacto@empresa.com", width="100%")),
                    rx.vstack(rx.text("Dirección / Localización", size="2", weight="medium"), rx.text_area(name="address", value=SupplierState.supplier_form["address"], placeholder="Av. Central 123...", width="100%")),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancelar", variant="soft")),
                        rx.button("Guardar Proveedor", type="submit", variant="solid", color_scheme="cyan"),
                        spacing="3",
                        width="100%",
                        justify="end",
                        padding_top="16px",
                    ),
                    spacing="4",
                    width="100%",
                 ),
                 on_submit=SupplierState.save_supplier,
             ),
             max_width="450px",
             border_radius="24px",
        ),
        open=SupplierState.show_supplier_modal,
        on_open_change=SupplierState.set_show_supplier_modal,
    )

def suppliers_page() -> rx.Component:
    """Página maestra de gestión de proveedores."""
    return rx.hstack(
        sidebar("/suppliers"),
        rx.container(
            rx.vstack(
                supplier_header(),
                supplier_filter_bar(),
                supplier_table(),
                add_supplier_modal(),
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
