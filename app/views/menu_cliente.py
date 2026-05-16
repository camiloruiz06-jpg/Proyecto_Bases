import flet as ft
from data_base.supabase_client import supabase
from datetime import date


def vista_menu_cliente(page: ft.Page, usuario, cerrar_sesion):

    BG_DARK = "#1A1A2E"
    BG_CARD = "#16213E"
    BG_CARD2 = "#0F3460"
    ACCENT = "#E94560"
    GOLD = "#F5A623"
    TEXT_PRIMARY = "#EAEAEA"
    TEXT_SECONDARY = "#A0A0B0"

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    hoy = date.today()
    fecha_texto = f"{dias[hoy.weekday()]}, {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"

    def limpiar_contenido():
        page.clean()
        page.bgcolor = BG_DARK
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
                        width=64,
                        height=64,
                        alignment=ft.Alignment(0, 0)
                    ),
                    ft.Text(titulo, size=16, weight="bold", color=TEXT_PRIMARY),
                    ft.Text(descripcion, size=12, color=TEXT_SECONDARY, text_align="center"),
                ],
                horizontal_alignment="center",
                spacing=10
            ),
            bgcolor=BG_CARD,
            padding=25,
            border_radius=20,
            width=200,
            height=200,
            on_click=accion,
            ink=True,
            shadow=ft.BoxShadow(blur_radius=15, color="#00000055"),
            animate=ft.Animation(300, "easeOut")
        )

    def mostrar_hacer_reserva(e=None):
        campo_fecha = ft.TextField(
            label="Fecha (YYYY-MM-DD)", hint_text=str(hoy),
            color=TEXT_PRIMARY, label_style=ft.TextStyle(color=GOLD),
            border_color=GOLD, focused_border_color=ACCENT,
            width=300, border_radius=10
        )
        campo_hora = ft.TextField(
            label="Hora (HH:MM)", hint_text="19:00",
            color=TEXT_PRIMARY, label_style=ft.TextStyle(color=GOLD),
            border_color=GOLD, focused_border_color=ACCENT,
            width=300, border_radius=10
        )
        campo_personas = ft.TextField(
            label="Número de personas",
            keyboard_type=ft.KeyboardType.NUMBER,
            color=TEXT_PRIMARY, label_style=ft.TextStyle(color=GOLD),
            border_color=GOLD, focused_border_color=ACCENT,
            width=300, border_radius=10
        )
        dropdown_mesa = ft.Dropdown(
            label="Mesa disponible", width=300,
            options=[], color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=GOLD)
        )
        mensaje = ft.Text("", size=13)

        def buscar_mesas(e):
            personas = campo_personas.value.strip()
            fecha = campo_fecha.value.strip()
            hora = campo_hora.value.strip()

            if not personas or not fecha or not hora:
                mensaje.value = "Completa fecha, hora y personas primero."
                mensaje.color = ACCENT
                page.update()
                return

            if not personas.isdigit() or int(personas) <= 0:
                mensaje.value = "Número de personas inválido."
                mensaje.color = ACCENT
                page.update()
                return

            todas = supabase.table("mesas").select("*")\
                .gte("capacidad", int(personas)).execute()

            ocupadas = supabase.table("reservas").select("id_mesa")\
                .eq("fecha", fecha).eq("hora", hora)\
                .eq("estado_reserva", "confirmada").execute()

            ids_ocupadas = [r["id_mesa"] for r in ocupadas.data]
            disponibles = [m for m in todas.data if m["id_mesa"] not in ids_ocupadas]

            if not disponibles:
                mensaje.value = "No hay mesas disponibles para ese horario."
                mensaje.color = ACCENT
                dropdown_mesa.options = []
            else:
                dropdown_mesa.options = [
                    ft.dropdown.Option(
                        key=str(m["id_mesa"]),
                        text=f"Mesa {m['id_mesa']} — {m.get('ubicacion', '?')} ({m['capacidad']} personas)"
                    )
                    for m in disponibles
                ]
                mensaje.value = f"{len(disponibles)} mesa(s) disponible(s)."
                mensaje.color = "#4CAF50"
            page.update()

        def confirmar_reserva(e):
            fecha = campo_fecha.value.strip()
            hora = campo_hora.value.strip()
            personas = campo_personas.value.strip()
            id_mesa = dropdown_mesa.value

            if not fecha or not hora or not personas or not id_mesa:
                mensaje.value = "Completa todos los campos."
                mensaje.color = ACCENT
                page.update()
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
                title=ft.Text("¡Reserva confirmada! 🎉", color="#4CAF50", weight="bold"),
                content=ft.Text(f"Tu mesa ha sido reservada para el {fecha} a las {hora}."),
                actions=[
                    ft.FilledButton("Perfecto", on_click=cerrar,
                        style=ft.ButtonStyle(bgcolor=ACCENT, color="#FFFFFF"))
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
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=GOLD,
                            on_click=lambda e: limpiar_contenido()),
                        ft.Text("Nueva Reserva", size=22, weight="bold", color=TEXT_PRIMARY)
                    ]),
                    ft.Divider(color="#FFFFFF22"),
                    campo_fecha, campo_hora, campo_personas,
                    ft.FilledButton(
                        "Buscar mesas disponibles",
                        on_click=buscar_mesas,
                        style=ft.ButtonStyle(bgcolor=BG_CARD2, color=GOLD)
                    ),
                    dropdown_mesa,
                    mensaje,
                    ft.FilledButton(
                        "Confirmar Reserva",
                        on_click=confirmar_reserva,
                        style=ft.ButtonStyle(bgcolor=ACCENT, color="#FFFFFF")
                    )
                ],
                spacing=15,
                scroll="auto"
            ),
            bgcolor=BG_CARD,
            padding=30,
            border_radius=20,
            width=400
        )

        page.clean()
        page.bgcolor = BG_DARK
        page.add(
            ft.Container(
                content=vista,
                alignment=ft.Alignment(0, 0),
                expand=True
            )
        )
        page.update()

    def mostrar_mis_reservas(e=None):
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", color=GOLD, weight="bold")),
                ft.DataColumn(ft.Text("Hora", color=GOLD, weight="bold")),
                ft.DataColumn(ft.Text("Mesa", color=GOLD, weight="bold")),
                ft.DataColumn(ft.Text("Personas", color=GOLD, weight="bold")),
                ft.DataColumn(ft.Text("Estado", color=GOLD, weight="bold")),
                ft.DataColumn(ft.Text("Acción", color=GOLD, weight="bold")),
            ],
            rows=[],
            heading_row_color="#0F3460"
        )

        def cargar():
            resultado = supabase.table("reservas").select(
                "*, mesas(ubicacion)"
            ).eq("id_cliente", usuario["id_cliente"]).execute()
            tabla.rows.clear()
            for r in resultado.data:
                color_estado = "#4CAF50" if r["estado_reserva"] == "confirmada" else ACCENT
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
                                style=ft.ButtonStyle(color=ACCENT),
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
                title=ft.Text("¿Cancelar reserva?", color=ACCENT, weight="bold"),
                content=ft.Text(f"¿Seguro que deseas cancelar la reserva del {r['fecha']}?", color=TEXT_PRIMARY),
                actions=[
                    ft.TextButton("No", on_click=cerrar),
                    ft.FilledButton("Sí, cancelar", on_click=confirmar,
                        style=ft.ButtonStyle(bgcolor=ACCENT, color="#FFFFFF"))
                ],
                actions_alignment="center",
                bgcolor=BG_CARD
            )
            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()

        vista = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=GOLD,
                            on_click=lambda e: limpiar_contenido()),
                        ft.Text("Mis Reservas", size=22, weight="bold", color=TEXT_PRIMARY)
                    ]),
                    ft.Divider(color="#FFFFFF22"),
                    ft.Container(content=tabla, bgcolor=BG_CARD, border_radius=10, padding=10)
                ],
                spacing=15,
                scroll="auto"
            ),
            bgcolor=BG_CARD,
            padding=30,
            border_radius=20,
            expand=True
        )

        page.clean()
        page.bgcolor = BG_DARK
        page.add(ft.Container(content=vista, padding=30, expand=True))
        cargar()
        page.update()

    def mostrar_perfil(e=None):
        vista = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=GOLD,
                            on_click=lambda e: limpiar_contenido()),
                        ft.Text("Mi Perfil", size=22, weight="bold", color=TEXT_PRIMARY)
                    ]),
                    ft.Divider(color="#FFFFFF22"),
                    ft.Container(
                        content=ft.Column(controls=[
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=80, color=GOLD),
                            ft.Text(usuario["nombre_cliente"], size=22, weight="bold", color=TEXT_PRIMARY),
                            ft.Text(usuario["correo"], size=14, color=TEXT_SECONDARY),
                            ft.Text(usuario.get("telefono") or "Sin teléfono", size=14, color=TEXT_SECONDARY),
                        ], horizontal_alignment="center", spacing=8),
                        bgcolor=BG_CARD2,
                        border_radius=20,
                        padding=30
                    ),
                    ft.FilledButton(
                        "Cerrar sesión",
                        icon=ft.Icons.LOGOUT,
                        on_click=lambda e: cerrar_sesion(),
                        style=ft.ButtonStyle(bgcolor=ACCENT, color="#FFFFFF")
                    )
                ],
                spacing=20,
                horizontal_alignment="center"
            ),
            bgcolor=BG_CARD,
            padding=30,
            border_radius=20,
            width=400
        )

        page.clean()
        page.bgcolor = BG_DARK
        page.add(ft.Container(content=vista, alignment=ft.Alignment(0, 0), expand=True))
        page.update()

    def construir_layout():
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(controls=[
                                    ft.Text(f"Hola, {usuario['nombre_cliente'].split()[0]} 👋",
                                        size=28, weight="bold", color=TEXT_PRIMARY),
                                    ft.Text(fecha_texto, size=13, color=TEXT_SECONDARY)
                                ], spacing=4),
                                ft.IconButton(
                                    icon=ft.Icons.ACCOUNT_CIRCLE,
                                    icon_color=GOLD,
                                    icon_size=36,
                                    tooltip="Mi perfil",
                                    on_click=mostrar_perfil
                                )
                            ],
                            alignment="spaceBetween"
                        ),
                        bgcolor=BG_CARD,
                        padding=25,
                        border_radius=20,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00000044")
                    ),
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Icon(ft.Icons.RESTAURANT, color=GOLD, size=36),
                            ft.Column(controls=[
                                ft.Text("Bienvenido al Restaurante",
                                    size=16, weight="bold", color=TEXT_PRIMARY),
                                ft.Text("Reserva tu mesa en segundos.",
                                    size=13, color=TEXT_SECONDARY)
                            ], spacing=2)
                        ], spacing=15),
                        bgcolor=BG_CARD2,
                        padding=20,
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=10, color="#00000044")
                    ),
                    ft.Text("¿Qué deseas hacer?", size=16,
                        weight="bold", color=TEXT_SECONDARY),
                    ft.Row(
                        controls=[
                            tarjeta_accion(
                                ft.Icons.ADD_CIRCLE, "Nueva Reserva",
                                "Reserva una mesa ahora", ACCENT, mostrar_hacer_reserva
                            ),
                            tarjeta_accion(
                                ft.Icons.CALENDAR_MONTH, "Mis Reservas",
                                "Ver y cancelar reservas", BG_CARD2, mostrar_mis_reservas
                            ),
                            tarjeta_accion(
                                ft.Icons.PERSON, "Mi Perfil",
                                "Ver mis datos", GOLD, mostrar_perfil
                            ),
                        ],
                        spacing=20,
                        wrap=True
                    ),
                ],
                spacing=20,
                scroll="auto"
            ),
            bgcolor=BG_DARK,
            padding=30,
            expand=True
        )

    page.bgcolor = BG_DARK
    return construir_layout()