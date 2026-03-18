import reflex as rx

def page_header(title: str, subtitle: str, actions: list[rx.Component] = None) -> rx.Component:
    """Encabezado de página estandarizado con diseño premium."""
    return rx.flex(
        rx.vstack(
            rx.heading(
                title, 
                size="8", 
                weight="bold", 
                color=rx.color("slate", 12),
                letter_spacing="-0.02em"
            ),
            rx.text(
                subtitle, 
                color=rx.color("slate", 10), 
                size="3",
                weight="medium"
            ),
            spacing="1",
        ),
        rx.spacer(),
        rx.hstack(
            *(actions or []),
            spacing="3",
            align="center",
        ),
        width="100%",
        align="center",
        padding_y="32px",
        border_bottom=f"1px solid {rx.color('slate', 3)}",
        margin_bottom="24px",
    )
