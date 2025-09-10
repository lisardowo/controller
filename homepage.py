import flet as ft
import random
from boton import boton

def homepage(page: ft.Page):
    # Generar nombre de usuario aleatorio
    nombres = ["Usuario", "Player", "Gamer", "Controller"]
    numero = random.randint(1000, 9999)
    nombre_usuario = f"{random.choice(nombres)}{numero}"
    
    return ft.Column([
        # Nombre de usuario en la parte superior
        ft.Text(
            nombre_usuario,
            size=24,
            color=ft.Colors.WHITE,
            weight=ft.FontWeight.BOLD
        ),
        
        # Imagen placeholder en el centro
        ft.Container(
            content=ft.Icon(
                ft.Icons.PHONE_ANDROID,
                size=150,
                color=ft.Colors.ORANGE
            ),
            width=200,
            height=200,
            bgcolor=ft.Colors.GREY_800,
            border_radius=20,
            alignment=ft.alignment.center
        ),
        
        # Botón ligeramente abajo de la imagen
        boton(page)
        
    ], 
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=30
    )