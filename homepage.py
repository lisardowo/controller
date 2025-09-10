import flet as ft
import random
import requests
import threading
from boton import boton

def homepage(page: ft.Page):
    # Iniciar servidor en hilo separado
    def start_server():
        import servidor
        servidor.app.run(host="127.0.0.1", port=5000, debug=False)
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Generar nombre de usuario aleatorio
    nombres = ["Usuario", "Player", "Gamer", "Controller"]
    numero = random.randint(1000, 9999)
    nombre_usuario = f"{random.choice(nombres)} #{numero}"
    
    nombre = nombre_usuario.split(" #")[0]
    numero = nombre_usuario.split(" #")[1]

    # Contenedor principal que se animará
    main_column = ft.Column(
        [
            ft.Container(height=100),
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
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
    )
    main_content = ft.Container(
        content=main_column,
        width=400,
        offset=ft.Offset(0, 0),
        animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
    )

    # Lista de dispositivos (inicialmente oculta)
    device_column = ft.Column([
        ft.Text("Dispositivos Disponibles", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
    ])
    device_list = ft.Container(
        content=device_column,
        width=400,
        offset=ft.Offset(1, 0),
        animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
    )

    def show_devices(e):
        # Animar el deslizamiento
        main_content.offset = ft.Offset(-1, 0)
        device_list.offset = ft.Offset(0, 0)
        page.update()
        
        # Buscar dispositivos en el servidor
        try:
            response = requests.get("http://127.0.0.1:5000/dispositivos", timeout=5)
            if response.status_code == 200:
                dispositivos = response.json()
                # Limpiar lista anterior
                device_column.controls = [
                    ft.Text("Dispositivos Disponibles", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ]
                
                # Agregar dispositivos a la lista
                for dispositivo in dispositivos:
                    device_card = ft.Container(
                        content=ft.Column([
                            ft.Text(dispositivo["nombre"], size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text(f"IP: {dispositivo['ip']}", size=12, color=ft.Colors.GREY_400),
                        ]),
                        bgcolor=ft.Colors.GREY_800,
                        border_radius=10,
                        padding=15,
                        margin=ft.margin.only(top=10),
                    )
                    device_column.controls.append(device_card)
                
                page.update()
                page.update()
        except requests.exceptions.RequestException as e:
            device_column.controls.append(
                ft.Text("Error: No se pudo conectar al servidor", color=ft.Colors.RED)
            )
            page.update()
            
    # Agregar el botón al contenido principal
    # main_column is a Column, so we append to its controls
    main_column.controls.append(boton(page, on_click=show_devices))
   
    
    # Layout principal
    return ft.Row([
        main_content,
        device_list,
    ])