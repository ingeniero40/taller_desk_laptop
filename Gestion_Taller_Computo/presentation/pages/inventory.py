import reflex as rx
from ..state.inventory_state import InventoryState
from ..components.sidebar import sidebar

def inventory_header() -> rx.Component:
    """Encabezado superior de la gestión de inventario."""
    return rx.flex(
        rx.vstack(
            rx.heading("Gestión de Inventario", size="8", weight="bold", color=rx.color("slate", 12)),
            rx.text("Catalogo maestro de repuestos y equipos.", color=rx.color("slate", 10), size="3"),
            spacing="1",
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon(tag="plus", size=18),
                rx.text("Nuevo Producto"),
                on_click=InventoryState.open_add_product_modal,
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
            rx.button(
                rx.icon(tag="refresh-cw", size=18),
                on_click=InventoryState.fetch_all_data,
                variant="soft",
                color_scheme="gray",
                radius="large",
            ),
            spacing="3",
        ),
        width="100%",
        align="center",
        padding_y="24px",
    )

def filter_bar() -> rx.Component:
    """Barra de búsqueda y filtros para el inventario."""
    return rx.hstack(
        rx.input(
            rx.input.slot(rx.icon(tag="search", size=18, color=rx.color("slate", 9))),
            placeholder="Buscar por SKU o Nombre...",
            width="320px",
            variant="soft",
            radius="large",
            value=InventoryState.search_query,
            on_change=InventoryState.set_search_query,
        ),
        rx.select(
            ["Todas", "Hardware", "Software", "Periféricos", "Repuestos", "Otros"],
            placeholder="Categoría",
            variant="soft",
            radius="large",
            value=InventoryState.selected_category,
            on_change=InventoryState.set_selected_category,
        ),
        spacing="3",
        width="100%",
        margin_bottom="16px",
    )

def product_table() -> rx.Component:
    """Tabla refinada de productos."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("SKU"),
                rx.table.column_header_cell("Producto"),
                rx.table.column_header_cell("Categoría"),
                rx.table.column_header_cell("Precio Venta"),
                rx.table.column_header_cell("Stock"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                InventoryState.filtered_products,
                lambda p: rx.table.row(
                    rx.table.cell(rx.code(p["sku"], variant="ghost")),
                    rx.table.cell(rx.text(p["name"], weight="medium")),
                    rx.table.cell(rx.badge(p["category"], color_scheme="gray", variant="outline")),
                    rx.table.cell(rx.text(f"${p['sale_price']}", weight="bold")),
                    rx.table.cell(rx.text(p["stock"], color=rx.color(p["status_color"], 11))),
                    rx.table.cell(
                        rx.badge(
                            rx.cond(p["is_low_stock"], "Stock Bajo", "En Stock"),
                            color_scheme=p["status_color"],
                            variant="soft",
                        )
                    ),
                    rx.table.cell(
                        rx.hstack(
                            rx.icon_button(
                                rx.icon(tag="arrow-up-down", size=16),
                                variant="soft",
                                color_scheme="cyan",
                                on_click=lambda: InventoryState.open_adjust_stock_modal(p["id"]),
                            ),
                            rx.icon_button(
                                rx.icon(tag="pencil", size=16),
                                variant="ghost",
                                color_scheme="gray",
                            ),
                            spacing="2",
                        )
                    ),
                    align="center",
                    _hover={"background": rx.color("slate", 3)},
                )
            )
        ),
        width="100%",
        variant="surface",
        border_radius="16px",
    )

def add_product_modal() -> rx.Component:
    """Modal con formulario para agregar productos."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Registrar Nuevo Producto"),
            rx.dialog.description("Completa los detalles técnicos del item."),
            rx.form(
                rx.vstack(
                    rx.grid(
                        rx.vstack(rx.text("SKU", size="2", weight="medium"), rx.input(name="sku", value=InventoryState.product_form["sku"], placeholder="Ej: HDD-1TB-WD", width="100%")),
                        rx.vstack(rx.text("Nombre", size="2", weight="medium"), rx.input(name="name", placeholder="Nombre comercial", width="100%")),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Precio Costo", size="2", weight="medium"), rx.input(name="cost_price", type="number", placeholder="0.00", width="100%")),
                        rx.vstack(rx.text("Precio Venta", size="2", weight="medium"), rx.input(name="sale_price", type="number", placeholder="0.00", width="100%")),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Stock Inicial", size="2", weight="medium"), rx.input(name="stock", type="number", default_value="0", width="100%")),
                        rx.vstack(rx.text("Stock Mínimo", size="2", weight="medium"), rx.input(name="min_stock", type="number", default_value="5", width="100%")),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Proveedor", size="2", weight="medium"),
                        rx.select(
                            InventoryState.supplier_ids,
                            name="supplier_id",
                            placeholder="Selecciona proveedor",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                        rx.button("Guardar Producto", type="submit", variant="solid", color_scheme="cyan"),
                        spacing="3",
                        width="100%",
                        justify="end",
                        padding_top="16px",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=InventoryState.save_product,
            ),
            max_width="450px",
            border_radius="24px",
            padding="24px",
        ),
        open=InventoryState.show_product_modal,
        on_open_change=InventoryState.set_show_product_modal,
    )

def stock_adjust_modal() -> rx.Component:
    """Modal para ajuste rápido de stock."""
    return rx.dialog.root(
        rx.dialog.content(
             rx.dialog.title("Ajuste de Existencias"),
             rx.dialog.description("Registra entradas (positivo) o salidas (negativo)."),
             rx.vstack(
                 rx.input(
                     type="number", 
                     placeholder="Ej: 10 o -5",
                     on_change=InventoryState.set_stock_adjustment,
                     width="100%",
                     size="3",
                 ),
                 rx.hstack(
                     rx.dialog.close(rx.button("Cerrar", variant="soft")),
                     rx.button("Confirmar Ajuste", on_click=InventoryState.confirm_stock_adjustment, color_scheme="cyan"),
                     spacing="3",
                     width="100%",
                     justify="end",
                 ),
                 spacing="4",
                 padding_top="16px",
             ),
             max_width="350px",
        ),
        open=InventoryState.show_stock_modal,
        on_open_change=InventoryState.set_show_stock_modal,
    )

def inventory_page() -> rx.Component:
    """Layout principal de la página de inventario."""
    return rx.hstack(
        sidebar("/inventory"),
        rx.container(
            rx.vstack(
                inventory_header(),
                filter_bar(),
                product_table(),
                add_product_modal(),
                stock_adjust_modal(),
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
