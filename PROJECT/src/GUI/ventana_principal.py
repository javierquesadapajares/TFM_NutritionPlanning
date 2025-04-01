# ventana_principal.py

import tkinter as tk
from tkinter import ttk

from src.GUI.estilos import configurar_estilos
from src.GUI.ventana_preguntasusuario import VentanaCalorias
from src.GUI.ventana_basedatos import BaseDatosApp

class MainApp:
    """Ventana principal de la aplicacion"""
    
    def __init__(self, root):
        self.root = root
        configurar_estilos(self.root)
        self.root.title("Planificación nutricional mediante algoritmos evolutivos")
        self.root.minsize(400, 300)

        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, pady=20, padx=20, sticky="ns")

        # Etiqueta principal
        ttk.Label(main_frame, text="Planificación nutricional mediante algoritmos evolutivos", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
    
        # Botones de opciones
        ttk.Button(main_frame, text="Planificar el menú", style="Small.TButton", command=self.abrir_calculadora).grid(row=1, column=0, padx=10, pady=10, sticky="n")
        ttk.Button(main_frame, text="Visualizar la base de datos", style="Small.TButton", command=self.visualizar_base_datos).grid(row=1, column=1, padx=10, pady=10, sticky="n")

        # Redimensionamiento de la ventana
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        

    def abrir_calculadora(self):
        self.root.withdraw()
        root2 = tk.Toplevel(self.root)
        app = VentanaCalorias(root2, self.root)

    def visualizar_base_datos(self):
        self.root.withdraw()
        root2 = tk.Toplevel(self.root)
        app = BaseDatosApp(root2, self.root)