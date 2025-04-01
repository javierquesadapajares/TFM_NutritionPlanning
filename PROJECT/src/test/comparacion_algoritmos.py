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
    """Carga los hipervolumenes desde un archivo JSON y los almacena en un diccionario."""

    with open(ruta_archivo, 'r') as f:
        datos = json.load(f)

    hipervolumenes = {}

    for sujeto in datos:
        seeds = datos[sujeto]
        for entry in seeds:
            # Si no es un número, asigna 0 en su lugar
            if isinstance(entry['hipervolumen'], (int, float)):
                hipervolumenes[(sujeto, entry['seed'])] = float(entry['hipervolumen'])
            else:
                hipervolumenes[(sujeto, entry['seed'])] = 0  

    return hipervolumenes

def is_better(rank_1, rank_2):
    """Determina si el primer método es mejor que el segundo basado en los rankings."""
    return rank_1 < rank_2

def prueba_wilcoxon(hipervolumenes_1, hipervolumenes_2, nombre_1, nombre_2):
    """Realiza la prueba de Wilcoxon entre dos conjuntos de hipervolumenes."""

    if len(hipervolumenes_1) < 2 or len(hipervolumenes_2) < 2:
        print(f"No hay suficientes datos para la prueba de Wilcoxon entre {nombre_1} y {nombre_2}. Se necesitan al menos 2 valores en cada grupo.")
        return
    
    _, p_value = stats.wilcoxon(hipervolumenes_1, hipervolumenes_2)

    mediana_1 = np.median(hipervolumenes_1)
    mediana_2 = np.median(hipervolumenes_2)

    print(f"Resultado de la prueba de Wilcoxon entre {nombre_1} y {nombre_2}:")
    print(f"p-value: {p_value:.4f}")
    print(f"Mediana de {nombre_1}: {mediana_1:.4f}")
    print(f"Mediana de {nombre_2}: {mediana_2:.4f}")

    if p_value >= 0.05:
        print("No hay suficiente evidencia para concluir diferencias significativas.")
    else:
        if mediana_1 > mediana_2:
            print(f"{nombre_1} es mejor que {nombre_2}.")
        else:
            print(f"{nombre_2} es mejor que {nombre_1}.")

def friedman_y_shaffer(hipervolumenes, nombres_archivos):
    """Realiza el test de rangos alineados de Friedman y la corrección post-hoc de Shaffer."""

    if len(hipervolumenes) < 2:
        print("No hay suficientes datos para la prueba de Friedman. Se necesitan al menos 2 métodos.")
        return

    _, pv, ranks, _ = friedman_aligned_ranks_test(*hipervolumenes)
    print(f"p-value: {pv:.4f}")

    ranks_dict = {nombre: rank for nombre, rank in zip(nombres_archivos, ranks)}

    ranking_ordenado = sorted(ranks_dict.items(), key=lambda item: item[1])
    print("\nRanking de los métodos (mejor al peor):")
    for i, (nombre, rank) in enumerate(ranking_ordenado, start=1):
        print(f"{i}. {nombre}: ranking promedio = {rank:.4f}")

    if pv < 0.05:
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

        hipervolumenes_1_lista = list(hipervolumenes_1.values())
        hipervolumenes_2_lista = list(hipervolumenes_2.values())

        if len(hipervolumenes_1_lista) > 1 and len(hipervolumenes_2_lista) > 1:
            prueba_wilcoxon(hipervolumenes_1_lista, hipervolumenes_2_lista, archivo_1, archivo_2)
        else:
            print("No hay suficientes datos para ejecutar la prueba de Wilcoxon.")

    elif tipo_comparacion == "2":
        archivos = []
        while True:
            archivo = input("Introduce la ruta del archivo (JSON) o escribe 'n' para terminar: ")
            if archivo.lower() == 'n':
                break
            archivos.append(archivo)

        hipervolumenes = []
        for archivo in archivos:
            datos = cargar_hipervolumenes(archivo)
            valores = list(datos.values())
            hipervolumenes.append(valores)

        if len(hipervolumenes) > 1:
            friedman_y_shaffer(hipervolumenes, archivos)
        else:
            print("No hay suficientes datos para ejecutar la prueba de Friedman.")

    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main()