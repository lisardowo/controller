import flet as ft
import random
from boton import boton

def homepage(page: ft.Page):
    # Generar nombre de usuario aleatorio
    nombres = ["Usuario", "Player", "Gamer", "Controller"]
    numero = random.randint(1000, 9999)
    nombre_usuario = f"{random.choice(nombres)} #{numero}"
    
    nombre = nombre_usuario.split(" #")[0]
    numero = nombre_usuario.split(" #")[1]

    def show_devices(e):
        main_content_container.offset = ft.Offset(-1, 0)
        device_list_container.offset = ft.Offset(0, 0)
        device_list.visible = True
        page.update()

    # Contenedor principal que se animará
    main_content = ft.Column(
        [
            ft.Container(height=100),  # Espaciador vertical
            # Nombre de usuario en la parte superior
            ft.Row(
                [
                    ft.Text(
                        nombre,
                        size=24,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f" #{numero}",
                        size=24,
                        color="#F5F5F5",
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # Imagen placeholder en el centro
            ft.Container(
                content=ft.Icon(
                    ft.Icons.PHONE_ANDROID,
                    size=150,
                    color=ft.Colors.ORANGE,
                ),
                width=200,
                height=200,
                bgcolor=ft.Colors.GREY_800,
                border_radius=20,
                alignment=ft.alignment.center,
            ),
            # Botón ligeramente abajo de la imagen
            boton(page, on_click=show_devices),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
    )

    # Lista de dispositivos (inicialmente oculta)
    device_list = ft.Column(
        [
            ft.Text("Dispositivos Disponibles", size=20, weight=ft.FontWeight.BOLD),
            # Aquí se agregarán los dispositivos encontrados
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        visible=False,  # Oculto por defecto
    )

    main_content_container = ft.Container(
        main_content,
        expand=True,
        offset=ft.Offset(0, 0),
        animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_OUT),
    )
    device_list_container = ft.Container(
        device_list,
        expand=True,
        offset=ft.Offset(1, 0),  # Empieza fuera de la pantalla
        animate_offset=ft.Animation(1000, ft.AnimationCurve.EASE_OUT),
    )

    # Contenedor de la fila principal
    return ft.Row(
        [
            main_content_container,
            device_list_container,
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
    )