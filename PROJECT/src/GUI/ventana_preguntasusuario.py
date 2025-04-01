# ventana_preguntasusuario

import time
import random
import tkinter as tk
from tkinter import ttk, messagebox

from src.GUI.estilos import configurar_estilos
from src.GUI.ventana_menu import VentanaMenu
from src.GUI.ventana_configuracion_algoritmo import ConfigPanel, config_algoritmo
from src.utilidades import database, funciones_auxiliares, constantes

# Importaciones de algoritmos
from src.algoritmos.nsga2.ag_nsga2_penalizacion_estatica import ejecutar_algoritmo_genetico as nsga2_est
from src.algoritmos.nsga2.ag_nsga2_metodo_separatista import ejecutar_algoritmo_genetico as nsga2_sep
from src.algoritmos.nsga3.ag_nsga3_penalizacion_estatica import ejecutar_algoritmo_genetico as nsga3_est
from src.algoritmos.nsga3.ag_nsga3_metodo_separatista import ejecutar_algoritmo_genetico as nsga3_sep
from src.algoritmos.spea2.ag_spea2_estatica import ejecutar_algoritmo_genetico as spea2_est
from src.algoritmos.spea2.ag_spea2_separatista import ejecutar_algoritmo_genetico as spea2_sep
from src.algoritmos.moead.ag_moead import ejecutar_algoritmo_genetico as moead


comida_bd = database.comida_basedatos()
seed = int(time.time())
random.seed(seed)


def obtener_diccionario_algoritmos():
    """Devuelve el diccionario que asocia cada clave de algoritmo con la funcion correspondiente."""

    return {
        "NSGA2-Estática": nsga2_est,
        "NSGA2-Separatista": nsga2_sep,
        "NSGA3-Estática": nsga3_est,
        "NSGA3-Separatista": nsga3_sep,
        "SPEA2-Estática": spea2_est,
        "SPEA2-Separatista": spea2_sep,
        "MOEAD": moead
    }

def obtener_grupos_comida(clase):
    """Obtiene una lista de grupos de comida con tabulacion jerarquica."""

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
    """Obtiene un diccionario con codigo y descripcion de cada grupo."""

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

        # Configuracion del frame principal
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

        # Crea widgets en datos del usuario
        self.crear_etiqueta_dato(self.datos_frame, "Peso (kg):", self.peso, row=0)
        self.crear_etiqueta_dato(self.datos_frame, "Altura (cm):", self.altura, row=1)
        self.crear_etiqueta_dato(self.datos_frame, "Edad:", self.edad, row=2)
        self.crear_etiqueta_combobox(self.datos_frame, "Sexo:", self.sexo, ["hombre", "mujer"], row=3)
        niveles = [act.value[0] for act in constantes.NivelActividad]
        self.crear_etiqueta_combobox(self.datos_frame, "Nivel de actividad:", self.nivel_actividad, niveles, row=4, ancho=60)

        # Crea listboxes para preferencias alimentarias
        self.lista_alergia = self.crear_listbox(self.prefs_frame, "Alérgico:", row=0)
        self.lista_gusta = self.crear_listbox(self.prefs_frame, "Te gusta:", row=1)
        self.lista_no_gusta = self.crear_listbox(self.prefs_frame, "No te gusta:", row=2)

        # Columna Derecha 
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.rowconfigure(0, weight=0)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # Panel de configuracion del algoritmo
        config_frame = self.crear_labelframe(right_frame, "Configuración del Algoritmo", row=0)
        self.config_panel = ConfigPanel(config_frame)
        self.config_panel.grid(row=0, column=0, sticky="ew")

        # Botones de la columna derecha
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
        """Crea un Labelframe."""

        labelframe = ttk.LabelFrame(parent, text=texto, padding=15, style="Left.TLabelframe")
        labelframe.grid(row=row, column=0, sticky="nsew", padx=5, pady=5, **grid_options)

        labelframe.rowconfigure(0, weight=1)
        labelframe.columnconfigure(0, weight=1)

        return labelframe
    

    def crear_boton(self, parent, texto, comando, row, column=0, **grid_options):
        """Crea un boton."""

        boton = ttk.Button(parent, text=texto, style="Small.TButton", command=comando)
        boton.grid(row=row, column=column, **grid_options)

        return boton
    

    def crear_etiqueta(self, parent, texto, row, column, **grid_options):
        """Crea una etiqueta."""

        etiqueta = ttk.Label(parent, text=texto, style="Small.TLabel")
        etiqueta.grid(row=row, column=column, **grid_options)

        return etiqueta
    

    def crear_etiqueta_dato(self, parent, etiqueta_texto, variable, row):
        """Crea un par etiqueta-entrada para datos numericos."""

        self.crear_etiqueta(parent, etiqueta_texto, row, 0, sticky="w", padx=10, pady=5)
        entrada = ttk.Entry(parent, textvariable=variable, style="Small.TEntry")
        entrada.grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        return entrada
    

    def crear_etiqueta_combobox(self, parent, etiqueta_texto, variable, opciones, row, ancho=12):
        """Crea un par etiqueta-combobox."""

        self.crear_etiqueta(parent, etiqueta_texto, row, 0, sticky="w", padx=10, pady=5)
        combo = ttk.Combobox(parent, textvariable=variable, values=opciones, style="Small.TCombobox", width=ancho)
        combo.grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        return combo
    

    def crear_listbox(self, parent, etiqueta, row):
        """Crea un listbox con etiqueta para selección múltiple y scrollbar."""

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
        """Se extrae el codigo inicial y se expande a todos los codigos que lo comienzan usando el diccionario de grupos."""

        seleccionados = [lista.get(i).split()[0] for i in lista.curselection()]
        expandido = set()
        dicc = obtener_diccionario_grupos(constantes.GruposComida)

        for seleccionado in seleccionados:
            for codigo in dicc.keys():

                if codigo.startswith(seleccionado):
                    expandido.add(codigo)

        return list(expandido)


    def calcular_calorias(self):
        """Calcula las calorías diarias"""

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


    def mostrar_menu(self):
        """Llama al algoritmo con la configuracion elegida y muestra la ventana del menu."""

        grupos_alergia = self.expandir_selecciones(self.lista_alergia)
        cal = self.calcular_calorias()
        grupos_gusta = self.expandir_selecciones(self.lista_gusta)
        grupos_no_gusta = self.expandir_selecciones(self.lista_no_gusta)

        alg = config_algoritmo["algoritmo"]
        if alg == "MOEAD":
            key = "MOEAD"
        else:
            key = f"{alg}-{config_algoritmo['tipo']}"

        algoritmos = obtener_diccionario_algoritmos()

        if key in algoritmos:
            func = algoritmos[key]

            if key.startswith("NSGA2") or key.startswith("SPEA2"):
                resultado = func(
                    comida_bd, cal, self.edad.get(), grupos_alergia,
                    grupos_gusta, grupos_no_gusta, seed,
                    n_gen=config_algoritmo["n_gen"],
                    pop_size=config_algoritmo["pop_size"],
                    prob_cruce=config_algoritmo["prob_cruce"],
                    prob_mut=config_algoritmo["prob_mut"]
                )

            elif key.startswith("NSGA3"):
                resultado = func(
                    comida_bd, cal, self.edad.get(), grupos_alergia,
                    grupos_gusta, grupos_no_gusta, seed,
                    n_gen=config_algoritmo["n_gen"],
                    pop_size=config_algoritmo["pop_size"],
                    prob_cruce=config_algoritmo["prob_cruce"],
                    prob_mut=config_algoritmo["prob_mut"],
                    n_partitions=config_algoritmo["n_partitions"],
                    met_ref=config_algoritmo["met_ref"]
                )

            elif key == "MOEAD":
                resultado = func(
                    comida_bd, cal, self.edad.get(), grupos_alergia,
                    grupos_gusta, grupos_no_gusta, seed,
                    n_gen=config_algoritmo["n_gen"],
                    prob_cruce=config_algoritmo["prob_cruce"],
                    prob_mut=config_algoritmo["prob_mut"],
                    n_partitions=config_algoritmo["n_partitions"],
                    n_neighbors=config_algoritmo["n_neighbors"],
                    prob_neighbor_mating=config_algoritmo["prob_neighbor_mating"],
                    met_ref=config_algoritmo["met_ref"]
                )

            else:
                resultado = nsga2_est(
                    comida_bd, cal, self.edad.get(), grupos_alergia,
                    grupos_gusta, grupos_no_gusta, seed,
                    n_gen=config_algoritmo["n_gen"],
                    pop_size=config_algoritmo["pop_size"],
                    prob_cruce=config_algoritmo["prob_cruce"],
                    prob_mut=config_algoritmo["prob_mut"]
                )

        if resultado is None or resultado.F is None or resultado.X is None:
            messagebox.showerror("Error", "No se ha generado ninguna solución válida. Prueba con otros parámetros.")
            return


        cv = resultado.F[:, 0]
        best_idx = cv.argmin()
        sol = resultado.X[best_idx]
        menu, datos = funciones_auxiliares.traducir_solucion(sol, comida_bd)

        self.root.withdraw()
        VentanaMenu(tk.Toplevel(), menu, datos, objetivo_calorico=cal, ventana_preguntas=self.root)


    def volver(self):
        """Cierra la ventana actual y vuelve a la ventana principal."""

        self.root.destroy()
        self.ventana_principal.deiconify()