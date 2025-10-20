# mutacion.py — Mutaciones guiadas por matriz de similitud

import numpy as np
from pymoo.core.mutation import Mutation
from src.utilidades.planificacion import elegir_posiciones_a_mutar, seleccionar_ruleta


def construir_contexto_mutacion_matriz(*, sim_matriz, validos_por_posicion, rng):
    """
    Prepara el contexto que usan las mutaciones por matriz.
    """
    valid_np = [np.asarray(v, dtype=np.int32) for v in validos_por_posicion]
    return {"sim_matriz": sim_matriz, "validos_por_posicion": valid_np, "rng": rng}


class MutacionMatrizBase(Mutation):
    """
    Mutación sobre índices guiada por la matriz de similitud.
    Para cada posición elegida se construyen pesos y se selecciona por ruleta.
    """
    def __init__(self, contexto: dict, prob: float = 1/77):
        super().__init__()
        self.ctx = contexto
        self.prob = float(prob)
        self.p_salto = 0.02        # salto aleatorio
        self.eps_suavizado = 0.01  # suavizado de pesos

    @property
    def rng(self):
        return self.ctx["rng"]

    def _do(self, problem, X, **kwargs):
        Y = X.copy().astype(np.int32, copy=False)
        for i in range(len(Y)):
            Y[i] = self.mutar_individuo(Y[i])
        return Y

    def mutar_individuo(self, x):
        x_nuevo = x.copy().astype(np.int32, copy=False)
        sim = self.ctx["sim_matriz"]
        validos = self.ctx["validos_por_posicion"]

        posiciones = elegir_posiciones_a_mutar(len(x_nuevo), self.prob, self.rng)

        # posiciones elegidas a mutar
        for pos in posiciones:
            idx_actual = int(x_nuevo[pos])
            candidatos = validos[pos]
            if candidatos.size == 0:
                continue

            # salto aleatorio
            if self.rng.random() < self.p_salto:
                otros = candidatos[candidatos != idx_actual]
                if otros.size > 0:
                    x_nuevo[pos] = int(self.rng.choice(otros))
                    continue

            # pesos guiados por similitud
            vec_sim = sim[idx_actual]
            pesos = np.asarray(self.construir_pesos(vec_sim, pos), dtype=float)
            pesos[idx_actual] = 0.0
            pesos_perm = pesos[candidatos]
            pesos_perm = (1.0 - self.eps_suavizado) * pesos_perm + self.eps_suavizado

            nuevo = seleccionar_ruleta(self.rng, pesos_perm, indices_validos=candidatos)
            x_nuevo[pos] = int(nuevo)

        return x_nuevo

    def construir_pesos(self, vector_similitud, pos):
        raise NotImplementedError


class MutacionMatrizRuletaSimilitud(MutacionMatrizBase):
    """Probabilidad proporcional a la similitud."""
    def construir_pesos(self, vector_similitud, pos):
        return np.asarray(vector_similitud, dtype=float)


class MutacionMatrizSoftmaxBoltzmann(MutacionMatrizBase):
    """Probabilidad por softmax con temperatura tau."""
    def __init__(self, contexto: dict, prob: float = 1/77, tau: float = 0.8):
        super().__init__(contexto, prob)
        self.tau = float(tau)

    def construir_pesos(self, vector_similitud, pos):
        sim = np.clip(np.asarray(vector_similitud, dtype=float), 0.0, 1.0)
        sim_centrada = sim - np.max(sim)
        tau_segura = self.tau if self.tau > 1e-12 else 1e-12
        return np.exp(sim_centrada / tau_segura)