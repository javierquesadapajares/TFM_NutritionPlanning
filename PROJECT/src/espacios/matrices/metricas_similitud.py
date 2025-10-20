# metricas_similitud.py — Métricas de similitud entre alimentos
# Coseno, Bray–Curtis y Jaccard.

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import pdist, squareform


def calcular_similitud_coseno(nutrientes):
    """Devuelve la matriz de similitud coseno a partir de vectores normalizados."""
    return cosine_similarity(nutrientes)


def calcular_similitud_braycurtis(nutrientes):
    """Convierte la distancia Bray–Curtis en similitud (1 - distancia)."""
    dist = pdist(nutrientes, metric="braycurtis")
    return 1.0 - squareform(dist)


def calcular_similitud_jaccard(nutrientes_binarios):
    """Devuelve la matriz de similitud Jaccard a partir de vectores one-hot."""
    dist = pdist(nutrientes_binarios, metric="jaccard")
    return 1.0 - squareform(dist)