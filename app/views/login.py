import flet as ft


def vista_login(page: ft.Page):

    titulo = ft.Text(
        "Sistema de Reservas",
        size=32,
        weight="bold",
        color="#4E342E"
    )

    subtitulo = ft.Text(
        "Iniciar Sesión",
        size=20,
        color="#6D4C41"
    )

    campo_correo = ft.TextField(
        label="Correo electrónico",
        width=350,
        border_radius=10,
        prefix_icon=ft.Icons.EMAIL
    )

    campo_contrasena = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=350,
        border_radius=10,
        prefix_icon=ft.Icons.LOCK
    )

    boton_login = ft.ElevatedButton(
            "Iniciar Sesión",
        width=350,
        height=50,
        style=ft.ButtonStyle(
            bgcolor="#6D4C41",
            color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    boton_registro = ft.TextButton(
        "¿No tienes cuenta? Registrarse"
    )

    contenedor = ft.Container(
        content=ft.Column(
            controls=[
                titulo,
                subtitulo,
                campo_correo,
                campo_contrasena,
                boton_login,
                boton_registro
            ],
            horizontal_alignment="center",
            spacing=20
        ),
        bgcolor="#FFFFFF",
        padding=40,
        border_radius=20,
        width=450
    )

    return contenedor