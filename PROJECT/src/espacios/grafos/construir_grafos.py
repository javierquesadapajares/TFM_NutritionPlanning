# construir_grafos.py — Genera grafos de similitud por tipo de gen
# Crea 3 (matrices) × 3 (filtros) × 5 (tipos) = 45 grafos en data/procesado/grafos/.

import os
import time
import math
import numpy as np
import networkx as nx

from PROJECT.src.utilidades.carga_datos_csv import leer_comidas
from src.utilidades.constantes import TipoComida
from src.utilidades.planificacion import filtrar_comida
from src.espacios.grafos.filtrado_aristas import filtrar_knn, filtrar_knn_doble, filtrar_umbral

DIR_MATRICES = os.path.join("data", "procesado", "matrices")
DIR_GRAFOS   = os.path.join("data", "procesado", "grafos")

MATRICES = {
    "coseno":     "matriz_coseno.npy",
    "braycurtis": "matriz_braycurtis.npy",
    "jaccard":    "matriz_jaccard.npy",
}

K_KNN = 7
K_KNN_DOBLE = 10
UMBRAL = 0.8

TIPOS = [
    ("desayuno",        TipoComida.DESAYUNO),
    ("bebida_desayuno", TipoComida.BEBIDA_DESAYUNO),
    ("snacks",          TipoComida.SNACKS),
    ("almuerzo_cena",   TipoComida.ALMUERZO_CENA),
    ("bebidas",         TipoComida.BEBIDAS),
]

EDAD_REFERENCIA = 18

# utilidades

def asegurar_dir(path):
    os.makedirs(path, exist_ok=True)

def cargar_matriz_similitud(nombre: str):
    """Carga una matriz de similitud."""
    ruta = os.path.join(DIR_MATRICES, MATRICES[nombre])
    return np.load(ruta).astype(np.float32, copy=False)

def indices_validos_por_tipo(comida_bd, tipo_token):
    """Índices válidos para un tipo concreto."""
    return np.asarray(filtrar_comida(comida_bd, tipo_token, EDAD_REFERENCIA), dtype=int)

def construir_grafo(M: np.ndarray, indices: np.ndarray, nombres: list[str] | None, nombre_tipo: str):
    """
    Grafo no dirigido sobre el subconjunto 'indices'. Peso = similitud M[u, v].
    Nodos con atributos: idx (global), idx_local, tipo y nombre (si se pasa).
    """
    G = nx.Graph()
    n = indices.size
    if n == 0:
        return G

    # nodos
    for i_local, i_global in enumerate(indices):
        attrs = {"idx": int(i_global), "idx_local": int(i_local), "tipo": nombre_tipo}
        if nombres is not None:
            attrs["nombre"] = nombres[int(i_global)]
        G.add_node(int(i_global), **attrs)

    # aristas (u < v)
    for a in range(n):
        u = int(indices[a])
        fila = M[u, indices]
        for b in range(a + 1, n):
            v = int(indices[b])
            w = float(fila[b])
            if math.isfinite(w):
                G.add_edge(u, v, weight=w)

    return G


def aplicar_filtro(G: nx.Graph, nombre: str) -> nx.Graph:
    """Aplica knn, knn_doble o umbral."""
    if nombre == "knn":
        return filtrar_knn(G, k=K_KNN, weight="weight")
    if nombre == "knn_doble":
        return filtrar_knn_doble(G, k=K_KNN_DOBLE, weight="weight")
    if nombre == "umbral":
        return filtrar_umbral(G, umbral=UMBRAL, weight="weight")
    raise ValueError("Filtro no reconocido")


def nombre_salida(matriz: str, filtro: str, tipo: str) -> str:
    return f"grafo_{matriz}_{filtro}_{tipo}.gpickle"


def guardar_grafo(G: nx.Graph, ruta: str):
    """Guarda el grafo en formato gpickle."""
    nx.write_gpickle(G, ruta)


def construir_y_guardar(M: np.ndarray, matriz: str, filtro: str, tipo_nombre: str, tipo_token, nombres, comida_bd):
    """Construye y guarda el grafo para una combinación (matriz, filtro, tipo)."""
    idx = indices_validos_por_tipo(comida_bd, tipo_token)
    G = construir_grafo(M, idx, nombres, tipo_nombre)
    Gf = aplicar_filtro(G, filtro)

    asegurar_dir(DIR_GRAFOS)
    ruta = os.path.join(DIR_GRAFOS, nombre_salida(matriz, filtro, tipo_nombre))
    guardar_grafo(Gf, ruta)
    print(f"   ✔ {tipo_nombre:15s}  nodos={Gf.number_of_nodes():4d}  aristas={Gf.number_of_edges():5d}  → {ruta}")


# ejecutar y crear grafos

def main():

    print("Construcción de grafos")
    print(f"Salida:   {DIR_GRAFOS}\n")

    comida_bd = leer_comidas()
    nombres = [a["nombre"] for a in comida_bd]

    matrices = {k: cargar_matriz_similitud(k) for k in MATRICES.keys()}

    filtros = ["knn", "knn_doble", "umbral"]
    total = len(matrices) * len(filtros) * len(TIPOS)
    i = 0

    for nombre_matriz, M in matrices.items():
        print(f"\n[MATRIZ] {nombre_matriz}")
        for filtro in filtros:
            print(f"  - filtro={filtro}")
            for (tipo_nombre, tipo_token) in TIPOS:
                i += 1
                print(f"    ({i:02d}/{total}) {nombre_matriz} · {filtro} · {tipo_nombre}")
                construir_y_guardar(
                    M=M,
                    matriz=nombre_matriz,
                    filtro=filtro,
                    tipo_nombre=tipo_nombre,
                    tipo_token=tipo_token,
                    nombres=nombres,
                    comida_bd=comida_bd,
                )

if __name__ == "__main__":
    main()