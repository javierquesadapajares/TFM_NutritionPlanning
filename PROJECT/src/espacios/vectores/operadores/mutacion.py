# mutacion.py — Mutaciones en espacio vectorial (nutrientes)
# Altera el vector de nutrientes y proyecta a un índice válido de esa posición.

import numpy as np
from pymoo.core.mutation import Mutation
from src.utilidades.planificacion import proyectar_al_mas_cercano, recortar_01


class MutacionBase(Mutation):
    """
    Base para operadores de mutación.
    Elige posiciones a mutar con probabilidad.
    Con baja probabilidad, salta a otro índice válido distinto (salto discreto).
    """
    def __init__(self, prob=1/77, rng=None):
        super().__init__()
        self.prob = float(prob)
        self.rng = rng or np.random.default_rng()
        self._X = None
        self._validos = None
        self._tipos = None
        self._medias = None
        self.p_salto_idx = 0.02  # 2%

    def vincular(self, problem):
        """Toma referencias a X_normalizado, a los índices válidos por posición y a las medias por tipo."""
        if self._X is None:
            self._X = np.asarray(problem.X_normalizado, dtype=float)
            self._validos = problem.validos_por_posicion
            self._tipos = getattr(problem, "tipos_por_posicion", None)
            self._medias = getattr(problem, "medias_por_tipo", None)

    def _do(self, problem, X, **kwargs):
        """Aplica la mutación a toda la población."""
        self.vincular(problem)
        Y = X.copy().astype(int)
        for i in range(len(Y)):
            Y[i] = self.mutar_individuo(Y[i])
        return Y

    def mutar_individuo(self, x):
        """Mutación de un individuo."""
        x = x.copy().astype(int)

        # selección de posiciones a mutar
        mask = self.rng.random(len(x)) < self.prob
        pos_mut = np.nonzero(mask)[0]
        if pos_mut.size == 0:
            pos_mut = np.array([int(self.rng.integers(0, len(x)))])

        for pos in pos_mut:
            idx = int(x[pos])

            # salto
            if self.rng.random() < self.p_salto_idx:
                cand = self._validos[pos]
                if cand.size > 1:
                    x[pos] = int(self.rng.choice(cand[cand != idx]))
                    continue

            # mutación en continuo y proyección
            v = self._X[idx]
            v2 = self.mutar_vector(v, pos)
            v2 = recortar_01(v2)
            x[pos] = proyectar_al_mas_cercano(v2, pos, self._X, self._validos)

        return x

    def mutar_vector(self, v, pos):
        """Devuelve el vector mutado en continuo (definir en subclase)."""
        raise NotImplementedError


class MutacionGaussiana(MutacionBase):
    """
    Mutación gaussiana.
    Suma ruido normal con desviación.
    """
    def __init__(self, prob=1/77, rng=None, sigma=0.05):
        super().__init__(prob=prob, rng=rng)
        self.sigma = float(sigma)

    def mutar_vector(self, v, pos):
        return v + self.rng.normal(0.0, self.sigma, size=v.shape)


class MutacionOposicion(MutacionBase):
    """
    Mutación por oposición respecto a la media del tipo.
    v' = mu + alpha * (mu - v)  (+ jitter).
    """
    def __init__(self, prob=1/77, rng=None, alpha=1.0, jitter_sigma=0.0):
        super().__init__(prob=prob, rng=rng)
        self.alpha = float(alpha)
        self.jitter_sigma = float(jitter_sigma)

    def mutar_vector(self, v, pos):
        if self._tipos is None or self._medias is None:
            return v
        tipo = self._tipos[pos]
        mu = self._medias.get(tipo, None)
        if mu is None:
            return v
        v_op = mu + self.alpha * (mu - v)
        if self.jitter_sigma > 0.0:
            v_op = v_op + self.rng.normal(0.0, self.jitter_sigma, size=v.shape)
        return v_op