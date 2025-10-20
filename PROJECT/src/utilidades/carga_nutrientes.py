# carga_nutrientes.py — Carga y prepara nutrientes
# Incluye: cargar datos, normalizar (0–1) y binarizar a one-hot.

import numpy as np
from sklearn.preprocessing import MinMaxScaler

from src.utilidades.carga_datos_csv import leer_comidas
from src.utilidades.constantes import UMBRAL_BINARIZACION


def cargar_datos_comida():
    """
    Carga datos de la BD y devuelve:
    - datos: lista de dicts originales
    - nombres: lista de nombres de alimentos
    - nutrientes: array (N, 4) con [calorias, proteinas, carbohidratos, grasas]
    """
    datos = leer_comidas()
    nombres = [a["nombre"] for a in datos]
    nutrientes = np.array(
        [[a["calorias"], a["proteinas"], a["carbohidratos"], a["grasas"]] for a in datos]
    )
    return datos, nombres, nutrientes


def normalizar_nutrientes(nutrientes):
    """Normaliza columnas a [0, 1]."""
    scaler = MinMaxScaler()
    return scaler.fit_transform(nutrientes)


def binarizar_nutrientes_onehot(nutrientes):
    """
    Binariza cada nutriente en bajo/medio/alto usando UMBRAL_BINARIZACION.
    Devuelve un array (N, 12) en el orden:
    [cal_bajo, cal_medio, cal_alto, prot_bajo, ..., gras_alto].
    """
    claves = ["calorias", "proteinas", "carbohidratos", "grasas"] 
    n = nutrientes.shape[0]
    out = np.zeros((n, 3 * len(claves)), dtype=np.uint8)

    col = 0
    for i, k in enumerate(claves):
        bajo, alto = UMBRAL_BINARIZACION[k]
        v = nutrientes[:, i]
        low = v <= bajo
        mid = (v > bajo) & (v <= alto)
        high = v > alto
        out[low, col] = 1
        out[mid, col + 1] = 1
        out[high, col + 2] = 1
        col += 3

    return out

def extraer_matriz_nutrientes(comida_bd):
    """Devuelve la matriz [calorias, proteinas, carbohidratos, grasas] a partir de comida_bd."""
    import numpy as np
    return np.array([
        [a["calorias"], a["proteinas"], a["carbohidratos"], a["grasas"]]
        for a in comida_bd
    ], dtype=float)


def preparar_datos(retornar_comida=False):
    """
    Prepara datos para el modelo:
    - normalizados: (N, 4) en [0, 1]
    - binarizados: (N, 12) one-hot
    Devuelve (nombres, normalizados, binarizados) o
    (datos, nombres, normalizados, binarizados) si retornar_comida=True.
    """
    datos, nombres, nutrientes = cargar_datos_comida()
    normalizados = normalizar_nutrientes(nutrientes)
    binarizados = binarizar_nutrientes_onehot(nutrientes)

    if retornar_comida:
        return datos, nombres, normalizados, binarizados
    return nombres, normalizados, binarizados