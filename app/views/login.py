import flet as ft
import hashlib
from data_base.supabase_client import supabase


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def vista_login(page: ft.Page, ir_registro, ir_panel_admin, ir_menu_cliente):

    mensaje_error = ft.Text("", color="red", size=13)

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

    def iniciar_sesion(e):
        correo = campo_correo.value.strip()
        contrasena = campo_contrasena.value.strip()

        if not correo or not contrasena:
            mensaje_error.value = "Por favor completa todos los campos."
            page.update()
            return

        contrasena_hash = hash_password(contrasena)

        # Buscar en administradores
        resultado_admin = (
            supabase.table("administradores")
            .select("*")
            .eq("correo", correo)
            .eq("contrasena", contrasena_hash)
            .execute()
        )

        if resultado_admin.data:
            ir_panel_admin(resultado_admin.data[0])
            return

        # Buscar en clientes
        resultado_cliente = (
            supabase.table("clientes")
            .select("*")
            .eq("correo", correo)
            .eq("contrasena", contrasena_hash)
            .execute()
        )

        if resultado_cliente.data:
            ir_menu_cliente(resultado_cliente.data[0])
            return

        mensaje_error.value = "Correo o contraseña incorrectos."
        page.update()

    boton_login = ft.FilledButton(
        "Iniciar Sesión",
        width=350,
        height=50,
        on_click=iniciar_sesion,
        style=ft.ButtonStyle(
            bgcolor="#6D4C41",
            color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    boton_registro = ft.TextButton(
        "¿No tienes cuenta? Registrarse",
        on_click=lambda e: ir_registro()
    )

    contenedor = ft.Container(
        content=ft.Column(
            controls=[
                titulo,
                subtitulo,
                campo_correo,
                campo_contrasena,
                mensaje_error,
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