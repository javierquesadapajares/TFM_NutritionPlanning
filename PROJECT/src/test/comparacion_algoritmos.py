import sys
import os
import json
import numpy as np
from scipy import stats

current_dir = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(current_dir, "../../"))
stac_parent = os.path.join(project_dir, "external", "stac")

if stac_parent not in sys.path:
    sys.path.insert(0, stac_parent)

from stac.nonparametric_tests import friedman_aligned_ranks_test, shaffer_multitest

def cargar_hipervolumenes(ruta_archivo):
    """Carga los hipervolumenes desde un archivo JSON y los agrupa por sujeto."""

    try:
        with open(ruta_archivo, 'r') as f:
            datos = json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo {ruta_archivo} no existe.")
        return {}

    hipervolumenes = {}

    for sujeto, seeds in datos.items():

        hipervolumenes[sujeto] = []
        for entry in seeds:

            hipervolumen = entry.get('hipervolumen', 0)
            
            if isinstance(hipervolumen, (int, float)):
                hipervolumenes[sujeto].append(float(hipervolumen))
            else:
                hipervolumenes[sujeto].append(0)

    return hipervolumenes

def crea_matriz_friedman(hipervolumenes_por_metodo):
    """Prepara los datos en formato matriz para el test de Friedman."""
    
    sujetos = list(hipervolumenes_por_metodo.values())[0].keys()
    matriz = []

    for sujeto in sujetos:
        fila = []
        for metodo in hipervolumenes_por_metodo.keys():
            
            observaciones = hipervolumenes_por_metodo[metodo][sujeto]
            fila.extend(observaciones)

        matriz.append(fila)

    return np.array(matriz), list(sujetos)


def is_better(rank_1, rank_2):
    """Determina si el primer método es mejor que el segundo basado en los rankings."""
    return rank_1 < rank_2

def prueba_wilcoxon(hipervolumenes_1, hipervolumenes_2, nombre_1, nombre_2):
    """Realiza el test de Wilcoxon."""

    for sujeto in hipervolumenes_1.keys():
        
        if sujeto in hipervolumenes_2:
            metodo_A = hipervolumenes_1[sujeto]
            metodo_B = hipervolumenes_2[sujeto]
            
            if len(metodo_A) < 2 or len(metodo_B) < 2:
                print(f"Sujeto {sujeto}: Datos insuficientes para aplicar Wilcoxon.")
                continue

            # Test de Wilcoxon
            stat, p_value = stats.wilcoxon(metodo_A, metodo_B)

            diferencias = np.array(metodo_A) - np.array(metodo_B)
            mediana_diferencias = np.median(diferencias)

            print(f"\nResultado de la prueba de Wilcoxon para {sujeto} entre {nombre_1} y {nombre_2}:")
            print(f"Estadístico de Wilcoxon: {stat:.4f}")
            print(f"p-value: {p_value:.4f}")
            print(f"Mediana de las diferencias: {mediana_diferencias:.4f}")

            if p_value >= 0.05:
                print("No hay suficiente evidencia para concluir diferencias significativas.")
            else:
                if mediana_diferencias > 0:
                    print(f"{nombre_1} es mejor que {nombre_2} para {sujeto}.")
                else:
                    print(f"{nombre_2} es mejor que {nombre_1} para {sujeto}.")


def friedman_y_shaffer(hipervolumenes_por_metodo):
    """Realiza el test de Friedman y la corrección post-hoc de Shaffer."""

    matriz, sujetos = crea_matriz_friedman(hipervolumenes_por_metodo)

    if matriz.shape[1] < 2:
        print("No hay suficientes métodos para realizar el test de Friedman.")
        return

    # Test de Friedman
    _, p_value, ranks, _ = friedman_aligned_ranks_test(*matriz.T)

    print(f"p-value: {p_value:.4f}")

    nombres_metodos = list(hipervolumenes_por_metodo.keys())
    ranks_dict = {nombre: rank for nombre, rank in zip(nombres_metodos, ranks)}
    ranking_ordenado = sorted(ranks_dict.items(), key=lambda item: item[1])
    
    print("\nRanking de los métodos (mejor al peor):")
    for i, (nombre, rank) in enumerate(ranking_ordenado, start=1):
        print(f"{i}. {nombre}: ranking promedio = {rank:.4f}")

    if p_value < 0.05:
        comparisons, _, _, adj_p_values = shaffer_multitest(ranks_dict)
        print("\nComparaciones significativas (Shaffer post-hoc):")
        for comp, apv in zip(comparisons, adj_p_values):
            cl, cr = comp.split(" vs ")
            if apv < 0.05:
                if is_better(ranks_dict[cl], ranks_dict[cr]):
                    print(f"{cl} es mejor que {cr} (p-valor ajustado: {apv:.4f})")
                else:
                    print(f"{cr} es mejor que {cl} (p-valor ajustado: {apv:.4f})")
            else:
                print(f"{cl} y {cr} no muestran diferencia significativa (p-valor ajustado: {apv:.4f})")
    else:
        print("\nNo hay suficiente evidencia para rechazar la hipótesis nula.")


def main():
    """Realiza comparaciones 1vs1 o NvsN."""
    tipo_comparacion = input("¿Qué tipo de comparación deseas realizar?\n1: Comparación 1vs1 usando Wilcoxon\n2: Comparación NvsN usando Friedman con Shaffer\nIntroduce 1 o 2: ")

    if tipo_comparacion == "1":
        archivo_1 = input("Introduce la ruta del archivo 1 (JSON): ")
        archivo_2 = input("Introduce la ruta del archivo 2 (JSON): ")
        hipervolumenes_1 = cargar_hipervolumenes(archivo_1)
        hipervolumenes_2 = cargar_hipervolumenes(archivo_2)

        prueba_wilcoxon(hipervolumenes_1, hipervolumenes_2, archivo_1, archivo_2)

    elif tipo_comparacion == "2":
        archivos = []
        nombres_metodos = []

        while True:
            archivo = input("Introduce la ruta del archivo (JSON) o escribe 'n' para terminar: ")
            if archivo.lower() == 'n':
                break
            archivos.append(archivo)
            nombres_metodos.append(os.path.basename(archivo).split(".")[0])

        hipervolumenes_por_metodo = {}
        for nombre, archivo in zip(nombres_metodos, archivos):
            hipervolumenes_por_metodo[nombre] = cargar_hipervolumenes(archivo)

        if len(hipervolumenes_por_metodo) > 1:
            friedman_y_shaffer(hipervolumenes_por_metodo)
        else:
            print("No hay suficientes métodos para ejecutar la prueba de Friedman.")

    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main()