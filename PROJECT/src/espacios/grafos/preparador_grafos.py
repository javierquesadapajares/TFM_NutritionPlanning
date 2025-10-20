# preparador_grafos.py - Preparación y ejecución única en el espacio de grafos
# Crea el problema, prepara válidos, elige grafos, construye contexto, define operadores y ejecuta.

import os
import numpy as np
import networkx as nx
import pickle
import networkx as nx
try:
    from networkx.readwrite import gpickle as nx_gpickle
except Exception:
    nx_gpickle = None
from pymoo.operators.crossover.pntx import TwoPointCrossover
from src.algoritmo.problema import PlanningComida
from src.algoritmo.ejecutor_ag import ejecutar_nsga3
from src.utilidades.planificacion import (
    construir_validos_por_posicion,
    tipos_por_posicion,
)
from src.algoritmo.inicializacion_mutacion import InicializacionCustom, MutacionCustom
from src.espacios.grafos.operadores.cruce import (
    CruceCaminoCorto,
    CruceCaminosSesgados,
)
from src.espacios.grafos.operadores.mutacion import (
    MutacionRadioGrafo,
    MutacionComunidadesGrafo,
)

from src.espacios.grafos.operadores.precalculos import construir_contexto_local, GrafosCtx


TIPOS = ["desayuno", "bebida_desayuno", "snacks", "almuerzo_cena", "bebidas"]

def leer_gpickle(ruta: str):
    # NX 2.x
    f = getattr(nx, "read_gpickle", None)
    if callable(f):
        return f(ruta)
    # NX 3.x
    if nx_gpickle is not None:
        try:
            return nx_gpickle.read_gpickle(ruta)
        except Exception:
            pass
    # Fallback: pickle puro
    with open(ruta, "rb") as h:
        return pickle.load(h)


def clave(s):
    return str(s).strip().lower()

def ruta_grafo(base_dir, metrica, filtro, tipo):
    fname = f"grafo_{metrica}_{filtro}_{tipo}.gpickle"
    return os.path.join(base_dir, fname)

def cargar_grafos(metrica: str, filtro: str, base_dir: str):
    """
    Lee los 5 grafos por métrica.
    """
    Gs = {}
    for t in TIPOS:
        ruta = ruta_grafo(base_dir, metrica, filtro, t)
        Gs[clave(t)] = leer_gpickle(ruta)
    return Gs


def construir_contexto_grafos(grafos: dict):
    """
    Crea el contexto rápido con todo precalculado.
    """
    ctx_por_tipo = {}
    for t, G in grafos.items():
        ctx_por_tipo[clave(t)] = construir_contexto_local(G)
    return GrafosCtx(por_tipo=ctx_por_tipo)


def preparar_operadores_grafos(
    problema,
    *,
    grafos: dict,
    ctx_grafos: GrafosCtx,
    cruce: str = "camino",          # "caminatas" | "camino" | "twopoint"
    mutacion: str = "radio",        # "radio" | "comunidades" | "custom"
    prob_cruce: float = 0.9,
    prob_mutacion: float = 1/77,
    rng=None,
):
    """
    Construye sampling + crossover + mutation para grafos.
    """
    rng = rng or np.random.default_rng()

    sampling = InicializacionCustom(problema, rng=rng)

    if cruce == "camino":
        crossover = CruceCaminoCorto(grafos=grafos, ctx_grafos=ctx_grafos, prob=prob_cruce, rng=rng)
    elif cruce == "caminatas":
        crossover = CruceCaminosSesgados(grafos=grafos, ctx_grafos=ctx_grafos, prob=prob_cruce, rng=rng)
    elif cruce == "twopoint":
        crossover = TwoPointCrossover(prob=prob_cruce)
    else:
        raise ValueError(f"Cruce no reconocido: {cruce}")

    if mutacion == "radio":
        mutation = MutacionRadioGrafo(
            problema, grafos=grafos, prob=prob_mutacion, rng=rng,
            ctx_grafos=ctx_grafos, radio=2, epsilon=0.05
        )
    elif mutacion == "comunidades":
        mutation = MutacionComunidadesGrafo(
            problema, grafos=grafos, prob=prob_mutacion, rng=rng,
            ctx_grafos=ctx_grafos, p_local=0.75
        )
    elif mutacion == "custom":
        mutation = MutacionCustom(problema, prob_mutacion=prob_mutacion, rng=rng)
    else:
        raise ValueError(f"Mutación no reconocida: {mutacion}")

    return {"sampling": sampling, "crossover": crossover, "mutation": mutation}


def ejecutar_grafos(
    comida_bd,
    objetivo_calorias,
    edad,
    gustos,
    no_gustos,
    alergias,
    *,
    metrica="coseno",               # "coseno" | "braycurtis" | "jaccard"
    filtro="knn",                   # "knn" | "knn_doble" | "umbral"
    carpeta_grafos=None,            
    cruce="camino",                 # "camino" | "caminatas"
    mutacion="radio",               # "radio"  | "comunidades"
    prob_cruce=0.9,
    prob_mutacion=1/77,
    seed=42,
    verbose=True,
):
    """
    Ejecuta una vez el espacio de grafos.
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

    # carga grafos (uno por tipo) y contexto
    base = os.path.join("data", "procesado", "grafos")
    grafos = cargar_grafos(metrica, filtro, base)
    ctx_grafos = construir_contexto_grafos(grafos)

    # operadores
    rng = np.random.default_rng(seed)
    operadores = preparar_operadores_grafos(
        problema,
        grafos=grafos,
        ctx_grafos=ctx_grafos,
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