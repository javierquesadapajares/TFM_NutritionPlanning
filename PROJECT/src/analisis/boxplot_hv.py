# boxplot_hv - Visualiza box-plot de hipervolumen entre espacios

import os
import json
import numpy as np
import matplotlib.pyplot as plt

RUTAS_JSON = [
    "data/procesado/vectores/resultados/hipervolumenes/nsga3_vectores_comparativa_base_cruce_twopoint_0_9_mut_custom_1_77.json",
    "data/procesado/vectores/resultados/hipervolumenes/nsga3_vectores_comparativa_base_cruce_uniforme_0_9_mut_gaussiana_0_1.json",
    "data/procesado/matrices/resultados/hipervolumenes/nsga3_matrices_comparativa_base_jaccard_cr_consenso_0_6_mut_jaccard_sim_0_1.json",
    "data/procesado/grafos/resultados/hipervolumenes/nsga3_grafo_comparativa_base_coseno_knn_cr_path_0_6_mut_cluster_0_1.json",
]

ETIQUETAS = ["Discreto", "Vectores", "Matrices", "Grafos"]

RUTA_SALIDA = "data/procesado/analisis/boxplot_hv_agregado.png"
TITULO_FIGURA = "Boxplot del HV entre espacios"


def leer_json(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def extraer_hv_y_sr(payload):
    hvs = []
    factibles, total = 0, 0
    for registros in payload["hv_por_sujeto"].values():
        for r in registros:
            hvs.append(float(r["hv"]))
            if r.get("genero_soluciones", False):
                factibles += 1
            total += 1
    return hvs, (factibles, total)

def ordenar_por_mediana(listas):
    meds = [float(np.median(np.asarray(v, dtype=float))) for v in listas]
    idx = list(range(len(listas)))
    idx.sort(key=lambda i: meds[i], reverse=True)
    return idx

def anotar_sr(ax, x, y, sr):
    fact, tot = sr
    pct = 100.0 * fact / max(tot, 1)
    ax.text(x, y, f"SR: {pct:.1f}%", ha="center", va="bottom", fontsize=10)


def main():
    hv_agregado = []
    sr_agregado = []
    for ruta in RUTAS_JSON:
        payload = leer_json(ruta)
        hvs, sr = extraer_hv_y_sr(payload)
        hv_agregado.append(hvs)
        sr_agregado.append(sr)

    orden = ordenar_por_mediana(hv_agregado)
    hv_ordenado = [hv_agregado[i] for i in orden]
    sr_ordenado = [sr_agregado[i] for i in orden]
    etiquetas_ordenadas = [ETIQUETAS[i] for i in orden]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    bp = ax.boxplot(
        hv_ordenado,
        tick_labels=etiquetas_ordenadas,
        showmeans=False,
        whis=1.5,
        patch_artist=True
    )

    colores = ["#b3cde3", "#ccebc5", "#fbb4ae", "#decbe4"]
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor(colores[i % len(colores)])
        box.set_alpha(0.9)
        box.set_edgecolor("#444444")
        box.set_linewidth(1.2)
    for med in bp["medians"]:
        med.set_color("#333333")
        med.set_linewidth(1.6)
    for whisk in bp["whiskers"]:
        whisk.set_color("#666666")
    for cap in bp["caps"]:
        cap.set_color("#666666")

    y_max = max(max(vals) if len(vals) > 0 else 0.0 for vals in hv_ordenado)
    if y_max <= 0:
        y_max = 1.0
    altura = abs(y_max) + 1.0
    y_top = y_max + 0.10 * altura
    for i, sr in enumerate(sr_ordenado, start=1):
        anotar_sr(ax, i, y_top, sr)

    ax.set_title(TITULO_FIGURA)
    ax.set_xlabel("Espacios")
    ax.set_ylabel("HV")
    ax.grid(True, axis="y", alpha=0.35)
    ax.set_ylim(0.0, y_top + 0.06 * altura)

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    fig.savefig(RUTA_SALIDA, dpi=180, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    main()