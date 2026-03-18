import reflex as rx

def stat_card(title: str, value: str, icon: str, growth: str = None, color: str = "cyan") -> rx.Component:
    """Tarjeta de métrica con diseño minimalista y efectos hover."""
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
                    rx.text(title, size="2", weight="medium", color=rx.color("slate", 10)),
                    spacing="3",
                    align="center",
                ),
                rx.hstack(
                    rx.heading(value, size="7", weight="bold", color=rx.color("slate", 12)),
                    rx.cond(
                        growth is not None,
                        rx.badge(
                            rx.hstack(
                                rx.icon(tag="trending-up", size=14),
                                rx.text(f"{growth}%"),
                                spacing="1",
                            ),
                            color_scheme="emerald",
                            variant="soft",
                        ),
                    ),
                    spacing="3",
                    align="center",
                ),
                spacing="2",
                align_items="start",
            ),
            justify="between",
            width="100%",
        ),
        padding="20px",
        border_radius="16px",
        background=rx.color("slate", 2),
        border=f"1px solid {rx.color('slate', 5)}",
        _hover={
            "transform": "translateY(-4px)",
            "border": f"1px solid {rx.color(color, 8)}",
            "box_shadow": f"0 10px 30px {rx.color(color, 3)}",
        },
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    )
