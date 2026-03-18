import reflex as rx
from .presentation.pages.dashboard import index as dashboard_page
from .presentation.pages.inventory import inventory_page
from .presentation.pages.billing import billing_page
from .presentation.pages.orders import orders_page
from .presentation.state.dashboard_state import DashboardState
from .presentation.state.inventory_state import InventoryState
from .presentation.state.billing_state import BillingState
from .presentation.state.order_state import OrderState

def index() -> rx.Component:
    """Retorna la página de dashboard configurada."""
    return dashboard_page()

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="cyan",
    )
)

app.add_page(
    index, 
    route="/", 
    title="Taller Desk & Laptop | Dashboard",
    on_load=DashboardState.on_load
)

app.add_page(
    inventory_page,
    route="/inventory",
    title="Taller Desk & Laptop | Inventario",
    on_load=InventoryState.on_load
)

app.add_page(
    billing_page,
    route="/billing",
    title="Taller Desk & Laptop | Facturación",
    on_load=BillingState.on_load
)

app.add_page(
    orders_page,
    route="/orders",
    title="Taller Desk & Laptop | Órdenes",
    on_load=OrderState.on_load
)

