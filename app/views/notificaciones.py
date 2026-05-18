import flet as ft
from data_base.supabase_client import supabase


def vista_notificaciones(page: ft.Page, volver_panel, usuario):

    mensaje = ft.Text("", size=13)

    campo_buscar = ft.TextField(
        label="Buscar por correo",
        width=250, border_radius=10,
        prefix_icon=ft.Icons.SEARCH,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )

    campo_fecha = ft.TextField(
        label="Filtrar por fecha (YYYY-MM-DD)",
        width=220, border_radius=10,
        color="#212121",
        label_style=ft.TextStyle(color="#4E342E")
    )

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("ID Reserva", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Correo cliente", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Mensaje", weight="bold", color="#212121")),
            ft.DataColumn(ft.Text("Fecha envío", weight="bold", color="#212121")),
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

    def cargar_notificaciones(correo=None, fecha=None):
        query = supabase.table("notificaciones").select("*").order("fecha_envio", desc=True)

        if correo:
            query = query.ilike("correo_cliente", f"%{correo}%")
        if fecha:
            query = query.gte("fecha_envio", fecha).lt("fecha_envio", fecha + "T23:59:59")

        resultado = query.execute()
        tabla.rows.clear()

        if not resultado.data:
            mensaje.value = "No se encontraron notificaciones."
            mensaje.color = "#6D4C41"
            page.update()
            return

        mensaje.value = f"{len(resultado.data)} notificación(es) encontrada(s)."
        mensaje.color = "#388E3C"

        for n in resultado.data:
            fecha_envio = str(n["fecha_envio"])[:16].replace("T", " ")
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(n["id_notificacion"]), color="#212121")),
                    ft.DataCell(ft.Text(str(n["id_reserva"]), color="#212121")),
                    ft.DataCell(ft.Text(n["correo_cliente"], color="#212121")),
                    ft.DataCell(ft.Text(n["mensaje"], color="#212121")),
                    ft.DataCell(ft.Text(fecha_envio, color="#212121")),
                ])
            )
        page.update()

    def aplicar_filtros(e):
        cargar_notificaciones(
            correo=campo_buscar.value.strip() or None,
            fecha=campo_fecha.value.strip() or None
        )

    def limpiar_filtros(e):
        campo_buscar.value = ""
        campo_fecha.value = ""
        mensaje.value = ""
        cargar_notificaciones()

    filtros = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Filtros", size=16, weight="bold", color="#4E342E"),
                ft.Row(controls=[
                    campo_buscar,
                    campo_fecha,
                ], spacing=10, wrap=True),
                ft.Row(controls=[
                    ft.FilledButton("Buscar", on_click=aplicar_filtros,
                        style=ft.ButtonStyle(bgcolor="#6D4C41", color="#FFFFFF")),
                    ft.OutlinedButton("Limpiar", on_click=limpiar_filtros)
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
                ft.Text("Notificaciones", size=24, weight="bold", color="#4E342E")
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

    cargar_notificaciones()

    return ft.Container(content=contenido, padding=30, expand=True)