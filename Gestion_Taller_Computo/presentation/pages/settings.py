import reflex as rx
from ..state.settings_state import SettingsState
from ..components.sidebar import sidebar

def settings_header() -> rx.Component:
    """Encabezado superior de configuración."""
    return rx.flex(
        rx.vstack(
            rx.heading("Configuración del Sistema", size="8", weight="bold", color=rx.color("slate", 12)),
            rx.text("Ajustes generales, cuentas de usuario y personalización operativa.", color=rx.color("slate", 10), size="3"),
            spacing="1",
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.icon(tag="save", size=18),
                rx.text("Guardar Cambios"),
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
            spacing="3",
        ),
        width="100%",
        align="center",
        padding_y="24px",
    )

def general_tab() -> rx.Component:
    """Formulario de datos generales del negocio."""
    return rx.card(
        rx.vstack(
            rx.heading("Detalles del Establecimiento", size="4", weight="bold"),
            rx.divider(width="100%", margin_y="8px"),
            rx.grid(
                rx.vstack(rx.text("Nombre del Negocio", size="2"), rx.input(value=SettingsState.workshop_info["name"], on_change=lambda v: SettingsState.set_workshop_info("name", v), width="100%")),
                rx.vstack(rx.text("Correo de Contacto", size="2"), rx.input(value=SettingsState.workshop_info["email"], on_change=lambda v: SettingsState.set_workshop_info("email", v), width="100%")),
                columns="2", spacing="4", width="100%",
            ),
            rx.vstack(rx.text("Dirección Principal", size="2"), rx.text_area(value=SettingsState.workshop_info["address"], on_change=lambda v: SettingsState.set_workshop_info("address", v), width="100%")),
            rx.grid(
                rx.vstack(rx.text("Teléfono de Atención", size="2"), rx.input(value=SettingsState.workshop_info["phone"], on_change=lambda v: SettingsState.set_workshop_info("phone", v), width="100%")),
                rx.vstack(rx.text("Impuesto por Defecto (%)", size="2"), rx.input(value=SettingsState.workshop_info["tax_rate"], on_change=lambda v: SettingsState.set_workshop_info("tax_rate", v), width="100%")),
                columns="2", spacing="4", width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        padding="24px",
        border_radius="16px",
        variant="surface",
    )

def users_tab() -> rx.Component:
    """Lista de administración de usuarios (Staff/Admins/Techs)."""
    return rx.vstack(
        rx.flex(
            rx.heading("Gestión de Usuarios", size="4", weight="bold"),
            rx.spacer(),
            rx.button(
                rx.icon(tag="user-plus", size=16),
                rx.text("Agregar Colaborador"),
                on_click=SettingsState.open_add_user_modal,
                size="2", variant="soft", color_scheme="cyan",
            ),
            width="100%",
            align="center",
            margin_bottom="12px",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Usuario"),
                    rx.table.column_header_cell("Nombre"),
                    rx.table.column_header_cell("Rol"),
                    rx.table.column_header_cell("Estado"),
                    rx.table.column_header_cell("Acciones"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    SettingsState.users,
                    lambda u: rx.table.row(
                        rx.table.cell(rx.text(u["username"], weight="medium")),
                        rx.table.cell(rx.text(u["name"])),
                        rx.table.cell(rx.badge(u["role"], color_scheme=u["role_color"], variant="soft")),
                        rx.table.cell(
                            rx.badge(
                                rx.cond(u["is_active"], "Activo", "Suspendido"),
                                color_scheme=rx.cond(u["is_active"], "green", "red"),
                                variant="outline",
                            )
                        ),
                        rx.table.cell(
                            rx.hstack(
                                rx.icon_button(
                                    rx.icon(tag="shield-half", size=16),
                                    variant="soft",
                                    tooltip="Cambiar Rol",
                                ),
                                rx.icon_button(
                                    rx.icon(tag="power", size=16),
                                    variant="ghost",
                                    color_scheme=rx.cond(u["is_active"], "red", "green"),
                                    on_click=lambda: SettingsState.toggle_user_active(u["id"], u["is_active"]),
                                ),
                                spacing="2",
                            )
                        ),
                        align="center",
                    )
                )
            ),
            width="100%",
            variant="surface",
        ),
        width="100%",
        spacing="4",
    )

def user_modal() -> rx.Component:
    """Modal para agregar staff."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nuevo Colaborador"),
            rx.dialog.description("Crea una cuenta para el equipo de administración o técnicos."),
            rx.form(
                 rx.vstack(
                    rx.grid(
                        rx.vstack(rx.text("Usuario", size="2", weight="medium"), rx.input(name="username", placeholder="Ej: pedro_tech", width="100%")),
                        rx.vstack(rx.text("Email", size="2", weight="medium"), rx.input(name="email", type="email", placeholder="p@email.com", width="100%")),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Nombre Completo", size="2", weight="medium"), 
                        rx.input(name="full_name", placeholder="Nombre y Apellido", width="100%"),
                        width="100%",
                    ),
                    rx.grid(
                        rx.vstack(rx.text("Password", size="2", weight="medium"), rx.input(name="password", type="password", placeholder="****", width="100%")),
                        rx.vstack(
                            rx.text("Rol", size="2", weight="medium"),
                            rx.select(["ADMIN", "TECHNICIAN", "CUSTOMER"], name="role", value="TECHNICIAN", width="100%"),
                        ),
                        columns="2", spacing="4", width="100%",
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancelar", variant="soft")),
                        rx.button("Crear Usuario", type="submit", variant="solid", color_scheme="cyan"),
                        spacing="3", width="100%", justify="end", padding_top="16px",
                    ),
                    spacing="4",
                    width="100%",
                 ),
                 on_submit=SettingsState.save_new_user,
            ),
            max_width="450px",
            border_radius="24px",
        ),
        open=SettingsState.show_user_modal,
        on_open_change=SettingsState.set_show_user_modal,
    )

def settings_page() -> rx.Component:
    """Layout principal de la página de ajustes."""
    return rx.hstack(
        sidebar("/settings"),
        rx.container(
            rx.vstack(
                settings_header(),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger(rx.icon(tag="info", size=16), "General", value="general", spacing="2"),
                        rx.tabs.trigger(rx.icon(tag="users", size=16), "Cuentas / Staff", value="users", spacing="2"),
                        rx.tabs.trigger(rx.icon(tag="palette", size=16), "Personalización", value="ui", spacing="2"),
                        width="100%",
                    ),
                    rx.tabs.content(
                        general_tab(),
                        value="general",
                        padding_y="24px",
                    ),
                    rx.tabs.content(
                        users_tab(),
                        value="users",
                        padding_y="24px",
                    ),
                    rx.tabs.content(
                        rx.card(rx.text("Opciones de apariencia del sistema (Dark Mode, Temas)... En desarrollo.")),
                        value="ui",
                        padding_y="24px",
                    ),
                    default_value="general",
                    width="100%",
                ),
                user_modal(),
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
