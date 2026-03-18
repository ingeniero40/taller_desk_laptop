import reflex as rx
from .presentation.pages.dashboard import index as dashboard_page
from .presentation.pages.inventory import inventory_page
from .presentation.pages.billing import billing_page
from .presentation.pages.orders import orders_page
from .presentation.pages.devices import devices_page
from .presentation.pages.suppliers import suppliers_page
from .presentation.pages.settings import settings_page
from .presentation.pages.support import support_page
from .presentation.pages.agenda import agenda_page
from .presentation.state.dashboard_state import DashboardState
from .presentation.state.inventory_state import InventoryState
from .presentation.state.billing_state import BillingState
from .presentation.state.order_state import OrderState
from .presentation.state.device_state import DeviceState
from .presentation.state.supplier_state import SupplierState
from .presentation.state.settings_state import SettingsState
from .presentation.state.auth_state import AuthState
from .presentation.state.agenda_state import AgendaState

def index() -> rx.Component:
    """Retorna la página de dashboard configurada."""
    return dashboard_page()

app = rx.App(
    theme=rx.theme(
        appearance="inherit",
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
    on_load=[AuthState.check_operations, InventoryState.on_load]
)

app.add_page(
    billing_page,
    route="/billing",
    title="Taller Desk & Laptop | Facturación",
    on_load=[AuthState.check_operations, BillingState.on_load]
)

app.add_page(
    orders_page,
    route="/orders",
    title="Taller Desk & Laptop | Órdenes",
    on_load=OrderState.on_load
)

app.add_page(
    devices_page,
    route="/devices",
    title="Taller Desk & Laptop | Dispositivos",
    on_load=DeviceState.on_load
)

app.add_page(
    suppliers_page,
    route="/suppliers",
    title="Taller Desk & Laptop | Proveedores",
    on_load=[AuthState.check_operations, SupplierState.on_load]
)

app.add_page(
    settings_page,
    route="/settings",
    title="Taller Desk & Laptop | Ajustes",
    on_load=[AuthState.check_admin, SettingsState.on_load]
)

app.add_page(
    support_page,
    route="/support",
    title="Taller Desk & Laptop | Soporte",
)

app.add_page(
    agenda_page,
    route="/agenda",
    title="Taller Desk & Laptop | Agenda",
    on_load=AgendaState.on_load
)

