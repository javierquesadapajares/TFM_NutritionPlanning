# ventana_configuracion_algoritmo.py

import tkinter as tk
from tkinter import ttk, messagebox

from src.GUI.estilos import configurar_estilos

# Configuracion algoritmo por defecto
config_algoritmo = {
    'algoritmo': 'NSGA3',         
    'tipo': 'Separatista',        
    'n_gen': 100,
    'pop_size': 100,
    'prob_cruce': 0.9,
    'prob_mut': 1/77,
    'n_partitions': 12,
    'met_ref': 'incremental',     
    'n_neighbors': 30,
    'prob_neighbor_mating': 0.9
}

class ConfigPanel(ttk.Frame):
    """Panel para configurar los parámetros del algoritmo."""

    def __init__(self, parent, **kwargs):

        super().__init__(parent, padding=15, **kwargs)
        configurar_estilos(self.winfo_toplevel())
        self.campos = {}
        self.crear_widgets()
        

    def crear_widgets(self):
        """Crea los campos de configuración del algoritmo."""

        # Campo "Algoritmo" (combobox)
        self.crear_etiqueta_campo("Algoritmo:", "algoritmo", ["NSGA2", "NSGA3", "SPEA2", "MOEAD"],
                                row=0, tipo="combobox")

        # Campo "Tipo" (radio)
        self.crear_etiqueta_campo("Tipo:", "tipo", ["Estática", "Separatista"],
                                row=1, tipo="radio")

        self.crear_etiqueta_campo("n_gen:", "n_gen", None, row=2)
        self.crear_etiqueta_campo("pop_size:", "pop_size", None, row=3)
        self.crear_etiqueta_campo("prob_cruce:", "prob_cruce", None, row=4)
        self.crear_etiqueta_campo("prob_mut:", "prob_mut", None, row=5)

        # Panel para NSGA3
        self.nsga3_frame = self.crear_labelframe("NSGA3", row=6)
        self.crear_etiqueta_campo("n_partitions:", "n_partitions", None, row=0, parent=self.nsga3_frame)
        self.crear_etiqueta_campo("met_ref:", "met_ref", ["incremental", "das-dennis"],
                                row=1, parent=self.nsga3_frame, tipo="combobox", sufijo="nsga3")

        # Panel para MOEAD
        self.moead_frame = self.crear_labelframe("MOEAD", row=7)
        self.crear_etiqueta_campo("n_partitions:", "n_partitions", None, row=3, parent=self.moead_frame, sufijo="moead")
        self.crear_etiqueta_campo("n_neighbors:", "n_neighbors", None, row=0, parent=self.moead_frame)
        self.crear_etiqueta_campo("prob_neighbor_mating:", "prob_neighbor_mating", None, row=1, parent=self.moead_frame)
        self.crear_etiqueta_campo("met_ref:", "met_ref", ["incremental", "das-dennis"],
                                row=2, parent=self.moead_frame, tipo="combobox", sufijo="moead")

        # Boton para guardar la configuracion
        boton_guardar = ttk.Button(self, text="Guardar Configuración", style="ConfigSmall.TButton", command=self.guardar)
        boton_guardar.grid(row=8, column=0, columnspan=2, pady=10)

        # Vincula el combobox de "algoritmo" para activar o desactivar paneles extra
        self.combo_alg.bind("<<ComboboxSelected>>", self.toggle_extra)
        self.toggle_extra()

    def crear_labelframe(self, texto, row, parent=None):
        """Crea un labelframe con título y padding."""

        if parent is None:
            parent = self

        labelframe = ttk.LabelFrame(parent, text=texto, padding=10)
        labelframe.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        return labelframe

    def crear_etiqueta_campo(self, etiqueta_texto, clave, opciones, row, parent=None, tipo="entry", sufijo=""):
        """Crea un par de widgets (etiqueta y campo) para la configuración."""

        if parent is None:
            parent = self

        etiqueta = ttk.Label(parent, text=etiqueta_texto, style="ConfigSmall.TLabel")
        etiqueta.grid(row=row, column=0, sticky="w", padx=5, pady=5)

        if tipo == "entry":
            entrada = ttk.Entry(parent, style="ConfigSmall.TEntry")
            entrada.insert(0, str(config_algoritmo[clave]))
            entrada.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            self.campos[f"{clave}{sufijo}"] = entrada

        elif tipo == "radio":
            var = tk.StringVar(value=config_algoritmo[clave])
            frame_radio = ttk.Frame(parent)
            frame_radio.grid(row=row, column=1, sticky="w", padx=5, pady=5)

            for opcion in opciones:
                rb = ttk.Radiobutton(frame_radio, text=opcion, variable=var, value=opcion)
                rb.pack(side=tk.LEFT, padx=5)

            self.campos[f"{clave}{sufijo}"] = var

            if clave == "tipo":
                self.tipo_var = var

        elif tipo == "combobox":
            var = tk.StringVar(value=config_algoritmo[clave])
            combo = ttk.Combobox(parent, textvariable=var, state="readonly", values=opciones, style="ConfigSmall.TCombobox")
            combo.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            self.campos[f"{clave}{sufijo}"] = var

            if clave == "algoritmo":
                self.algoritmo_var = var
                self.combo_alg = combo


    def toggle_extra(self, event=None):
        """Muestra u oculta los paneles extra de NSGA3 y MOEAD."""

        self.nsga3_frame.grid_remove()
        self.moead_frame.grid_remove()

        if self.algoritmo_var.get() == "MOEAD":
            self.campos["pop_size"].config(state="disabled")
            self.moead_frame.grid()

        else:
            self.campos["pop_size"].config(state="normal")

            if self.algoritmo_var.get() == "NSGA3":
                self.nsga3_frame.grid()

    def guardar(self):
        """Guarda la configuración"""

        try:
            config_algoritmo['algoritmo'] = self.campos['algoritmo'].get()
            config_algoritmo['tipo'] = self.campos['tipo'].get()
            config_algoritmo['n_gen'] = int(self.campos['n_gen'].get())
            config_algoritmo['pop_size'] = int(self.campos['pop_size'].get())
            config_algoritmo['prob_cruce'] = float(self.campos['prob_cruce'].get())
            config_algoritmo['prob_mut'] = float(self.campos['prob_mut'].get())

            if config_algoritmo['algoritmo'] == "NSGA3":
                config_algoritmo['n_partitions'] = int(self.campos['n_partitions'].get())
                config_algoritmo['met_ref'] = self.campos['met_refnsga3'].get()

            if config_algoritmo['algoritmo'] == "MOEAD":
                config_algoritmo['n_partitions'] = int(self.campos['n_partitionsmoead'].get())
                config_algoritmo['n_neighbors'] = int(self.campos['n_neighbors'].get())
                config_algoritmo['prob_neighbor_mating'] = float(self.campos['prob_neighbor_mating'].get())
                config_algoritmo['met_ref'] = self.campos['met_refmoead'].get()

        except Exception as e:
            messagebox.showerror("Error", f"Revisa los valores: {e}")
            return

        messagebox.showinfo("Configuración", "La configuración se ha guardado correctamente.")
