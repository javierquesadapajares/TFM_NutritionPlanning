# problema.py — Definición del problema para Pymoo
# Objetivos (minimizar):
#   F1: Desviación calórica respecto al objetivo diario.
#   F2: Desviación total de macronutrientes (P/C/G) respecto a sus objetivos (%).
#   F3: Preferencias de grupos (resta por gustos, suma por no-gustos).
# Restricciones (0 si se cumplen):
#   G1: Alergias (penalización si aparece algún grupo con alergia).
#   G2: Calorías fuera del rango [90%, 110%] del objetivo diario.
#   G3: Macronutrientes fuera de sus rangos permitidos.

import numpy as np
from pymoo.core.problem import Problem

from src.utilidades.constantes import (
    NUM_GENES, NUM_DIAS, NUM_ALIMENTOS_DIARIO,
    OBJETIVO_PROTEINAS, OBJETIVO_CARBOHIDRATOS, OBJETIVO_GRASAS,
    LIMITE_PROTEINAS, LIMITE_CARBOHIDRATOS, LIMITE_GRASAS,
    PENALIZACION_PREFERENCIA, PENALIZACION_ALERGIA
)
from src.utilidades.nutricion import calculo_macronutrientes
from src.utilidades.planificacion import filtrar_comida


# -----------------------------
# OBJETIVOS Y RESTRICCIONES
# -----------------------------

def objetivo_calorias(calorias_diarias, objetivo_calorico):
    """F1: desviación absoluta respecto al objetivo calórico."""
    return np.abs(np.asarray(objetivo_calorico) - np.asarray(calorias_diarias))


def restriccion_calorias(calorias_diarias, objetivo_calorico):
    """G2: penalización si las calorías se salen del ±10% del objetivo."""
    calorias_diarias = np.asarray(calorias_diarias)
    objetivo_calorico = np.asarray(objetivo_calorico)
    li = objetivo_calorico * 0.9
    ls = objetivo_calorico * 1.1
    return np.where((calorias_diarias < li) | (calorias_diarias > ls),
                    np.abs(objetivo_calorico - calorias_diarias),
                    0.0)


def objetivo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias):
    """F2: suma de desviaciones absolutas de P/C/G respecto a sus objetivos (%)."""
    p, c, g = calculo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)
    return (np.abs(p - OBJETIVO_PROTEINAS) +
            np.abs(c - OBJETIVO_CARBOHIDRATOS) +
            np.abs(g - OBJETIVO_GRASAS))


def restriccion_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias):
    """G3: penalización si P/C/G salen de sus rangos permitidos."""
    p, c, g = calculo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)
    pen = np.zeros_like(p, dtype=float)
    pen += np.where((p < LIMITE_PROTEINAS[0]) | (p > LIMITE_PROTEINAS[1]),
                    np.abs(p - OBJETIVO_PROTEINAS), 0.0)
    pen += np.where((c < LIMITE_CARBOHIDRATOS[0]) | (c > LIMITE_CARBOHIDRATOS[1]),
                    np.abs(c - OBJETIVO_CARBOHIDRATOS), 0.0)
    pen += np.where((g < LIMITE_GRASAS[0]) | (g > LIMITE_GRASAS[1]),
                    np.abs(g - OBJETIVO_GRASAS), 0.0)
    return pen


def objetivo_preferencia_grupo(grupos_alimentos, grupos_gusta, grupos_no_gusta):
    """F3: resta por gustos y suma por no-gustos según los grupos de cada alimento."""
    ga = np.asarray(grupos_alimentos)
    if ga.ndim == 1:
        gust = np.isin(ga, grupos_gusta)
        disg = np.isin(ga, grupos_no_gusta)
        return (-np.sum(gust) + np.sum(disg)) * PENALIZACION_PREFERENCIA

    gust = np.isin(ga, grupos_gusta)
    disg = np.isin(ga, grupos_no_gusta)
    return (-gust.sum(axis=1) + disg.sum(axis=1)) * PENALIZACION_PREFERENCIA


def restriccion_alergia(grupos_alimentos, grupos_alergia):
    """G1: penalización por alimentos que pertenecen a grupos con alergia."""
    ga = np.asarray(grupos_alimentos)
    w = (PENALIZACION_ALERGIA ** 2)
    if ga.ndim == 1:
        alerg = np.isin(ga, grupos_alergia)
        return np.sum(alerg) * w

    alerg = np.isin(ga, grupos_alergia)
    return alerg.sum(axis=1) * w


# -----------------------------
# PROBLEMA
# -----------------------------

class PlanningComida(Problem):
    """
    Problema de planificación nutricional usando índices de alimentos.
    Variables: NUM_GENES índices enteros del catálogo.
    """

    def __init__(self, comida_bd, objetivo_calorias, edad,
                 grupos_alergia, grupos_gusta, grupos_no_gusta):

        super().__init__(n_var=NUM_GENES, n_obj=3, n_constr=3,
                         xl=0, xu=len(comida_bd) - 1, elementwise=False)

        self.comida_bd = comida_bd
        self.objetivo_calorias = float(objetivo_calorias)
        self.edad = int(edad)
        self.grupos_alergia = grupos_alergia
        self.grupos_gusta = grupos_gusta
        self.grupos_no_gusta = grupos_no_gusta

        # Listas de índices por tipo de comida
        self.almuerzo_cena   = np.array(filtrar_comida(comida_bd, "almuerzo_cena",   self.edad), dtype=int)
        self.bebidas         = np.array(filtrar_comida(comida_bd, "bebidas",         self.edad), dtype=int)
        self.desayuno        = np.array(filtrar_comida(comida_bd, "desayuno",        self.edad), dtype=int)
        self.bebida_desayuno = np.array(filtrar_comida(comida_bd, "bebida_desayuno", self.edad), dtype=int)
        self.snacks          = np.array(filtrar_comida(comida_bd, "snacks",          self.edad), dtype=int)

        # Campos que se pueden establecer desde otros módulos
        self.X_normalizado = None
        self.validos_por_posicion = None
        self.tipos_por_posicion = None
        self.medias_por_tipo = None

        # Valores precalculados por alimento
        self._cal = np.array([a["calorias"]      for a in self.comida_bd], dtype=float)
        self._pro = np.array([a["proteinas"]     for a in self.comida_bd], dtype=float)
        self._car = np.array([a["carbohidratos"] for a in self.comida_bd], dtype=float)
        self._gra = np.array([a["grasas"]        for a in self.comida_bd], dtype=float)
        self._grp = np.array([a["grupo"]         for a in self.comida_bd], dtype=object)

    def _evaluate(self, X, out, *args, **kwargs):
        """
        X: matriz (N, NUM_GENES) con índices de alimentos.
        Calcula:
          F1 = desviación calórica total
          F2 = desviación de macronutrientes total
          F3 = preferencias (gustos/no-gustos)
          G1 = alergias
          G2 = calorías fuera de rango
          G3 = macronutrientes fuera de rango
        """
        X = X.astype(int, copy=False)
        n_ind, _ = X.shape

        f_cal = np.zeros(n_ind)
        f_mac = np.zeros(n_ind)
        f_pref = np.zeros(n_ind)
        g_ale = np.zeros(n_ind)
        g_cal = np.zeros(n_ind)
        g_mac = np.zeros(n_ind)

        for dia in range(NUM_DIAS):
            ini = dia * NUM_ALIMENTOS_DIARIO
            fin = ini + NUM_ALIMENTOS_DIARIO
            idx = X[:, ini:fin] 

            # Totales del día por individuo
            cals  = self._cal[idx].sum(axis=1)
            pros  = self._pro[idx].sum(axis=1)
            carbs = self._car[idx].sum(axis=1)
            gras  = self._gra[idx].sum(axis=1)

            # Grupos del día por individuo
            grupos_dia = self._grp[idx]

            # Preferencias y alergias
            f_pref += objetivo_preferencia_grupo(grupos_dia, self.grupos_gusta, self.grupos_no_gusta)
            g_ale  += restriccion_alergia(grupos_dia, self.grupos_alergia)

            # Calorías
            f_cal += objetivo_calorias(cals, self.objetivo_calorias)
            g_cal += restriccion_calorias(cals, self.objetivo_calorias)

            # Macronutrientes
            f_mac += objetivo_macronutrientes(pros, carbs, gras)
            g_mac += restriccion_macronutrientes(pros, carbs, gras)

        out["F"] = np.column_stack([f_cal, f_mac, f_pref])
        out["G"] = np.column_stack([g_ale, g_cal, g_mac])