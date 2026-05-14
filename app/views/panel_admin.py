import flet as ft
from data_base.supabase_client import supabase


def vista_panel_admin(page: ft.Page, usuario, cerrar_sesion):

    def obtener_stats():
        total_clientes = len(supabase.table("clientes").select("id_cliente").execute().data)
        mesas_disponibles = len(supabase.table("mesas").select("id_mesa").eq("estado", "disponible").execute().data)
        from datetime import date
        hoy = str(date.today())
        reservas_hoy = len(supabase.table("reservas").select("id_reservas").eq("fecha", hoy).eq("estado_reserva", "confirmada").execute().data)
        total_reservas = len(supabase.table("reservas").select("id_reservas").eq("estado_reserva", "confirmada").execute().data)
        return total_clientes, mesas_disponibles, reservas_hoy, total_reservas

    total_clientes, mesas_disponibles, reservas_hoy, total_reservas = obtener_stats()

    def tarjeta_stat(icono, titulo, valor, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icono, color=color, size=32),
                    ft.Text(str(valor), size=28, weight="bold", color="#4E342E"),
                    ft.Text(titulo, size=13, color="#6D4C41")
                ],
                horizontal_alignment="center",
                spacing=5
            ),
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=15,
            width=180,
            height=130,
            shadow=ft.BoxShadow(blur_radius=8, color="#00000022")
        )

    def boton_nav(icono, texto, destino):
        return ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(icono, color="#FFFFFF", size=20),
                    ft.Text(texto, color="#FFFFFF", size=14)
                ],
                spacing=10
            ),
            on_click=lambda e: destino()
        )

    def ir_clientes():
        page.clean()
        page.add(ft.Text("Gestión de Clientes — próximamente", size=24, color="#4E342E"))
        page.update()

    def ir_mesas():
        page.clean()
        page.add(ft.Text("Gestión de Mesas — próximamente", size=24, color="#4E342E"))
        page.update()

    def ir_reservas():
        page.clean()
        page.add(ft.Text("Gestión de Reservas — próximamente", size=24, color="#4E342E"))
        page.update()

    def ir_historial():
        page.clean()
        page.add(ft.Text("Historial — próximamente", size=24, color="#4E342E"))
        page.update()

    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("🍽️ Reservas", size=20, weight="bold", color="#FFFFFF"),
                ft.Divider(color="#FFFFFF44"),
                boton_nav(ft.Icons.PEOPLE, "Clientes", ir_clientes),
                boton_nav(ft.Icons.TABLE_RESTAURANT, "Mesas", ir_mesas),
                boton_nav(ft.Icons.BOOK_ONLINE, "Reservas", ir_reservas),
                boton_nav(ft.Icons.HISTORY, "Historial", ir_historial),
                ft.Divider(color="#FFFFFF44"),
                ft.TextButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOGOUT, color="#FFCCBC", size=20),
                            ft.Text("Cerrar sesión", color="#FFCCBC", size=14)
                        ],
                        spacing=10
                    ),
                    on_click=lambda e: cerrar_sesion()
                )
            ],
            spacing=10
        ),
        bgcolor="#6D4C41",
        padding=20,
        width=200,
        expand=False
    )

    contenido = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    f"Bienvenido, {usuario['nombre_admin']} 👋",
                    size=26,
                    weight="bold",
                    color="#4E342E"
                ),
                ft.Text("Panel de Administración", size=14, color="#6D4C41"),
                ft.Divider(),
                ft.Text("Resumen del sistema", size=16, weight="bold", color="#4E342E"),
                ft.Row(
                    controls=[
                        tarjeta_stat(ft.Icons.PEOPLE, "Clientes", total_clientes, "#6D4C41"),
                        tarjeta_stat(ft.Icons.TABLE_RESTAURANT, "Mesas disponibles", mesas_disponibles, "#388E3C"),
                        tarjeta_stat(ft.Icons.TODAY, "Reservas hoy", reservas_hoy, "#1976D2"),
                        tarjeta_stat(ft.Icons.BOOK_ONLINE, "Reservas totales", total_reservas, "#F57C00"),
                    ],
                    spacing=15
                ),
            ],
            spacing=20
        ),
        padding=30,
        expand=True
    )

    return ft.Row(
        controls=[sidebar, contenido],
        expand=True,
        spacing=0
    )
