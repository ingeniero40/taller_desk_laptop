import reflex as rx

def sidebar_item(text: str, icon: str, href: str, active: bool = False) -> rx.Component:
    """Ítem de navegación individual para la barra lateral."""
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon, size=18, color=rx.color("cyan", 9) if active else rx.color("slate", 11)),
            rx.text(
                text, 
                size="2", 
                weight="medium",
                color=rx.color("cyan", 9) if active else rx.color("slate", 11)
            ),
            spacing="3",
            padding="12px 16px",
            border_radius="12px",
            background=rx.color("cyan", 3) if active else "transparent",
            _hover={
                "background": rx.color("slate", 3),
                "cursor": "pointer",
            },
            transition="all 0.2s ease-in-out",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )

def sidebar(active_page: str = "/") -> rx.Component:
    """Barra lateral principal con diseño premium."""
    return rx.flex(
        rx.vstack(
            # Logo / Título
            rx.hstack(
                rx.icon(tag="layout-dashboard", size=24, color=rx.color("cyan", 9)),
                rx.heading("GRAVITY", size="6", weight="bold", color=rx.color("slate", 12)),
                rx.badge("Pro", color_scheme="cyan", variant="soft"),
                spacing="3",
                align="center",
                padding_y="24px",
            ),
            
            # Navegación Principal
            rx.vstack(
                rx.text("PRINCIPAL", size="1", weight="bold", color=rx.color("slate", 9), padding_left="16px"),
                sidebar_item("Dashboard", "home", "/", active=(active_page == "/")),
                sidebar_item("Ordenes", "clipboard-list", "/orders", active=(active_page == "/orders")), # Próximamente
                sidebar_item("Dispositivos", "laptop", "/devices", active=(active_page == "/devices")), # Próximamente
                spacing="2",
                width="100%",
            ),
            
            rx.divider(width="100%", margin_y="16px", opacity=0.3),
            
            # Negocio e Inventario
            rx.vstack(
                rx.text("GESTIÓN", size="1", weight="bold", color=rx.color("slate", 9), padding_left="16px"),
                sidebar_item("Inventario", "package", "/inventory", active=(active_page == "/inventory")),
                sidebar_item("Facturación", "receipt-text", "/billing", active=(active_page == "/billing")), # Próximamente
                sidebar_item("Proveedores", "truck", "/suppliers", active=(active_page == "/suppliers")), # Próximamente
                spacing="2",
                width="100%",
            ),
            
            rx.spacer(),
            
            # Configuración
            rx.vstack(
                sidebar_item("Configuración", "settings", "/settings", active=(active_page == "/settings")),
                sidebar_item("Soporte", "help-circle", "/support", active=(active_page == "/support")),
                spacing="2",
                width="100%",
                padding_bottom="24px",
            ),
            
            spacing="4",
            height="100vh",
            padding_x="20px",
            width="100%",
        ),
        direction="column",
        width="260px",
        height="100vh",
        background_color=rx.color("slate", 1),
        border_right=f"1px solid {rx.color('slate', 4)}",
        position="sticky",
        top="0",
        left="0",
        z_index="100",
        display=["none", "none", "flex", "flex", "flex"], # Responsivo (escondido en móvil por ahora)
    )
