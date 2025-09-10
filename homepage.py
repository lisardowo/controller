import flet as ft
import random
import requests
import threading
from boton import boton

def homepage(page: ft.Page):
    # --- Configuración del Servidor ---
    def start_server():
        import servidor
        servidor.app.run(host="0.0.0.0", port=5000, debug=False)
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # --- Generación de Nombre de Usuario ---
    nombres = ["Usuario", "Player", "Gamer", "Controller"]
    numero = random.randint(1000, 9999)
    nombre_usuario = f"{random.choice(nombres)} #{numero}"
    nombre, numero_str = nombre_usuario.split(" #")

    # --- VISTA 1: Pantalla Principal (Visible al inicio) ---
    main_column = ft.Column(
        [
            ft.Container(height=100),
            ft.Row(
                [
                    ft.Text(nombre, size=24, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text(f" #{numero_str}", size=24, color="#4a5d62", weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(
                content=ft.Image(
                    src = "controller/assets/Idle.png"
                ),
                width=350,
                height=350,
                
                
                alignment=ft.alignment.center,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
        expand=True,
    )
    
    main_view = ft.Container(
        content=main_column,
        expand=True,
        offset=ft.Offset(0, 0),
        animate_offset=ft.Animation(350, ft.AnimationCurve.EASE_OUT),
    )

    # --- VISTA 2: Pantalla de Dispositivos (Oculta al inicio) ---
    
    # Columna para la lista de dispositivos
    device_column = ft.Column(
        [ft.Text("Dispositivos", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # Función para regresar a la pantalla de inicio
    def disconnect_and_return(e):
        main_view.offset = ft.Offset(0, 0)
        secondary_view.offset = ft.Offset(1, 0)
        page.update()

    # Columna para el placeholder de la derecha
    Conectado_column = ft.Column(
        [
            # Creamos una columna interna para agrupar la imagen y el botón
            ft.Column(
                [
                    # Contenedor con margen para mover la imagen
                    ft.Container(
                        content=ft.Image(
                            src="controller/assets/conectado.png",
                            
                        ),
                        width=450,
                        height=450,
                        margin=ft.margin.only(right=80),
                        alignment=ft.alignment.center,
                    ),
                    # El espaciador ahora funcionará correctamente dentro de este grupo
                    ft.Container(height=12),
                    ft.ElevatedButton(
                        "Desconectar",
                        on_click=disconnect_and_return,
                        bgcolor=ft.Colors.RED_ACCENT_700,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=90),
                        ),
                    )
                ],
                # Esta columna interna alinea sus propios elementos
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        # La columna principal centra el grupo completo
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )

    # Contenedor que agrupa la lista y el placeholder
    secondary_view = ft.Container(
        content=ft.Row(
            [
                # Contenedor para la lista (ocupa 1 parte del espacio)
                ft.Container(content=device_column, padding=10, expand=1),
                # Contenedor para el placeholder (ocupa 1 parte del espacio)
                ft.Container(content=Conectado_column, padding=10, expand=1),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        expand=True,
        offset=ft.Offset(1, 0), # Empieza fuera de la pantalla, a la derecha
        animate_offset=ft.Animation(350, ft.AnimationCurve.EASE_OUT),
    )

    # --- Lógica de Animación y Búsqueda ---
    def show_devices(e):
        main_view.offset = ft.Offset(-1, 0)
        secondary_view.offset = ft.Offset(0, 0)
        page.update()
        
        try:
            response = requests.get("http://127.0.0.1:5000/dispositivos", timeout=5)
            if response.status_code == 200:
                dispositivos = response.json()
                device_column.controls = [ft.Text("Dispositivos", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)]
                for dispositivo in dispositivos:
                    device_column.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(dispositivo["nombre"], weight=ft.FontWeight.BOLD),
                                ft.Text(f"IP: {dispositivo['ip']}", size=12, color=ft.Colors.GREY_400),
                            ]),
                            bgcolor=ft.Colors.GREY_800,
                            border_radius=10,
                            padding=15,
                            margin=ft.margin.only(top=10),
                        )
                    )
            else:
                device_column.controls = [ft.Text("Error al buscar", color=ft.Colors.RED)]
            page.update()
        except requests.exceptions.RequestException:
            device_column.controls = [
                ft.Text("Error de Conexión", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                ft.Text("No se pudo conectar al servidor."),
            ]
            page.update()
            
    # Agregar el botón a la columna principal
    main_column.controls.append(boton(page, on_click=show_devices))
   
    # --- Layout Final de la Página ---
    # El Stack permite que las vistas se superpongan para la animación
    return ft.Stack([
        main_view,
        secondary_view,
    ])