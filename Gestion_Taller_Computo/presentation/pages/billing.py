import reflex as rx
from ..state.billing_state import BillingState
from ..components.sidebar import sidebar

def billing_header() -> rx.Component:
    """Encabezado superior de facturación."""
    return rx.flex(
        rx.vstack(
            rx.heading("Facturación y Cobros", size="8", weight="bold", color=rx.color("slate", 12)),
            rx.text("Seguimiento de ingresos, saldos y pagos de clientes.", color=rx.color("slate", 10), size="3"),
            spacing="1",
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon(tag="receipt", size=18),
                rx.text("Nueva Factura"),
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
            rx.button(
                rx.icon(tag="refresh-cw", size=18),
                on_click=BillingState.fetch_invoices,
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

def invoice_table() -> rx.Component:
    """Tabla de facturas generadas."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("No. Factura"),
                rx.table.column_header_cell("Fecha"),
                rx.table.column_header_cell("Total"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                BillingState.filtered_invoices,
                lambda i: rx.table.row(
                    rx.table.cell(rx.text(i["invoice_number"], weight="bold")),
                    rx.table.cell(rx.text(i["date"])),
                    rx.table.cell(rx.text(f"${i['total']}", weight="bold")),
                    rx.table.cell(
                        rx.badge(
                            i["status"],
                            color_scheme=i["status_color"],
                            variant="soft",
                        )
                    ),
                    rx.table.cell(
                        rx.hstack(
                            rx.icon_button(
                                rx.icon(tag="dollar-sign", size=16),
                                variant="soft",
                                color_scheme="emerald",
                                on_click=lambda: BillingState.open_payment_modal(i),
                            ),
                            rx.icon_button(
                                rx.icon(tag="eye", size=16),
                                variant="ghost",
                                color_scheme="slate",
                            ),
                            spacing="2",
                        )
                    )
                )
            )
        )
    )

def payment_modal() -> rx.Component:
    """Modal para procesar un pago de factura."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Procesar Pago"),
            rx.dialog.description(f"Registrando abono para Factura {BillingState.selected_invoice['invoice_number']}"),
            rx.vstack(
                rx.vstack(
                    rx.text("Monto a Pagar", size="2", weight="medium"),
                    rx.input(
                         type="number", 
                         value=BillingState.payment_amount.to_string(),
                         on_change=BillingState.set_payment_amount,
                         width="100%",
                         size="3",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Método de Pago", size="2", weight="medium"),
                    rx.select(
                        ["Efectivo", "Tarjeta", "Transferencia"],
                        on_change=BillingState.set_payment_method,
                        value=BillingState.payment_method,
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Referencia / Comprobante", size="2", weight="medium"),
                    rx.input(
                        placeholder="Ej: TRANS-123456",
                        on_change=BillingState.set_payment_reference,
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cancelar", variant="soft")),
                    rx.button("Confirmar Pago", on_click=BillingState.process_payment, color_scheme="emerald"),
                    spacing="3",
                    width="100%",
                    justify="end",
                    padding_top="16px",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="400px",
            border_radius="24px",
        ),
        open=BillingState.show_payment_modal,
        on_open_change=BillingState.set_show_payment_modal,
    )

def billing_page() -> rx.Component:
    """Layout de la página de facturación."""
    return rx.hstack(
        sidebar("/billing"),
        rx.container(
            rx.vstack(
                billing_header(),
                invoice_table(),
                payment_modal(),
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
