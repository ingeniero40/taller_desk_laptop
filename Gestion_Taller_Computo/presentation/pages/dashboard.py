import reflex as rx
from ..state.dashboard_state import DashboardState
from ..components.sidebar import sidebar
from ..components.metrics import stat_card

def dashboard_header() -> rx.Component:
    """Encabezado superior del dashboard."""
    return rx.flex(
        rx.vstack(
            rx.heading("Dashboard Administrativo", size="8", weight="bold", color=rx.color("slate", 12)),
            rx.text("Monitoreo general del taller y rendimiento operativo.", color=rx.color("slate", 10), size="3"),
            spacing="1",
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon(tag="plus", size=18),
                rx.text("Nueva Orden"),
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
            rx.button(
                rx.icon(tag="refresh-cw", size=18, animation="spin 3s linear infinite" if DashboardState.is_loading else "none"),
                on_click=DashboardState.fetch_metrics,
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

def kpi_grid() -> rx.Component:
    """Cuadrícula de indicadores clave."""
    return rx.grid(
        stat_card(
            "Ingresos del Mes", 
            rx.text(f"${DashboardState.financials['total_collected']}"), 
            "dollar-sign", 
            growth=rx.text(f"{DashboardState.financials['revenue_growth']}"), 
            color="emerald"
        ),
        stat_card(
            "Órdenes en Taller", 
            rx.text(f"{DashboardState.summary['total_orders']}"), 
            "clipboard-list", 
            color="cyan"
        ),
        stat_card(
            "Reparos Finalizados", 
            rx.text(f"{DashboardState.summary['COMPLETED']}"), 
            "check-circle-2", 
            color="indigo"
        ),
        stat_card(
            "Alertas de Stock", 
            rx.text(f"{rx.len(DashboardState.critical_stock)}"), 
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
                            rx.avatar(fallback=t["technician"][0:2].upper(), size="2"),
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
