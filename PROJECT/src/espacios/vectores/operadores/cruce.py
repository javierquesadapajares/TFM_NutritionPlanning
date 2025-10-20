# cruce.py — Cruces en espacio vectorial (nutrientes)
# Combina vectores de nutrientes y proyecta cada gen al índice válido más cercano.

import numpy as np
from pymoo.core.crossover import Crossover
from src.utilidades.planificacion import proyectar_al_mas_cercano, recortar_01


class CruceBase(Crossover):
    """
    Base para operadores de cruce sobre vectores de nutrientes.
    Toma los vectores de los dos padres, aplica regla de cruce
    y proyecta al índice mas cercano."
    """
    def __init__(self, prob=1.0, rng=None):
        super().__init__(2, 2)  # 2 padres → 2 hijos
        self.prob = float(prob)
        self.rng = rng or np.random.default_rng()
        self._X = None
        self._validos = None

    def vincular(self, problem):
        """Toma referencias a X_normalizado y a los índices válidos por posición."""
        if self._X is None:
            self._X = np.asarray(problem.X_normalizado, dtype=float)
            self._validos = problem.validos_por_posicion

    def _do(self, problem, X, **kwargs):
        """Aplica el cruce a un conjunto de parejas y devuelve la descendencia."""
        self.vincular(problem)

        # normalización a (n_parejas, 2, n_genes)
        Xw = X if X.shape[1] == 2 else np.swapaxes(X, 0, 1)
        n_matings, _, n_genes = Xw.shape
        hijos = np.empty((n_matings, 2, n_genes), dtype=int)

        for m in range(n_matings):
            a = Xw[m, 0].astype(int, copy=False)
            b = Xw[m, 1].astype(int, copy=False)

            # si no hay cruce los padres pasan tal cual
            if self.rng.random() > self.prob:
                hijos[m, 0] = a
                hijos[m, 1] = b
                continue

            h1 = a.copy()
            h2 = b.copy()

            # por cada gen en el cromosoma
            for pos in range(n_genes):
                va = self._X[int(a[pos])]
                vb = self._X[int(b[pos])]

                # regla de cruce
                w1, w2 = self.cruzar_vectores(va, vb, pos)

                # recorte y proyección a índice válido
                w1 = recortar_01(w1)
                w2 = recortar_01(w2)
                h1[pos] = proyectar_al_mas_cercano(w1, pos, self._X, self._validos)
                h2[pos] = proyectar_al_mas_cercano(w2, pos, self._X, self._validos)

            hijos[m, 0] = h1
            hijos[m, 1] = h2

        # devuelve (2, n_parejas, n_genes)
        return np.swapaxes(hijos, 0, 1)

    def cruzar_vectores(self, v_a, v_b, pos):
        """Devuelve dos vectores hijos a partir de dos padres."""
        raise NotImplementedError


class CruceUniforme(CruceBase):
    """
    Cruce uniforme.
    Para cada componente del vector, el hijo hereda de A o de B con probabilidad 50%.
    """
    def cruzar_vectores(self, v_a, v_b, pos):
        mask = self.rng.integers(0, 2, size=v_a.shape)  # 0 o 1
        h1 = np.where(mask == 1, v_a, v_b)
        h2 = np.where(mask == 0, v_a, v_b)
        return h1, h2


class CruceSBX(CruceBase):
    """
    SBX (Simulated Binary Crossover).
    Genera dos hijos simétricos alrededor de los padres. 'eta_c' controla la dispersión:
    """
    def __init__(self, prob=1.0, rng=None, eta_c=15.0):
        super().__init__(prob=prob, rng=rng)
        self.eta_c = float(eta_c)

    def cruzar_vectores(self, v_a, v_b, pos):
        u = self.rng.uniform(0.0, 1.0, size=v_a.shape)
        expo = 1.0 / (self.eta_c + 1.0)
        beta = np.where(u <= 0.5, (2.0 * u) ** expo, (1.0 / (2.0 * (1.0 - u))) ** expo)
        h1 = 0.5 * ((1.0 + beta) * v_a + (1.0 - beta) * v_b)
        h2 = 0.5 * ((1.0 - beta) * v_a + (1.0 + beta) * v_b)
        return h1, h2