# ejecutor_ag.py — Ejecutor NSGA-III
# Configuración:
# - 100 generaciones
# - población 100
# - direcciones de referencia "incremental" con 12 particiones
# - cruce a dos puntos y mutación/inicialización personalizada

import numpy as np
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.operators.crossover.pntx import TwoPointCrossover

from src.algoritmo.inicializacion_mutacion import InicializacionCustom, MutacionCustom

POBLACION_FIJA = 100
GENERACIONES_FIJAS = 100

def ref_dirs_100_incremental_12(n_objetivos=3):
    """Genera direcciones de referencia 'incremental' con 12 y los ajusta a EXACTAMENTE 100."""
    dirs = get_reference_directions("incremental", n_objetivos, n_partitions=12)
    n = len(dirs)
    if n == POBLACION_FIJA:
        return dirs
    if n > POBLACION_FIJA:
        return dirs[:POBLACION_FIJA]
    extras = np.tile(dirs[-1], (POBLACION_FIJA - n, 1))
    return np.vstack([dirs, extras])

def operadores_indices(problem, prob_cruce=0.9, prob_mutacion=1/77, rng=None):
    """Inicialización por posición + cruce a dos puntos + mutación por posición."""
    rng = rng or np.random.default_rng()
    return {
        "sampling": InicializacionCustom(problem, rng=rng),
        "crossover": TwoPointCrossover(prob=prob_cruce),
        "mutation": MutacionCustom(problem, prob_mutacion=prob_mutacion, rng=rng),
    }

def ejecutar_nsga3(problem, operadores, seed, verbose=True):
    """Ejecuta NSGA-III."""
    ref_dirs = ref_dirs_100_incremental_12(n_objetivos=3)
    alg = NSGA3(
        pop_size=POBLACION_FIJA,
        ref_dirs=ref_dirs,
        sampling=operadores["sampling"] if isinstance(operadores, dict) else operadores.sampling,
        crossover=operadores["crossover"] if isinstance(operadores, dict) else operadores.crossover,
        mutation=operadores["mutation"] if isinstance(operadores, dict) else operadores.mutation,
        eliminate_duplicates=True,
    )
    return minimize(
        problem=problem,
        algorithm=alg,
        termination=("n_gen", GENERACIONES_FIJAS),
        save_history=True,
        verbose=verbose,
        seed=seed,
    )