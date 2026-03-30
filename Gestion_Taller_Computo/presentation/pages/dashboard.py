import reflex as rx
from ..state.dashboard_state import DashboardState
from ..components.sidebar import sidebar
from ..components.metrics import stat_card
from ..components.page_header import page_header

def dashboard_header() -> rx.Component:
    """Encabezado superior del dashboard."""
    return page_header(
        "Dashboard Administrativo",
        "Monitoreo general del taller y rendimiento operativo.",
        actions=[
            rx.button(
                rx.icon(tag="refresh-cw", size=18, animation=rx.cond(DashboardState.is_loading, "spin 3s linear infinite", "none")),
                on_click=DashboardState.fetch_metrics,
                variant="soft",
                color_scheme="gray",
                radius="large",
            )
        ]
    )

def kpi_grid() -> rx.Component:
    """Cuadrícula de indicadores clave."""
    return rx.grid(
        stat_card(
            "Ingresos del Mes", 
            rx.text("$", DashboardState.financials['total_collected']), 
            "dollar-sign", 
            growth=DashboardState.financials['revenue_growth'], 
            color="green"
        ),
        stat_card(
            "Órdenes en Taller", 
            rx.text(DashboardState.summary['total_orders']), 
            "clipboard-list", 
            color="cyan"
        ),
        stat_card(
            "Reparos Finalizados", 
            rx.text(DashboardState.summary['COMPLETED']), 
            "circle-check", 
            color="indigo"
        ),
        stat_card(
            "Alertas de Stock", 
            rx.text(DashboardState.critical_stock.length()), 
            "package", 
            color="amber"
        ),
        columns=rx.breakpoints(initial="1", sm="2", lg="4"),
        spacing="5",
        width="100%",
    )

def recent_activity() -> rx.Component:
    """Tabla de actividad reciente y rendimiento de técnicos."""
    return rx.grid(
        # Lista de Técnicos
        rx.card(
            rx.vstack(
                rx.heading("Desempeño de Técnicos", size="4", weight="bold", margin_bottom="12px"),
                rx.vstack(
                    rx.foreach(
                        DashboardState.technicians,
                        lambda t: rx.hstack(
                            rx.avatar(fallback=t["technician"], size="2"),
                            rx.vstack(
                                rx.text(t["technician"], size="2", weight="medium"),
                                rx.text(f"{t['status']}: {t['order_count']}", size="1", color=rx.color("slate", 10)),
                                spacing="0",
                            ),
                            rx.spacer(),
                            rx.badge(f"{t['order_count']}", color_scheme="cyan", variant="solid"),
                            width="100%",
                            padding_y="4px",
                        )
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
            padding="20px",
            border_radius="16px",
            background=rx.color("slate", 3),
        ),
        # Productos Críticos
        rx.card(
            rx.vstack(
                rx.heading("Stock por Reposición", size="4", weight="bold", margin_bottom="12px"),
                rx.vstack(
                    rx.foreach(
                        DashboardState.critical_stock,
                        lambda p: rx.hstack(
                            rx.icon(tag="package", size=18, color=rx.color("amber", 9)),
                            rx.vstack(
                                rx.text(p["name"], size="2", weight="medium", overflow="hidden", white_space="nowrap", text_overflow="ellipsis", width="150px"),
                                rx.text(f"Stock: {p['stock']} / Min: {p['min_stock']}", size="1", color=rx.color("amber", 11)),
                                spacing="0",
                            ),
                            spacing="3",
                            width="100%",
                            padding_y="8px",
                            border_bottom=f"1px solid {rx.color('slate', 5)}",
                        )
                    ),
                    spacing="0",
                    width="100%",
                ),
                rx.button("Ir a Inventario", variant="ghost", color_scheme="cyan", size="2", margin_top="8px", width="100%"),
            ),
            padding="20px",
            border_radius="16px",
            background=rx.color("slate", 3),
        ),
        columns=rx.breakpoints(initial="1", lg="2"),
        spacing="5",
        width="100%",
    )

def recent_orders_table() -> rx.Component:
    """Tabla detallada de las últimas órdenes ingresadas."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Órdenes Recientes", size="5", weight="bold"),
                rx.spacer(),
                rx.button("Ver Todas", variant="ghost", color_scheme="cyan", size="2"),
                width="100%",
                align="center",
                margin_bottom="16px",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Ticket"),
                        rx.table.column_header_cell("Dispositivo"),
                        rx.table.column_header_cell("Cliente"),
                        rx.table.column_header_cell("Fecha"),
                        rx.table.column_header_cell("Estado"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        DashboardState.recent_orders,
                        lambda order: rx.table.row(
                            rx.table.row_header_cell(order["ticket"]),
                            rx.table.cell(order["device"]),
                            rx.table.cell(order["customer"]),
                            rx.table.cell(order["date"]),
                            rx.table.cell(
                                rx.badge(
                                    order["status"],
                                    color_scheme=rx.match(
                                        order["status"],
                                        ("COMPLETED", "emerald"),
                                        ("RECEIVED", "blue"),
                                        ("IN_REPAIR", "amber"),
                                        "slate",
                                    ),
                                    variant="soft",
                                )
                            ),
                        ),
                    ),
                ),
                width="100%",
            ),
            width="100%",
        ),
        padding="24px",
        border_radius="16px",
        background=rx.color("slate", 3),
        margin_top="32px",
    )

def index() -> rx.Component:
    """Contenedor principal del Dashboard Administrativo."""
    return rx.hstack(
        sidebar(),
        rx.container(
            rx.vstack(
                dashboard_header(),
                kpi_grid(),
                rx.heading("Actividad del Taller", size="5", weight="bold", margin_top="32px", color=rx.color("slate", 11)),
                recent_activity(),
                recent_orders_table(),
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
