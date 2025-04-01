import json
import os
import numpy as np
from pymoo.indicators.hv import HV
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

# Ruta base donde están los archivos JSON
BASE_PATH = "PROJECT/src/test/resultados/tablas"

# Ruta del archivo JSON que se usará para calcular los hipervolúmenes
RUTA_JSON_RESULTADOS = "PROJECT/src/test/resultados/tablas/ag_nsga3/penalizacion_estatica/uniform/direcciones_referencia_uniform_medio.json"

def obtener_archivos_json(base_path):
    """Genera una lista de archivos JSON excluyendo los que están en hipervolumenes"""

    archivos_json = []
    
    for root, _, files in os.walk(base_path):
        # Excluir carpetas que contengan "hipervolumenes"
        if "hipervolumenes" in root:
            continue

        # Agregar solo archivos JSON
        for file in files:
            if file.endswith(".json"):
                archivos_json.append(os.path.join(root, file))
    
    return archivos_json

# Lista de archivos JSON actualizada dinámicamente
ARCHIVOS_JSON = obtener_archivos_json(BASE_PATH)

# Ruta de salida
RUTA_SALIDA = 'PROJECT/src/test/resultados/tablas/ag_nsga3/penalizacion_estatica/uniform/hipervolumenes/hipervolumenes_nsga3_uniform_medio.json'


def leer_json(ruta_archivo):
    """Lee un archivo JSON y devuelve su contenido."""

    try:
        with open(ruta_archivo, 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"Error: El archivo {ruta_archivo} no existe.")
        return None


def extraer_soluciones_factibles(ruta_archivo):
    """Extrae todas las soluciones factibles de un archivo JSON."""

    datos = leer_json(ruta_archivo)
    if datos is None:
        return []

    soluciones_factibles = []
    for sujeto in datos['resultados']:
        for seed in sujeto['soluciones_por_seed']:
            if seed['genero_soluciones']:
                for solucion in seed['soluciones']:
                    restricciones = solucion['verificacion']
                    if (restricciones['cumple_restriccion_calorias'] and
                        restricciones['cumple_restriccion_macronutrientes'] and
                        restricciones['cumple_restriccion_alergia']):
                        soluciones_factibles.append(solucion['fitness'])

    return soluciones_factibles


def calcular_punto_referencia(archivos_json):
    """Calcula el punto de referencia usando todas las soluciones factibles."""

    todas_soluciones_factibles = []
    for archivo in archivos_json:
        todas_soluciones_factibles.extend(extraer_soluciones_factibles(archivo))

    if not todas_soluciones_factibles:
        print("No hay soluciones factibles para calcular el punto de referencia.")
        return np.array([1e6] * 3)

    soluciones_array = np.array(todas_soluciones_factibles)
    punto_referencia = np.max(soluciones_array, axis=0) * 1.1  
    print("Punto de referencia:", punto_referencia)

    return punto_referencia


def filtrar_no_dominadas(soluciones):
    """Filtra y devuelve las soluciones no dominadas."""

    if len(soluciones) == 0:
        return []
    elif len(soluciones) == 1:
        return soluciones
    
    soluciones_array = np.array(soluciones)
    nds = NonDominatedSorting()
    indices_no_dominados = nds.do(soluciones_array, only_non_dominated_front=True)

    return soluciones_array[indices_no_dominados]


def calcular_hipervolumen_por_seed(ruta_archivo, punto_referencia):
    """Calcula el hipervolumen de las soluciones no dominadas por cada seed."""

    calculo_hv = HV(ref_point=punto_referencia)
    soluciones_por_seed = extraer_soluciones_por_seed(ruta_archivo)
    hipervolumenes_por_sujeto = {}

    for sujeto_id, seeds in soluciones_por_seed.items():
        hipervolumenes_por_sujeto[sujeto_id] = []

        for seed in seeds:
            soluciones = seed['soluciones_factibles']

            if soluciones is not None and len(soluciones) > 0:
                soluciones_no_dominadas = filtrar_no_dominadas(soluciones)
                soluciones_no_dominadas = np.array(soluciones_no_dominadas)

                if soluciones_no_dominadas.shape[0] > 0:
                    hipervolumen_actual = calculo_hv.do(soluciones_no_dominadas)
                else:
                    hipervolumen_actual = 0
            else:
                hipervolumen_actual = 0

            hipervolumenes_por_sujeto[sujeto_id].append({
                "seed": seed['seed'],
                "hipervolumen": hipervolumen_actual
            })

    return hipervolumenes_por_sujeto


def extraer_soluciones_por_seed(ruta_archivo):
    """Extrae soluciones factibles agrupadas por seed."""

    datos = leer_json(ruta_archivo)
    if datos is None:
        return {}

    soluciones_por_seed = {}
    for index_sujeto, sujeto in enumerate(datos['resultados']):
        sujeto_id = f"sujeto {index_sujeto + 1}"
        soluciones_por_seed[sujeto_id] = []

        for seed in sujeto['soluciones_por_seed']:
            soluciones_factibles = []
            if seed['genero_soluciones']:
                for solucion in seed['soluciones']:
                    restricciones = solucion['verificacion']
                    if (restricciones['cumple_restriccion_calorias'] and
                        restricciones['cumple_restriccion_macronutrientes'] and
                        restricciones['cumple_restriccion_alergia']):
                        soluciones_factibles.append(solucion['fitness'])

            soluciones_por_seed[sujeto_id].append({
                'seed': seed['seed'],
                'soluciones_factibles': soluciones_factibles if soluciones_factibles else []
            })

    return soluciones_por_seed


def guardar_en_json(datos, ruta_salida):
    """Guarda los resultados en un archivo JSON."""
    with open(ruta_salida, 'w') as archivo:
        json.dump(datos, archivo, indent=4)
    print(f"Hipervolúmenes guardados en {ruta_salida}")


def main():
    """Función principal que calcula el punto de referencia o los hipervolumenes por seed."""

    accion = input("¿Qué acción realizar? (1: Calcular punto de referencia, 2: Calcular hipervolumen por seed): ")

    if accion == "1":
        calcular_punto_referencia(ARCHIVOS_JSON)

    elif accion == "2":
        punto_referencia = calcular_punto_referencia(ARCHIVOS_JSON)
        if punto_referencia is not None:
            hipervolumenes = calcular_hipervolumen_por_seed(RUTA_JSON_RESULTADOS, punto_referencia)
            guardar_en_json(hipervolumenes, RUTA_SALIDA)
            
    else:
        print("Opción no válida. Elige 1 o 2.")


if __name__ == "__main__":
    main()