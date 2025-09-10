import flet as ft


def boton(page, on_click=None):
    def handle_click(e):
        print("¡Botón presionado!")
        if on_click:
            on_click(e)

    return ft.ElevatedButton(
        "Buscar Dispositivos",
        on_click=handle_click,
        bgcolor=ft.Colors.ORANGE,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )