import flet as ft


def boton(page: ft.Page, on_click=None):
    btn = ft.FilledButton(
        text="Buscar Dispositivos",
        on_click=on_click,
        bgcolor=ft.Colors.ORANGE,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=20,
            elevation=4
        )
    )

    return ft.Row(
        [btn],
        alignment=ft.MainAxisAlignment.CENTER
    )