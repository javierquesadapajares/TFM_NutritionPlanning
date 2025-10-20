# cruce.py - Cruces guiados por grafo

import numpy as np
import networkx as nx
from pymoo.core.crossover import Crossover

from src.utilidades.planificacion import tipos_por_posicion, seleccionar_ruleta
from src.espacios.grafos.operadores.precalculos import (
    GraphLocalCtx, GrafosCtx, asegurar_dist_desde_weight
)

def clave(tipo):
    return str(tipo).strip().lower()

def peso(G, u, v):
    return float(G[u][v].get("weight", 0.0)) if G.has_edge(u, v) else 0.0


class CruceGrafoBase(Crossover):
    """
    Recorre posición a posición y decide el hijo usando el grafo del tipo.
    Si hay 'ctx_grafos', usa estructuras rápidas; si no, usa networkx.
    """
    def __init__(self, grafos=None, ctx_grafos=None, prob=1.0, rng=None):
        super().__init__(2, 2)
        self.grafos = grafos or {}      # dict: tipo -> grafo nx
        self.ctx = ctx_grafos           # GrafosCtx o None
        self.prob = float(prob)
        self.rng = rng or np.random.default_rng()
        self.tipos = [ clave(t) for t in tipos_por_posicion() ]

    def recursos(self, pos):
        """
        Si hay contexto precalculado para ese rol, se usa
        """
        k = self.tipos[pos]
        ctx_local = self.ctx.por_tipo[k]
        G = ctx_local.G
        return G, ctx_local


    def _do(self, problem, X, **kwargs):
        # normalización a (n_parejas, 2, n_genes)
        Xw = np.swapaxes(X, 0, 1) if X.shape[0] == 2 and X.shape[1] != 2 else X
        n_m, _, n_g = Xw.shape
        if len(self.tipos) != n_g:
            self.tipos = [ clave(t) for t in tipos_por_posicion() ]

        hijos = np.empty((n_m, 2, n_g), dtype=int)

        for m in range(n_m):
            pA = Xw[m, 0].astype(int, copy=False)
            pB = Xw[m, 1].astype(int, copy=False)

            # si no hay cruce los padres pasan tal cual
            if self.rng.random() > self.prob:
                hijos[m, 0] = pA
                hijos[m, 1] = pB
                continue

            h1 = pA.copy()
            h2 = pB.copy()

            # por cada gen en el cromosoma
            for pos in range(n_g):
                a = int(pA[pos])
                b = int(pB[pos])
                if a == b:
                    h1[pos] = h2[pos] = a
                    continue

                # se usa el contexto precalculado
                G, ctx_local = self.recursos(pos)
                if G is None or a not in G or b not in G:
                    h1[pos], h2[pos] = a, b
                    continue
                
                # regla de cruce
                na, nb = self.cruzar_gen(G, ctx_local, a, b, pos)
                h1[pos], h2[pos] = int(na), int(nb)

            hijos[m, 0] = h1
            hijos[m, 1] = h2

        # devuelve (2, n_parejas, n_genes)
        return np.swapaxes(hijos, 0, 1)

    def cruzar_gen(self, G, ctx_local, a, b, pos):
        """Devuelve dos nodos hijos a partir de dos padres."""
        raise NotImplementedError


class CruceCaminoCorto(CruceGrafoBase):
    """
    Usa el camino más corto entre a y b. Si hay nodos intermedios,
    elige dos del interior. Si no, deja los padres.
    """
    def cruzar_gen(self, G, ctx_local, a, b, pos):
        asegurar_dist_desde_weight(G)  # crea 'dist' = 1 - weight
        try:
            path = nx.shortest_path(G, source=a, target=b, weight="dist")
        except nx.NetworkXNoPath:
            return a, b
        except Exception:
            # sin peso como último recurso
            try:
                path = nx.shortest_path(G, source=a, target=b)
            except Exception:
                return a, b

        # se devuelven los padres si no hay nodos intermedios
        if len(path) < 3:
            return a, b

        interior = np.asarray(path[1:-1], dtype=int)
        if interior.size == 1:
            v = int(interior[0])
            return v, v

        # se pondera por grado para preferir nodos “conectores”
        grados = np.array([G.degree(int(v), weight="weight") for v in interior], dtype=float)
        hijo1 = seleccionar_ruleta(self.rng, grados, indices_validos=interior)

        # para el segundo hijo, quitamos el primero
        resto = interior[interior != int(hijo1)] if interior.size > 1 else interior
        if resto.size == 0:
            return int(hijo1), int(hijo1)
        grados2 = np.array([G.degree(int(v), weight="weight") for v in resto], dtype=float)
        hijo2 = seleccionar_ruleta(self.rng, grados2, indices_validos=resto)
        return int(hijo1), int(hijo2)


class CruceCaminosSesgados(CruceGrafoBase):
    """
    Pequeñas caminatas desde cada padre hacia el otro.
    Se pondera por peso de arista y se da un bonus si el vecino toca al destino.
    """
    def __init__(self, grafos=None, ctx_grafos=None, prob=1.0, rng=None,
                 pasos=3, repeticiones=2, prob_conservar=0.10, beta=1.0):
        super().__init__(grafos=grafos, ctx_grafos=ctx_grafos, prob=prob, rng=rng)
        self.pasos = int(pasos)
        self.repeticiones = int(repeticiones)
        self.prob_conservar = float(prob_conservar)
        self.beta = float(beta)

    def caminata(self, G, origen, destino, visitas):
        """
        Hace una caminata corta desde un padre intentando acercarse al otro.
        """
        actual = int(origen)
        anterior = None

        for _ in range(self.pasos):

            # vecinos del nodo actual
            vecinos = list(G.neighbors(actual))
            if not vecinos:
                break

            # cálculo del peso para cada vecino
            pesos = []
            for v in vecinos:
                w = peso(G, actual, v)
                # bonus si el vecino está conectado al destino
                bonus = (1.0 + self.beta) if G.has_edge(int(v), int(destino)) else 1.0
                # pequeño castigo a volver atrás inmediata
                if anterior is not None and int(v) == int(anterior):
                    bonus *= 0.7
                pesos.append(w * bonus)

            # si la suma es cero no se elige nada
            s = float(np.sum(pesos))
            if s <= 0.0 or not np.isfinite(s):
                break
            
            # convierte pesos a probabilidades
            idx = int(self.rng.choice(len(vecinos), p=np.asarray(pesos) / s))
            elegido = int(vecinos[idx])

            # se guarda el nodo visitado y se avanza un paso en la caminata
            visitas.append(elegido)
            anterior, actual = actual, elegido

    def cruzar_gen(self, G, ctx_local, a, b, pos):

        # con cierta probabilidad no cruza
        if self.rng.random() < self.prob_conservar:
            return a, b
        
        # se acumula las visitas de varias caminatas en ambas direcciones
        visitas = []
        for _ in range(self.repeticiones):
            self.caminata(G, a, b, visitas)
            self.caminata(G, b, a, visitas)

        if not visitas:
            return a, b

        # frecuencia de aparición en caminatas
        vals, cnts = np.unique(np.asarray(visitas, dtype=int), return_counts=True)

        # probabilidad proporcional a la frecuencia
        p = cnts / cnts.sum()

        if vals.size == 1:
            return int(vals[0]), int(vals[0])

        # elección hijos
        e1 = int(self.rng.choice(vals, p=p))
        resto = vals[vals != e1] if vals.size > 1 else vals
        if resto.size == 0:
            return e1, e1
        
        cnts2 = cnts[vals != e1] if vals.size > 1 else cnts
        p2 = cnts2 / cnts2.sum() if cnts2.sum() > 0 else None
        e2 = int(self.rng.choice(resto, p=p2)) if p2 is not None else int(self.rng.choice(resto))
        return e1, e2