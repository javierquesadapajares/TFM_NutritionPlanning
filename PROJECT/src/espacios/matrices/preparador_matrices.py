# preparador_matrices.py — Preparación y ejecución única en el espacio matricial
# Crea el problema, prepara válidos, elige la matriz de similitud, define operadores y ejecuta.

import os
import numpy as np

from src.algoritmo.problema import PlanningComida
from src.algoritmo.ejecutor_ag import ejecutar_nsga3
from src.algoritmo.inicializacion_mutacion import InicializacionCustom, MutacionCustom

from src.espacios.matrices.operadores.cruce import (
    construir_contexto_cruce_matriz,
    CruceMatrizConsensoPonderado,
    CruceMatrizAntiConsenso,
)
from src.espacios.matrices.operadores.mutacion import (
    construir_contexto_mutacion_matriz,
    MutacionMatrizRuletaSimilitud,
    MutacionMatrizSoftmaxBoltzmann,
)

from src.utilidades.planificacion import (
    construir_validos_por_posicion,
    tipos_por_posicion,
)

def cargar_matriz_similitud(nombre: str):
    """
    Devuelve la matriz de similitud guardada en data/procesado/matrices/.
    """
    base = os.path.join("data", "procesado", "matrices")
    archivo = {
        "coseno": "matriz_coseno.npy",
        "braycurtis": "matriz_braycurtis.npy",
        "jaccard": "matriz_jaccard.npy",
    }[nombre]
    return np.load(os.path.join(base, archivo))



def preparar_operadores_matrices(
    problema,
    *,
    matriz: str = "coseno",        # "coseno"|"braycurtis"|"jaccard"
    cruce: str = "consenso",       # "consenso"|"anticonsenso"|"twopoint"
    mutacion: str = "ruleta",      # "ruleta"|"softmax"| "custom"
    prob_cruce: float = 0.9,
    prob_mutacion: float = 1/77,
    rng=None,
):
    """
    Construye sampling + crossover + mutation usando una matriz de similitud.
    """
    rng = rng or np.random.default_rng()

    sampling = InicializacionCustom(problema, rng=rng)

    sim = cargar_matriz_similitud(matriz)
    validos = problema.validos_por_posicion

    if cruce == "twopoint":
        from pymoo.operators.crossover.pntx import TwoPointCrossover
        crossover = TwoPointCrossover(prob=prob_cruce)
    elif cruce == "consenso":
        ctx_c = construir_contexto_cruce_matriz(sim_matriz=sim, validos_por_posicion=validos, rng=rng)
        crossover = CruceMatrizConsensoPonderado(ctx_c, prob=prob_cruce)
    elif cruce == "anticonsenso":
        ctx_c = construir_contexto_cruce_matriz(sim_matriz=sim, validos_por_posicion=validos, rng=rng)
        crossover = CruceMatrizAntiConsenso(ctx_c, prob=prob_cruce)

    if mutacion == "custom":
       mutation = MutacionCustom(problema, prob_mutacion=prob_mutacion, rng=rng)
    elif mutacion == "ruleta":
        ctx_m = construir_contexto_mutacion_matriz(sim_matriz=sim, validos_por_posicion=validos, rng=rng)
        mutation = MutacionMatrizRuletaSimilitud(ctx_m, prob=prob_mutacion)
    elif mutacion == "softmax":
        ctx_m = construir_contexto_mutacion_matriz(sim_matriz=sim, validos_por_posicion=validos, rng=rng)
        mutation = MutacionMatrizSoftmaxBoltzmann(ctx_m, prob=prob_mutacion, tau=0.8)

    return {"sampling": sampling, "crossover": crossover, "mutation": mutation}


def ejecutar_matrices(
    comida_bd,
    objetivo_calorias,
    edad,
    gustos,
    no_gustos,
    alergias,
    *,
    matriz="coseno",             # "coseno"|"braycurtis"|"jaccard"
    cruce="consenso",            # "consenso"|"anticonsenso"|"twopoint"
    mutacion="ruleta",           # "ruleta"|"softmax"|"custom"
    prob_cruce=0.9,
    prob_mutacion=1/77,
    seed=42,
    verbose=True,
):
    """
    Ejecuta una vez el espacio matricial.
    Devuelve el resultado de pymoo.
    """
    # problema
    problema = PlanningComida(
        comida_bd=comida_bd,
        objetivo_calorias=objetivo_calorias,
        edad=edad,
        grupos_alergia=alergias,
        grupos_gusta=gustos,
        grupos_no_gusta=no_gustos,
    )

    # válidos por posición y tipos
    problema.validos_por_posicion = construir_validos_por_posicion(comida_bd, edad)
    problema.tipos_por_posicion = tipos_por_posicion()

    # operadores
    rng = np.random.default_rng(seed)
    operadores = preparar_operadores_matrices(
        problema,
        matriz=matriz,
        cruce=cruce,
        mutacion=mutacion,
        prob_cruce=prob_cruce,
        prob_mutacion=prob_mutacion,
        rng=rng,
    )

    # ejecutar
    return ejecutar_nsga3(
        problem=problema,
        operadores=operadores,
        seed=seed,
        verbose=verbose,
    )