# ventana_menu.py

import tkinter as tk
from tkinter import ttk

from src.utilidades import constantes
from src.GUI.estilos import configurar_estilos


class VentanaMenu:
    """Ventana del menu"""

    def __init__(self, root, menu, datos_dia, objetivo_calorico, ventana_preguntas):
        self.root = root
        configurar_estilos(self.root)
        self.ventana_calorias = ventana_preguntas
        self.root.title("Menú Generado")
        self.root.minsize(1024, 768)

        self.root.protocol("WM_DELETE_WINDOW", self.volver)

        # Crea el marco principal
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Crea la tabla de menu
        for col, dia in enumerate(constantes.DIAS_SEMANA):
            lbl = ttk.Label(frame, text=dia, font=("Arial", 12, "bold"), borderwidth=1, relief="solid")
            lbl.grid(row=0, column=col + 1, sticky="nsew")
            frame.columnconfigure(col + 1, weight=1)

        for row, comida in enumerate(constantes.COMIDAS):
            lbl = ttk.Label(frame, text=comida["nombre"], font=("Arial", 12, "bold"), borderwidth=1, relief="solid")
            lbl.grid(row=row + 1, column=0, sticky="nsew")
            frame.rowconfigure(row + 1, weight=1)

            for col, dia in enumerate(constantes.DIAS_SEMANA):
                alimentos, _ = menu.get(dia, {}).get(comida["nombre"], (["-"], 0))
                text = "\n".join(alimentos)
                lbl = ttk.Label(frame, text=text, borderwidth=1, relief="solid", wraplength=120)
                lbl.grid(row=row + 1, column=col + 1, sticky="nsew")

        # Añade objetivo calorico y calorias/micronutriente
        objetivo_lbl = ttk.Label(frame, text=f"Objetivo calórico: {objetivo_calorico:.2f}", font=("Arial", 10, "bold"), borderwidth=1, relief="solid", wraplength=120)
        objetivo_lbl.grid(row=len(constantes.COMIDAS) + 1, column=0, sticky="nsew")

        for col, dia in enumerate(constantes.DIAS_SEMANA):
            calorias = datos_dia[dia]["calorias"]
            porcentaje_proteinas = datos_dia[dia]["porcentaje_proteinas"]
            porcentaje_carbohidratos = datos_dia[dia]["porcentaje_carbohidratos"]
            porcentaje_grasas = datos_dia[dia]["porcentaje_grasas"]

            resumen = f"Calorías: {calorias}\n"
            resumen += f"Proteínas: {porcentaje_proteinas:.2f}%\n"
            resumen += f"Carbohidratos: {porcentaje_carbohidratos:.2f}%\n"
            resumen += f"Grasas: {porcentaje_grasas:.2f}%\n"

            lbl = ttk.Label(frame, text=resumen, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", wraplength=120)
            lbl.grid(row=len(constantes.COMIDAS) + 1, column=col + 1, sticky="nsew")

        # Ajusta tamaño de celdas
        for i in range(len(constantes.COMIDAS) + 2):
            frame.rowconfigure(i, weight=1)
        for i in range(len(constantes.DIAS_SEMANA) + 1):
            frame.columnconfigure(i, weight=1)

        # Crea botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=len(constantes.COMIDAS) + 2, column=0, columnspan=len(constantes.DIAS_SEMANA) + 1, pady=10)

        ttk.Button(button_frame, text="Atrás", style="Small.TButton", command=self.volver).pack(side="left", padx=(50, 20), expand=True)
        ttk.Button(button_frame, text="Cerrar", style="Small.TButton", command=self.cerrar).pack(side="left", padx=(20, 50), expand=True)


    def cerrar(self):
        """Termina la ejecucion de la aplicacion"""

        self.root.quit()

    def volver(self):
        """Vuelve a la pantalla anterior"""
        
        self.root.destroy()
        self.ventana_calorias.deiconify()