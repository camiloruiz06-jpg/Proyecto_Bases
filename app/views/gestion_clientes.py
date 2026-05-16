import flet as ft
import hashlib
from data_base.supabase_client import supabase


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def vista_gestion_clientes(page: ft.Page, volver_panel, usuario):

    mensaje = ft.Text("", size=13)

    campo_nombre = ft.TextField(label="Nombre completo", width=300, border_radius=10, prefix_icon=ft.Icons.PERSON)
    campo_correo = ft.TextField(label="Correo electrónico", width=300, border_radius=10, prefix_icon=ft.Icons.EMAIL)
    campo_telefono = ft.TextField(label="Teléfono (opcional)", width=300, border_radius=10, prefix_icon=ft.Icons.PHONE)
    campo_contrasena = ft.TextField(
        label="Contraseña (dejar vacío para no cambiar)",
        password=True,
        can_reveal_password=True,
        width=300,
        border_radius=10,
        prefix_icon=ft.Icons.LOCK
    )

    cliente_seleccionado = {"id": None}

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Nombre", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Correo", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Teléfono", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Acciones", weight="bold", color="#212121")),
        ],
        rows=[],
        border=ft.Border(
            top=ft.BorderSide(1, "#E0E0E0"),
            bottom=ft.BorderSide(1, "#E0E0E0"),
            left=ft.BorderSide(1, "#E0E0E0"),
            right=ft.BorderSide(1, "#E0E0E0")
        ),
        border_radius=10,
        heading_row_color="#F5F1E8"
    )

    def cargar_clientes():
        resultado = supabase.table("clientes").select("*").execute()
        tabla.rows.clear()
        for c in resultado.data:
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(c["id_cliente"]), color="#212121")),
                        ft.DataCell(ft.Text(c["nombre_cliente"], color="#212121")),
                        ft.DataCell(ft.Text(c["correo"], color="#212121")),
                        ft.DataCell(ft.Text(c["telefono"] or "—", color="#212121")),
                        ft.DataCell(
                            ft.Row(controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color="#6D4C41",
                                    tooltip="Editar",
                                    on_click=lambda e, cli=c: seleccionar_cliente(cli)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color="red",
                                    tooltip="Eliminar",
                                    on_click=lambda e, cli=c: confirmar_eliminar(cli)
                                )
                            ])
                        )
                    ]
                )
            )
        page.update()

    def limpiar_formulario():
        campo_nombre.value = ""
        campo_correo.value = ""
        campo_telefono.value = ""
        campo_contrasena.value = ""
        cliente_seleccionado["id"] = None
        mensaje.value = ""
        boton_guardar.text = "Guardar"
        boton_guardar.style = ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")
        page.update()

    def seleccionar_cliente(c):
        campo_nombre.value = c["nombre_cliente"]
        campo_correo.value = c["correo"]
        campo_telefono.value = c["telefono"] or ""
        campo_contrasena.value = ""
        cliente_seleccionado["id"] = c["id_cliente"]
        boton_guardar.text = "Actualizar"
        boton_guardar.style = ft.ButtonStyle(bgcolor="#1976D2", color="#FFFFFF")
        mensaje.value = "Cliente cargado para edición."
        mensaje.color = "#1976D2"
        page.update()

    def guardar_cliente(e):
        nombre = campo_nombre.value.strip()
        correo = campo_correo.value.strip()
        telefono = campo_telefono.value.strip() or None
        contrasena = campo_contrasena.value.strip()

        if not nombre or not correo:
            mensaje.value = "Nombre y correo son obligatorios."
            mensaje.color = "red"
            page.update()
            return

        if "@" not in correo or "." not in correo.split("@")[-1]:
            mensaje.value = "Correo no válido."
            mensaje.color = "red"
            page.update()
            return

        if cliente_seleccionado["id"]:
            # Actualizar
            datos = {
                "nombre_cliente": nombre,
                "correo": correo,
                "telefono": telefono
            }
            if contrasena:
                datos["contrasena"] = hash_password(contrasena)

            supabase.table("clientes").update(datos).eq("id_cliente", cliente_seleccionado["id"]).execute()
            mensaje.value = "Cliente actualizado correctamente."
        else:
            # Nuevo cliente
            if not contrasena:
                mensaje.value = "La contraseña es obligatoria."
                mensaje.color = "red"
                page.update()
                return

            existente = supabase.table("clientes").select("id_cliente").eq("correo", correo).execute()
            if existente.data:
                mensaje.value = "Este correo ya está registrado."
                mensaje.color = "red"
                page.update()
                return

            supabase.table("clientes").insert({
                "nombre_cliente": nombre,
                "correo": correo,
                "telefono": telefono,
                "contrasena": hash_password(contrasena)
            }).execute()
            mensaje.value = "Cliente registrado correctamente."

        mensaje.color = "green"
        limpiar_formulario()
        cargar_clientes()

    def confirmar_eliminar(c):
        def eliminar(e):
            dialogo.open = False
            page.update()
            supabase.table("clientes").delete().eq("id_cliente", c["id_cliente"]).execute()
            mensaje.value = f"Cliente {c['nombre_cliente']} eliminado."
            mensaje.color = "green"
            cargar_clientes()

        def cancelar(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Eliminar cliente?", color="red", weight="bold"),
            content=ft.Text(f"¿Seguro que deseas eliminar a {c['nombre_cliente']}? También se eliminarán sus reservas."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.FilledButton(
                    "Eliminar",
                    on_click=eliminar,
                    style=ft.ButtonStyle(bgcolor="red", color="#FFFFFF")
                )
            ],
            actions_alignment="center"
        )
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    boton_guardar = ft.FilledButton(
        "Guardar",
        on_click=guardar_cliente,
        style=ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")
    )

    boton_limpiar = ft.OutlinedButton(
        "Limpiar",
        on_click=lambda e: limpiar_formulario()
    )

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Registro / Edición de Cliente", size=16, weight="bold", color="#4E342E"),
                campo_nombre,
                campo_correo,
                campo_telefono,
                campo_contrasena,
                mensaje,
                ft.Row(controls=[boton_guardar, boton_limpiar], spacing=10)
            ],
            spacing=15
        ),
        bgcolor="#FFFFFF",
        padding=20,
        border_radius=15,
        width=360,
        shadow=ft.BoxShadow(blur_radius=8, color="#00000022")
    )

    contenido = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: volver_panel(),
                        tooltip="Volver al panel"
                    ),
                    ft.Text("Gestión de Clientes", size=24, weight="bold", color="#4E342E")
                ]
            ),
            formulario,
            ft.Text("Listado de Clientes", size=16, weight="bold", color="#4E342E"),
            ft.Container(
                content=tabla,
                bgcolor="#FFFFFF",
                border_radius=10,
                padding=10
            )
        ],
        spacing=20,
        scroll="auto",
        expand=True
    )

    cargar_clientes()

    return ft.Container(content=contenido, padding=30, expand=True)