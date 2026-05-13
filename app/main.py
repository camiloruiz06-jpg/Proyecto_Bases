import flet as ft

from views.login import vista_login


def main(page: ft.Page):

    page.title = "Sistema de Reservas"
    page.window_width = 900
    page.window_height = 700
    page.bgcolor = "#F5F1E8"

    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    page.add(
        vista_login(page)
    )


ft.run(main)