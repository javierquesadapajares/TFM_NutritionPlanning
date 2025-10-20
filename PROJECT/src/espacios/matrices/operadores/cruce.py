# cruce.py — Cruces guiados por matriz de similitud

import numpy as np
from pymoo.core.crossover import Crossover
from src.utilidades.planificacion import seleccionar_ruleta


def construir_contexto_cruce_matriz(*, sim_matriz, validos_por_posicion, rng):
    """
    Prepara el contexto que usan los cruces por matriz.
    """
    valid_np = [np.asarray(v, dtype=np.int32) for v in validos_por_posicion]
    return {"sim_matriz": sim_matriz, "validos_por_posicion": valid_np, "rng": rng}


class CruceMatrizBase(Crossover):
    """
    Crossover sobre índices usando una matriz de similitud.
    """
    def __init__(self, contexto: dict, prob: float = 1.0):
        super().__init__(2, 2)
        self.ctx = contexto
        self.prob = float(prob)

    @property
    def rng(self):
        return self.ctx["rng"]

    def _do(self, problem, X, **kwargs):
        # normalización a (n_matings, 2, n_genes)
        X_work = np.swapaxes(X, 0, 1) if X.shape[0] == 2 and X.shape[1] != 2 else X

        sim = self.ctx["sim_matriz"]
        validos = self.ctx["validos_por_posicion"]
        n_matings, _, n_genes = X_work.shape
        hijos = np.empty((n_matings, 2, n_genes), dtype=np.int32)

        for m in range(n_matings):
            # padres
            pA = X_work[m, 0].astype(np.int32, copy=False)
            pB = X_work[m, 1].astype(np.int32, copy=False)

            # si prob<prob no hay cruce y se copian los padres
            if self.rng.random() > self.prob:
                hijos[m, 0], hijos[m, 1] = pA, pB
                continue

            h1, h2 = pA.copy(), pB.copy()
            estado = {}

            # por cada gen en el cromosoma
            for pos in range(n_genes):
                idxA, idxB = int(pA[pos]), int(pB[pos])
                cand = validos[pos]     # candidatos permitidos

                # si no hay candidatos se hereda el indice del padre
                if cand.size == 0:
                    h1[pos], h2[pos] = idxA, idxB
                    continue

                # filas de similitud
                simA, simB = sim[idxA], sim[idxB]

                # hijo 1
                s1 = self.construir_scores_h1(simA, simB, pos, idxA, idxB, estado)
                if np.isscalar(s1):
                    h1[pos] = int(s1)
                else:
                    w1 = np.asarray(s1, dtype=float)
                    w1[idxA] = 0.0  # evita que el hijo copie tal cual al padre
                    h1[pos] = int(seleccionar_ruleta(self.rng, w1[cand], indices_validos=cand))

                # hijo 2
                s2 = self.construir_scores_h2(simA, simB, pos, idxA, idxB, estado)
                if np.isscalar(s2):
                    h2[pos] = int(s2)
                else:
                    w2 = np.asarray(s2, dtype=float)
                    w2[idxB] = 0.0
                    h2[pos] = int(seleccionar_ruleta(self.rng, w2[cand], indices_validos=cand))

            hijos[m, 0], hijos[m, 1] = h1, h2

        # devolver con forma (2, n_matings, n_genes)
        return np.swapaxes(hijos, 0, 1)


    def construir_scores_h1(self, simA, simB, pos, idxA, idxB, estado):
        raise NotImplementedError

    def construir_scores_h2(self, simA, simB, pos, idxA, idxB, estado):
        raise NotImplementedError


class CruceMatrizConsensoPonderado(CruceMatrizBase):
    """
    score = (1 - alpha) * simA + alpha * simB
    """
    def __init__(self, contexto: dict, prob: float = 1.0,
                 alpha_h1=(0.0, 1.0), alpha_h2=(0.0, 1.0), por_gen=True):
        super().__init__(contexto, prob)
        self.alpha_h1, self.alpha_h2 = alpha_h1, alpha_h2
        self.por_gen = bool(por_gen)

    def muestrear_alpha(self, cfg):
        """Devuelve un alpha uniforme en [a,b], ordenado y recortado a [0,1]."""
        a, b = float(cfg[0]), float(cfg[1])
        if a > b: a, b = b, a
        a, b = max(0.0, min(a, 1.0)), max(0.0, min(b, 1.0))
        return float(self.rng.uniform(a, b))

    def alphas(self, estado, forzar_nuevo=False):
        """
        Decide si se fija un alpha por hijo o se muestrea un alpha nuevo en cada gen.
        """
        if not self.por_gen and not forzar_nuevo:
            if "a1" not in estado: estado["a1"] = self.muestrear_alpha(self.alpha_h1)
            if "a2" not in estado: estado["a2"] = self.muestrear_alpha(self.alpha_h2)
            return estado["a1"], estado["a2"]
        return self.muestrear_alpha(self.alpha_h1), self.muestrear_alpha(self.alpha_h2)

    def construir_scores_h1(self, simA, simB, pos, idxA, idxB, estado):
        a1, _ = self.alphas(estado, forzar_nuevo=self.por_gen)
        return (1.0 - a1) * np.asarray(simA, dtype=float) + a1 * np.asarray(simB, dtype=float)

    def construir_scores_h2(self, simA, simB, pos, idxA, idxB, estado):
        _, a2 = self.alphas(estado, forzar_nuevo=self.por_gen)
        return (1.0 - a2) * np.asarray(simA, dtype=float) + a2 * np.asarray(simB, dtype=float)


class CruceMatrizAntiConsenso(CruceMatrizBase):
    """
    Favorece candidatos alejados de ambos padres.
    2 - (simA + simB)
    """
    def __init__(self, contexto: dict, prob: float = 1.0, excluir_padres=True):
        super().__init__(contexto, prob)
        self.excluir_padres = bool(excluir_padres)

    def calcular_scores(self, simA, simB, idxA, idxB):
        s = (1.0 - np.asarray(simA, dtype=float)) + (1.0 - np.asarray(simB, dtype=float))
        if self.excluir_padres:
            s[idxA] = 0.0
            s[idxB] = 0.0
        return s

    def construir_scores_h1(self, simA, simB, pos, idxA, idxB, estado):
        return self.calcular_scores(simA, simB, idxA, idxB)

    def construir_scores_h2(self, simA, simB, pos, idxA, idxB, estado):
        return self.calcular_scores(simA, simB, idxA, idxB)