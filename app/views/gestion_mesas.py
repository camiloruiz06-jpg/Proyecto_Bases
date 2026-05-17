import flet as ft
from data_base.supabase_client import supabase


def vista_gestion_mesas(page: ft.Page, volver_panel, usuario):

    mensaje = ft.Text("", size=13)

    campo_capacidad = ft.TextField(
        label="Capacidad (personas)", width=300, border_radius=10,
        prefix_icon=ft.Icons.PEOPLE, keyboard_type=ft.KeyboardType.NUMBER,
        color="#212121", label_style=ft.TextStyle(color="#4E342E")
    )
    campo_ubicacion = ft.Dropdown(
        label="Ubicación", width=300,
        options=[
            ft.dropdown.Option("Salón Principal"),
            ft.dropdown.Option("Terraza"),
            ft.dropdown.Option("Salón Privado"),
        ]
    )
    campo_estado = ft.Dropdown(
        label="Estado", width=300,
        options=[
            ft.dropdown.Option("disponible"),
            ft.dropdown.Option("ocupada"),
        ],
        value="disponible"
    )
    campo_buscar_id = ft.TextField(
        label="Buscar por ID", width=200, border_radius=10,
        prefix_icon=ft.Icons.SEARCH, keyboard_type=ft.KeyboardType.NUMBER,
        color="#212121", label_style=ft.TextStyle(color="#4E342E")
    )

    mesa_seleccionada = {"id": None}

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Capacidad", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Ubicación", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Estado", weight="bold", color="#212121")),
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

    def cargar_mesas(filtro_id=None):
        if filtro_id:
            resultado = supabase.table("mesas").select("*").eq("id_mesa", filtro_id).execute()
        else:
            resultado = supabase.table("mesas").select("*").execute()
        tabla.rows.clear()
        for m in resultado.data:
            color_estado = "#388E3C" if m["estado"] == "disponible" else "#D32F2F"
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(m["id_mesa"]), color="#212121")),
                    ft.DataCell(ft.Text(str(m["capacidad"]), color="#212121")),
                    ft.DataCell(ft.Text(m.get("ubicacion", "—"), color="#212121")),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(m["estado"], color="#FFFFFF", size=12),
                            bgcolor=color_estado,
                            border_radius=10,
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4)
                        )
                    ),
                    ft.DataCell(
                        ft.Row(controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT, icon_color="#6D4C41", tooltip="Editar",
                                on_click=lambda e, mesa=m: seleccionar_mesa(mesa)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE, icon_color="red", tooltip="Eliminar",
                                on_click=lambda e, mesa=m: confirmar_eliminar(mesa)
                            )
                        ])
                    )
                ])
            )
        page.update()

    def buscar_por_id(e):
        id_texto = campo_buscar_id.value.strip()
        if not id_texto:
            cargar_mesas()
        elif id_texto.isdigit():
            cargar_mesas(filtro_id=int(id_texto))
        else:
            mensaje.value = "El ID debe ser un número."
            mensaje.color = "red"
            page.update()

    def limpiar_busqueda(e):
        campo_buscar_id.value = ""
        cargar_mesas()

    def limpiar_formulario():
        campo_capacidad.value = ""
        campo_ubicacion.value = None
        campo_estado.value = "disponible"
        mesa_seleccionada["id"] = None
        mensaje.value = ""
        boton_guardar.text = "Guardar"
        boton_guardar.style = ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")
        page.update()

    def seleccionar_mesa(m):
        campo_capacidad.value = str(m["capacidad"])
        campo_ubicacion.value = m.get("ubicacion", None)
        campo_estado.value = m["estado"]
        mesa_seleccionada["id"] = m["id_mesa"]
        boton_guardar.text = "Actualizar"
        boton_guardar.style = ft.ButtonStyle(bgcolor="#1976D2", color="#FFFFFF")
        mensaje.value = "Mesa cargada para edición."
        mensaje.color = "#1976D2"
        page.update()

    def guardar_mesa(e):
        capacidad = campo_capacidad.value.strip()
        ubicacion = campo_ubicacion.value
        estado = campo_estado.value

        if not capacidad or not ubicacion:
            mensaje.value = "Capacidad y ubicación son obligatorias."
            mensaje.color = "red"
            page.update()
            return

        if not capacidad.isdigit() or int(capacidad) <= 0:
            mensaje.value = "La capacidad debe ser un número mayor a 0."
            mensaje.color = "red"
            page.update()
            return

        if mesa_seleccionada["id"]:
            supabase.table("mesas").update({
                "capacidad": int(capacidad),
                "ubicacion": ubicacion,
                "estado": estado
            }).eq("id_mesa", mesa_seleccionada["id"]).execute()
            mensaje.value = "Mesa actualizada correctamente."
        else:
            supabase.table("mesas").insert({
                "capacidad": int(capacidad),
                "ubicacion": ubicacion,
                "estado": estado
            }).execute()
            mensaje.value = "Mesa registrada correctamente."

        mensaje.color = "green"
        limpiar_formulario()
        cargar_mesas()

    def confirmar_eliminar(m):
        def eliminar(e):
            dialogo.open = False
            page.update()
            supabase.table("mesas").delete().eq("id_mesa", m["id_mesa"]).execute()
            mensaje.value = f"Mesa {m['id_mesa']} eliminada."
            mensaje.color = "green"
            cargar_mesas()

        def cancelar(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Eliminar mesa?", color="red", weight="bold"),
            content=ft.Text(f"¿Seguro que deseas eliminar la mesa {m['id_mesa']}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.FilledButton("Eliminar", on_click=eliminar,
                    style=ft.ButtonStyle(bgcolor="red", color="#FFFFFF"))
            ],
            actions_alignment="center"
        )
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    boton_guardar = ft.FilledButton(
        "Guardar", on_click=guardar_mesa,
        style=ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")
    )
    boton_limpiar = ft.OutlinedButton("Limpiar", on_click=lambda e: limpiar_formulario())

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Registro / Edición de Mesa", size=16, weight="bold", color="#4E342E"),
                campo_capacidad, campo_ubicacion, campo_estado,
                mensaje,
                ft.Row(controls=[boton_guardar, boton_limpiar], spacing=10)
            ],
            spacing=15
        ),
        bgcolor="#FFFFFF", padding=20, border_radius=15, width=360,
        shadow=ft.BoxShadow(blur_radius=8, color="#00000022")
    )

    contenido = ft.Column(
        controls=[
            ft.Row(controls=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_panel(),
                    tooltip="Volver al panel"),
                ft.Text("Gestión de Mesas", size=24, weight="bold", color="#4E342E")
            ]),
            formulario,
            ft.Text("Listado de Mesas", size=16, weight="bold", color="#4E342E"),
            ft.Row(controls=[
                campo_buscar_id,
                ft.FilledButton("Buscar", on_click=buscar_por_id,
                    style=ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")),
                ft.OutlinedButton("Ver todos", on_click=limpiar_busqueda)
            ], spacing=10),
            ft.Container(content=tabla, bgcolor="#FFFFFF", border_radius=10, padding=10)
        ],
        spacing=20, scroll="auto", expand=True
    )

    cargar_mesas()
    return ft.Container(content=contenido, padding=30, expand=True)