# inicializacion_mutacion.py — Inicialización y mutación por posición
# - InicializacionCustom: genera individuos eligiendo índices válidos por gen.
# - MutacionCustom: recorre genes y cambia a otro índice válido con cierta probabilidad.

import numpy as np
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.core.mutation import Mutation


class InicializacionCustom(IntegerRandomSampling):
    """Crea individuos eligiendo índices válidos por gen."""
    def __init__(self, problem, rng=None):
        super().__init__()
        self.problem = problem
        self.rng = rng or np.random.default_rng()

    def _do(self, problem, n_samples, **kwargs):
        n_var = problem.n_var
        poblacion = np.empty((n_samples, n_var), dtype=int)
        validos = self.problem.validos_por_posicion

        for i in range(n_samples):
            for pos in range(n_var):
                poblacion[i, pos] = int(self.rng.choice(validos[pos]))
        return poblacion


class MutacionCustom(Mutation):
    """Con prob_mutacion por gen, sustituye por otro índice válido de esa posición."""
    def __init__(self, problem, prob_mutacion=1/77, rng=None):
        super().__init__()
        self.problem = problem
        self.prob_mutacion = float(prob_mutacion)
        self.rng = rng or np.random.default_rng()

    def _do(self, problem, X, **kwargs):
        X_mut = X.copy()
        validos = self.problem.validos_por_posicion
        n_var = problem.n_var

        for i in range(len(X_mut)):
            for pos in range(n_var):
                if self.rng.random() < self.prob_mutacion:
                    X_mut[i, pos] = int(self.rng.choice(validos[pos]))
        return X_mut