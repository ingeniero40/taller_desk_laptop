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
            "Ingresos Mes", 
            rx.text("$", DashboardState.financials['total_collected']), 
            "dollar-sign", 
            growth=DashboardState.financials['revenue_growth'], 
            color="green"
        ),
        stat_card(
            "Eficiencia TAT", 
            rx.text(DashboardState.avg_hours, " h"), 
            "timer", 
            color="amber"
        ),
        stat_card(
            "Órdenes en Taller", 
            rx.text(DashboardState.summary['total_orders']), 
            "clipboard-list", 
            color="cyan"
        ),
        stat_card(
            "Finalizados", 
            rx.text(DashboardState.summary['COMPLETED']), 
            "circle-check", 
            color="indigo"
        ),
        columns=rx.breakpoints(initial="2", sm="2", lg="4"),
        spacing="5",
        width="100%",
    )

def recent_activity() -> rx.Component:
    """Tabla de actividad reciente y rendimiento de técnicos."""
    return rx.grid(
        # Gráfica de Ingresos
        rx.card(
            rx.vstack(
                rx.heading("Ingresos Diarios (7d)", size="4", weight="bold", margin_bottom="20px"),
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="revenue",
                        stroke=rx.color("green", 9),
                        fill=rx.color("green", 5),
                    ),
                    rx.recharts.x_axis(data_key="date", hide=True),
                    rx.recharts.y_axis(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.graphing_tooltip(),
                    data=DashboardState.financials["last_7_days"],
                    width="100%",
                    height=200,
                ),
            ),
            padding="24px",
            border_radius="16px",
            background=rx.color("slate", 3),
        ),
        # Desempeño de Técnicos
        rx.card(
            rx.vstack(
                rx.heading("Técnicos Activos", size="4", weight="bold", margin_bottom="12px"),
                rx.vstack(
                    rx.foreach(
                        DashboardState.technicians,
                        lambda t: rx.hstack(
                             # Fixed untyped var access with .to(str)
                            rx.avatar(fallback=t["technician"].to(str)[:2].to(str), size="2"),
                            rx.vstack(
                                rx.text(t["technician"].to(str), size="2", weight="medium"),
                                rx.text(t["status"].to(str), size="1", color=rx.color("slate", 10)),
                                spacing="0",
                            ),
                            rx.spacer(),
                            rx.badge(t["order_count"].to(str), color_scheme="indigo", variant="solid"),
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
        # Incidencias Recurrentes
        rx.card(
            rx.vstack(
                rx.heading("Incidencias Recurrentes", size="4", weight="bold", margin_bottom="12px"),
                rx.vstack(
                    rx.foreach(
                        DashboardState.top_incidents,
                        lambda i: rx.hstack(
                            rx.icon(tag="alert-circle", size=18, color=rx.color("red", 9)),
                            rx.text(i["problem"].to(str), size="2", weight="medium", width="150px", overflow="hidden", white_space="nowrap", text_overflow="ellipsis"),
                            rx.spacer(),
                            rx.text("Frecuencia: ", i["count"].to(str), size="1", color=rx.color("slate", 10)),
                            width="100%",
                            padding_y="6px",
                        )
                    ),
                    spacing="2",
                    width="100%",
                ),
            ),
            padding="20px",
            border_radius="16px",
            background=rx.color("slate", 3),
        ),
        # Inventario Crítico
        rx.card(
            rx.vstack(
                rx.heading("Stock por Reposición", size="4", weight="bold", margin_bottom="12px"),
                rx.vstack(
                    rx.foreach(
                        DashboardState.critical_stock,
                        lambda p: rx.hstack(
                            rx.icon(tag="package", size=18, color=rx.color("amber", 9)),
                            rx.vstack(
                                rx.text(p["name"].to(str), size="2", weight="medium", width="150px", overflow="hidden", white_space="nowrap", text_overflow="ellipsis"),
                                rx.text("Stock: ", p["stock"].to(str), " / Min: ", p["min_stock"].to(str), size="1", color=rx.color("amber", 11)),
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
            ),
            padding="20px",
            border_radius="16px",
            background=rx.color("slate", 3),
        ),
        columns=rx.breakpoints(initial="1", md="2", lg="2"),
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
                rx.button("Ver Todas", variant="ghost", color_scheme="indigo", size="2"),
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
                            rx.table.row_header_cell(order["ticket"].to(str)),
                            rx.table.cell(order["device"].to(str)),
                            rx.table.cell(order["customer"].to(str)),
                            rx.table.cell(order["date"].to(str)),
                            rx.table.cell(
                                rx.badge(
                                    order["status"].to(str),
                                    color_scheme=rx.match(
                                        order["status"].to(str),
                                        ("COMPLETED", "green"),
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
