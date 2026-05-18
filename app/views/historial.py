import flet as ft
from data_base.supabase_client import supabase


def vista_historial(page: ft.Page, volver_panel, usuario):

    mensaje = ft.Text("", size=13)

    # ── FILTROS ───────────────────────────────────────────
    campo_buscar_cliente = ft.TextField(
        label="Buscar por nombre de cliente",
        width=250, border_radius=10,
        prefix_icon=ft.Icons.SEARCH,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )

    campo_fecha_desde = ft.TextField(
        label="Desde (YYYY-MM-DD)",
        width=180, border_radius=10,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )

    campo_fecha_hasta = ft.TextField(
        label="Hasta (YYYY-MM-DD)",
        width=180, border_radius=10,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )

    filtro_estado = ft.Dropdown(
        label="Estado",
        width=160,
        options=[
            ft.dropdown.Option("todos"),
            ft.dropdown.Option("confirmada"),
            ft.dropdown.Option("cancelada"),
        ],
        value="todos"
    )

    # ── TABLA ─────────────────────────────────────────────
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Cliente", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Mesa", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Fecha", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Hora", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Personas", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Estado", weight="bold", color="#212121")),
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

    def cargar_historial(nombre=None, desde=None, hasta=None, estado=None):
        query = supabase.table("reservas").select(
            "*, clientes(nombre_cliente), mesas(ubicacion)"
        )

        if estado and estado != "todos":
            query = query.eq("estado_reserva", estado)
        if desde:
            query = query.gte("fecha", desde)
        if hasta:
            query = query.lte("fecha", hasta)

        resultado = query.order("fecha", desc=True).execute()

        tabla.rows.clear()

        reservas = resultado.data

        # Filtrar por nombre del cliente si se ingresó
        if nombre:
            reservas = [
                r for r in reservas
                if nombre.lower() in r["clientes"]["nombre_cliente"].lower()
            ]

        if not reservas:
            mensaje.value = "No se encontraron reservas."
            mensaje.color = "#6D4C41"
            page.update()
            return

        mensaje.value = f"{len(reservas)} reserva(s) encontrada(s)."
        mensaje.color = "#388E3C"

        for r in reservas:
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
                ])
            )
        page.update()

    def aplicar_filtros(e):
        cargar_historial(
            nombre=campo_buscar_cliente.value.strip() or None,
            desde=campo_fecha_desde.value.strip() or None,
            hasta=campo_fecha_hasta.value.strip() or None,
            estado=filtro_estado.value
        )

    def limpiar_filtros(e):
        campo_buscar_cliente.value = ""
        campo_fecha_desde.value = ""
        campo_fecha_hasta.value = ""
        filtro_estado.value = "todos"
        mensaje.value = ""
        cargar_historial()

    # ── LAYOUT ────────────────────────────────────────────
    filtros = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Filtros", size=16, weight="bold", color="#4E342E"),
                ft.Row(controls=[
                    campo_buscar_cliente,
                    campo_fecha_desde,
                    campo_fecha_hasta,
                    filtro_estado,
                ], wrap=True, spacing=10),
                ft.Row(controls=[
                    ft.FilledButton("Buscar", on_click=aplicar_filtros,
                        style=ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")),
                    ft.OutlinedButton("Limpiar filtros", on_click=limpiar_filtros)
                ], spacing=10),
                mensaje
            ],
            spacing=15
        ),
        bgcolor="#FFFFFF",
        padding=20,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=8, color="#00000022")
    )

    contenido = ft.Column(
        controls=[
            ft.Row(controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: volver_panel(),
                    tooltip="Volver al panel"
                ),
                ft.Text("Historial de Reservas", size=24, weight="bold", color="#4E342E")
            ]),
            filtros,
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

    cargar_historial()

    return ft.Container(content=contenido, padding=30, expand=True)