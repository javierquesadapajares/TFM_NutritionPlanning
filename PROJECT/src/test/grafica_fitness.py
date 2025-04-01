#grafica_fitness.py

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importaciones de algoritmos.
from src.utilidades import database, constantes
from src.algoritmos.nsga2.ag_nsga2_penalizacion_estatica import ejecutar_algoritmo_genetico as nsga2_est
from src.algoritmos.nsga2.ag_nsga2_metodo_separatista import ejecutar_algoritmo_genetico as nsga2_sep
from src.algoritmos.nsga3.ag_nsga3_penalizacion_estatica import ejecutar_algoritmo_genetico as nsga3_est
from src.algoritmos.nsga3.ag_nsga3_metodo_separatista import ejecutar_algoritmo_genetico as nsga3_sep
from src.algoritmos.spea2.ag_spea2_estatica import ejecutar_algoritmo_genetico as spea2_est
from src.algoritmos.spea2.ag_spea2_separatista import ejecutar_algoritmo_genetico as spea2_sep
from src.algoritmos.moead.ag_moead import ejecutar_algoritmo_genetico as moead

SEEDS = constantes.SEEDS

sujetos = database.sujetos_basedatos()
comida_bd = database.comida_basedatos()

objetivos = ["calorias", "macronutrientes", "preferencias"]

# Diccionario de algoritmos
algoritmos = {
    "NSGA2-Estatica": nsga2_est,
    "NSGA2-Separatista": nsga2_sep,
    "NSGA3-Estatica": nsga3_est,
    "NSGA3-Separatista": nsga3_sep,
    "SPEA2-Estatica": spea2_est,
    "SPEA2-Separatista": spea2_sep,
    "MOEAD": moead
}


def obtener_llave_fitness(nombre_algoritmo):
    """Devuelve valores de fitness segun el manejo de restricciones """

    if "Estatica" in nombre_algoritmo or nombre_algoritmo == "MOEAD":
        return "raw"
    else:
        return "F"


def extraer_mediana_por_generacion(resultado, llave, obj_idx):
    """Extrae la mediana por generacion"""
    medianas_generacion = []
    for gen in resultado.history:
        pop = gen.pop
        fitness = pop.get(llave)  # fitness: array de forma (n_individuos, n_objetivos)
        med = np.median(fitness[:, obj_idx])
        medianas_generacion.append(med)
    return np.array(medianas_generacion)


def ejecutar_algoritmo_para_sujeto(alg_func, sujeto, nombre_alg):
    """Ejecuta un algoritmo para un sujeto 31 veces y retorna las medianas"""
    llave = obtener_llave_fitness(nombre_alg)
    resultados_por_seed = []

    for seed in SEEDS:
    
        if nombre_alg == "MOEAD":
            resultado = alg_func(
                comida_bd=comida_bd,
                objetivo_calorico=sujeto['calorias'],
                edad=sujeto['edad'],
                grupos_alergia=sujeto['alergias'],
                grupos_gusta=sujeto['gustos'],
                grupos_no_gusta=sujeto['disgustos'],
                seed=seed,
                n_gen=100,
                prob_cruce=0.9,
                prob_mut=1/77,
                n_neighbors=30,
                prob_neighbor_mating=0.9,
                n_partitions=12,
                met_ref="incremental"
            )
        else:
            try:
                resultado = alg_func(
                    comida_bd=comida_bd,
                    objetivo_calorico=sujeto['calorias'],
                    edad=sujeto['edad'],
                    grupos_alergia=sujeto['alergias'],
                    grupos_gusta=sujeto['gustos'],
                    grupos_no_gusta=sujeto['disgustos'],
                    seed=seed,
                    n_gen=100,
                    pop_size=100,
                    prob_cruce=0.9,
                    prob_mut=1/77
                )
            except TypeError as e:
                if "n_partitions" in str(e) or "met_ref" in str(e):
                    resultado = alg_func(
                        comida_bd=comida_bd,
                        objetivo_calorico=sujeto['calorias'],
                        edad=sujeto['edad'],
                        grupos_alergia=sujeto['alergias'],
                        grupos_gusta=sujeto['gustos'],
                        grupos_no_gusta=sujeto['disgustos'],
                        seed=seed,
                        n_gen=100,
                        pop_size=100,
                        prob_cruce=0.9,
                        prob_mut=1/77,
                        n_partitions=12,
                        met_ref="incremental"
                    )
                else:
                    raise e
                
        # Para esta semilla, extraemos la mediana por generación para cada objetivo.
        resultados_por_seed.append({
            "calorias": extraer_mediana_por_generacion(resultado, llave, 0),
            "macronutrientes": extraer_mediana_por_generacion(resultado, llave, 1),
            "preferencias": extraer_mediana_por_generacion(resultado, llave, 2)
        })
    # Agregamos: para cada objetivo, calculamos la mediana (sobre las 31 ejecuciones) por generación.
    n_gen = len(resultados_por_seed[0]["calorias"])
    medianas_agregadas = {
        "calorias": np.median(np.array([r["calorias"] for r in resultados_por_seed]), axis=0),
        "macronutrientes": np.median(np.array([r["macronutrientes"] for r in resultados_por_seed]), axis=0),
        "preferencias": np.median(np.array([r["preferencias"] for r in resultados_por_seed]), axis=0)
    }
    return medianas_agregadas

# Función que genera las gráficas: 5 sujetos x 3 objetivos.
def generar_graficas():
    # Creamos la carpeta "graficas" si no existe.
    os.makedirs("graficas", exist_ok=True)
    
    # Para cada sujeto.
    for subj_idx, sujeto in enumerate(sujetos):
        # Primero, para este sujeto, ejecutamos cada algoritmo (5x7x31 = 1085 ejecuciones totales).
        resultados_algoritmo = {}  # key: nombre de algoritmo, value: diccionario con 3 arrays (medianas)
        for alg_nombre, alg_func in algoritmos.items():
            print(f"Ejecutando {alg_nombre} para Sujeto {subj_idx+1}")
            resultados_algoritmo[alg_nombre] = ejecutar_algoritmo_para_sujeto(alg_func, sujeto, alg_nombre)
        
        # Ahora, para cada uno de los 3 objetivos, generamos una gráfica.
        for obj in objetivos:
            plt.figure()
            generaciones = None
            for alg_nombre, res in resultados_algoritmo.items():
                datos = res[obj]
                if generaciones is None:
                    generaciones = np.arange(1, len(datos) + 1)
                plt.plot(generaciones, datos, label=alg_nombre)
            plt.title(f"Evolucion del Fitness ({obj.capitalize()}) para Sujeto {subj_idx+1}")
            plt.xlabel("Generaciones")
            plt.ylabel(f"Fitness Mediano ({obj.capitalize()})")
            plt.legend()
            plt.grid(True)
            nombre_archivo = os.path.join("graficas", f"fitness_sujeto{subj_idx+1}_{obj}.png")
            plt.savefig(nombre_archivo)
            plt.close()
            print("Grafica guardada:", nombre_archivo)

if __name__ == "__main__":
    generar_graficas()