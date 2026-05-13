import flet as ft

from views.login import vista_login
from views.registro import vista_registro


def main(page: ft.Page):

    page.title = "Sistema de Reservas"
    page.window_width = 900
    page.window_height = 700
    page.bgcolor = "#F5F1E8"

    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # FUNCION PARA IR AL LOGIN
    def mostrar_login():

        page.clean()

        page.add(
            vista_login(page, mostrar_registro)
        )

    # FUNCION PARA IR AL REGISTRO
    def mostrar_registro():

        page.clean()

        page.add(
            vista_registro(page, mostrar_login)
        )

    # INICIAR EN LOGIN
    mostrar_login()


ft.run(main)