import reflex as rx
from ..state.settings_state import SettingsState
from ..state.auth_state import AuthState

def sidebar_item(text: str, icon: str, href: str, active: bool = False) -> rx.Component:
    """Ítem de navegación individual con estilo premium."""
    return rx.link(
        rx.hstack(
            rx.icon(
                tag=icon, 
                size=18, 
                color=rx.color("cyan", 9) if active else rx.color("slate", 10),
                stroke_width=2,
            ),
            rx.text(
                text, 
                size="2", 
                weight="medium" if active else "regular",
                color=rx.color("slate", 12) if active else rx.color("slate", 10)
            ),
            spacing="3",
            padding="10px 16px",
            border_radius="10px",
            background=rx.cond(
                active,
                f"linear-gradient(90deg, {rx.color('cyan', 3)} 0%, {rx.color('cyan', 2)} 100%)",
                "transparent"
            ),
            border=rx.cond(
                active,
                f"1px solid {rx.color('cyan', 5)}",
                "1px solid transparent"
            ),
            _hover={
                "background": rx.color("slate", 3),
                "cursor": "pointer",
                "transform": "translateX(4px)",
            },
            transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
            width="100%",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )

def sidebar(active_page: str = "/") -> rx.Component:
    """Barra lateral Gravity Design."""
    return rx.flex(
        rx.vstack(
            # Logo / Título con efecto de brillo
            rx.hstack(
                rx.box(
                    rx.icon(tag="bolt", size=22, color="white"),
                    background=f"linear-gradient(135deg, {rx.color('cyan', 9)} 0%, {rx.color('indigo', 9)} 100%)",
                    padding="8px",
                    border_radius="8px",
                    box_shadow=f"0 4px 12px {rx.color('cyan', 4)}",
                ),
                rx.heading("GRAVITY", size="6", weight="bold", color=rx.color("slate", 12), letter_spacing="1px"),
                spacing="3",
                align="center",
                padding_y="32px",
                padding_x="12px",
            ),
            
            # Navegación Principal
            rx.vstack(
                rx.text("SISTEMA", size="1", weight="bold", color=rx.color("slate", 9), padding_left="16px", letter_spacing="1.5px"),
                sidebar_item("Dashboard", "layout-dashboard", "/", active=(active_page == "/")),
                sidebar_item("Órdenes", "clipboard-list", "/orders", active=(active_page == "/orders")),
                sidebar_item("Admisión", "package-plus", "/admission", active=(active_page == "/admission")),
                sidebar_item("Agenda", "calendar-days", "/agenda", active=(active_page == "/agenda")),
                sidebar_item("Dispositivos", "laptop", "/devices", active=(active_page == "/devices")),
                spacing="2",
                width="100%",
            ),
            
            rx.divider(width="80%", margin_y="16px", opacity=0.3, align_self="center"),
            
            # Operaciones (Solo Admin y Recepcionista)
            rx.cond(
                AuthState.can_see_operations,
                rx.vstack(
                    rx.text("OPERACIONES", size="1", weight="bold", color=rx.color("slate", 9), padding_left="16px", letter_spacing="1.5px"),
                    sidebar_item("Inventario", "package", "/inventory", active=(active_page == "/inventory")),
                    sidebar_item("Facturación", "receipt-text", "/billing", active=(active_page == "/billing")),
                    sidebar_item("Proveedores", "truck", "/suppliers", active=(active_page == "/suppliers")),
                    spacing="2",
                    width="100%",
                ),
            ),
            
            rx.spacer(),
            
            # Footer / Configuración
            rx.vstack(
                rx.divider(width="100%", margin_bottom="16px", opacity=0.3),
                rx.cond(
                    AuthState.can_see_settings,
                    sidebar_item("Configuración", "settings", "/settings", active=(active_page == "/settings")),
                ),
                sidebar_item("Centro de Soporte", "circle-help", "/support", active=(active_page == "/support")),
                
                # Dark Mode Switch
                rx.hstack(
                    rx.icon(tag="moon", size=18, color=rx.color("slate", 10)),
                    rx.text("Modo Oscuro", size="1", weight="medium", color=rx.color("slate", 10)),
                    rx.spacer(),
                    rx.switch(
                        checked=rx.cond(rx.color_mode == "dark", True, False),
                        on_change=rx.toggle_color_mode,
                        radius="full",
                        color_scheme="cyan",
                    ),
                    width="100%",
                    padding="12px 16px",
                    border_radius="10px",
                    border=f"1px solid {rx.color('slate', 4)}",
                    background=rx.color("black", 1),
                    margin_top="16px",
                ),
                
                # Role Selector (Mock para desarrollo)
                rx.select(
                    ["ADMIN", "TECHNICIAN", "RECEPTIONIST"],
                    value=AuthState.current_role,
                    on_change=AuthState.set_role_mock,
                    size="1",
                    variant="soft",
                    width="100%",
                    margin_top="8px",
                ),
                spacing="2",
                width="100%",
                padding_bottom="32px",
            ),
            
            spacing="1",
            height="100vh",
            padding_x="16px",
            width="100%",
        ),
        direction="column",
        width="280px",
        height="100vh",
        background_color=rx.color("slate", 1),
        border_right=f"1px solid {rx.color('slate', 4)}",
        position="sticky",
        top="0",
        left="0",
        z_index="100",
        display=["none", "none", "flex", "flex", "flex"],
    )
