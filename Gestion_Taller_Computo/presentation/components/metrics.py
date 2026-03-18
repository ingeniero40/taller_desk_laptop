import reflex as rx

def stat_card(title: str, value: str, icon: str, growth: str = None, color: str = "cyan") -> rx.Component:
    """Tarjeta de métrica con diseño premium y efectos dinámicos."""
    return rx.card(
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon(tag=icon, size=22, color=rx.color(color, 9)),
                        background=rx.color(color, 3),
                        padding="10px",
                        border_radius="10px",
                    ),
                    rx.vstack(
                        rx.text(title, size="2", weight="medium", color=rx.color("slate", 10)),
                        rx.heading(value, size="7", weight="bold", color=rx.color("slate", 12)),
                        spacing="0",
                        align_items="start",
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.cond(
                    growth is not None,
                    rx.badge(
                        rx.hstack(
                            rx.icon(tag="trending-up", size=14),
                            rx.text(growth), # Asumimos que growth ahora es una variable de estado o string
                            spacing="1",
                        ),
                        color_scheme="green",
                        variant="soft",
                        radius="full",
                        margin_top="12px",
                    ),
                ),
                spacing="2",
                align_items="start",
            ),
            justify="between",
            width="100%",
        ),
        padding="24px",
        border_radius="20px",
        background_color=rx.color("white", 1),
        border=f"1px solid {rx.color('slate', 4)}",
        box_shadow=f"0 4px 6px -1px {rx.color('slate', 3)}, 0 2px 4px -1px {rx.color('slate', 2)}",
        _hover={
            "transform": "translateY(-6px)",
            "border": f"1px solid {rx.color(color, 7)}",
            "box_shadow": f"0 20px 25px -5px {rx.color(color, 3)}, 0 10px 10px -5px {rx.color(color, 2)}",
        },
        transition="all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)",
    )
