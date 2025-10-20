# construir_matrices.py — Calcula y guarda matrices de similitud

import os
import numpy as np

from src.utilidades.carga_nutrientes import preparar_datos
from src.espacios.matrices.metricas_similitud import (
    calcular_similitud_coseno,
    calcular_similitud_braycurtis,
    calcular_similitud_jaccard,
)

# Carpeta de salida
DIR_SIMILITUD = os.path.join("data", "procesado", "matrices", "similitud")

def guardar_matriz(matriz, nombre):
    """Guarda .npy en data/procesado/matrices/similitud/."""
    os.makedirs(DIR_SIMILITUD, exist_ok=True)
    ruta = os.path.join(DIR_SIMILITUD, nombre)
    np.save(ruta, matriz)
    print(f"Guardado: {ruta}")

def generar_matrices_similitud():
    """Calcula y guarda coseno, Bray–Curtis y Jaccard."""
    _, nutrientes_norm, nutrientes_onehot = preparar_datos()

    print("Matriz coseno.")
    sim_cos = calcular_similitud_coseno(nutrientes_norm)
    guardar_matriz(sim_cos, "matriz_coseno.npy")

    print("Matriz Bray–Curtis.")
    sim_bc = calcular_similitud_braycurtis(nutrientes_norm)
    guardar_matriz(sim_bc, "matriz_braycurtis.npy")

    print("Matriz Jaccard.")
    sim_j = calcular_similitud_jaccard(nutrientes_onehot)
    guardar_matriz(sim_j, "matriz_jaccard.npy")

if __name__ == "__main__":
    generar_matrices_similitud()