# ventana_comidas.py - Muestra los alimentos y sus datos

import tkinter as tk
from tkinter import ttk

from src.utilidades.carga_datos_csv import leer_comidas
from src.GUI.estilos import configurar_estilos


class BaseDatosApp:
    """Ventana de la base de datos"""

    def __init__(self, root, ventana_principal):
        self.root = root
        configurar_estilos(self.root)
        self.ventana_principal = ventana_principal
        self.root.title("Base de Datos")
        self.root.minsize(400, 300)

        self.root.protocol("WM_DELETE_WINDOW", self.volver)

        # Lista de alimentos
        datos = leer_comidas()

        datos_ordenados = sorted(datos, key=lambda item: item["grupo"])

        # Crea el Treeview para mostrar los datos de los alimentos
        self.tree = ttk.Treeview(root, columns=("Nombre", "Grupo", "Calorias", "Grasas", "Proteinas", "Carbohidratos"), show='headings')
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Grupo", text="Grupo")
        self.tree.heading("Calorias", text="Calorias (kcal)")
        self.tree.heading("Grasas", text="Grasas (g)")
        self.tree.heading("Proteinas", text="Proteinas (g)")
        self.tree.heading("Carbohidratos", text="Carbohidratos (g)")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Agrega datos al Treeview
        for item in datos_ordenados:
            self.tree.insert("", "end", values=(item["nombre"], item["grupo"], item["calorias"], item["grasas"], item["proteinas"], item["carbohidratos"]))

        # Agrega scrollbar
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Crea boton de regreso a la ventana principal
        ttk.Button(root, text="Volver", style="Small.TButton", command=self.volver).grid(row=1, column=0, columnspan=2, pady=10)

        # Configurar redimensionamiento
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)


    def volver(self):
        """Vuelve a la ventana principal"""
        self.root.destroy()
        self.ventana_principal.deiconify()