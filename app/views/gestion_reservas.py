import flet as ft
from data_base.supabase_client import supabase
from datetime import date, datetime


def vista_gestion_reservas(page: ft.Page, volver_panel, usuario):

    mensaje = ft.Text("", size=13)

    campo_fecha = ft.TextField(
        label="Fecha (YYYY-MM-DD)", hint_text=str(date.today()),
        width=300, border_radius=10,
        prefix_icon=ft.Icons.CALENDAR_TODAY,
        color="#212121", label_style=ft.TextStyle(color="#4E342E")
    )
    campo_hora = ft.TextField(
        label="Hora (HH:MM)", hint_text="19:00",
        width=300, border_radius=10,
        prefix_icon=ft.Icons.ACCESS_TIME,
        color="#212121", label_style=ft.TextStyle(color="#4E342E")
    )
    campo_personas = ft.TextField(
        label="Número de personas",
        width=300, border_radius=10,
        prefix_icon=ft.Icons.PEOPLE,
        keyboard_type=ft.KeyboardType.NUMBER,
        color="#212121", label_style=ft.TextStyle(color="#4E342E")
    )
    dropdown_cliente = ft.Dropdown(label="Cliente", width=300, options=[])
    dropdown_mesa = ft.Dropdown(label="Mesa", width=300, options=[])
    dropdown_estado = ft.Dropdown(
        label="Estado", width=300,
        options=[
            ft.dropdown.Option("confirmada"),
            ft.dropdown.Option("cancelada"),
        ],
        value="confirmada"
    )

    reserva_seleccionada = {"id": None}

    def cargar_dropdowns():
        clientes = supabase.table("clientes").select("id_cliente, nombre_cliente").execute()
        dropdown_cliente.options = [
            ft.dropdown.Option(key=str(c["id_cliente"]), text=c["nombre_cliente"])
            for c in clientes.data
        ]
        mesas = supabase.table("mesas").select("id_mesa, capacidad, ubicacion").execute()
        dropdown_mesa.options = [
            ft.dropdown.Option(
                key=str(m["id_mesa"]),
                text=f"Mesa {m['id_mesa']} — {m.get('ubicacion', '?')} ({m['capacidad']} personas)"
            )
            for m in mesas.data
        ]
        page.update()

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Cliente", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Mesa", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Fecha", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Hora", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Personas", weight="bold", color="#212121")),
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

    def cargar_reservas():
        resultado = supabase.table("reservas").select(
            "*, clientes(nombre_cliente), mesas(ubicacion)"
        ).execute()
        tabla.rows.clear()
        for r in resultado.data:
            color_estado = "#388E3C" if r["estado_reserva"] == "confirmada" else "#D32F2F"
            nombre_cliente = r["clientes"]["nombre_cliente"] if r.get("clientes") else "—"
            ubicacion = r["mesas"]["ubicacion"] if r.get("mesas") else "—"
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r["id_reservas"]), color="#212121")),
                    ft.DataCell(ft.Text(nombre_cliente, color="#212121")),
                    ft.DataCell(ft.Text(f"Mesa {r['id_mesa']} - {ubicacion}", color="#212121")),
                    ft.DataCell(ft.Text(str(r["fecha"]), color="#212121")),
                    ft.DataCell(ft.Text(str(r["hora"]), color="#212121")),
                    ft.DataCell(ft.Text(str(r["numero_personas"]), color="#212121")),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(r["estado_reserva"], color="#FFFFFF", size=12),
                            bgcolor=color_estado,
                            border_radius=10,
                            padding=ft.Padding(left=10, right=10, top=4, bottom=4)
                        )
                    ),
                    ft.DataCell(
                        ft.Row(controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT, icon_color="#6D4C41", tooltip="Editar",
                                on_click=lambda e, res=r: seleccionar_reserva(res)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CANCEL, icon_color="red", tooltip="Cancelar",
                                on_click=lambda e, res=r: cancelar_reserva(res)
                            )
                        ])
                    )
                ])
            )
        page.update()

    def limpiar_formulario():
        campo_fecha.value = ""
        campo_hora.value = ""
        campo_personas.value = ""
        dropdown_cliente.value = None
        dropdown_mesa.value = None
        dropdown_estado.value = "confirmada"
        reserva_seleccionada["id"] = None
        mensaje.value = ""
        boton_guardar.text = "Guardar"
        boton_guardar.style = ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")
        page.update()

    def seleccionar_reserva(r):
        campo_fecha.value = str(r["fecha"])
        campo_hora.value = str(r["hora"])
        campo_personas.value = str(r["numero_personas"])
        dropdown_cliente.value = str(r["id_cliente"])
        dropdown_mesa.value = str(r["id_mesa"])
        dropdown_estado.value = r["estado_reserva"]
        reserva_seleccionada["id"] = r["id_reservas"]
        boton_guardar.text = "Actualizar"
        boton_guardar.style = ft.ButtonStyle(bgcolor="#1976D2", color="#FFFFFF")
        mensaje.value = "Reserva cargada para edición."
        mensaje.color = "#1976D2"
        page.update()

    def validar_fecha_hora(fecha, hora):
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            mensaje.value = "Fecha inválida. Usa YYYY-MM-DD (ej: 2026-05-17)"
            mensaje.color = "red"
            page.update()
            return False
        try:
            datetime.strptime(hora, "%H:%M")
        except ValueError:
            mensaje.value = "Hora inválida. Usa HH:MM (ej: 19:00)"
            mensaje.color = "red"
            page.update()
            return False
        return True

    def guardar_reserva(e):
        fecha = campo_fecha.value.strip()
        hora = campo_hora.value.strip()
        personas = campo_personas.value.strip()
        id_cliente = dropdown_cliente.value
        id_mesa = dropdown_mesa.value
        estado = dropdown_estado.value

        if not fecha or not hora or not personas or not id_cliente or not id_mesa:
            mensaje.value = "Todos los campos son obligatorios."
            mensaje.color = "red"
            page.update()
            return

        if not personas.isdigit() or int(personas) <= 0:
            mensaje.value = "El número de personas debe ser mayor a 0."
            mensaje.color = "red"
            page.update()
            return

        if not validar_fecha_hora(fecha, hora):
            return

        try:
            if reserva_seleccionada["id"]:
                ocupada = supabase.table("reservas").select("id_reservas")\
                    .eq("id_mesa", int(id_mesa))\
                    .eq("fecha", fecha)\
                    .eq("hora", hora)\
                    .eq("estado_reserva", "confirmada")\
                    .neq("id_reservas", reserva_seleccionada["id"])\
                    .execute()

                if ocupada.data:
                    mensaje.value = "Esa mesa ya está reservada para esa fecha y hora."
                    mensaje.color = "red"
                    page.update()
                    return

                supabase.table("reservas").update({
                    "fecha": fecha,
                    "hora": hora,
                    "numero_personas": int(personas),
                    "id_cliente": int(id_cliente),
                    "id_mesa": int(id_mesa),
                    "estado_reserva": estado
                }).eq("id_reservas", reserva_seleccionada["id"]).execute()
                mensaje.value = "Reserva actualizada correctamente."

            else:
                ocupada = supabase.table("reservas").select("id_reservas")\
                    .eq("id_mesa", int(id_mesa))\
                    .eq("fecha", fecha)\
                    .eq("hora", hora)\
                    .eq("estado_reserva", "confirmada")\
                    .execute()

                if ocupada.data:
                    mensaje.value = "Esa mesa ya está reservada para esa fecha y hora."
                    mensaje.color = "red"
                    page.update()
                    return

                supabase.table("reservas").insert({
                    "fecha": fecha,
                    "hora": hora,
                    "numero_personas": int(personas),
                    "id_cliente": int(id_cliente),
                    "id_mesa": int(id_mesa),
                    "estado_reserva": estado
                }).execute()
                mensaje.value = "Reserva creada correctamente."

            mensaje.color = "green"
            limpiar_formulario()
            cargar_reservas()

        except Exception as ex:
            if "23505" in str(ex):
                mensaje.value = "Esa mesa ya está reservada para esa fecha y hora."
            else:
                mensaje.value = "Error al guardar. Intenta de nuevo."
            mensaje.color = "red"
            page.update()

    def cancelar_reserva(r):
        def confirmar(e):
            dialogo.open = False
            page.update()
            supabase.table("reservas").update(
                {"estado_reserva": "cancelada"}
            ).eq("id_reservas", r["id_reservas"]).execute()
            mensaje.value = "Reserva cancelada."
            mensaje.color = "green"
            cargar_reservas()

        def cerrar(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Cancelar reserva?", color="red", weight="bold"),
            content=ft.Text("¿Seguro que deseas cancelar esta reserva?"),
            actions=[
                ft.TextButton("No", on_click=cerrar),
                ft.FilledButton("Sí, cancelar", on_click=confirmar,
                    style=ft.ButtonStyle(bgcolor="red", color="#FFFFFF"))
            ],
            actions_alignment="center"
        )
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    boton_guardar = ft.FilledButton(
        "Guardar", on_click=guardar_reserva,
        style=ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")
    )
    boton_limpiar = ft.OutlinedButton("Limpiar", on_click=lambda e: limpiar_formulario())

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Nueva / Editar Reserva", size=16, weight="bold", color="#4E342E"),
                dropdown_cliente, dropdown_mesa,
                campo_fecha, campo_hora, campo_personas,
                dropdown_estado, mensaje,
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
                ft.Text("Gestión de Reservas", size=24, weight="bold", color="#4E342E")
            ]),
            formulario,
            ft.Text("Listado de Reservas", size=16, weight="bold", color="#4E342E"),
            ft.Container(content=tabla, bgcolor="#FFFFFF", border_radius=10, padding=10)
        ],
        spacing=20, scroll="auto", expand=True
    )

    cargar_dropdowns()
    cargar_reservas()

    return ft.Container(content=contenido, padding=30, expand=True)