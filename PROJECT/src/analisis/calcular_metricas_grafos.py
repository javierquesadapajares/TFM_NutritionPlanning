# calcular_metricas_grafos.py - Lee los grafos y crea un .csv como resumen

import os
import sys
import math
import pickle
import pandas as pd
import networkx as nx

# Compatibilidad NX 3.x (gpickle)
try:
    from networkx.readwrite import gpickle as nx_gpickle
except Exception:
    nx_gpickle = None


THIS_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
GRAFOS_DIR = os.path.join(PROJECT_DIR, "data", "procesado", "grafos")
CSV_SALIDA = os.path.join(GRAFOS_DIR, "resumen_grafos.csv")
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)


def leer_gpickle(ruta: str):
    """Intenta leer con NX 2.x/3.x; si falla, pickle."""
    f = getattr(nx, "read_gpickle", None)
    if callable(f):
        return f(ruta)
    if nx_gpickle is not None:
        try:
            return nx_gpickle.read_gpickle(ruta)
        except Exception:
            pass
    with open(ruta, "rb") as h:
        return pickle.load(h)


def parse_filename(fname: str):
    """
    Formato: grafo_{metrica}_{filtrado}_{tipo}.gpickle.
    """
    base = os.path.basename(fname).lower()
    if base.startswith("grafo_") and base.endswith(".gpickle"):
        cuerpo = base[len("grafo_"):-len(".gpickle")]
        partes = cuerpo.split("_")
        
        if len(partes) >= 3:
            if partes[1] == "knn" and len(partes) >= 4 and partes[2] == "doble":
                metrica = partes[0]
                filtrado = "knn_doble"
                tipo = "_".join(partes[3:])
                return metrica, filtrado, tipo
            metrica = partes[0]
            filtrado = partes[1]
            tipo = "_".join(partes[2:])
            return metrica, filtrado, tipo
    return "desconocido", "desconocido", os.path.splitext(base)[0]


# métricas

def grado_stats(G: nx.Graph):
    deg = [d for _, d in G.degree()]
    m = float(sum(deg)) / len(deg) if deg else 0.0
    var = sum((g - m) ** 2 for g in deg) / len(deg) if deg else 0.0
    return m, math.sqrt(var)

def clustering_medio(G: nx.Graph):
    return float(nx.average_clustering(G))


def modularidad_greedy(G: nx.Graph):
    from networkx.algorithms import community
    comunidades = list(community.greedy_modularity_communities(G))
    mod = community.modularity(G, comunidades)
    return len(comunidades), float(mod)

def apl_y_diametro_gcc(G: nx.Graph):
    if G.number_of_nodes() == 0:
        return float("nan"), float("nan")

    comps = list(nx.connected_components(G))
    if not comps:
        return float("nan"), float("nan")

    GCC = G.subgraph(max(comps, key=len)).copy()
    n = GCC.number_of_nodes()
    if n <= 1:
        return 0.0, 0.0

    apl = float(nx.average_shortest_path_length(GCC))
    diam = float(nx.diameter(GCC))
    return apl, diam


def calcular_metricas(G: nx.Graph):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    comps = list(nx.connected_components(G))
    GCC = G.subgraph(max(comps, key=len)).copy() if comps else nx.Graph()
    dens = float(nx.density(G)) if n > 1 else 0.0
    g_mean, g_std = grado_stats(G)
    clust = clustering_medio(G)
    n_comm, mod = modularidad_greedy(G)
    apl, diam = apl_y_diametro_gcc(G)
    return {
        "n_nodos": n,
        "n_aristas": m,
        "n_componentes": len(comps),
        "tamano_componente_principal": GCC.number_of_nodes(),
        "densidad": dens,
        "grado_medio": g_mean,
        "desviacion_grado": g_std,
        "clustering_medio": clust,
        "n_comunidades": n_comm,
        "modularidad": mod,
        "longitud_media_camino": apl,
        "diametro": diam,
    }


def main():
    archivos = sorted([f for f in os.listdir(GRAFOS_DIR) if f.endswith(".gpickle")])
    if not archivos:
        print("No hay grafos .gpickle.")
        return

    filas = []
    for fname in archivos:
        ruta = os.path.join(GRAFOS_DIR, fname)
        metrica, filtrado, tipo = parse_filename(fname)
        print(f"- {fname}   ({metrica}/{filtrado}/{tipo})")

        G = leer_gpickle(ruta)

        met = calcular_metricas(G)
        met.update({"archivo": fname, "metrica": metrica, "filtrado": filtrado, "tipo": tipo})
        filas.append(met)

    df = pd.DataFrame(filas)
    cols = [
        "metrica", "filtrado", "tipo", "archivo",
        "n_nodos", "n_aristas", "densidad",
        "n_componentes", "tamano_componente_principal",
        "grado_medio", "desviacion_grado", "clustering_medio",
        "n_comunidades", "modularidad",
        "longitud_media_camino", "diametro",
    ]
    df = df[[c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]]

    os.makedirs(GRAFOS_DIR, exist_ok=True)
    df.to_csv(CSV_SALIDA, index=False, encoding="utf-8")
    print(f"CSV: {CSV_SALIDA}")

if __name__ == "__main__":
    main()