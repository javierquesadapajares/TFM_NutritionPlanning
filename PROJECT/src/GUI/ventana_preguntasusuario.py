# ventana_preguntasusuario.py

import time
import random
import tkinter as tk
from tkinter import ttk, messagebox

from src.utilidades import constantes
from src.utilidades.planificacion import traducir_solucion
from src.utilidades.carga_datos_csv import leer_comidas
from src.GUI.estilos import configurar_estilos
from src.GUI.ventana_menu import VentanaMenu
from src.GUI.ventana_configuracion_algoritmo import ConfigPanel, config_algoritmo

from src.espacios.vectores.preparador_vectores import ejecutar_vectores
from src.espacios.matrices.preparador_matrices import ejecutar_matrices
from src.espacios.grafos.preparador_grafos import ejecutar_grafos


comida_bd = leer_comidas()
seed = int(time.time())
random.seed(seed)


def obtener_grupos_comida(clase):
    """Obtiene una lista de grupos de comida con tabulación jerárquica."""
    grupos = []
    for _, subclase in vars(clase).items():
        if isinstance(subclase, tuple):
            codigo = subclase[0]
            descripcion = subclase[1]
            tab = " " * (2 * (len(codigo) - 1))
            grupos.append(f"{tab}{codigo} - {descripcion}")
        elif isinstance(subclase, type):
            grupos.extend(obtener_grupos_comida(subclase))
    return grupos


def obtener_diccionario_grupos(clase):
    """Obtiene un diccionario con código y descripción de cada grupo."""
    diccionario = {}
    for _, subclase in vars(clase).items():
        if isinstance(subclase, tuple):
            diccionario[subclase[0]] = subclase[1]
        elif isinstance(subclase, type):
            diccionario.update(obtener_diccionario_grupos(subclase))
    return diccionario


class VentanaCalorias:

    def __init__(self, root, ventana_principal):
        self.root = root
        self.ventana_principal = ventana_principal
        self.root.title("Preguntas al usuario")
        self.root.minsize(900, 600)
        configurar_estilos(self.root)

        self.root.protocol("WM_DELETE_WINDOW", self.volver)

        # Config frame principal
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)

        # Columna Izquierda
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        left_frame.rowconfigure(0, weight=0)
        left_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(2, weight=0)
        left_frame.columnconfigure(0, weight=1)

        # Paneles de datos del usuario y preferencias alimentarias
        self.datos_frame = self.crear_labelframe(left_frame, "Datos del Usuario", row=0)
        self.prefs_frame = self.crear_labelframe(left_frame, "Preferencias Alimentarias", row=1)

        self.crear_boton(left_frame, "Volver", self.volver, row=2, column=0, sticky="w", padx=5, pady=10)

        # Variables de usuario
        self.peso = tk.DoubleVar(value=75)
        self.altura = tk.DoubleVar(value=175)
        self.edad = tk.IntVar(value=23)
        self.sexo = tk.StringVar(value="hombre")
        self.nivel_actividad = tk.StringVar(value="Sedentario (poco o ningun ejercicio)")

        # Widgets de datos del usuario
        self.crear_etiqueta_dato(self.datos_frame, "Peso (kg):", self.peso, row=0)
        self.crear_etiqueta_dato(self.datos_frame, "Altura (cm):", self.altura, row=1)
        self.crear_etiqueta_dato(self.datos_frame, "Edad:", self.edad, row=2)
        self.crear_etiqueta_combobox(self.datos_frame, "Sexo:", self.sexo, ["hombre", "mujer"], row=3)
        niveles = [act.value[0] for act in constantes.NivelActividad]
        self.crear_etiqueta_combobox(self.datos_frame, "Nivel de actividad:", self.nivel_actividad, niveles, row=4, ancho=60)

        # Listboxes de preferencias
        self.lista_alergia = self.crear_listbox(self.prefs_frame, "Alérgico:", row=0)
        self.lista_gusta = self.crear_listbox(self.prefs_frame, "Te gusta:", row=1)
        self.lista_no_gusta = self.crear_listbox(self.prefs_frame, "No te gusta:", row=2)

        # Columna Derecha
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.rowconfigure(0, weight=0)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # Panel de configuración del algoritmo
        config_frame = self.crear_labelframe(right_frame, "Configuración del Algoritmo", row=0)
        self.config_panel = ConfigPanel(config_frame)
        self.config_panel.grid(row=0, column=0, sticky="ew")

        # Botones derecha
        botones_frame = ttk.Frame(right_frame)
        botones_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=10)
        botones_frame.columnconfigure(0, weight=1)

        self.crear_boton(botones_frame, "Calcular Calorías", self.calcular_calorias,
                         row=0, column=0, sticky="ew", padx=5, pady=(0, 10))

        self.resultado = ttk.Label(botones_frame, text="", style="Small.TLabel")
        self.resultado.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))

        self.crear_boton(botones_frame, "Mostrar Menú", self.mostrar_menu,
                         row=3, column=0, sticky="ew", padx=5, pady=(20, 0))


    def crear_labelframe(self, parent, texto, row, **grid_options):
        labelframe = ttk.LabelFrame(parent, text=texto, padding=15, style="Left.TLabelframe")
        labelframe.grid(row=row, column=0, sticky="nsew", padx=5, pady=5, **grid_options)
        labelframe.rowconfigure(0, weight=1)
        labelframe.columnconfigure(0, weight=1)
        return labelframe

    def crear_boton(self, parent, texto, comando, row, column=0, **grid_options):
        boton = ttk.Button(parent, text=texto, style="Small.TButton", command=comando)
        boton.grid(row=row, column=column, **grid_options)
        return boton

    def crear_etiqueta(self, parent, texto, row, column, **grid_options):
        etiqueta = ttk.Label(parent, text=texto, style="Small.TLabel")
        etiqueta.grid(row=row, column=column, **grid_options)
        return etiqueta

    def crear_etiqueta_dato(self, parent, etiqueta_texto, variable, row):
        self.crear_etiqueta(parent, etiqueta_texto, row, 0, sticky="w", padx=10, pady=5)
        entrada = ttk.Entry(parent, textvariable=variable, style="Small.TEntry")
        entrada.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        return entrada

    def crear_etiqueta_combobox(self, parent, etiqueta_texto, variable, opciones, row, ancho=12):
        self.crear_etiqueta(parent, etiqueta_texto, row, 0, sticky="w", padx=10, pady=5)
        combo = ttk.Combobox(parent, textvariable=variable, values=opciones, style="Small.TCombobox", width=ancho)
        combo.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        return combo

    def crear_listbox(self, parent, etiqueta, row):
        self.crear_etiqueta(parent, etiqueta, row, 0, sticky="w", padx=10, pady=5)
        frame_lb = ttk.Frame(parent)
        frame_lb.grid(row=row, column=1, sticky="nsew", padx=10, pady=5)
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(1, weight=1)

        listbox = tk.Listbox(frame_lb, selectmode="multiple", width=40, height=6,
                             exportselection=False, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(frame_lb, orient="vertical", command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        grupos = obtener_grupos_comida(constantes.GruposComida)
        for g in grupos:
            listbox.insert(tk.END, g)
        return listbox

    def expandir_selecciones(self, lista):
        """Expande el prefijo de código seleccionado a todos los códigos que lo comienzan."""
        seleccionados = [lista.get(i).split()[0] for i in lista.curselection()]
        expandido = set()
        dicc = obtener_diccionario_grupos(constantes.GruposComida)
        for seleccionado in seleccionados:
            for codigo in dicc.keys():
                if codigo.startswith(seleccionado):
                    expandido.add(codigo)
        return list(expandido)

    def calcular_calorias(self):
        """Calcula las calorías diarias (Mifflin-St Jeor + factor actividad)."""
        peso = self.peso.get()
        altura = self.altura.get()
        edad = self.edad.get()
        sexo = self.sexo.get()
        nivel = self.nivel_actividad.get()
        factor = next((act.value[1] for act in constantes.NivelActividad if act.value[0] == nivel), 1.2)

        if sexo.lower() == "hombre":
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

        cal = round(tmb * factor, 2)
        self.resultado.config(text=f"Calorías diarias: {cal}")
        return cal

    def _usar_discreto_en_cualquier_espacio(self, cfg) -> bool:
        """
        Si el usuario elige 'twopoint' o 'custom' en cualquier espacio,
        se ejecuta el pipeline de vectores (discreto) que soporta dichos operadores.
        """
        esp = cfg["espacio"]
        if esp == "discreto":
            return True

        if esp == "vectores":
            cruce = cfg["vectores"]["cruce"]
            mut = cfg["vectores"]["mutacion"]
        elif esp == "matrices":
            cruce = cfg["matrices"]["cruce"]
            mut = cfg["matrices"]["mutacion"]
        else:  # "grafos"
            cruce = cfg["grafos"]["cruce"]
            mut = cfg["grafos"]["mutacion"]

        return (cruce == "twopoint") or (mut == "custom")

    def mostrar_menu(self):
        """Llama al algoritmo con la configuración elegida y muestra la ventana del menú."""
        grupos_alergia = self.expandir_selecciones(self.lista_alergia)
        cal = self.calcular_calorias()
        grupos_gusta = self.expandir_selecciones(self.lista_gusta)
        grupos_no_gusta = self.expandir_selecciones(self.lista_no_gusta)

        cfg = self.config_panel.leer_config()

        if self._usar_discreto_en_cualquier_espacio(cfg):
            esp = cfg["espacio"]
            if esp == "discreto":
                cruce = cfg["discreto"]["cruce"]        
                mut = cfg["discreto"]["mutacion"]       
            elif esp == "vectores":
                cruce = cfg["vectores"]["cruce"]
                mut = cfg["vectores"]["mutacion"]
            elif esp == "matrices":
                cruce = cfg["matrices"]["cruce"]
                mut = cfg["matrices"]["mutacion"]
            else:  
                cruce = cfg["grafos"]["cruce"]
                mut = cfg["grafos"]["mutacion"]

            resultado = ejecutar_vectores(
                comida_bd, cal, self.edad.get(),
                grupos_gusta, grupos_no_gusta, grupos_alergia,
                cruce=cruce,                        
                mutacion=mut,                       
                prob_cruce=cfg["prob_cruce"],
                prob_mutacion=cfg["prob_mut"],
                seed=seed,
                verbose=True,
            )

        else:
            
            espacio = cfg["espacio"]

            if espacio == "vectores":
                resultado = ejecutar_vectores(
                    comida_bd, cal, self.edad.get(),
                    grupos_gusta, grupos_no_gusta, grupos_alergia,
                    cruce=cfg["vectores"]["cruce"],             
                    mutacion=cfg["vectores"]["mutacion"],       
                    prob_cruce=cfg["prob_cruce"],
                    prob_mutacion=cfg["prob_mut"],
                    seed=seed,
                    verbose=True,
                )

            elif espacio == "matrices":
                resultado = ejecutar_matrices(
                    comida_bd, cal, self.edad.get(),
                    grupos_gusta, grupos_no_gusta, grupos_alergia,
                    matriz=cfg["matrices"]["matriz"],           
                    cruce=cfg["matrices"]["cruce"],             
                    mutacion=cfg["matrices"]["mutacion"],       
                    prob_cruce=cfg["prob_cruce"],
                    prob_mutacion=cfg["prob_mut"],
                    seed=seed,
                    verbose=True,
                )

            else:  # grafos
                resultado = ejecutar_grafos(
                    comida_bd, cal, self.edad.get(),
                    grupos_gusta, grupos_no_gusta, grupos_alergia,
                    metrica=cfg["grafos"]["metrica"],           
                    filtro=cfg["grafos"]["filtro"],             
                    cruce=cfg["grafos"]["cruce"],               
                    mutacion=cfg["grafos"]["mutacion"],         
                    prob_cruce=cfg["prob_cruce"],
                    prob_mutacion=cfg["prob_mut"],
                    seed=seed,
                    verbose=True,
                )

        if resultado is None or getattr(resultado, "F", None) is None or getattr(resultado, "X", None) is None:
            messagebox.showerror("Error", "No se ha generado ninguna solución válida. Prueba con otros parámetros.")
            return

        cv = resultado.F[:, 0]
        best_idx = cv.argmin()
        sol = resultado.X[best_idx]
        menu, datos = traducir_solucion(sol, comida_bd)

        self.root.withdraw()
        VentanaMenu(tk.Toplevel(), menu, datos, objetivo_calorico=cal, ventana_preguntas=self.root)

    def volver(self):
        """Cierra la ventana actual y vuelve a la ventana principal."""
        self.root.destroy()
        self.ventana_principal.deiconify()