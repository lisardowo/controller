import flet as ft
from boton import boton 
from homepage import homepage

def main(page: ft.Page):
    page.title = "Controller"
    page.bgcolor = ft.Colors.BLACK
    page.add(
        homepage(page)
       
    ),
        
  

ft.app(target=main)
