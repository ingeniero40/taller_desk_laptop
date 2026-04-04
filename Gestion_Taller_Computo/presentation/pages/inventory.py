import reflex as rx
from ..state.inventory_state import InventoryState
from ..components.sidebar import sidebar
from ..components.page_header import page_header

def stat_mini(label: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """Indicadores rápidos sobre la tabla de inventario con diseño Glassmorphism."""
    return rx.hstack(
        rx.box(
            rx.icon(tag=icon, size=18, color=rx.color(color, 9)),
            padding="10px", 
            border_radius="10px",
            background=rx.color(color, 3),
            display="flex",
            align_items="center",
            justify_content="center",
        ),
        rx.vstack(
            rx.text(label, size="1", color=rx.color("slate", 10), weight="medium"),
            rx.text(value, size="4", weight="bold", letter_spacing="-0.02em"),
            spacing="0",
        ),
        spacing="3",
        padding="12px 20px",
        border_radius="16px",
        background=rx.color("slate", 1),
        border=f"1px solid {rx.color('slate', 4)}",
        min_width="160px",
        transition="transform 0.2s ease",
        _hover={"transform": "translateY(-2px)", "box_shadow": "0 4px 12px rgba(0,0,0,0.05)"},
    )

def inventory_header() -> rx.Component:
    """Encabezado superior de la gestión de inventario."""
    return page_header(
        "Gestión de Inventario",
        "Catálogo maestro de repuestos y equipos para reparaciones.",
        actions=[
            rx.button(
                rx.icon(tag="plus", size=18),
                rx.text("Nuevo Producto"),
                on_click=InventoryState.open_add_product_modal,
                color_scheme="indigo",
                variant="solid",
                radius="large",
                size="3",
            ),
            rx.button(
                rx.icon(tag="refresh-cw", size=18),
                on_click=InventoryState.fetch_all_data,
                variant="soft",
                color_scheme="gray",
                radius="large",
                size="3",
            ),
        ]
    )

def filter_bar() -> rx.Component:
    """Barra de búsqueda y filtros con KPIs integrados."""
    return rx.vstack(
        rx.hstack(
            stat_mini("Items Críticos", InventoryState.low_stock_count, "alert-triangle", "red"),
            stat_mini("Valor Capital", InventoryState.total_value, "banknote", "teal"),

            stat_mini("Total SKUs", InventoryState.products.length(), "hash", "blue"),

            spacing="4",
            width="100%",
            justify="start",
            padding_bottom="12px",
        ),
        rx.hstack(
            rx.box(
                rx.input(
                    rx.input.slot(rx.icon(tag="search", size=18, color=rx.color("slate", 9))),
                    placeholder="Buscar SKU o nombre de producto...",
                    width="100%",
                    variant="soft",
                    radius="large",
                    size="3",
                    value=InventoryState.search_query,
                    on_change=InventoryState.set_search_query,
                    background=rx.color("slate", 1),
                ),
                flex="1",
            ),
            rx.select(
                InventoryState.categories,
                placeholder="Filtrar por Categoría",
                variant="soft",
                radius="large",
                size="3",
                value=InventoryState.selected_category,
                on_change=InventoryState.set_selected_category,
                background=rx.color("slate", 1),
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        spacing="2",
        margin_bottom="16px",
    )

def product_table() -> rx.Component:
    """Tabla refinada de productos con estados visuales mejorados."""
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("SKU", width="120px"),
                    rx.table.column_header_cell("Producto"),
                    rx.table.column_header_cell("Categoría", width="150px"),
                    rx.table.column_header_cell("Precio Venta", width="150px"),
                    rx.table.column_header_cell("Stock", width="100px"),
                    rx.table.column_header_cell("Estado", width="120px"),
                    rx.table.column_header_cell("", width="100px"), # Acciones
                )
            ),
            rx.table.body(
                rx.foreach(
                    InventoryState.filtered_products,
                    lambda p: rx.table.row(
                        rx.table.cell(rx.code(p["sku"], variant="ghost", color_scheme="gray")),
                        rx.table.cell(
                            rx.vstack(
                                rx.text(p["name"], weight="bold", size="3"),
                                spacing="0",
                            )
                        ),
                        rx.table.cell(rx.badge(p["category"], color_scheme="gray", variant="outline", radius="full")),
                        rx.table.cell(rx.text(f"${p['sale_price']}", weight="bold", color=rx.color("slate", 12))),
                        rx.table.cell(
                            rx.text(
                                p["stock"], 
                                weight="bold",
                                color=rx.color(p["status_color"], 11)
                            )
                        ),
                        rx.table.cell(
                            rx.badge(
                                rx.cond(p["is_low_stock"], "BAJO STOCK", "OK"),
                                color_scheme=p["status_color"],
                                variant="soft",
                                radius="full",
                                size="1",
                            )
                        ),
                        rx.table.cell(
                            rx.hstack(
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon(tag="arrow-up-down", size=16),
                                        variant="soft",
                                        color_scheme="indigo",
                                        radius="full",
                                        on_click=lambda: InventoryState.open_adjust_stock_modal(p["id"]),
                                    ),
                                    content="Ajustar Stock",
                                ),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon(tag="history", size=16),
                                        variant="soft",
                                        color_scheme="indigo",
                                        radius="full",
                                        on_click=lambda: InventoryState.open_movements_history(p["id"], p["name"]),
                                    ),
                                    content="Ver Historial",
                                ),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon(tag="pencil", size=16),
                                        variant="ghost",
                                        color_scheme="gray",
                                        radius="full",
                                    ),
                                    content="Editar",
                                ),
                                spacing="2",
                                justify="end",
                            )
                        ),
                        align="center",
                        transition="background-color 0.2s ease",
                        _hover={"background": rx.color("slate", 2)},
                    )
                )
            ),
            width="100%",
            variant="surface",
            size="3",
        ),
        border_radius="20px",
        overflow="hidden",
        border=f"1px solid {rx.color('slate', 4)}",
        box_shadow="0 4px 20px rgba(0,0,0,0.03)",
        background=rx.color("slate", 1),
    )

def add_product_modal() -> rx.Component:
    """Modal premium para agregar productos."""
    return rx.dialog.root(
        rx.dialog.content(
             rx.vstack(
                rx.hstack(
                    rx.icon(tag="package-plus", size=24, color=rx.color("cyan", 9)),
                    rx.dialog.title("Nuevo Producto", margin="0"),
                    spacing="3",
                    align="center",
                ),
                rx.separator(width="100%", size="1"),
                rx.form(
                    rx.vstack(
                        rx.grid(
                            rx.vstack(rx.text("SKU", size="2", weight="bold"), rx.input(name="sku", value=InventoryState.product_form["sku"], placeholder="Ej: REP-001", width="100%", radius="large")),
                            rx.vstack(rx.text("Nombre", size="2", weight="bold"), rx.input(name="name", placeholder="Nombre del producto", width="100%", radius="large")),
                            columns="2", spacing="4", width="100%",
                        ),
                        rx.grid(
                            rx.vstack(rx.text("Costo ($)", size="2", weight="bold"), rx.input(name="cost_price", type="number", placeholder="0.00", width="100%", radius="large")),
                            rx.vstack(rx.text("Venta ($)", size="2", weight="bold"), rx.input(name="sale_price", type="number", placeholder="0.00", width="100%", radius="large")),
                            columns="2", spacing="4", width="100%",
                        ),
                        rx.grid(
                            rx.vstack(rx.text("Stock Inicial", size="2", weight="bold"), rx.input(name="stock", type="number", default_value="0", width="100%", radius="large")),
                            rx.vstack(rx.text("Stock Mín.", size="2", weight="bold"), rx.input(name="min_stock", type="number", default_value="5", width="100%", radius="large")),
                            columns="2", spacing="4", width="100%",
                        ),
                        rx.vstack(
                            rx.text("Proveedor Responsable", size="2", weight="bold"),
                            rx.select(
                                InventoryState.supplier_ids,
                                name="supplier_id",
                                placeholder="Elegir proveedor...",
                                width="100%",
                                radius="large",
                            ),
                            width="100%",
                        ),
                        rx.hstack(
                            rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray", size="3", radius="large")),
                            rx.button("Guardar en Catálogo", type="submit", variant="solid", color_scheme="indigo", size="3", radius="large"),
                            spacing="3",
                            width="100%",
                            justify="end",
                            padding_top="20px",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    on_submit=InventoryState.save_product,
                ),
                spacing="4",
                width="100%",
            ),
            max_width="500px",
            border_radius="24px",
            padding="32px",
            background=rx.color("slate", 1),
        ),
        open=InventoryState.show_product_modal,
        on_open_change=InventoryState.set_show_product_modal,
    )

def stock_adjust_modal() -> rx.Component:
    """Modal para ajuste rápido de stock."""
    return rx.dialog.root(
        rx.dialog.content(
             rx.vstack(
                rx.hstack(
                    rx.icon(tag="arrow-up-down", size=22, color=rx.color("cyan", 9)),
                    rx.dialog.title("Ajustar Existencias", margin="0"),
                    spacing="3",
                    align="center",
                ),
                rx.text("Registra entradas (+) o salidas (-) de este producto.", size="2", color=rx.color("slate", 10)),
                rx.input(
                    type="number", 
                    placeholder="Ej: 10 o -5",
                    on_change=InventoryState.set_stock_adjustment,
                    width="100%",
                    size="3",
                    radius="large",
                    auto_focus=True,
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cerrar", variant="soft", color_scheme="gray", radius="large")),
                    rx.button("Confirmar", on_click=InventoryState.confirm_stock_adjustment, color_scheme="indigo", radius="large"),
                    spacing="3",
                    width="100%",
                    justify="end",
                    padding_top="10px",
                ),
                spacing="4",
                width="100%",
             ),
             max_width="380px",
             border_radius="24px",
             padding="28px",
        ),
        open=InventoryState.show_stock_modal,
        on_open_change=InventoryState.set_show_stock_modal,
    )

def history_modal() -> rx.Component:
    """Modal premium para el historial de movimientos."""
    return rx.dialog.root(
        rx.dialog.content(
             rx.vstack(
                rx.hstack(
                    rx.icon(tag="history", size=22, color=rx.color("indigo", 9)),
                    rx.dialog.title(f"Historial: {InventoryState.selected_product_name}", margin="0"),
                    spacing="3",
                    align="center",
                ),
                rx.separator(width="100%"),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            InventoryState.product_movements,
                            lambda m: rx.box(
                                rx.hstack(
                                    rx.badge(m["type"], color_scheme=m["type_color"], variant="surface", size="1"),
                                    rx.vstack(
                                        rx.hstack(
                                            rx.text(f"Cantidad: {m['quantity']}", weight="bold", size="2"),
                                            rx.spacer(),
                                            rx.text(m["date"], size="1", color=rx.color("slate", 10)),
                                        ),
                                        rx.text(m["notes"], size="2", color=rx.color("slate", 11)),
                                        spacing="1",
                                    ),
                                    spacing="3",
                                    width="100%",
                                    align="start",
                                ),
                                padding="12px",
                                border_radius="12px",
                                border=f"1px solid {rx.color('slate', 4)}",
                                background=rx.color("slate", 2),
                                width="100%",
                            )
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    height="300px",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cerrar", variant="soft", color_scheme="gray", radius="large")),
                    justify="end",
                    width="100%",
                ),
                spacing="4",
                width="100%",
             ),
             max_width="500px",
             border_radius="28px",
             padding="32px",
        ),
        open=InventoryState.show_movements_modal,
        on_open_change=InventoryState.set_show_movements_modal,
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
                history_modal(),
                spacing="6",
                padding_bottom="60px",
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
