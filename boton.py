import flet as ft


def boton(page: ft.Page):
    btn = ft.FilledButton(
        text="Botón personalizado",
        bgcolor=ft.Colors.ORANGE,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=20,
            elevation=4
        )
    )

    def handle_click(e):
        btn.text = "¡Clickeado!"
        page.update()

    btn.on_click = handle_click

    return ft.Row(
        [btn],
        alignment=ft.MainAxisAlignment.CENTER
    )