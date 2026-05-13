import flet as ft

def vista_registro(page: ft.Page, ir_login):

    titulo = ft.Text(
        "Crear Cuenta",
        size=32,
        weight="bold",
        color="#4E342E"
    )

    campo_nombre = ft.TextField(
        label="Nombre completo",
        width=350,
        border_radius=10,
        prefix_icon=ft.Icons.PERSON
    )

    campo_correo = ft.TextField(
        label="Correo electrónico",
        width=350,
        border_radius=10,
        prefix_icon=ft.Icons.EMAIL
    )

    campo_telefono = ft.TextField(
        label="Teléfono",
        width=350,
        border_radius=10,
        prefix_icon=ft.Icons.PHONE
    )

    campo_contrasena = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=350,
        border_radius=10,
        prefix_icon=ft.Icons.LOCK
    )

    boton_registro = ft.ElevatedButton(
        "Registrarse",
        width=350,
        height=50,
        style=ft.ButtonStyle(
            bgcolor="#6D4C41",
            color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    boton_volver = ft.TextButton(
        "Volver al login",
        on_click=lambda e: ir_login()
    )

    contenedor = ft.Container(
        content=ft.Column(
            controls=[
                titulo,
                campo_nombre,
                campo_correo,
                campo_telefono,
                campo_contrasena,
                boton_registro,
                boton_volver
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