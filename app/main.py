import flet as ft
from views.login import vista_login
from views.registro import vista_registro
from views.panel_admin import vista_panel_admin


def main(page: ft.Page):

    page.title = "Sistema de Reservas"
    page.window_width = 900
    page.window_height = 700
    page.bgcolor = "#F5F1E8"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    def mostrar_login():
        page.clean()
        page.add(vista_login(page, mostrar_registro, ir_panel_admin, ir_menu_cliente))

    def mostrar_registro():
        page.clean()
        page.add(vista_registro(page, mostrar_login))

    def ir_panel_admin(usuario):
        page.clean()
        page.add(vista_panel_admin(page, usuario, mostrar_login))
        page.update()

    def ir_menu_cliente(usuario):
        page.clean()
        page.add(ft.Text(
            f"Bienvenido, {usuario['nombre_cliente']}",
            size=24,
            color="#4E342E"
        ))
        page.update()

    mostrar_login()


ft.run(main)