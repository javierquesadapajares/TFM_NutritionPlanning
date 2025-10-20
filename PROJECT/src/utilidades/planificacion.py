# planificacion.py — Utilidades de planificación del menú y helpers comunes

import numpy as np
from src.utilidades.constantes import (
    GruposComida, DIAS_SEMANA, COMIDAS, NUM_DIAS, MAPA_COMPONENTES_POR_COMIDA, TipoComida
)
from src.utilidades.nutricion import calculo_macronutrientes


def filtrar_comida(comida_bd, tipo, edad):
    """Devuelve índices de alimentos válidos según 'tipo' y 'edad'."""
    match tipo:
        case TipoComida.ALMUERZO_CENA:
            return [
                i for i, item in enumerate(comida_bd) if not item["grupo"].startswith(
                    (
                        GruposComida.Frutas.JUGOS_DE_FRUTAS[0],
                        GruposComida.Frutas.ZUMOS[0],
                        GruposComida.Bebidas.BEBIDAS[0],
                        GruposComida.Alcohol.ALCOHOL[0],
                        GruposComida.Lacteos.LecheVaca.LECHE_VACA[0],
                        GruposComida.Lacteos.BEBIDAS_LACTEAS[0],
                        GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0],
                        GruposComida.Azucares.AZUCARES[0],
                        GruposComida.Cereales.CEREALES[0],
                    )
                ) or item["grupo"] in {
                    GruposComida.Cereales.ARROZ[0],
                    GruposComida.Cereales.PASTA[0],
                    GruposComida.Cereales.PIZZAS[0],
                    GruposComida.Cereales.PANES[0],
                }
            ]

        case TipoComida.BEBIDAS:
            bebidas = [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    (
                        GruposComida.Bebidas.BEBIDAS[0],
                        GruposComida.Frutas.JUGOS_DE_FRUTAS[0],
                        GruposComida.Frutas.ZUMOS[0],
                    )
                ) and not item["grupo"].startswith(
                    GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0]
                )
            ]
            if edad >= 18:
                bebidas += [
                    i for i, item in enumerate(comida_bd) if item["grupo"].startswith(GruposComida.Alcohol.ALCOHOL[0])
                ]
            return bebidas

        case TipoComida.DESAYUNO:
            return [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    (
                        GruposComida.Cereales.CEREALES[0],
                        GruposComida.Huevos.HUEVOS[0],
                        GruposComida.Frutas.FRUTAS_GENERALES[0],
                        GruposComida.Carne.CarneGeneral.BACON[0],
                    )
                ) and item["grupo"] not in {
                    GruposComida.Cereales.ARROZ[0],
                    GruposComida.Cereales.PASTA[0],
                    GruposComida.Cereales.PIZZAS[0],
                }
            ]

        case TipoComida.BEBIDA_DESAYUNO:
            return [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(
                    (
                        GruposComida.Lacteos.LecheVaca.LECHE_VACA[0],
                        GruposComida.Lacteos.BEBIDAS_LACTEAS[0],
                        GruposComida.Bebidas.BebidasEnPolvoEsenciasInfusiones.BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES[0],
                        GruposComida.Frutas.ZUMOS[0],
                        GruposComida.Frutas.JUGOS_DE_FRUTAS[0],
                    )
                )
            ]

        case TipoComida.SNACKS:
            return [
                i for i, item in enumerate(comida_bd) if item["grupo"].startswith(("F", "S"))
            ]

        case _:
            return []


def tipos_por_posicion():
    """Tipos por posición a partir de MAPA_COMPONENTES_POR_COMIDA (se recorre semana completa)."""
    tipos = []
    for _ in range(NUM_DIAS):
        for c in COMIDAS:
            tipos.extend(MAPA_COMPONENTES_POR_COMIDA[c["nombre"]])
    return tipos


def plantilla_cromosoma(comida_bd, edad):
    """Devuelve (tipos, válidos) para todo el cromosoma semanal (con caché por tipo)."""
    tipos = tipos_por_posicion()
    cache = {}
    validos = []
    for t in tipos:
        if t not in cache:
            cache[t] = np.array(filtrar_comida(comida_bd, t, edad), dtype=int)
        validos.append(cache[t])
    return tipos, validos


def corregir_solucion(solucion, validos):
    """Sustituye índices fuera del conjunto válido por el primero de su posición."""
    s = np.array(solucion, copy=True)
    for pos in range(len(s)):
        if s[pos] not in validos[pos]:
            s[pos] = validos[pos][0]
    return s


# -----------------------------
# Traducción de soluciones
# -----------------------------

def traducir_solucion(solucion, comida_bd):
    """
    Convierte índices a menú por día y a resumen de nutrientes.
    Devuelve (menu, datos_dia).
    """
    menu = {}
    datos_dia = {dia: {"calorias": 0, "proteinas": 0, "carbohidratos": 0, "grasas": 0} for dia in DIAS_SEMANA}

    idx_global = 0
    for dia in DIAS_SEMANA:
        menu[dia] = {}
        for c in COMIDAS:
            n = c["num_alimentos"]
            lista = []
            cal_tot = 0
            for _ in range(n):
                if idx_global >= len(solucion):
                    break
                idx = int(solucion[idx_global])
                a = comida_bd[idx]
                lista.append(f"- {a['nombre']} ({a['grupo']})")
                cal_tot += a["calorias"]
                datos_dia[dia]["calorias"] += a["calorias"]
                datos_dia[dia]["proteinas"] += a["proteinas"]
                datos_dia[dia]["carbohidratos"] += a["carbohidratos"]
                datos_dia[dia]["grasas"] += a["grasas"]
                idx_global += 1
            menu[dia][c["nombre"]] = (lista, cal_tot)

    for dia, info in datos_dia.items():
        if info["calorias"] > 0:
            p, c, g = calculo_macronutrientes(info["proteinas"], info["carbohidratos"], info["grasas"])
            info["porcentaje_proteinas"] = p
            info["porcentaje_carbohidratos"] = c
            info["porcentaje_grasas"] = g
        else:
            info["porcentaje_proteinas"] = 0
            info["porcentaje_carbohidratos"] = 0
            info["porcentaje_grasas"] = 0

    return menu, datos_dia


# -----------------------------
# Extras comunes: medias, proyección, distancias, ruleta, clip
# -----------------------------

def construir_validos_por_posicion(comida_bd, edad):
    """Lista pos->array de índices válidos según el tipo de esa posición (con caché por tipo)."""
    tpos = tipos_por_posicion()
    cache = {}
    validos = []
    for t in tpos:
        if t not in cache:
            cache[t] = np.array(filtrar_comida(comida_bd, t, edad), dtype=int)
        validos.append(cache[t])
    return validos


def calcular_medias_por_tipo(X_norm, comida_bd, edad):
    """Media nutricional normalizada por tipo de componente."""
    medias = {}
    usados = []
    for c in COMIDAS:
        for t in MAPA_COMPONENTES_POR_COMIDA.get(c["nombre"], []):
            if t not in usados:
                usados.append(t)
    for t in usados:
        idx = np.array(filtrar_comida(comida_bd, t, edad), dtype=int)
        medias[t] = X_norm[idx].mean(axis=0) if idx.size > 0 else None
    return medias


def proyectar_al_mas_cercano(v, pos, X_norm, validos_por_posicion):
    """Índice válido más cercano a v (distancia euclídea) para la posición dada."""
    cand = validos_por_posicion[pos]
    W = X_norm[cand]
    d2 = np.einsum("ij,ij->i", W - v, W - v)
    j = int(np.argmin(d2))
    return int(cand[j])


def distancia_euclidiana(a, b):
    """Distancia euclídea entre dos vectores."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = a - b
    return float(np.sqrt(np.dot(d, d)))


def recortar_01(v):
    """Recorta a [0, 1]."""
    return np.clip(v, 0.0, 1.0)


def normalizar_pesos(w):
    """Devuelve un vector de probabilidades que suma 1 (o None si no aporta info)."""
    w = np.asarray(w, dtype=float)
    if w.size == 0:
        return None
    w = np.nan_to_num(w, nan=0.0, posinf=0.0, neginf=0.0)
    w[w < 0.0] = 0.0
    s = w.sum()
    if s <= 0.0:
        return None
    return w / s


def seleccionar_ruleta(rng, pesos, indices_validos=None):
    """
    Selección por ruleta. Si 'pesos' no sirven, elige uniforme
    sobre 'indices_validos' o sobre el rango len(pesos).
    """
    p = normalizar_pesos(pesos)

    if indices_validos is None:
        n = len(pesos)
        if p is None:
            return int(rng.integers(n))
        return int(rng.choice(np.arange(n, dtype=int), p=p))

    indices_validos = np.asarray(indices_validos, dtype=int)
    if p is None:
        return int(rng.choice(indices_validos))
    if p.shape[0] != indices_validos.shape[0]:
        return int(rng.choice(indices_validos))

    return int(rng.choice(indices_validos, p=p))

def elegir_posiciones_a_mutar(longitud, prob_mut, rng):
    """Devuelve las posiciones a mutar con prob_mut; si no sale ninguna, fuerza una."""
    mask = rng.random(longitud) < prob_mut
    pos = np.nonzero(mask)[0].tolist()
    if not pos:
        pos.append(int(rng.integers(0, longitud)))
    return pos