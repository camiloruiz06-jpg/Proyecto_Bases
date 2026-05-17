import flet as ft
from data_base.supabase_client import supabase
from datetime import date, datetime


def vista_menu_cliente(page: ft.Page, usuario, cerrar_sesion):

    BG_MAIN = "#F5F1E8"
    BG_CARD = "#FFFFFF"
    PRIMARY = "#6D4C41"
    PRIMARY_DARK = "#4E342E"
    ACCENT = "#A1887F"
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#6D4C41"
    SUCCESS = "#388E3C"
    ERROR = "#D32F2F"

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    hoy = date.today()
    fecha_texto = f"{dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"

    def limpiar_contenido():
        page.clean()
        page.bgcolor = BG_MAIN
        page.add(construir_layout())
        page.update()

    def tarjeta_accion(icono, titulo, descripcion, color, accion):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(icono, color="#FFFFFF", size=32),
                        bgcolor=color,
                        border_radius=50,
                        width=65,
                        height=65,
                        alignment=ft.Alignment(0, 0)
                    ),
                    ft.Text(titulo, size=16, weight="bold", color=PRIMARY_DARK),
                    ft.Text(descripcion, size=12, color=TEXT_SECONDARY, text_align="center")
                ],
                horizontal_alignment="center",
                spacing=12
            ),
            bgcolor=BG_CARD,
            padding=25,
            border_radius=20,
            width=220,
            height=210,
            ink=True,
            on_click=accion,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000022")
        )

    # ========= NUEVA RESERVA =========
    def mostrar_hacer_reserva(e=None):

        campo_fecha = ft.TextField(
            label="Fecha (YYYY-MM-DD)", hint_text=str(hoy),
            width=320, border_radius=10, color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=PRIMARY),
            border_color=ACCENT, focused_border_color=PRIMARY
        )
        campo_hora = ft.TextField(
            label="Hora (HH:MM)", hint_text="19:00",
            width=320, border_radius=10, color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=PRIMARY),
            border_color=ACCENT, focused_border_color=PRIMARY
        )
        campo_personas = ft.TextField(
            label="Número de personas",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=320, border_radius=10, color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=PRIMARY),
            border_color=ACCENT, focused_border_color=PRIMARY
        )
        dropdown_mesa = ft.Dropdown(
            label="Mesa disponible", width=320,
            options=[], label_style=ft.TextStyle(color=PRIMARY)
        )
        mensaje = ft.Text("", size=13)

        def validar_fecha_hora(fecha, hora):
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                mensaje.value = "Fecha inválida. Usa YYYY-MM-DD (ej: 2026-05-17)"
                mensaje.color = ERROR
                page.update()
                return False
            try:
                datetime.strptime(hora, "%H:%M")
            except ValueError:
                mensaje.value = "Hora inválida. Usa HH:MM (ej: 19:00)"
                mensaje.color = ERROR
                page.update()
                return False
            return True

        def buscar_mesas(e):
            personas = campo_personas.value.strip()
            fecha = campo_fecha.value.strip()
            hora = campo_hora.value.strip()

            if not personas or not fecha or not hora:
                mensaje.value = "Completa todos los campos."
                mensaje.color = ERROR
                page.update()
                return

            if not personas.isdigit() or int(personas) <= 0:
                mensaje.value = "Número inválido."
                mensaje.color = ERROR
                page.update()
                return

            if not validar_fecha_hora(fecha, hora):
                return

            todas = supabase.table("mesas").select("*").gte("capacidad", int(personas)).execute()
            ocupadas = supabase.table("reservas").select("id_mesa")\
                .eq("fecha", fecha).eq("hora", hora)\
                .eq("estado_reserva", "confirmada").execute()

            ids_ocupadas = [r["id_mesa"] for r in ocupadas.data]
            disponibles = [m for m in todas.data if m["id_mesa"] not in ids_ocupadas]

            if not disponibles:
                mensaje.value = "No hay mesas disponibles."
                mensaje.color = ERROR
                dropdown_mesa.options = []
            else:
                dropdown_mesa.options = [
                    ft.dropdown.Option(
                        key=str(m["id_mesa"]),
                        text=f"Mesa {m['id_mesa']} - {m.get('ubicacion', '?')} ({m['capacidad']} personas)"
                    )
                    for m in disponibles
                ]
                mensaje.value = f"{len(disponibles)} mesa(s) disponible(s)."
                mensaje.color = SUCCESS
            page.update()

        def confirmar_reserva(e):
            fecha = campo_fecha.value.strip()
            hora = campo_hora.value.strip()
            personas = campo_personas.value.strip()
            id_mesa = dropdown_mesa.value

            if not fecha or not hora or not personas or not id_mesa:
                mensaje.value = "Completa todos los campos."
                mensaje.color = ERROR
                page.update()
                return

            if not validar_fecha_hora(fecha, hora):
                return

            supabase.table("reservas").insert({
                "id_cliente": usuario["id_cliente"],
                "id_mesa": int(id_mesa),
                "fecha": fecha,
                "hora": hora,
                "numero_personas": int(personas),
                "estado_reserva": "confirmada"
            }).execute()

            def cerrar(e):
                dialogo.open = False
                page.update()
                limpiar_contenido()

            dialogo = ft.AlertDialog(
                modal=True,
                title=ft.Text("¡Reserva confirmada!", color=SUCCESS, weight="bold"),
                content=ft.Text(f"Tu mesa fue reservada para el {fecha} a las {hora}."),
                actions=[
                    ft.FilledButton("Perfecto", on_click=cerrar,
                        style=ft.ButtonStyle(bgcolor=PRIMARY, color="#FFFFFF"))
                ],
                actions_alignment="center"
            )
            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()

        vista = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=PRIMARY,
                            on_click=lambda e: limpiar_contenido()),
                        ft.Text("Nueva Reserva", size=24, weight="bold", color=PRIMARY_DARK)
                    ]),
                    campo_fecha, campo_hora, campo_personas,
                    ft.FilledButton("Buscar mesas disponibles", on_click=buscar_mesas,
                        style=ft.ButtonStyle(bgcolor=PRIMARY, color="#FFFFFF")),
                    dropdown_mesa,
                    mensaje,
                    ft.FilledButton("Confirmar Reserva", on_click=confirmar_reserva,
                        style=ft.ButtonStyle(bgcolor=PRIMARY_DARK, color="#FFFFFF"))
                ],
                spacing=18, scroll="auto"
            ),
            bgcolor=BG_CARD, padding=30, border_radius=20, width=420,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000022")
        )

        page.clean()
        page.bgcolor = BG_MAIN
        page.add(ft.Container(content=vista, alignment=ft.Alignment(0, 0), expand=True))
        page.update()

    # ========= MIS RESERVAS =========
    def mostrar_mis_reservas(e=None):

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", weight="bold", color=PRIMARY_DARK)),
                ft.DataColumn(ft.Text("Hora", weight="bold", color=PRIMARY_DARK)),
                ft.DataColumn(ft.Text("Mesa", weight="bold", color=PRIMARY_DARK)),
                ft.DataColumn(ft.Text("Personas", weight="bold", color=PRIMARY_DARK)),
                ft.DataColumn(ft.Text("Estado", weight="bold", color=PRIMARY_DARK)),
                ft.DataColumn(ft.Text("Acción", weight="bold", color=PRIMARY_DARK)),
            ],
            rows=[],
            heading_row_color="#F5F1E8"
        )

        def cargar():
            resultado = supabase.table("reservas").select(
                "*, mesas(ubicacion)"
            ).eq("id_cliente", usuario["id_cliente"]).execute()
            tabla.rows.clear()
            for r in resultado.data:
                color_estado = SUCCESS if r["estado_reserva"] == "confirmada" else ERROR
                ubicacion = r["mesas"]["ubicacion"] if r.get("mesas") else "—"
                tabla.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(r["fecha"]), color=TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(str(r["hora"]), color=TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(f"Mesa {r['id_mesa']} - {ubicacion}", color=TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(str(r["numero_personas"]), color=TEXT_PRIMARY)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(r["estado_reserva"], color="#FFFFFF", size=11),
                            bgcolor=color_estado,
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=3, bottom=3)
                        )),
                        ft.DataCell(
                            ft.TextButton("Cancelar",
                                style=ft.ButtonStyle(color=ERROR),
                                on_click=lambda e, res=r: cancelar(res),
                                disabled=r["estado_reserva"] == "cancelada"
                            )
                        )
                    ])
                )
            page.update()

        def cancelar(r):
            def confirmar(e):
                dialogo.open = False
                page.update()
                supabase.table("reservas").update(
                    {"estado_reserva": "cancelada"}
                ).eq("id_reservas", r["id_reservas"]).execute()
                cargar()

            def cerrar(e):
                dialogo.open = False
                page.update()

            dialogo = ft.AlertDialog(
                modal=True,
                title=ft.Text("¿Cancelar reserva?", color=ERROR, weight="bold"),
                content=ft.Text(f"¿Seguro que deseas cancelar la reserva del {r['fecha']}?"),
                actions=[
                    ft.TextButton("No", on_click=cerrar),
                    ft.FilledButton("Sí, cancelar", on_click=confirmar,
                        style=ft.ButtonStyle(bgcolor=ERROR, color="#FFFFFF"))
                ],
                actions_alignment="center"
            )
            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()

        vista = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=PRIMARY,
                            on_click=lambda e: limpiar_contenido()),
                        ft.Text("Mis Reservas", size=24, weight="bold", color=PRIMARY_DARK)
                    ]),
                    ft.Container(
                        content=tabla, bgcolor=BG_CARD, border_radius=10, padding=10,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00000022")
                    )
                ],
                spacing=20, scroll="auto"
            ),
            bgcolor=BG_MAIN, padding=30, expand=True
        )

        page.clean()
        page.bgcolor = BG_MAIN
        page.add(vista)
        cargar()
        page.update()

    # ========= PERFIL =========
    def mostrar_perfil(e=None):

        vista = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=PRIMARY,
                            on_click=lambda e: limpiar_contenido()),
                        ft.Text("Mi Perfil", size=24, weight="bold", color=PRIMARY_DARK)
                    ]),
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=90, color=PRIMARY),
                    ft.Text(usuario["nombre_cliente"], size=24, weight="bold", color=PRIMARY_DARK),
                    ft.Text(usuario["correo"], size=14, color=TEXT_SECONDARY),
                    ft.Text(usuario.get("telefono") or "Sin teléfono", size=14, color=TEXT_SECONDARY),
                    ft.FilledButton(
                        "Cerrar sesión", icon=ft.Icons.LOGOUT,
                        on_click=lambda e: cerrar_sesion(),
                        style=ft.ButtonStyle(bgcolor=PRIMARY, color="#FFFFFF")
                    )
                ],
                horizontal_alignment="center", spacing=15
            ),
            bgcolor=BG_CARD, padding=40, border_radius=20, width=400,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000022")
        )

        page.clean()
        page.bgcolor = BG_MAIN
        page.add(ft.Container(content=vista, alignment=ft.Alignment(0, 0), expand=True))
        page.update()

    # ========= LAYOUT PRINCIPAL =========
    def construir_layout():
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(controls=[
                                    ft.Text(
                                        f"Hola, {usuario['nombre_cliente'].split()[0]} 👋",
                                        size=28, weight="bold", color=PRIMARY_DARK
                                    ),
                                    ft.Text(fecha_texto, size=13, color=TEXT_SECONDARY)
                                ], spacing=4),
                                ft.IconButton(
                                    icon=ft.Icons.ACCOUNT_CIRCLE,
                                    icon_color=PRIMARY, icon_size=38,
                                    tooltip="Mi perfil", on_click=mostrar_perfil
                                )
                            ],
                            alignment="spaceBetween"
                        ),
                        bgcolor=BG_CARD, padding=25, border_radius=20,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00000022")
                    ),
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Icon(ft.Icons.RESTAURANT, color=PRIMARY, size=36),
                            ft.Column(controls=[
                                ft.Text("Bienvenido al Restaurante",
                                    size=18, weight="bold", color=PRIMARY_DARK),
                                ft.Text("Reserva tu mesa fácilmente.",
                                    size=13, color=TEXT_SECONDARY)
                            ], spacing=3)
                        ], spacing=15),
                        bgcolor=BG_CARD, padding=20, border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00000022")
                    ),
                    ft.Text("¿Qué deseas hacer?", size=18, weight="bold", color=PRIMARY_DARK),
                    ft.Row(
                        controls=[
                            tarjeta_accion(ft.Icons.ADD_CIRCLE, "Nueva Reserva",
                                "Reserva una mesa fácilmente", PRIMARY, mostrar_hacer_reserva),
                            tarjeta_accion(ft.Icons.CALENDAR_MONTH, "Mis Reservas",
                                "Consulta o cancela reservas", ACCENT, mostrar_mis_reservas),
                            tarjeta_accion(ft.Icons.PERSON, "Mi Perfil",
                                "Consulta tus datos", "#8D6E63", mostrar_perfil),
                        ],
                        spacing=20, wrap=True
                    )
                ],
                spacing=25, scroll="auto"
            ),
            bgcolor=BG_MAIN, padding=30, expand=True
        )

    page.bgcolor = BG_MAIN
    return construir_layout()