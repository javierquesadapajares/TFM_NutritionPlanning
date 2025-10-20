# mutacion.py - Mutaciones guiadas por grafo

import numpy as np
import networkx as nx
from pymoo.core.mutation import Mutation

from src.utilidades.planificacion import (
    tipos_por_posicion,
    construir_validos_por_posicion,
    seleccionar_ruleta,
)

from src.espacios.grafos.operadores.precalculos import GraphLocalCtx, GrafosCtx


def clave(tipo):
    return str(tipo).strip().lower()

def peso(G, u, v):
    return float(G[u][v].get("weight", 0.0)) if G.has_edge(u, v) else 0.0


class MutacionGrafoBase(Mutation):
    """
    Recorre cada gen y aplica la mutación con probabilidad 'prob'.
    Si hay 'ctx_grafos' lo usa.
    """
    def __init__(self, problem, grafos, prob=0.1, rng=None,
                 validos_por_posicion=None, ctx_grafos=None, edad=18):
        super().__init__()
        self.problem = problem
        self.grafos = grafos or {}
        self.prob = float(prob)
        self.rng = rng or np.random.default_rng()
        self.ctx = ctx_grafos

        self.tipos = [ clave(t) for t in tipos_por_posicion() ]

        if validos_por_posicion is not None:
            self.validos = validos_por_posicion
        else:
            comida_bd = getattr(problem, "comida_bd", [])
            self.validos = construir_validos_por_posicion(comida_bd, edad)

        # cache de grafo por posición
        self.grafo_pos = [ self.recurso(pos)[0] for pos in range(len(self.tipos)) ]

    def recurso(self, pos):
        """
        Si hay contexto precalculado para ese rol, se usa.
        """
        k = self.tipos[pos]
        ctx_local = self.ctx.por_tipo[k]
        G = ctx_local.G
        return G, ctx_local

    def _do(self, problem, X, **kwargs):
        n, m = X.shape
        m = min(m, len(self.tipos))

        for i in range(n):
            x = X[i]
            for pos in range(m):
                if self.rng.random() >= self.prob:
                    continue

                actual = int(x[pos])

                # usa contexto para velocidad
                G, ctx_local = self.recurso(pos)

                # si hay problemas muta aleatoriamente entre válidos
                if G is None or actual not in G or G.number_of_nodes() <= 1:
                    cand = self.validos[pos]
                    if cand.size > 0:
                        x[pos] = int(self.rng.choice(cand))
                    continue

                nuevo = self.mutar(G, ctx_local, actual, pos)

                if nuevo is None:
                    cand = self.validos[pos]
                    if cand.size > 0:
                        nuevo = int(self.rng.choice(cand))
                    else:
                        nuevo = actual
                x[pos] = int(nuevo)

        return X

    def mutar(self, G, ctx_local, actual, pos):
        raise NotImplementedError


class MutacionRadioGrafo(MutacionGrafoBase):
    """
    Elige entre vecinos directos y vecinos con radio 2.
    """
    def __init__(self, problem, grafos, prob=0.1, rng=None, validos_por_posicion=None,
                 ctx_grafos=None, edad=18, radio=2, epsilon=0.05):
        super().__init__(problem, grafos, prob, rng, validos_por_posicion, ctx_grafos, edad)
        self.radio = max(1, int(radio))
        self.epsilon = float(epsilon)

    def mutar(self, G, ctx_local, actual, pos):
        # salto aleatorio
        if self.epsilon > 0 and self.rng.random() < self.epsilon:
            cand = self.validos[pos]
            if cand.size > 0:
                return int(self.rng.choice(cand))
            return None

        # vecinos directos
        if self.radio == 1:
            vecinos = list(G.neighbors(actual))
            if not vecinos:
                return None
            
            # filtra por válidos de ese tipo
            permitidos = set(map(int, self.validos[pos])) if self.validos[pos].size else None
            cand = [int(v) for v in vecinos if (permitidos is None or int(v) in permitidos)]
            if not cand:
                return None
            
            # poonderación por peso de aristas
            pesos = [peso(G, actual, v) for v in cand]

            # ruleta sobre candidatos
            elegido = seleccionar_ruleta(self.rng, pesos, indices_validos=np.asarray(cand, dtype=int))
            return int(elegido) if elegido is not None else None

        # radio 2: vecinos directos + vecinos de vecinos
        vecinos1 = list(G.neighbors(actual))
        if not vecinos1:
            return None

        scores = {}

        # directos
        for v in vecinos1:
            w = peso(G, actual, v)
            if w > 0.0:
                iv = int(v)
                scores[iv] = max(scores.get(iv, 0.0), float(w))

        # a 2 saltos
        vistos = {int(actual)} | {int(x) for x in vecinos1}
        for h in vecinos1:
            w_uh = peso(G, actual, h)
            if w_uh <= 0.0:
                continue
            for v in G.neighbors(h):
                iv = int(v)
                if iv in vistos:
                    continue
                w_hv = peso(G, h, v)
                if w_hv <= 0.0:
                    continue
                score = float(min(w_uh, w_hv))
                if score > scores.get(iv, 0.0):
                    scores[iv] = score

        if not scores:
            return None

        permitidos = set(map(int, self.validos[pos])) if self.validos[pos].size else None
        cand = np.array([c for c in scores.keys() if (permitidos is None or c in permitidos)], dtype=int)
        if cand.size == 0:
            return None

        pesos = [scores[c] for c in cand]
        elegido = seleccionar_ruleta(self.rng, pesos, indices_validos=cand)
        return int(elegido) if elegido is not None else None


class MutacionComunidadesGrafo(MutacionGrafoBase):
    """
    Elige dentro de la misma comunidad con prob. Si no, elige en otra.
    """
    def __init__(self, problem, grafos, prob=0.1, rng=None, validos_por_posicion=None,
                 ctx_grafos=None, edad=18, p_local=0.75):
        super().__init__(problem, grafos, prob, rng, validos_por_posicion, ctx_grafos, edad)
        self.p_local = float(p_local)

    def mutar(self, G, ctx_local, actual, pos):

        # pasa el id de la BD a posición de array
        pos_actual = ctx_local.g2l.get(int(actual), None)
        if pos_actual is None:
            return None

        # coomunidad del nodo y sus miembros
        cid = int(ctx_local.comm_id[pos_actual])

        if cid >= 0 and cid < len(ctx_local.communities):
            # nodos en la comunidad del noodo
            dentro = ctx_local.communities[cid]
            dentro = dentro[dentro != pos_actual]

            # nodos en otras coomunidades
            fuera_list = [ctx_local.communities[c] for c in range(len(ctx_local.communities)) if c != cid]
            fuera = np.concatenate(fuera_list) if fuera_list else np.empty(0, dtype=int)
        else:
            # si el nodo no tiene comunidad, se usan el resto de nodos
            todo = np.arange(ctx_local.l2g.size, dtype=int)
            fuera = todo[todo != pos_actual]
            dentro = np.empty(0, dtype=int)

        # convierte posiciones de array a ids BD
        def pos_a_id(arr):
            return ctx_local.l2g[arr] if arr.size else np.empty(0, dtype=int)

        # proobabilidad de elegir dentro de comunidad
        elegir_dentro = (self.rng.random() < self.p_local)
        cand = pos_a_id(dentro if elegir_dentro else fuera)
        if cand.size == 0:
            cand = pos_a_id(fuera if elegir_dentro else dentro)
            if cand.size == 0:
                return None

        # aplicar válidos del tipo
        permitidos = set(map(int, self.validos[pos])) if self.validos[pos].size else None
        if permitidos is not None:
            cand = cand[np.fromiter((int(v) in permitidos for v in cand), dtype=bool)]
            if cand.size == 0:
                return None

        # pesos para la ruleta. Usa la arista. Si no, fuerza del nodo
        pesos = []
        for v in cand:
            w = peso(G, actual, int(v))
            if w <= 0.0:
                pos_v = ctx_local.g2l.get(int(v), None)
                w = float(ctx_local.deg_weight[pos_v]) if pos_v is not None else 0.0
            pesos.append(float(w))

        elegido = seleccionar_ruleta(self.rng, pesos, indices_validos=cand)
        return int(elegido) if elegido is not None else None