# ejecutar_vectores.py — Ejecuta 155 veces en espacio vectorial (varias configuraciones)
# Guarda JSON y genera gráficas por sujeto/objetivo en data/procesado/vectores/resultados/soluciones/.

import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt

from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

from src.utilidades import constantes
from PROJECT.src.utilidades.carga_datos_csv import leer_comidas, leer_sujetos_con_preferencias
from src.espacios.vectores.preparador_vectores import ejecutar_vectores as ejecutar_una_vez


# opciones y configuraciones

OPCIONES_CRUCE = ["twopoint", "uniforme", "sbx"]
OPCIONES_MUTACION = ["custom", "gaussiana", "oposicion"]

CONFIGS = [
    {"cruce": "twopoint",  "mutacion": "custom", "prob_cruce": 0.9, "prob_mut": 0.1},
    {"cruce": "uniforme",  "mutacion": "custom",    "prob_cruce": 0.9, "prob_mut": 1/77},
    # {"cruce": "sbx",       "mutacion": "oposicion", "prob_cruce": 0.9, "prob_mut": 0.1},
]


# salidas

BASE_DIR = os.path.join("data", "procesado", "vectores", "resultados", "soluciones")
BASE_JSON = os.path.join(BASE_DIR, "json")
BASE_GRAF = os.path.join(BASE_DIR, "graficas")
os.makedirs(BASE_JSON, exist_ok=True)
os.makedirs(BASE_GRAF, exist_ok=True)



# utilidades

def mediana_por_generacion(resultado, obj_idx):
    """Mediana del objetivo indicado por generación."""
    medianas = []
    for gen in resultado.history:
        F = gen.pop.get("F")
        medianas.append(np.median(F[:, obj_idx]))
    return np.array(medianas, dtype=float)


def etiqueta_prob(p):
    """Convierte 0.9 → '0_9' para nombres de archivo."""
    s = f"{p:.6f}".rstrip("0").rstrip(".")
    return s.replace(".", "_")


def nombre_json(cruce, mutacion, prob_cruce, prob_mut):
    """Nombre del JSON (prefijo 'vectores_')."""
    return f"vectores_cruce_{cruce}_{etiqueta_prob(prob_cruce)}_mut_{mutacion}_{etiqueta_prob(prob_mut)}.json"


def indices_a_json(vector_indices):
    """Lista de índices como string JSON."""
    return json.dumps(np.asarray(vector_indices).tolist())



def ejecutar_configuracion(comida_bd, sujetos, seeds, cruce, mutacion, prob_cruce, prob_mut):
    """
    Ejecuta una configuración completa (5 sujetos × 31 seeds).
    Devuelve el bloque JSON, series para gráficas y etiqueta.
    """
    nds = NonDominatedSorting()
    etiqueta_curva = f"{cruce} + {mutacion} (pc={prob_cruce}, pm={prob_mut})"

    bloque = {
        "descripcion": f"Cruce: {cruce} (p={prob_cruce}) — Mutación: {mutacion} (p={prob_mut})",
        "resultados": []
    }

    series_por_sujeto = {"calorias": {}, "macronutrientes": {}, "preferencias": {}}

    for si, sujeto in enumerate(sujetos):
        print(f"\nSujeto {si+1}")
        sujeto_json = {
            "sujeto_id": int(si + 1),
            "calorias": float(sujeto["calorias"]),
            "edad": int(sujeto["edad"]),
            "alergias": sujeto["alergias"],
            "gustos": sujeto["gustos"],
            "disgustos": sujeto["disgustos"],
            "soluciones_por_seed": []
        }

        med_cal, med_mac, med_pref = [], [], []

        for seed in seeds:
            print(f"Cruce={cruce} mutacion={mutacion} | sujeto={si+1} seed={seed} "
                  f"| pc={prob_cruce} pm={prob_mut}")

            t0 = time.time()
            res = ejecutar_una_vez(
                comida_bd=comida_bd,
                objetivo_calorias=sujeto["calorias"],
                edad=sujeto["edad"],
                gustos=sujeto["gustos"],
                no_gustos=sujeto["disgustos"],
                alergias=sujeto["alergias"],
                cruce=cruce,
                mutacion=mutacion,
                prob_cruce=prob_cruce,
                prob_mutacion=prob_mut,
                seed=seed,
                verbose=True,
            )
            dt = time.time() - t0

            pop = res.pop
            F = pop.get("F")
            G = pop.get("G")
            X = pop.get("X")

            # CV y factibilidad
            if G is None or len(G) == 0:
                mask_feas = np.zeros(len(F), dtype=bool)
                cv_min = cv_mediana = cv_media = 0.0
            else:
                Gpos = np.maximum(G, 0.0)
                cv_vec = Gpos.sum(axis=1)
                cv_min = float(cv_vec.min())
                cv_mediana = float(np.median(cv_vec))
                cv_media = float(cv_vec.mean())
                mask_feas = (G <= 0.0).all(axis=1)

            # ND factibles
            if F is not None and mask_feas.any():
                nd_local = nds.do(F[mask_feas], only_non_dominated_front=True)
                nd_idx = np.flatnonzero(mask_feas)[nd_local]
            else:
                nd_idx = []

            # Soluciones por seed
            soluciones_seed = []
            for i in nd_idx:
                soluciones_seed.append({
                    "solucion": indices_a_json(X[i]),
                    "fitness": [float(f) for f in F[i]]
                })

            sujeto_json["soluciones_por_seed"].append({
                "seed": int(seed),
                "tiempo_ejecucion": f"{dt:.2f}",
                "num_soluciones": len(nd_idx),
                "genero_soluciones": bool(len(nd_idx) > 0),
                "cv_min": cv_min,
                "cv_mediana": cv_mediana,
                "cv_media": cv_media,
                "soluciones": soluciones_seed
            })

            # Mediana por generación para gráficas
            if F is not None and F.size > 0:
                med_cal.append(mediana_por_generacion(res, 0))
                med_mac.append(mediana_por_generacion(res, 1))
                med_pref.append(mediana_por_generacion(res, 2))

        # Mediana de medianas
        if med_cal:
            series_por_sujeto["calorias"][si] = np.median(np.stack(med_cal, axis=0), axis=0)
            series_por_sujeto["macronutrientes"][si] = np.median(np.stack(med_mac, axis=0), axis=0)
            series_por_sujeto["preferencias"][si] = np.median(np.stack(med_pref, axis=0), axis=0)

        bloque["resultados"].append(sujeto_json)

    return bloque, series_por_sujeto, etiqueta_curva


def ejecutar_lote_vectores():
    comida_bd = leer_comidas()
    sujetos = leer_sujetos_con_preferencias()
    seeds = constantes.SEEDS

    acumulado_series = {}
    etiquetas = []

    for cfg in CONFIGS:
        cruce = cfg["cruce"]
        mutacion = cfg["mutacion"]
        prob_cruce = cfg["prob_cruce"]
        prob_mut = cfg["prob_mut"]

        bloque, series_por_sujeto, etiqueta = ejecutar_configuracion(
            comida_bd, sujetos, seeds, cruce, mutacion, prob_cruce, prob_mut
        )

        # guarda JSON
        archivo_json = nombre_json(cruce, mutacion, prob_cruce, prob_mut)
        with open(os.path.join(BASE_JSON, archivo_json), "w", encoding="utf-8") as f:
            json.dump(bloque, f, indent=2, ensure_ascii=False)
        print(f"JSON  → {os.path.join(BASE_JSON, archivo_json)}")

        # acumula curvas para gráficas
        for si in range(len(sujetos)):
            for obj in ("calorias", "macronutrientes", "preferencias"):
                serie = series_por_sujeto[obj].get(si)
                if serie is None:
                    continue
                acumulado_series[(si, obj, etiqueta)] = serie

        if etiqueta not in etiquetas:
            etiquetas.append(etiqueta)

    # gráficas (una por sujeto y objetivos)
    objetivos = ["calorias", "macronutrientes", "preferencias"]
    for si in range(len(sujetos)):
        for obj in objetivos:
            fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
            for etiqueta in etiquetas:
                serie = acumulado_series.get((si, obj, etiqueta))
                if serie is None:
                    continue
                gens = np.arange(1, len(serie) + 1)
                ax.plot(gens, serie, label=etiqueta, linewidth=1.6)
            ax.set_title(f"{obj.capitalize()} — Sujeto {si+1}")
            ax.set_xlabel("Generaciones")
            ax.set_ylabel(f"Mediana F ({obj})")
            ax.grid(True, alpha=0.35)
            if etiquetas:
                ax.legend(fontsize=8, frameon=False, loc="best")
            fname_png = f"{obj}_sujeto_{si+1}.png"
            fig.savefig(os.path.join(BASE_GRAF, fname_png), dpi=140, bbox_inches="tight")
            plt.close(fig)

    print(f"PNG   → {BASE_GRAF}")
    print("\nEjecución completa.")


if __name__ == "__main__":
    ejecutar_lote_vectores()