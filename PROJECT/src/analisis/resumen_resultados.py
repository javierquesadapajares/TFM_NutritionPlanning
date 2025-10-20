# resumen_resultados.py - Genera un CSV con métricas por configuración y por sujeto.

import os
import csv
import json
import numpy as np

from pymoo.indicators.hv import HV
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting


BASE_PROCESADO = os.path.join("PROJECT", "data", "procesado")
CARPETA_SALIDA = os.path.join(BASE_PROCESADO, "resumen")
CSV_SALIDA = os.path.join(CARPETA_SALIDA, "resumen_metricas_por_config_y_sujeto.csv")


def listar_jsons(base_dir):
    """
    Devuelve todas las rutas a archivos .json,
    excluyendo carpetas que contengan 'hipervolumenes'.
    """
    rutas = []
    for raiz, _, ficheros in os.walk(base_dir):
        if "hipervolumenes" in raiz.lower():
            continue
        for nombre in ficheros:
            if nombre.lower().endswith(".json"):
                rutas.append(os.path.join(raiz, nombre))
    return rutas


def leer_json(ruta):
    """Lee el JSON (sin silencios)."""
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def es_seed_con_exito(seed):
    """Devuelve True si esa seed se marcó como “con soluciones”."""
    return bool(seed.get("genero_soluciones", seed.get("genero", False)))


def es_solucion_factible(sol):
    """Comprueba factibilidad."""
    verif = sol.get("verificacion")
    if verif is None:
        return True
    return (
        verif.get("cumple_restriccion_calorias", False) and
        verif.get("cumple_restriccion_macronutrientes", False) and
        verif.get("cumple_restriccion_alergia", False)
    )


def fitness_factibles_por_sujeto(datos):
    """Junta todas las soluciones factibles de todas las seeds por sujeto."""
    salida = {}
    for entrada_sujeto in datos["resultados"]:
        sid = int(entrada_sujeto["sujeto_id"])
        lista = []
        for seed in entrada_sujeto["soluciones_por_seed"]:
            if not es_seed_con_exito(seed):
                continue
            for sol in seed["soluciones"]:
                if es_solucion_factible(sol):
                    lista.append(sol["fitness"])
        salida[sid] = lista
    return salida


def fitness_factibles_por_seed_y_sujeto(datos):
    """Devuelve las soluciones factibles agrupadas por seed."""
    salida = {}
    for entrada_sujeto in datos["resultados"]:
        sid = int(entrada_sujeto["sujeto_id"])
        lista_por_seed = []
        for seed in entrada_sujeto["soluciones_por_seed"]:
            fitness_seed = []
            if es_seed_con_exito(seed):
                for sol in seed["soluciones"]:
                    if es_solucion_factible(sol):
                        fitness_seed.append(sol["fitness"])
            lista_por_seed.append(fitness_seed)
        salida[sid] = lista_por_seed
    return salida


def frente_no_dominado(matriz):
    """Devuelve el frente no dominado."""
    if not matriz:
        return np.zeros((0, 3), dtype=np.float64)
    S = np.asarray(matriz, dtype=np.float64)
    if S.ndim == 1:
        S = S.reshape(1, -1)
    if len(S) <= 1:
        return S
    nd = NonDominatedSorting().do(S, only_non_dominated_front=True)
    return S[nd]


def calcular_punto_referencia_global(base_dir, margen=0.10):
    """
    Construye el punto de referencia para el HV con un margen del 10%.
    """
    todo_fitness = []
    archivos = listar_jsons(base_dir)

    for ruta in archivos:
        datos = leer_json(ruta)
        por_sujeto = fitness_factibles_por_sujeto(datos)
        for lista in por_sujeto.values():
            todo_fitness.extend(lista)

    S = np.asarray(todo_fitness, dtype=np.float64)
    if S.ndim == 1:
        S = S.reshape(1, -1)
    ref = np.max(S, axis=0) * (1.0 + margen)
    print(f"Punto de referencia: {ref.tolist()}")
    return ref


def hipervolumen_de_seed(fitness_seed, hv):
    """
    Calcula el HV de una seed.
    """
    frente = frente_no_dominado(fitness_seed)
    if frente.shape[0] == 0:
        return 0.0
    return float(hv.do(frente))


def resumir_json_por_sujeto(ruta_json, ref_point):
    """
    Devuelve filas de resumen por sujeto.
    """
    datos = leer_json(ruta_json)
    descripcion = datos.get("descripcion", "")
    por_seed_y_sujeto = fitness_factibles_por_seed_y_sujeto(datos)
    hv_obj = HV(ref_point=np.asarray(ref_point, dtype=np.float64))

    filas = []
    for bloque_sujeto in datos["resultados"]:
        sid = int(bloque_sujeto["sujeto_id"])

        seeds = bloque_sujeto["soluciones_por_seed"]
        n_seeds_total = len(seeds)
        n_exitos = sum(1 for s in seeds if es_seed_con_exito(s))
        success_rate_pct = (n_exitos / n_seeds_total * 100.0) if n_seeds_total > 0 else 0.0

        cv_min_vals = [float(s.get("cv_min", 0.0)) for s in seeds]
        cv_mediana_vals = [float(s.get("cv_mediana", 0.0)) for s in seeds]
        cv_media_vals = [float(s.get("cv_media", 0.0)) for s in seeds]

        cv_min_media = float(np.mean(cv_min_vals)) if n_seeds_total else 0.0
        cv_mediana_media = float(np.mean(cv_mediana_vals)) if n_seeds_total else 0.0
        cv_media_media = float(np.mean(cv_media_vals)) if n_seeds_total else 0.0

        hv_vals = [hipervolumen_de_seed(fitness_seed, hv_obj) for fitness_seed in por_seed_y_sujeto[sid]]
        hv_arr = np.asarray(hv_vals, dtype=np.float64) if hv_vals else np.zeros(0, dtype=np.float64)
        hv_media = float(np.mean(hv_arr)) if hv_arr.size else 0.0
        hv_std = float(np.std(hv_arr)) if hv_arr.size else 0.0
        hv_cv_pct = float(hv_std / hv_media * 100.0) if hv_media > 0.0 else 0.0
        n_seeds_valid_hv = int(np.sum(hv_arr > 0.0))

        filas.append({
            "archivo": os.path.basename(ruta_json),
            "ruta": ruta_json,
            "descripcion": descripcion,
            "sujeto_id": sid,
            "seeds_total": n_seeds_total,
            "success_rate_pct": success_rate_pct,
            "cv_min_media": cv_min_media,
            "cv_mediana_media": cv_mediana_media,
            "cv_media_media": cv_media_media,
            "hv_media": hv_media,
            "hv_std": hv_std,
            "hv_cv_pct": hv_cv_pct,
            "n_seeds_valid_hv": n_seeds_valid_hv
        })

    return filas


def generar_resumen(base_dir=BASE_PROCESADO, csv_salida=CSV_SALIDA, margen_ref=0.10):
    """
    Calcula punto de referencia. Recorre todos los JSON
    Calcula métricas por archivo×sujeto. Guarda el CSV final.
    """

    ref_point = calcular_punto_referencia_global(base_dir, margen=margen_ref)

    rutas = listar_jsons(base_dir)

    todas_filas = []
    for ruta in rutas:
        filas = resumir_json_por_sujeto(ruta, ref_point)
        if filas:
            todas_filas.extend(filas)

    os.makedirs(os.path.dirname(csv_salida), exist_ok=True)
    campos = [
        "archivo", "ruta", "descripcion", "sujeto_id",
        "seeds_total", "success_rate_pct",
        "cv_min_media", "cv_mediana_media", "cv_media_media",
        "hv_media", "hv_std", "hv_cv_pct",
        "n_seeds_valid_hv"
    ]
    with open(csv_salida, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(todas_filas)

    print(f"Resumen guardado en: {csv_salida}")


if __name__ == "__main__":
    generar_resumen()