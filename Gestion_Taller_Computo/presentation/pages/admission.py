import reflex as rx
from ..state.admission_state import AdmissionState
from ..components.sidebar import sidebar
from ..components.page_header import page_header

# ── Barra de Progreso del Wizard ──────────────────────────────────────────────

def wizard_progress() -> rx.Component:
    """Indicador visual de pasos con barra de progreso."""
    steps = [
        ("1", "Cliente"),
        ("2", "Equipo"),
        ("3", "Problema"),
        ("4", "Confirmación"),
    ]

    def step_dot(num: str, label: str) -> rx.Component:
        is_active = AdmissionState.current_step == int(num)
        is_done = AdmissionState.current_step > int(num)
        return rx.vstack(
            rx.box(
                rx.cond(is_done, rx.icon(tag="check", size=14, color="white"), rx.text(num, size="1", weight="bold", color="white")),
                width="32px",
                height="32px",
                border_radius="full",
                background=rx.cond(
                    is_done, rx.color("green", 9),
                    rx.cond(is_active, rx.color("cyan", 9), rx.color("slate", 5))
                ),
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text(label, size="1", color=rx.cond(is_active, rx.color("cyan", 9), rx.color("slate", 9)), weight=rx.cond(is_active, "bold", "regular")),
            spacing="1",
            align_items="center",
        )

    return rx.vstack(
        rx.hstack(
            step_dot("1", "Cliente"),
            rx.box(height="2px", flex="1", background=rx.cond(AdmissionState.current_step > 1, rx.color("cyan", 6), rx.color("slate", 4)), margin_top="-16px"),
            step_dot("2", "Equipo"),
            rx.box(height="2px", flex="1", background=rx.cond(AdmissionState.current_step > 2, rx.color("cyan", 6), rx.color("slate", 4)), margin_top="-16px"),
            step_dot("3", "Problema"),
            rx.box(height="2px", flex="1", background=rx.cond(AdmissionState.current_step > 3, rx.color("cyan", 6), rx.color("slate", 4)), margin_top="-16px"),
            step_dot("4", "Confirmación"),
            width="100%",
            align_items="center",
            spacing="2",
        ),
        rx.hstack(
            rx.text(AdmissionState.step_label, size="2", weight="bold", color=rx.color("cyan", 9)),
            rx.spacer(),
            rx.text(
                "Paso ", AdmissionState.current_step, " de ", AdmissionState.total_steps,
                size="2", color=rx.color("slate", 10)
            ),
            width="100%",
        ),
        spacing="3",
        padding="20px 24px",
        border_radius="16px",
        background=rx.color("slate", 1),
        border=f"1px solid {rx.color('slate', 4)}",
        width="100%",
    )

# ── PASO 1: Identificar Cliente ───────────────────────────────────────────────

def step_customer() -> rx.Component:
    return rx.vstack(
        rx.heading("¿Quién trae el equipo?", size="5", weight="bold"),
        rx.text("Busca un cliente existente o registra uno nuevo.", size="2", color=rx.color("slate", 10)),

        # Búsqueda de cliente
        rx.cond(
            ~AdmissionState.new_customer_mode,
            rx.vstack(
                rx.hstack(
                    rx.input(
                        placeholder="Buscar por nombre o correo...",
                        value=AdmissionState.customer_search,
                        on_change=AdmissionState.set_customer_search,
                        flex="1",
                        radius="large",
                    ),
                    rx.button(
                        rx.icon(tag="search", size=16),
                        rx.text("Buscar"),
                        on_click=AdmissionState.search_customer,
                        color_scheme="cyan",
                        variant="solid",
                        radius="large",
                    ),
                    width="100%",
                    spacing="3",
                ),
                # Resultados de búsqueda
                rx.cond(
                    AdmissionState.customers_found.length() >= 1,
                    rx.vstack(
                        rx.text("Resultados:", size="2", weight="bold", color=rx.color("slate", 10)),
                        rx.foreach(
                            AdmissionState.customers_found,
                            lambda c: rx.card(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(c["name"], size="2", weight="bold"),
                                        rx.text(c["email"], size="1", color=rx.color("slate", 10)),
                                        spacing="0",
                                    ),
                                    rx.spacer(),
                                    rx.button(
                                        "Seleccionar",
                                        on_click=AdmissionState.select_customer(c["id"], c["name"]),
                                        size="1",
                                        color_scheme=rx.cond(
                                            AdmissionState.selected_customer_id == c["id"],
                                            "green", "cyan"
                                        ),
                                        variant="soft",
                                    ),
                                    width="100%",
                                    align_items="center",
                                ),
                                padding="12px",
                                border=rx.cond(
                                    AdmissionState.selected_customer_id == c["id"],
                                    f"1px solid {rx.color('cyan', 6)}",
                                    f"1px solid {rx.color('slate', 4)}"
                                ),
                                border_radius="10px",
                            )
                        ),
                        spacing="2",
                        width="100%",
                    ),
                ),
                rx.cond(
                    AdmissionState.selected_customer_id != "",
                    rx.hstack(
                        rx.icon(tag="circle-check", size=18, color=rx.color("green", 9)),
                        rx.text(
                            "Cliente seleccionado: ",
                            rx.text.span(AdmissionState.selected_customer_name, weight="bold"),
                            size="2", color=rx.color("green", 9),
                        ),
                        spacing="2",
                        padding="12px",
                        border_radius="10px",
                        background=rx.color("green", 2),
                        width="100%",
                    ),
                ),
                rx.divider(margin_y="8px", opacity=0.3),
                rx.button(
                    rx.icon(tag="user-plus", size=16),
                    rx.text("Registrar Cliente Nuevo"),
                    on_click=AdmissionState.enable_new_customer,
                    variant="ghost",
                    color_scheme="cyan",
                    size="2",
                ),
                spacing="3",
                width="100%",
            ),
        ),

        # Formulario de nuevo cliente
        rx.cond(
            AdmissionState.new_customer_mode,
            rx.vstack(
                rx.hstack(
                    rx.icon(tag="user-plus", size=20, color=rx.color("cyan", 9)),
                    rx.text("Nuevo Cliente", size="3", weight="bold"),
                    spacing="2",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Nombre Completo *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Ej: Juan García López",
                            value=AdmissionState.new_customer_name,
                            on_change=AdmissionState.set_new_customer_name,
                            width="100%",
                            radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Correo Electrónico *", size="2", weight="medium"),
                        rx.input(
                            placeholder="correo@ejemplo.com",
                            value=AdmissionState.new_customer_email,
                            on_change=AdmissionState.set_new_customer_email,
                            type="email",
                            width="100%",
                            radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Teléfono", size="2", weight="medium"),
                        rx.input(
                            placeholder="+52 81 0000 0000",
                            value=AdmissionState.new_customer_phone,
                            on_change=AdmissionState.set_new_customer_phone,
                            type="tel",
                            width="100%",
                            radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                rx.button(
                    rx.icon(tag="arrow-left", size=14),
                    rx.text("Volver a búsqueda"),
                    on_click=AdmissionState.enable_new_customer,
                    variant="ghost",
                    color_scheme="gray",
                    size="2",
                ),
                spacing="4",
                padding="20px",
                border_radius="12px",
                background=rx.color("cyan", 1),
                border=f"1px solid {rx.color('cyan', 4)}",
                width="100%",
            ),
        ),
        spacing="4",
        width="100%",
    )

# ── PASO 2: Datos del Equipo ──────────────────────────────────────────────────

def step_device() -> rx.Component:
    return rx.vstack(
        rx.heading("Datos del Equipo", size="5", weight="bold"),
        rx.text("Completa la información del dispositivo que se entrega.", size="2", color=rx.color("slate", 10)),

        # Toggle: equipo existente o nuevo
        rx.hstack(
            rx.checkbox(
                "El cliente ya tiene un equipo registrado",
                checked=AdmissionState.has_existing_device,
                on_change=AdmissionState.toggle_existing_device,
                color_scheme="cyan",
            ),
        ),

        # Selección de dispositivo existente
        rx.cond(
            AdmissionState.has_existing_device,
            rx.vstack(
                rx.text("Dispositivos registrados del cliente:", size="2", weight="medium"),
                rx.select(
                    AdmissionState.device_options,

                    value=AdmissionState.selected_device_id,
                    on_change=AdmissionState.set_selected_device,
                    placeholder="Seleccionar dispositivo...",
                    width="100%",
                    radius="large",
                ),
                spacing="2",
                width="100%",
            ),
        ),

        # Formulario nuevo dispositivo
        rx.cond(
            ~AdmissionState.has_existing_device,
            rx.vstack(
                rx.grid(
                    rx.vstack(
                        rx.text("Tipo de Equipo", size="2", weight="medium"),
                        rx.select(
                            ["Laptop", "PC Desktop", "All-in-One", "Tablet", "Impresora", "Otro"],
                            value=AdmissionState.device_type,
                            on_change=AdmissionState.set_device_type,
                            width="100%",
                            radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Marca *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Ej: Dell, HP, Lenovo...",
                            value=AdmissionState.device_brand,
                            on_change=AdmissionState.set_device_brand,
                            width="100%",
                            radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Modelo *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Ej: Inspiron 15, Pavilion...",
                            value=AdmissionState.device_model,
                            on_change=AdmissionState.set_device_model,
                            width="100%",
                            radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Número de Serie *", size="2", weight="medium"),
                        rx.input(
                            placeholder="Serial único del dispositivo",
                            value=AdmissionState.device_serial,
                            on_change=AdmissionState.set_device_serial,
                            width="100%",
                            radius="large",
                        ),
                        spacing="1", width="100%",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),

                # Estado Físico
                rx.vstack(
                    rx.text("Estado Físico del Equipo", size="2", weight="medium"),
                    rx.select(
                        ["Excelente", "Bueno", "Regular", "Dañado", "En partes"],
                        value=AdmissionState.physical_condition,
                        on_change=AdmissionState.set_physical_condition,
                        width="100%",
                        radius="large",
                    ),
                    spacing="1",
                    width="100%",
                ),

                # Evidencia Fotográfica (Contexto 9)
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="camera", size=18, color=rx.color("cyan", 9)),
                        rx.text("Evidencia Fotográfica", size="2", weight="medium"),
                        rx.badge("Contexto 9", color_scheme="cyan", variant="solid", size="1"),
                        spacing="2",
                    ),
                    rx.upload(
                        rx.vstack(
                            rx.button("Seleccionar Fotos (Antes)", variant="soft", color_scheme="cyan"),
                            rx.text("O arrastra y suelta aquí", size="1", color=rx.color("slate", 9)),
                        ),
                        id="upload_entry",
                        multiple=True,
                        accept={"image/*": [".jpg", ".jpeg", ".png"]},
                        max_files=5,
                        on_drop=AdmissionState.handle_entry_image_upload(rx.upload_files(upload_id="upload_entry")),
                        border=f"2px dashed {rx.color('cyan', 5)}",
                        padding="20px",
                        border_radius="12px",
                        width="100%",
                        background=rx.color("cyan", 1),
                    ),
                    # Previsualización de imágenes
                    rx.cond(
                        AdmissionState.entry_images_urls.length() > 0,
                        rx.hstack(
                            rx.foreach(
                                AdmissionState.entry_images_urls,
                                lambda url: rx.box(
                                    rx.image(src=url, width="60px", height="60px", border_radius="8px", object_fit="cover"),
                                    border=f"1px solid {rx.color('slate', 4)}",
                                    border_radius="10px",
                                    padding="2px",
                                )
                            ),
                            spacing="2",
                            flex_wrap="wrap",
                            padding_top="10px",
                        ),
                        rx.fragment()
                    ),
                    spacing="2",
                    width="100%",
                    padding_top="10px",
                ),
                spacing="4",
                width="100%",
            ),
        ),
        spacing="4",
        width="100%",
    )

# ── PASO 3: Descripción del Problema ─────────────────────────────────────────

def step_problem() -> rx.Component:
    return rx.vstack(
        rx.heading("Descripción del Problema", size="5", weight="bold"),
        rx.text("Describe el fallo o servicio solicitado con el mayor detalle posible.", size="2", color=rx.color("slate", 10)),

        rx.vstack(
            rx.text("¿Qué problema presenta el equipo? *", size="2", weight="medium"),
            rx.text_area(
                placeholder="Ej: La laptop no enciende, hace click al girar el ventilador y tiene la pantalla manchada en la esquina superior derecha...",
                value=AdmissionState.problem_description,
                on_change=AdmissionState.set_problem_description,
                rows="6",
                width="100%",
                resize="vertical",
            ),
            spacing="1",
            width="100%",
        ),

        rx.vstack(
            rx.text("Nivel de Urgencia", size="2", weight="medium"),
            rx.hstack(
                rx.foreach(
                    [
                        {"val": "Baja", "color": "blue", "icon": "arrow-down"},
                        {"val": "Media", "color": "amber", "icon": "minus"},
                        {"val": "Alta", "color": "orange", "icon": "arrow-up"},
                        {"val": "Crítica", "color": "red", "icon": "triangle-alert"},
                    ],
                    lambda p: rx.button(
                        rx.icon(tag=p["icon"], size=14),
                        rx.text(p["val"], size="2"),
                        on_click=AdmissionState.set_problem_priority(p["val"]),
                        color_scheme=p["color"],
                        variant=rx.cond(
                            AdmissionState.problem_priority == p["val"],
                            "solid",
                            "soft"
                        ),
                        radius="large",
                    )
                ),
                spacing="2",
                flex_wrap="wrap",
            ),
            spacing="2",
            width="100%",
        ),
        spacing="5",
        width="100%",
    )

# ── PASO 4: Confirmación y Resumen ────────────────────────────────────────────

def step_confirmation() -> rx.Component:
    return rx.vstack(
        rx.heading("Resumen de Admisión", size="5", weight="bold"),
        rx.text("Revisa los datos antes de generar la Orden de Trabajo.", size="2", color=rx.color("slate", 10)),

        # Grid de resumen
        rx.grid(
            # Card: Cliente
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.box(rx.icon(tag="user", size=18, color=rx.color("cyan", 9)), padding="8px", border_radius="8px", background=rx.color("cyan", 2)),
                        rx.text("Cliente", size="2", weight="bold"),
                        spacing="2",
                    ),
                    rx.text(
                        rx.cond(
                            AdmissionState.new_customer_mode,
                            AdmissionState.new_customer_name,
                            AdmissionState.selected_customer_name,
                        ),
                        size="3",
                        weight="bold",
                        color=rx.color("slate", 12),
                    ),
                    rx.cond(
                        AdmissionState.new_customer_mode,
                        rx.badge("Nuevo cliente", color_scheme="cyan", variant="soft", size="1"),
                        rx.badge("Existente", color_scheme="green", variant="soft", size="1"),
                    ),
                    spacing="2",
                ),
                padding="16px",
            ),
            # Card: Dispositivo
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.box(rx.icon(tag="laptop", size=18, color=rx.color("indigo", 9)), padding="8px", border_radius="8px", background=rx.color("indigo", 2)),
                        rx.text("Dispositivo", size="2", weight="bold"),
                        spacing="2",
                    ),
                    rx.text(
                        AdmissionState.device_type, " ", AdmissionState.device_brand, " ", AdmissionState.device_model,
                        size="3", weight="bold", color=rx.color("slate", 12),
                    ),
                    rx.text("Serie: ", AdmissionState.device_serial, size="1", color=rx.color("slate", 10)),
                    rx.hstack(
                        rx.badge(AdmissionState.physical_condition, color_scheme="gray", variant="soft", size="1"),
                        spacing="1",
                    ),
                    spacing="2",
                ),
                padding="16px",
            ),
            # Card: Problema
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.box(rx.icon(tag="wrench", size=18, color=rx.color("amber", 9)), padding="8px", border_radius="8px", background=rx.color("amber", 2)),
                        rx.text("Problema + Prioridad", size="2", weight="bold"),
                        spacing="2",
                    ),
                    rx.text(AdmissionState.problem_description, size="2", color=rx.color("slate", 11), no_of_lines=3),
                    rx.badge(
                        AdmissionState.problem_priority,
                        color_scheme=rx.cond(
                            AdmissionState.problem_priority == "Crítica", "red",
                            rx.cond(
                                AdmissionState.problem_priority == "Alta", "orange",
                                rx.cond(AdmissionState.problem_priority == "Media", "amber", "blue")
                            )
                        ),
                        variant="soft",
                        size="1",
                        radius="full",
                    ),
                    spacing="2",
                ),
                padding="16px",
            ),
            columns="3",
            spacing="4",
            width="100%",
        ),

        # Estado de resultado
        rx.cond(
            AdmissionState.admission_complete,
            rx.card(
                rx.hstack(
                    rx.icon(tag="circle-check", size=28, color=rx.color("green", 9)),
                    rx.vstack(
                        rx.text("¡Admisión exitosa!", size="4", weight="bold", color=rx.color("green", 9)),
                        rx.text(
                            "Número de Ticket generado: ",
                            rx.text.span(AdmissionState.generated_ticket, weight="bold", color=rx.color("cyan", 9)),
                            size="3",
                        ),
                        spacing="1",
                    ),
                    spacing="4",
                    align_items="center",
                ),
                padding="20px",
                background=rx.color("green", 2),
                border=f"1px solid {rx.color('green', 5)}",
                border_radius="12px",
                width="100%",
            ),
        ),
        rx.cond(
            AdmissionState.error_message != "",
            rx.hstack(
                rx.icon(tag="triangle-alert", size=18, color=rx.color("red", 9)),
                rx.text(AdmissionState.error_message, size="2", color=rx.color("red", 9)),
                spacing="2",
                padding="12px",
                border_radius="10px",
                background=rx.color("red", 2),
                border=f"1px solid {rx.color('red', 4)}",
                width="100%",
            ),
        ),
        spacing="5",
        width="100%",
    )

# ── Contenido del Paso Activo ─────────────────────────────────────────────────

def step_content() -> rx.Component:
    return rx.box(
        rx.cond(AdmissionState.current_step == 1, step_customer(), rx.fragment()),
        rx.cond(AdmissionState.current_step == 2, step_device(), rx.fragment()),
        rx.cond(AdmissionState.current_step == 3, step_problem(), rx.fragment()),
        rx.cond(AdmissionState.current_step == 4, step_confirmation(), rx.fragment()),
        width="100%",
    )

# ── Navegación del Wizard ─────────────────────────────────────────────────────

def wizard_nav() -> rx.Component:
    return rx.hstack(
        rx.cond(
            AdmissionState.current_step > 1,
            rx.button(
                rx.icon(tag="arrow-left", size=16),
                rx.text("Anterior"),
                on_click=AdmissionState.prev_step,
                variant="soft",
                color_scheme="gray",
                radius="large",
            ),
        ),
        rx.spacer(),
        rx.cond(
            AdmissionState.current_step == 4,
            rx.cond(
                ~AdmissionState.admission_complete,
                rx.button(
                    rx.cond(
                        AdmissionState.is_loading,
                        rx.spinner(size="2"),
                        rx.icon(tag="check-circle", size=18),
                    ),
                    rx.text("Generar Orden de Trabajo"),
                    on_click=AdmissionState.finalize_admission,
                    color_scheme="green",
                    variant="solid",
                    radius="large",
                    disabled=AdmissionState.is_loading,
                ),
                rx.button(
                    rx.icon(tag="plus", size=16),
                    rx.text("Nueva Admisión"),
                    on_click=AdmissionState.reset_wizard,
                    color_scheme="cyan",
                    variant="solid",
                    radius="large",
                ),
            ),
            rx.button(
                rx.text("Siguiente"),
                rx.icon(tag="arrow-right", size=16),
                on_click=AdmissionState.next_step,
                color_scheme="cyan",
                variant="solid",
                radius="large",
            ),
        ),
        width="100%",
        padding_top="8px",
    )

# ── Página Principal ──────────────────────────────────────────────────────────

def admission_page() -> rx.Component:
    """Flujo de Admisión de Equipos — Wizard multi-paso."""
    return rx.hstack(
        sidebar("/admission"),
        rx.container(
            rx.vstack(
                page_header(
                    "Admisión de Equipos",
                    "Flujo de recepción, registro de cliente y generación automática de órdenes.",
                    actions=[
                        rx.button(
                            rx.icon(tag="rotate-ccw", size=18),
                            rx.text("Reiniciar"),
                            on_click=AdmissionState.reset_wizard,
                            variant="ghost",
                            color_scheme="gray",
                            radius="large",
                        )
                    ],
                ),
                # Wizard Card
                rx.card(
                    rx.vstack(
                        wizard_progress(),
                        rx.divider(opacity=0.3),
                        step_content(),
                        rx.divider(opacity=0.3),
                        wizard_nav(),
                        spacing="5",
                        padding="28px",
                        width="100%",
                    ),
                    border_radius="20px",
                    border=f"1px solid {rx.color('slate', 4)}",
                    width="100%",
                ),
                spacing="6",
                padding_bottom="48px",
                width="100%",
            ),
            size="3",
            padding_x="40px",
        ),
        background_color=rx.color("slate", 2),
        min_height="100vh",
        spacing="0",
        align_items="start",
    )
