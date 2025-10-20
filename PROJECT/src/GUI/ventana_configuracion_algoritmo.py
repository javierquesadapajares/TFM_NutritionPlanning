# ventana_configuracion_algoritmo.py - Permite elegir el espacio y sus hiperparámetros a ejecutar

import tkinter as tk
from tkinter import ttk, messagebox

from src.GUI.estilos import configurar_estilos

# Configuración por defecto
config_algoritmo = {
    "espacio": "discreto",
    "prob_cruce": 0.9,
    "prob_mut": 1/77,
    "discreto": {
        "cruce": "twopoint",     
        "mutacion": "custom",    
    },
    "vectores": {
        "cruce": "uniforme",           # "uniforme"|"sbx"|"twopoint"
        "mutacion": "gaussiana",       # "gaussiana"|"oposicion"|"custom"
    },
    "matrices": {
        "matriz": "coseno",            # "coseno"|"braycurtis"|"jaccard"
        "cruce": "consenso",           # "consenso"|"anticonsenso"|"twopoint"
        "mutacion": "ruleta",          # "ruleta"|"softmax"|"custom"
    },
    "grafos": {
        "metrica": "coseno",           # "coseno"|"braycurtis"|"jaccard"
        "filtro": "knn",               # "knn"|"knn_doble"|"umbral"
        "cruce": "camino",             # "camino"|"caminatas"|"twopoint"
        "mutacion": "radio",           # "radio"|"comunidades"|"custom"
    },
}


class ConfigPanel(ttk.Frame):
    """Panel para configurar los parámetros del algoritmo."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, padding=15, **kwargs)
        configurar_estilos(self.winfo_toplevel())
        self.vars = {}
        self._construir_widgets()

    def _construir_widgets(self):
        # Espacio + probs globales
        fila = 0
        self._lbl(self, "Espacio:", fila, 0)
        self.vars["espacio"] = tk.StringVar(value=config_algoritmo["espacio"])
        self.combo_espacio = ttk.Combobox(
            self,
            textvariable=self.vars["espacio"],
            state="readonly",
            values=["discreto", "vectores", "matrices", "grafos"],
            style="ConfigSmall.TCombobox",
            width=20,
        )
        self.combo_espacio.grid(row=fila, column=1, sticky="ew", padx=5, pady=5)

        fila += 1
        self._lbl(self, "prob_cruce:", fila, 0)
        self.vars["prob_cruce"] = tk.StringVar(value=str(config_algoritmo["prob_cruce"]))
        ttk.Entry(self, textvariable=self.vars["prob_cruce"], style="ConfigSmall.TEntry").grid(
            row=fila, column=1, sticky="ew", padx=5, pady=5
        )

        fila += 1
        self._lbl(self, "prob_mut:", fila, 0)
        self.vars["prob_mut"] = tk.StringVar(value=str(config_algoritmo["prob_mut"]))
        ttk.Entry(self, textvariable=self.vars["prob_mut"], style="ConfigSmall.TEntry").grid(
            row=fila, column=1, sticky="ew", padx=5, pady=5
        )

        # Frames específicos por espacio
        fila += 1
        self.frame_discreto = self._labelframe(self, "DISCRETO", fila)
        self._build_discreto(self.frame_discreto)

        fila += 1
        self.frame_vectores = self._labelframe(self, "VECTORES", fila)
        self._build_vectores(self.frame_vectores)

        fila += 1
        self.frame_matrices = self._labelframe(self, "MATRICES", fila)
        self._build_matrices(self.frame_matrices)

        fila += 1
        self.frame_grafos = self._labelframe(self, "GRAFOS", fila)
        self._build_grafos(self.frame_grafos)

        # Botón guardar (opcional; leer_config ya devuelve lo actual)
        fila += 1
        boton_guardar = ttk.Button(
            self, text="Guardar Configuración", style="ConfigSmall.TButton", command=self.guardar
        )
        boton_guardar.grid(row=fila, column=0, columnspan=2, pady=10)

        # Toggle por espacio
        self.combo_espacio.bind("<<ComboboxSelected>>", self._toggle_frames)
        self._toggle_frames()

        # Expansión
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

    def _build_discreto(self, parent):
        # Fijos, pero visibles para claridad
        self._lbl(parent, "cruce:", 0, 0)
        self.vars["discreto_cruce"] = tk.StringVar(value=config_algoritmo["discreto"]["cruce"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["discreto_cruce"],
            state="readonly",
            values=["twopoint"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self._lbl(parent, "mutacion:", 1, 0)
        self.vars["discreto_mut"] = tk.StringVar(value=config_algoritmo["discreto"]["mutacion"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["discreto_mut"],
            state="readonly",
            values=["custom"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    def _build_vectores(self, parent):
        # ahora con 'twopoint' y 'custom' disponibles
        self._lbl(parent, "cruce:", 0, 0)
        self.vars["vectores_cruce"] = tk.StringVar(value=config_algoritmo["vectores"]["cruce"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["vectores_cruce"],
            state="readonly",
            values=["uniforme", "sbx", "twopoint"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self._lbl(parent, "mutacion:", 1, 0)
        self.vars["vectores_mut"] = tk.StringVar(value=config_algoritmo["vectores"]["mutacion"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["vectores_mut"],
            state="readonly",
            values=["gaussiana", "oposicion", "custom"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    def _build_matrices(self, parent):
        self._lbl(parent, "matriz:", 0, 0)
        self.vars["matrices_matriz"] = tk.StringVar(value=config_algoritmo["matrices"]["matriz"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["matrices_matriz"],
            state="readonly",
            values=["coseno", "braycurtis", "jaccard"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self._lbl(parent, "cruce:", 1, 0)
        self.vars["matrices_cruce"] = tk.StringVar(value=config_algoritmo["matrices"]["cruce"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["matrices_cruce"],
            state="readonly",
            values=["consenso", "anticonsenso", "twopoint"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self._lbl(parent, "mutacion:", 2, 0)
        self.vars["matrices_mut"] = tk.StringVar(value=config_algoritmo["matrices"]["mutacion"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["matrices_mut"],
            state="readonly",
            values=["ruleta", "softmax", "custom"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    def _build_grafos(self, parent):
        self._lbl(parent, "metrica:", 0, 0)
        self.vars["grafos_metrica"] = tk.StringVar(value=config_algoritmo["grafos"]["metrica"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["grafos_metrica"],
            state="readonly",
            values=["coseno", "braycurtis", "jaccard"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self._lbl(parent, "filtro:", 1, 0)
        self.vars["grafos_filtro"] = tk.StringVar(value=config_algoritmo["grafos"]["filtro"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["grafos_filtro"],
            state="readonly",
            values=["knn", "knn_doble", "umbral"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self._lbl(parent, "cruce:", 2, 0)
        self.vars["grafos_cruce"] = tk.StringVar(value=config_algoritmo["grafos"]["cruce"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["grafos_cruce"],
            state="readonly",
            values=["camino", "caminatas", "twopoint"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self._lbl(parent, "mutacion:", 3, 0)
        self.vars["grafos_mut"] = tk.StringVar(value=config_algoritmo["grafos"]["mutacion"])
        ttk.Combobox(
            parent,
            textvariable=self.vars["grafos_mut"],
            state="readonly",
            values=["radio", "comunidades", "custom"],
            style="ConfigSmall.TCombobox",
            width=20,
        ).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

    # --- utilidades UI ------------------------------------------------------

    def _labelframe(self, parent, texto, row):
        lf = ttk.LabelFrame(parent, text=texto, padding=10)
        lf.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        return lf

    def _lbl(self, parent, texto, row, col):
        ttk.Label(parent, text=texto, style="ConfigSmall.TLabel").grid(
            row=row, column=col, sticky="w", padx=5, pady=5
        )

    def _toggle_frames(self, event=None):
        for f in (self.frame_discreto, self.frame_vectores, self.frame_matrices, self.frame_grafos):
            f.grid_remove()

        esp = self.vars["espacio"].get()
        if esp == "discreto":
            self.frame_discreto.grid()
        elif esp == "vectores":
            self.frame_vectores.grid()
        elif esp == "matrices":
            self.frame_matrices.grid()
        else:
            self.frame_grafos.grid()

    # --- API pública --------------------------------------------------------

    def leer_config(self):
        """Devuelve un dict con la configuración actual (sin necesidad de pulsar Guardar)."""
        try:
            prob_cruce = float(self.vars["prob_cruce"].get())
            prob_mut = float(self.vars["prob_mut"].get())
        except Exception:
            prob_cruce = float(config_algoritmo["prob_cruce"])
            prob_mut = float(config_algoritmo["prob_mut"])

        esp = self.vars["espacio"].get()

        cfg = {
            "espacio": esp,
            "prob_cruce": prob_cruce,
            "prob_mut": prob_mut,
            "discreto": {
                "cruce": self.vars["discreto_cruce"].get(),
                "mutacion": self.vars["discreto_mut"].get(),
            },
            "vectores": {
                "cruce": self.vars["vectores_cruce"].get(),
                "mutacion": self.vars["vectores_mut"].get(),
            },
            "matrices": {
                "matriz": self.vars["matrices_matriz"].get(),
                "cruce": self.vars["matrices_cruce"].get(),
                "mutacion": self.vars["matrices_mut"].get(),
            },
            "grafos": {
                "metrica": self.vars["grafos_metrica"].get(),
                "filtro": self.vars["grafos_filtro"].get(),
                "cruce": self.vars["grafos_cruce"].get(),
                "mutacion": self.vars["grafos_mut"].get(),
            },
        }
        return cfg

    def guardar(self):
        """Guarda la configuración (actualiza el diccionario global)."""
        try:
            cfg = self.leer_config()

            # Actualiza el diccionario global (cuidado con typos)
            config_algoritmo["espacio"] = cfg["espacio"]
            config_algoritmo["prob_cruce"] = cfg["prob_cruce"]
            config_algoritmo["prob_mut"] = cfg["prob_mut"]
            config_algoritmo["discreto"] = cfg["discreto"]
            config_algoritmo["vectores"] = cfg["vectores"]
            config_algoritmo["matrices"] = cfg["matrices"]
            config_algoritmo["grafos"] = cfg["grafos"]

        except Exception as e:
            messagebox.showerror("Error", f"Revisa los valores: {e}")
            return

        messagebox.showinfo("Configuración", "La configuración se ha guardado correctamente.")