import reflex as rx
from .presentation.pages.dashboard import index as dashboard_page
from .presentation.state.dashboard_state import DashboardState

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

