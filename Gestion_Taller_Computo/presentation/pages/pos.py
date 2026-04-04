import reflex as rx
from ..components.sidebar import sidebar
from ..state.pos_state import POSState


def pos_header() -> rx.Component:
    """Encabezado del Punto de Venta."""
    return rx.hstack(
        rx.vstack(
            rx.heading("Punto de Venta (POS)", size="7", weight="bold"),
            rx.text("Escaneo de productos y venta rápida de accesorios.", size="3", color_scheme="gray"),
            align_items="start",
            spacing="1",
        ),
        rx.spacer(),
        rx.badge(
            rx.hstack(
                rx.icon(tag="user", size=16),
                rx.text("Público General"),
                spacing="2",
            ),
            color_scheme="indigo",
            size="3",
            variant="soft",
            radius="full",
            padding_x="16px",
        ),
        width="100%",
        padding_y="20px",
        align="center",
    )


def scanner_section() -> rx.Component:
    """Entrada para código de barras."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="barcode", size=24, color=rx.color("cyan", 9)),
                rx.heading("Escáner / Buscador", size="4"),
                spacing="3",
                align="center",
            ),
            rx.input(
                placeholder="Escanee código de barras o escriba SKU...",
                value=POSState.search_query,
                on_change=POSState.set_search_query,
                on_key_down=lambda e: rx.cond(
                    e == "Enter",
                    POSState.handle_barcode_scan(POSState.search_query),
                    rx.console_log("Waiting for Enter...") # Or just a no-op event if possible
                ),
                width="100%",
                size="3",
                variant="surface",
                auto_focus=True,
            ),
            rx.text(
                "Presione ENTER para procesar el código", 
                size="1", 
                color_scheme="gray"
            ),
            spacing="3",
            width="100%",
        ),
        padding="20px",
        variant="classic",
    )


def cart_table() -> rx.Component:
    """Lista de productos en la venta actual."""
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="shopping-cart", size=20),
            rx.heading("Detalle de Venta", size="4"),
            spacing="3",
            align="center",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Producto"),
                    rx.table.column_header_cell("Cant."),
                    rx.table.column_header_cell("Precio"),
                    rx.table.column_header_cell("Total"),
                    rx.table.column_header_cell(""),
                )
            ),
            rx.table.body(
                rx.foreach(
                    POSState.cart,
                    lambda item: rx.table.row(
                        rx.table.cell(rx.text(item["name"], weight="medium")),
                        rx.table.cell(
                            rx.input(
                                value=item["quantity"].to(str),
                                on_change=lambda v: POSState.update_quantity(item["id"], v),
                                width="60px",
                                size="1",
                                text_align="center",
                            )
                        ),
                        rx.table.cell(rx.text(f"${item['price']}")),
                        rx.table.cell(rx.text(f"${item['total']}", weight="bold")),
                        rx.table.cell(
                            rx.icon_button(
                                rx.icon(tag="trash-2", size=14),
                                color_scheme="red",
                                variant="ghost",
                                on_click=lambda: POSState.remove_from_cart(item["id"]),
                            )
                        ),
                    )
                )
            ),
            width="100%",
            variant="surface",
        ),
        rx.cond(
            POSState.cart.length() == 0,
            rx.center(
                rx.vstack(
                    rx.icon(tag="shopping-basket", size=48, opacity=0.2),
                    rx.text("El carrito está vacío", color_scheme="gray"),
                    padding="40px",
                ),
                width="100%",
            ),
        ),
        width="100%",
        spacing="4",
    )


def checkout_sidebar() -> rx.Component:
    """Panel lateral de cobro."""
    return rx.card(
        rx.vstack(
            rx.heading("Resumen de Pago", size="5"),
            rx.divider(),
            
            rx.hstack(
                rx.text("Total a Pagar:", size="4", weight="medium"),
                rx.spacer(),
                rx.heading(f"${POSState.total}", size="7", color_scheme="indigo"),
                width="100%",
                align="center",
            ),
            
            rx.vstack(
                rx.text("Método de Pago", size="2", weight="bold"),
                rx.select(
                    ["Efectivo", "Tarjeta", "Transferencia"],
                    value=POSState.payment_method,
                    on_change=POSState.set_payment_method,
                    width="100%",
                    size="2",
                ),
                width="100%",
                align_items="start",
            ),
            
            rx.cond(
                POSState.payment_method == "Efectivo",
                rx.vstack(
                    rx.text("Efectivo Recibido", size="2", weight="bold"),
                    rx.input(
                        type="number",
                        placeholder="0.00",
                        value=POSState.received_amount.to(str),
                        on_change=POSState.set_received_amount,
                        width="100%",
                        size="3",
                    ),
                    rx.hstack(
                        rx.text("Cambio:", size="3"),
                        rx.text(f"${POSState.change}", size="4", weight="bold", color_scheme="green"),
                        width="100%",
                        justify="between",
                    ),
                    width="100%",
                    align_items="start",
                )
            ),
            
            rx.button(
                "FINALIZAR VENTA",
                on_click=POSState.finalize_sale,
                loading=POSState.is_processing,
                width="100%",
                size="4",
                color_scheme="indigo",
                height="60px",
                disabled=POSState.cart.length() == 0,
            ),
            
            spacing="5",
            width="100%",
        ),
        width="100%",
        height="100%",
        padding="24px",
    )


def success_modal() -> rx.Component:
    """Modal de confirmación de venta."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.center(
                    rx.box(
                        rx.icon(tag="check", size=40, color="white"),
                        background=rx.color("green", 9),
                        padding="12px",
                        border_radius="full",
                    ),
                    width="100%",
                    padding_y="10px",
                ),
                rx.dialog.title("Venta Exitosa", text_align="center", width="100%"),
                rx.dialog.description(
                    f"Se ha generado la factura {POSState.last_invoice_num} correctamente.",
                    text_align="center",
                ),
                rx.hstack(
                    rx.button(
                        "Imprimir Ticket", 
                        variant="soft", 
                        color_scheme="gray",
                        on_click=rx.window_alert("Funcionalidad de impresión en desarrollo.") 
                    ),
                    rx.button("Nueva Venta", on_click=POSState.close_success),
                    width="100%",
                    justify="center",
                    spacing="3",
                    padding_top="20px",
                ),
                spacing="3",
            ),
        ),
        open=POSState.show_success_modal,
    )


def pos_page() -> rx.Component:
    """Layout principal del POS."""
    return rx.hstack(
        sidebar("/pos"),
        rx.container(
            rx.vstack(
                pos_header(),
                rx.grid(
                    rx.vstack(
                        scanner_section(),
                        cart_table(),
                        spacing="5",
                        width="100%",
                    ),
                    rx.vstack(
                        checkout_sidebar(),
                        width="100%",
                    ),
                    columns="3", # 2 for content, 1 for checkout
                    spacing="6",
                    width="100%",
                ),
                success_modal(),
                spacing="5",
                padding_bottom="48px",
                width="100%",
            ),
            size="4",
            padding_x="40px",
        ),
        background_color=rx.color("slate", 1),
        width="100%",
        min_height="100vh",
        align_items="start",
    )
