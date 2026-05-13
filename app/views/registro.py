import flet as ft
import hashlib
from data_base.supabase_client import supabase


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def vista_registro(page: ft.Page, ir_login):

    mensaje_estado = ft.Text("", size=13)

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
        label="Teléfono (opcional)",
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

    campo_confirmar = ft.TextField(
        label="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        width=350,
        border_radius=10,
        prefix_icon=ft.Icons.LOCK_OUTLINE
    )

    def registrar(e):
        nombre = campo_nombre.value.strip()
        correo = campo_correo.value.strip()
        telefono = campo_telefono.value.strip() or None
        contrasena = campo_contrasena.value.strip()
        confirmar = campo_confirmar.value.strip()

        if not nombre or not correo or not contrasena or not confirmar:
            mensaje_estado.value = "Completa todos los campos obligatorios."
            mensaje_estado.color = "red"
            page.update()
            return

        if "@" not in correo or "." not in correo.split("@")[-1]:
            mensaje_estado.value = "Ingresa un correo electrónico válido."
            mensaje_estado.color = "red"
            page.update()
            return

        if contrasena != confirmar:
            mensaje_estado.value = "Las contraseñas no coinciden."
            mensaje_estado.color = "red"
            page.update()
            return

        if len(contrasena) < 6:
            mensaje_estado.value = "La contraseña debe tener al menos 6 caracteres."
            mensaje_estado.color = "red"
            page.update()
            return

        existente = (
            supabase.table("clientes")
            .select("id_cliente")
            .eq("correo", correo)
            .execute()
        )

        if existente.data:
            mensaje_estado.value = "Este correo ya está registrado."
            mensaje_estado.color = "red"
            page.update()
            return

        nuevo_cliente = {
            "nombre_cliente": nombre,
            "correo": correo,
            "telefono": telefono,
            "contrasena": hash_password(contrasena)
        }

        resultado = supabase.table("clientes").insert(nuevo_cliente).execute()

        if resultado.data:
            def cerrar_dialogo(e):
                dialogo.open = False
                page.update()
                ir_login()

            dialogo = ft.AlertDialog(
                modal=True,
                title=ft.Text("¡Registro exitoso!", color="#4E342E", weight="bold"),
                content=ft.Text("Tu cuenta ha sido creada. Ahora puedes iniciar sesión."),
                actions=[
                    ft.FilledButton(
                        "Ir al Login",
                        on_click=cerrar_dialogo,
                        style=ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")
                    )
                ],
                actions_alignment="center"
            )

            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()
        else:
            mensaje_estado.value = "Error al registrar. Intenta de nuevo."
            mensaje_estado.color = "red"
            page.update()

    boton_registro = ft.FilledButton(
        "Registrarse",
        width=350,
        height=50,
        on_click=registrar,
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
                campo_confirmar,
                mensaje_estado,
                boton_registro,
                boton_volver
            ],
            horizontal_alignment="center",
            spacing=20,
            scroll="auto"
        ),
        bgcolor="#FFFFFF",
        padding=40,
        border_radius=20,
        width=450
    )

    return contenedor