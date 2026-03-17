import reflex as rx

config = rx.Config(
    app_name="Gestion_Taller_Computo",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)