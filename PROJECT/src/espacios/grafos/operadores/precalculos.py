# precalculos.py - Precálculos básicos para trabajar con grafos.
# Calcula distancias, mapeos global a local, vecinos y comunidades.

from dataclasses import dataclass
from typing import Dict, List, Optional

import re
import unicodedata
import numpy as np
import networkx as nx


TIPOS = ["desayuno", "bebida_desayuno", "snacks", "almuerzo_cena", "bebidas"]


def tipo_a_clave(tipo: str):
    """Normaliza el texto a minúsculas, sin acentos y con '_'."""
    s = str(tipo).strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[\\/\-\s]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s



@dataclass
class GraphLocalCtx:
    """
    Datos precalculados por grafo.
    """
    G: nx.Graph
    nodes_g: np.ndarray
    g2l: Dict[int, int]
    l2g: np.ndarray
    nbr_idx: List[np.ndarray]
    nbr_w:   List[np.ndarray]
    deg_weight: np.ndarray
    comm_id:   np.ndarray
    communities: List[np.ndarray]


@dataclass
class GrafosCtx:
    """Contexto de todos los grafos por tipo."""
    por_tipo: Dict[str, GraphLocalCtx]



def asegurar_dist_desde_weight(G: nx.Graph):
    """
    Crea distancia partir de pesos si no existe.
    """
    if nx.get_edge_attributes(G, "dist"):
        return
    for _, _, d in G.edges(data=True):
        w = float(d.get("weight", 0.0))
        d["dist"] = max(0.0, 1.0 - w)


def construir_contexto_local(G: nx.Graph):
    """
    Prepara todo lo necesario para operar rápido sobre el grafo.
    - Crea distancia a partir de pesos si no existe.
    - Asigna a cada id de la BD una posición para usar arrays.
    - Guarda, por posición, la lista de vecinos y sus pesos.
    - Calcula el grado ponderado y las comunidades.
    """
    asegurar_dist_desde_weight(G)

    # lista ordenada de ids como en la BD para poder indexar
    ids_bd = np.fromiter((int(n) for n in G.nodes), dtype=int)
    ids_bd.sort()
    N = ids_bd.size

    # conversión entre el índice de la BD y la posición en el array
    pos_por_id = {int(id_bd): i for i, id_bd in enumerate(ids_bd)}  # BD -> posición
    id_por_pos = ids_bd.copy()                                      # posición -> BD

    # para cada posición, se guardan vecinos y sus pesos
    vecinos_por_pos = [None] * max(N, 1)
    pesos_por_pos   = [None] * max(N, 1)

    for pos in range(N):
        id_bd = int(id_por_pos[pos])
        vecinos_id = list(G.neighbors(id_bd))

        if vecinos_id:
            # se pasan ids de vecinos a posiciones
            vecinos_pos = np.fromiter((pos_por_id.get(int(v), -1) for v in vecinos_id), dtype=int)
            vecinos_pos = vecinos_pos[vecinos_pos >= 0]

            if vecinos_pos.size:
                # pesos alineados con esas posiciones
                pesos = np.fromiter(
                    (float(G[id_bd][int(id_por_pos[j])].get("weight", 0.0)) for j in vecinos_pos),
                    dtype=float
                )
                order = np.argsort(vecinos_pos, kind="mergesort")
                vecinos_por_pos[pos] = vecinos_pos[order]
                pesos_por_pos[pos]   = pesos[order]
                continue

        # si no tiene vecinos, se deja array vacio
        vecinos_por_pos[pos] = np.empty(0, dtype=int)
        pesos_por_pos[pos]   = np.empty(0, dtype=float)

    # grado ponderado
    grado_ponderado = np.zeros(N, dtype=float)
    for nodo_id, w in G.degree(weight="weight"):
        pos = pos_por_id.get(int(nodo_id))
        if pos is not None:
            grado_ponderado[int(pos)] = float(w)

    # comunidades ordenadas
    from networkx.algorithms import community
    if G.number_of_nodes() > 0:
        grupos = list(community.greedy_modularity_communities(G, weight="weight"))
        grupos = sorted(grupos, key=lambda s: (-len(s), min(int(x) for x in s)))
    else:
        grupos = []

    # para cada posición, se guarda su id de comunidadd
    comunidad_por_pos = np.full(N, -1, dtype=int)
    comunidades_en_pos = []
    for cid, grupo in enumerate(grupos):
    
        # conversión de ids de BD a poosición en array
        comp_pos = np.fromiter((pos_por_id.get(int(n), -1) for n in grupo), dtype=int)
        comp_pos = comp_pos[comp_pos >= 0]
        comp_pos.sort()
        comunidades_en_pos.append(comp_pos)
        for j in comp_pos:
            comunidad_por_pos[int(j)] = cid

    # devuelve contexto
    return GraphLocalCtx(
        G=G,
        nodes_g=ids_bd,            # ids de la BD
        g2l=pos_por_id,            # BD -> posición
        l2g=id_por_pos,            # posición -> BD
        nbr_idx=vecinos_por_pos,   # vecinos en posiciones
        nbr_w=pesos_por_pos,
        deg_weight=grado_ponderado,
        comm_id=comunidad_por_pos,     # comunidad por posición
        communities=comunidades_en_pos # listas de posiciones por comunidad
    )



def construir_contexto_grafos(grafos: Dict[str, nx.Graph]):
    """
    Crea el contexto por tipo.
    """
    ctx = {}
    for tipo, G in grafos.items():
        t = tipo_a_clave(tipo)
        if t in TIPOS:
            ctx[t] = construir_contexto_local(G)
    return GrafosCtx(por_tipo=ctx)


def obtener_distancias_a_destino_local(ctx: GraphLocalCtx, dst_local: int):
    """
    Devuelve las distancias desde todos los nodos al destino..
    """
    N = ctx.l2g.size
    out = np.full(N, np.inf, dtype=np.float32)
    dst_g = int(ctx.l2g[int(dst_local)])

    lengths = nx.single_source_dijkstra_path_length(ctx.G, source=dst_g, weight="dist")
    for g, d in lengths.items():
        l = ctx.g2l.get(int(g))
        if l is not None:
            out[int(l)] = float(d)

    return out


def sesgo_exponencial_a_destino_local(ctx: GraphLocalCtx, dst_local: int, beta: float):
    """
    Devuelve exp(-beta * dist) hacia el destino.
    """
    d = obtener_distancias_a_destino_local(ctx, int(dst_local)).astype(np.float32, copy=False)
    return np.exp(-float(beta) * d)



def filtrar_por_permitidos(ctx: GraphLocalCtx, candidatos_pos: np.ndarray, ids_permitidos: set[int]):
    """
    Filtra candidatos usando un conjunto de ids de la BD permitidos.
    """
    if not ids_permitidos or candidatos_pos.size == 0:
        return candidatos_pos

    # Convertir cada posición a su id de la BD y quedarnos con los que están permitidos
    ids_bd = ctx.l2g[candidatos_pos]
    mascara = np.fromiter((int(x) in ids_permitidos for x in ids_bd), dtype=bool, count=ids_bd.size)
    return candidatos_pos[mascara]


def camino_interior_mas_corto(ctx: GraphLocalCtx, a_g: int, b_g: int) -> Optional[List[int]]:
    """
    Devuelve los nodos INTERIORES del camino más corto entre a_g y b_g.
    Si son adyacentes, devuelve [].
    """
    try:
        path = nx.shortest_path(ctx.G, source=int(a_g), target=int(b_g), weight="dist")
    except Exception:
        return None
    if len(path) < 3:
        return []
    interior = path[1:-1]
    return [int(x) for x in interior]