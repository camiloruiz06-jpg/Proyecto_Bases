import flet as ft
from views.login import vista_login
from views.registro import vista_registro
from views.panel_admin import vista_panel_admin
from views.menu_cliente import vista_menu_cliente


def main(page: ft.Page):

    page.title = "Sistema de Reservas"
    page.window_width = 900
    page.window_height = 700
    page.bgcolor = "#F5F1E8"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    def mostrar_login():
        page.clean()
        page.bgcolor = "#F5F1E8"
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        page.add(vista_login(page, mostrar_registro, ir_panel_admin, ir_menu_cliente))
        page.update()

    def mostrar_registro():
        page.clean()
        page.bgcolor = "#F5F1E8"
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        page.add(vista_registro(page, mostrar_login))
        page.update()

    def ir_panel_admin(usuario):
        page.clean()
        page.bgcolor = "#F5F1E8"
        page.horizontal_alignment = "start"
        page.vertical_alignment = "start"
        page.add(vista_panel_admin(page, usuario, mostrar_login))
        page.update()

    def ir_menu_cliente(usuario):
        page.clean()
        page.bgcolor = "#1A1A2E"
        page.horizontal_alignment = "start"
        page.vertical_alignment = "start"
        page.add(vista_menu_cliente(page, usuario, mostrar_login))
        page.update()

    mostrar_login()


ft.run(main)