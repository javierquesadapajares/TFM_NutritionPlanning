# filtrado_aristas.py — Filtros de aristas para grafos de similitud

import heapq
import networkx as nx


def filtrar_knn(grafo: nx.Graph, k: int = 7, weight: str = "weight"):
    """
    KNN simple: para cada nodo conserva sus k aristas de mayor peso.
    """
    G = nx.Graph()
    G.add_nodes_from(grafo.nodes(data=True))

    # top-k por nodo
    for u in grafo.nodes:
        vecinos = [(v, grafo[u][v][weight]) for v in grafo[u] if weight in grafo[u][v]]
        if not vecinos:
            continue

        topk = heapq.nlargest(min(k, len(vecinos)), vecinos, key=lambda x: x[1])
        for v, w in topk:
            G.add_edge(u, v, weight=w)

    return G


def filtrar_knn_doble(grafo: nx.Graph, k: int = 10, weight: str = "weight"):
    """
    KNN doble: mantiene u–v solo si v está en top-k(u) y u en top-k(v).
    """
    G = nx.Graph()
    G.add_nodes_from(grafo.nodes(data=True))

    # top-k por nodo
    knn = {}
    for u in grafo.nodes:
        vec = [(v, grafo[u][v][weight]) for v in grafo[u] if weight in grafo[u][v]]
        if not vec:
            knn[u] = set()
            continue
        topk = heapq.nlargest(min(k, len(vec)), vec, key=lambda x: x[1])
        knn[u] = {v for v, _ in topk}

    # añadir solo aristas recíprocas
    for u in grafo.nodes:
        for v in knn[u]:
            if u in knn.get(v, set()) and u < v:
                G.add_edge(u, v, weight=grafo[u][v][weight])

    return G


def filtrar_umbral(grafo: nx.Graph, umbral: float = 0.8, weight: str = "weight"):
    """
    Conserva aristas con peso >= umbral.
    """
    G = nx.Graph()
    G.add_nodes_from(grafo.nodes(data=True))

    for u, v, d in grafo.edges(data=True):
        if weight in d and d[weight] >= umbral:
            G.add_edge(u, v, weight=d[weight])

    return G