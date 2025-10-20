# preparador_vectores.py - Preparación y ejecución única en el espacio vectorial
# Crea el problema, prepara válidos, carga el contexto, define los operadores y ejecuta

import numpy as np

from src.algoritmo.problema import PlanningComida
from src.algoritmo.ejecutor_ag import ejecutar_nsga3
from src.algoritmo.inicializacion_mutacion import InicializacionCustom, MutacionCustom
from src.espacios.vectores.operadores.cruce import CruceUniforme, CruceSBX
from src.espacios.vectores.operadores.mutacion import MutacionGaussiana, MutacionOposicion
from src.utilidades.carga_nutrientes import extraer_matriz_nutrientes, normalizar_nutrientes
from src.utilidades.planificacion import (
    construir_validos_por_posicion,
    tipos_por_posicion,
    calcular_medias_por_tipo,
)


def preparar_operadores_vectores(
    problema,
    *,
    cruce: str = "twopoint",      # "twopoint"|"uniforme" |"sbx"
    mutacion: str = "custom",     # "custom"|"gaussiana"|"oposicion"
    prob_cruce: float = 0.9,
    prob_mutacion: float = 1/77,
    rng=None,
):
    """Construye sampling + crossover + mutation para el espacio vectorial."""
    rng = rng or np.random.default_rng()

    sampling = InicializacionCustom(problema, rng=rng)

    if cruce == "twopoint":
        from pymoo.operators.crossover.pntx import TwoPointCrossover
        crossover = TwoPointCrossover(prob=prob_cruce)
    elif cruce == "uniforme":
        crossover = CruceUniforme(prob=prob_cruce, rng=rng)
    elif cruce == "sbx":
        crossover = CruceSBX(prob=prob_cruce, rng=rng, eta_c=15.0)

    if mutacion == "custom":
        mutation = MutacionCustom(problema, prob_mutacion=prob_mutacion, rng=rng)
    elif mutacion == "gaussiana":
        mutation = MutacionGaussiana(prob=prob_mutacion, rng=rng, sigma=0.05)
    elif mutacion == "oposicion":
        mutation = MutacionOposicion(prob=prob_mutacion, rng=rng, alpha=1.0, jitter_sigma=0.0)

    return {"sampling": sampling, "crossover": crossover, "mutation": mutation}


def ejecutar_vectores(
    comida_bd,
    objetivo_calorias,
    edad,
    gustos,
    no_gustos,
    alergias,
    *,
    cruce="twopoint",           # "twopoint" | "uniforme" | "sbx"
    mutacion="custom",          # "custom"   | "gaussiana" | "oposicion"
    prob_cruce=0.9,
    prob_mutacion=1/77,
    seed=42,
    verbose=True,
):
    """
    Ejecuta una vez el espacio vectorial.
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

    # matriz de nutrientes normalizada y medias por tipo (para oposición)
    nutrientes = extraer_matriz_nutrientes(comida_bd)
    X_normalizado = normalizar_nutrientes(nutrientes)
    problema.X_normalizado = X_normalizado
    problema.medias_por_tipo = calcular_medias_por_tipo(X_normalizado, comida_bd, edad)

    # operadores
    rng = np.random.default_rng(seed)
    operadores = preparar_operadores_vectores(
        problema,
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