# extraer_hipervolumen.py - Extrae el HV por seed y por sujeto para cada método

import os
import json
import numpy as np
from pymoo.indicators.hv import HV

from src.analisis.resumen_resultados import (
    listar_jsons,
    leer_json,
    es_seed_con_exito,
    es_solucion_factible,
    frente_no_dominado,
    hipervolumen_de_seed,
    calcular_punto_referencia_global,
)

BASE_DIR = os.path.join("PROJECT", "data", "procesado")
OUT_DIR = os.path.join(BASE_DIR, "hipervolumenes")
os.makedirs(OUT_DIR, exist_ok=True)

REF_MARGIN = 0.10

EXCLUDE_DIR_KEYS = {"hipervolumenes", "resumen", "estadistica", "graficas"}


def extraer_por_sujeto_y_seed(datos_json):
    """
    Devuelve: para cada sujeto y seed, la lista de fitness factibles de esa seed
    y sus datos (generó soluciones, cv_mediana y tiempo).
    """
    Fs_por_sujeto_seed = {}
    meta_por_sujeto_seed = {}

    for subj in datos_json["resultados"]:
        sid = int(subj["sujeto_id"])
        Fs_por_sujeto_seed.setdefault(sid, {})
        meta_por_sujeto_seed.setdefault(sid, {})

        for seed_obj in subj["soluciones_por_seed"]:
            seed = int(seed_obj.get("seed", -1))
            genero = es_seed_con_exito(seed_obj)
            cv_med = float(seed_obj.get("cv_mediana", 0.0))
            t_exec = float(seed_obj.get("tiempo_ejecucion", 0.0))

            Fs = []
            if genero:
                for sol in seed_obj["soluciones"]:
                    if es_solucion_factible(sol):
                        Fs.append(sol["fitness"])

            Fs_por_sujeto_seed[sid][seed] = Fs
            meta_por_sujeto_seed[sid][seed] = {
                "genero_soluciones": genero,
                "cv_mediana": cv_med,
                "tiempo_s": t_exec,
            }

    return Fs_por_sujeto_seed, meta_por_sujeto_seed


def exportar_hv_por_metodo(ruta_json, datos_json, ref_point_global):
    """
    Para un archivo, calcula HV por seed y sujeto y guarda un JSON.
    """
    metodo = os.path.basename(ruta_json)
    descripcion = str(datos_json.get("descripcion", ""))

    Fs_por_suj_seed, meta_por_suj_seed = extraer_por_sujeto_y_seed(datos_json)

    hv_por_suj = {}
    hv_obj = HV(ref_point=np.asarray(ref_point_global, dtype=np.float64))

    for sid in sorted(Fs_por_suj_seed.keys()):
        registros = []
        for seed in sorted(Fs_por_suj_seed[sid].keys()):
            soluciones = Fs_por_suj_seed[sid][seed]

            S = frente_no_dominado(soluciones)
            hv_val = float(hv_obj.do(S)) if S.size > 0 else 0.0

            meta = meta_por_suj_seed[sid][seed]
            registros.append({
                "seed": int(seed),
                "hv": hv_val,
                "n_nd": int(S.shape[0]),
                "genero_soluciones": bool(meta.get("genero_soluciones", False)),
                "cv_mediana": float(meta.get("cv_mediana", 0.0)),
                "tiempo_s": float(meta.get("tiempo_s", 0.0)),
            })
        hv_por_suj[str(sid)] = registros

    payload = {
        "metodo": metodo,
        "descripcion": descripcion,
        "ref_point_global": list(ref_point_global),
        "ref_margin": REF_MARGIN,
        "hv_por_sujeto": hv_por_suj,
    }

    out_path = os.path.join(OUT_DIR, metodo)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def main():

    ref_global = calcular_punto_referencia_global(BASE_DIR, margen=REF_MARGIN)

    rutas = listar_jsons(BASE_DIR)
    rutas = [r for r in rutas if not any(k in r.lower() for k in EXCLUDE_DIR_KEYS)]

    for ruta in rutas:
        datos = leer_json(ruta)
        exportar_hv_por_metodo(ruta, datos, ref_global)

if __name__ == "__main__":
    main()