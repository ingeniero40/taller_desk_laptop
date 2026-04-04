import reflex as rx
from ..state.billing_state import BillingState
from ..components.sidebar import sidebar
from ..components.page_header import page_header

def billing_header() -> rx.Component:
    """Encabezado superior de facturación."""
    return page_header(
        "Facturación y Cobros",
        "Seguimiento de ingresos, saldos y pagos de clientes.",
        actions=[
            rx.button(
                rx.icon(tag="file-text", size=18),
                rx.text("Nuevo Presupuesto"),
                on_click=lambda: BillingState.set_show_quote_modal(True),
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
            rx.button(
                rx.icon(tag="refresh-cw", size=18),
                on_click=BillingState.fetch_all_docs,
                variant="soft",
                color_scheme="gray",
                radius="large",
            ),
        ]
    )

def billing_summary() -> rx.Component:
    """Resumen financiero rápido."""
    return rx.grid(
        rx.card(
            rx.vstack(
                rx.text("Total Facturado", size="2", color_scheme="gray"),
                rx.heading("$12,450.00", size="6"), # Placeholder for aggregate state later
                spacing="1",
            ),
            variant="surface",
        ),
        rx.card(
            rx.vstack(
                rx.text("Pendiente de Cobro", size="2", color_scheme="gray"),
                rx.heading("$3,120.00", size="6", color_scheme="red"),
                spacing="1",
            ),
            variant="surface",
        ),
        rx.card(
            rx.vstack(
                rx.text("Presupuestos Aprobados", size="2", color_scheme="gray"),
                rx.heading("12", size="6", color_scheme="indigo"),
                spacing="1",
            ),
            variant="surface",
        ),
        columns="3",
        spacing="4",
        width="100%",
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
                                color_scheme="green",
                                on_click=lambda: BillingState.open_payment_modal(i),
                            ),
                            rx.icon_button(
                                rx.icon(tag="eye", size=16),
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

def quote_table() -> rx.Component:
    """Tabla de presupuestos."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("No. Presupuesto"),
                rx.table.column_header_cell("Resumen"),
                rx.table.column_header_cell("Expiración"),
                rx.table.column_header_cell("Total"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                BillingState.quotes,
                lambda q: rx.table.row(
                    rx.table.cell(rx.text(q["number"], weight="bold")),
                    rx.table.cell(rx.text(q["items"], size="2")),
                    rx.table.cell(rx.text(q["expiry"])),
                    rx.table.cell(rx.text(f"${q['total']}", weight="bold")),
                    rx.table.cell(
                        rx.badge(
                            q["status"],
                            color_scheme=q["status_color"],
                            variant="soft",
                        )
                    ),
                    rx.table.cell(
                        rx.hstack(
                            rx.cond(
                                q["status"] == "APPROVED",
                                rx.icon_button(
                                    rx.icon(tag="file-check", size=16),
                                    variant="soft",
                                    color_scheme="indigo",
                                    on_click=lambda: BillingState.convert_quote_to_invoice(q["id"]),
                                ),
                            ),
                            rx.cond(
                                (q["status"] == "DRAFT") | (q["status"] == "SENT"),
                                rx.icon_button(
                                    rx.icon(tag="check", size=16),
                                    variant="soft",
                                    color_scheme="green",
                                    on_click=lambda: BillingState.approve_quote(q["id"]),
                                ),
                            ),
                            rx.icon_button(
                                rx.icon(tag="printer", size=16),
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
                    rx.button("Confirmar Pago", on_click=BillingState.process_payment, color_scheme="green"),
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

def quote_modal() -> rx.Component:
    """Modal para crear un nuevo presupuesto."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nuevo Presupuesto"),
            rx.dialog.description("Complete los detalles del presupuesto para el cliente."),
            rx.form(
                rx.vstack(
                    rx.text("ID del Cliente (UUID)", size="2", weight="bold"),
                    rx.input(
                        placeholder="Ej: 550e8400-e29b-41d4-a716-446655440000",
                        name="customer_id",
                        width="100%",
                        required=True,
                    ),
                    rx.text("ID Orden de Trabajo (Opcional)", size="2", weight="bold"),
                    rx.input(
                        name="work_order_id",
                        width="100%",
                    ),
                    rx.text("Resumen de Servicios", size="2", weight="bold"),
                    rx.text_area(
                        placeholder="Reparación de placa base, cambio de pantalla...",
                        name="items_summary",
                        width="100%",
                    ),
                    rx.text("Monto Total (IVA Incluido)", size="2", weight="bold"),
                    rx.input(
                        type="number",
                        name="amount",
                        width="100%",
                        required=True,
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cancelar", variant="soft", color_scheme="gray")
                        ),
                        rx.button("Guardar Presupuesto", type="submit", color_scheme="cyan"),
                        width="100%",
                        justify="end",
                        spacing="3",
                        padding_top="16px",
                    ),
                    spacing="3",
                ),
                on_submit=BillingState.save_quote,
            ),
            style={"max_width": "450px"},
        ),
        open=BillingState.show_quote_modal,
    )

def billing_page() -> rx.Component:
    """Layout de la página de facturación."""
    return rx.hstack(
        sidebar("/billing"),
        rx.container(
            rx.vstack(
                billing_header(),
                billing_summary(),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Facturas", value="invoices"),
                        rx.tabs.trigger("Presupuestos", value="quotes"),
                    ),
                    rx.tabs.content(
                        rx.vstack(
                            invoice_table(),
                            spacing="4",
                            padding_top="16px",
                        ),
                        value="invoices",
                    ),
                    rx.tabs.content(
                        rx.vstack(
                            quote_table(),
                            spacing="4",
                            padding_top="16px",
                        ),
                        value="quotes",
                    ),
                    default_value="invoices",
                    width="100%",
                ),
                payment_modal(),
                quote_modal(),
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
