import flet as ft
import hashlib
from data_base.supabase_client import supabase


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def vista_registro(page: ft.Page, ir_login):

    mensaje_estado = ft.Text("", size=13)

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

        # Validar teléfono
        if telefono:
            if not telefono.isdigit():
                mensaje_estado.value = "El teléfono solo puede contener números."
                mensaje_estado.color = "red"
                page.update()
                return
            if len(telefono) != 10:
                mensaje_estado.value = "El teléfono debe tener exactamente 10 dígitos."
                mensaje_estado.color = "red"
                page.update()
                return

        # Verificar correo duplicado
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

        # Verificar teléfono duplicado
        if telefono:
            tel_existente = (
                supabase.table("clientes")
                .select("id_cliente")
                .eq("telefono", telefono)
                .execute()
            )
            if tel_existente.data:
                mensaje_estado.value = "Este teléfono ya está registrado."
                mensaje_estado.color = "red"
                page.update()
                return

        try:
            resultado = supabase.table("clientes").insert({
                "nombre_cliente": nombre,
                "correo": correo,
                "telefono": telefono,
                "contrasena": hash_password(contrasena)
            }).execute()

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

        except Exception as ex:
            if "23505" in str(ex):
                mensaje_estado.value = "El correo o teléfono ya está registrado."
            else:
                mensaje_estado.value = "Error al registrar. Intenta de nuevo."
            mensaje_estado.color = "red"
            page.update()

    campo_nombre = ft.TextField(
        label="Nombre completo",
        width=350, border_radius=10,
        prefix_icon=ft.Icons.PERSON,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )
    campo_correo = ft.TextField(
        label="Correo electrónico",
        width=350, border_radius=10,
        prefix_icon=ft.Icons.EMAIL,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )
    campo_telefono = ft.TextField(
        label="Teléfono (opcional)",
        width=350, border_radius=10,
        prefix_icon=ft.Icons.PHONE,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )
    campo_contrasena = ft.TextField(
        label="Contraseña",
        password=True, can_reveal_password=True,
        width=350, border_radius=10,
        prefix_icon=ft.Icons.LOCK,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )
    campo_confirmar = ft.TextField(
        label="Confirmar contraseña",
        password=True, can_reveal_password=True,
        width=350, border_radius=10,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )

    boton_registro = ft.FilledButton(
        "Registrarse",
        width=350, height=50,
        on_click=registrar,
        style=ft.ButtonStyle(
            bgcolor="#6D4C41", color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    boton_volver = ft.TextButton(
        "Volver al login",
        on_click=lambda e: ir_login()
    )

    boton_volver_top = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        tooltip="Volver al login",
        on_click=lambda e: ir_login(),
        icon_color="#6D4C41"
    )

    contenedor = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Crear Cuenta",
                            size=32, weight="bold",
                            color="#4E342E", expand=True
                        ),
                        boton_volver_top
                    ],
                    alignment="spaceBetween"
                ),
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