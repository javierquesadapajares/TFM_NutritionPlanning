# nutricion.py — Utilidades nutricionales
# Contiene:
# - cálculo de porcentajes P/C/G a partir de gramos.
# - calorías totales a partir de P/C/G.
# - suma de nutrientes de una lista de índices.
# - desviaciones respecto a objetivos calóricos y de macros.

import numpy as np

def calculo_macronutrientes(proteinas, carbohidratos, grasas):
    """Devuelve (porc_proteinas, porc_carbohidratos, porc_grasas) sobre el total calórico."""
    proteinas = np.asarray(proteinas)
    carbohidratos = np.asarray(carbohidratos)
    grasas = np.asarray(grasas)

    cal_p = proteinas * 4
    cal_c = carbohidratos * 4
    cal_g = grasas * 9
    total = cal_p + cal_c + cal_g
    total_seguro = np.where(total == 0, 1, total)

    p = (cal_p / total_seguro) * 100
    c = (cal_c / total_seguro) * 100
    g = (cal_g / total_seguro) * 100
    return p, c, g

def calorias_totales(proteinas, carbohidratos, grasas):
    """Devuelve kcal totales a partir de gramos de P/C/G."""
    return proteinas * 4 + carbohidratos * 4 + grasas * 9

def sumar_nutrientes(indices, comida_bd):
    """Suma P/C/G y kcal de una lista de índices de alimentos."""
    p = sum(comida_bd[i]["proteinas"] for i in indices)
    c = sum(comida_bd[i]["carbohidratos"] for i in indices)
    g = sum(comida_bd[i]["grasas"] for i in indices)
    kcal = sum(comida_bd[i]["calorias"] for i in indices)
    return {"proteinas": p, "carbohidratos": c, "grasas": g, "calorias": kcal}

def desviacion_calorias(kcal, objetivo):
    """Desviación absoluta respecto al objetivo calórico."""
    return abs(objetivo - kcal)

def desviacion_macros_porcentual(prot, carb, gras, obj_p, obj_c, obj_g):
    """Suma de |porcentajes - objetivos| dada la ingesta en gramos y los objetivos en %."""
    p, c, g = calculo_macronutrientes(prot, carb, gras)
    return abs(p - obj_p) + abs(c - obj_c) + abs(g - obj_g)