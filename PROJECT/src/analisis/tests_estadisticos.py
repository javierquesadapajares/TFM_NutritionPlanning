# tests_estadisticos.py - Comparación de métodos con Wilcoxon (pares) y Friedman+Shaffer (global).

import os, json, itertools
import numpy as np
from scipy import stats
from scipy.stats import combine_pvalues
from stac.nonparametric_tests import friedman_aligned_ranks_test, shaffer_multitest

CARPETA_BASE = os.path.join("PROJECT", "data", "procesado")
CARPETA_SALIDA = os.path.join(CARPETA_BASE, "estadistica", "tests")
os.makedirs(CARPETA_SALIDA, exist_ok=True)

ARCHIVOS_ENTRADA = [
    r"PROJECT\data\procesado\vectores\resultados\hipervolumenes\nsga3_vectores_comparativa_base_cruce_twopoint_0_9_mut_custom_1_77.json",
    r"PROJECT\data\procesado\vectores\resultados\hipervolumenes\nsga3_vectores_comparativa_base_cruce_twopoint_0_9_mut_gaussiana_0_1.json",
    r"PROJECT\data\procesado\vectores\resultados\hipervolumenes\nsga3_vectores_comparativa_base_cruce_uniforme_0_9_mut_custom_1_77.json",
    r"PROJECT\data\procesado\vectores\resultados\hipervolumenes\nsga3_vectores_comparativa_base_cruce_uniforme_0_9_mut_gaussiana_0_1.json",
]

METRICA_MAYOR_ES_MEJOR = True  # HV mayor = mejor


def construir_rutas_archivos(entradas):
    """Resuelve rutas para los archivos; acepta rutas completas o basenames."""
    indice = {}
    for raiz, _, ficheros in os.walk(CARPETA_BASE):
        if "hipervolumenes" in raiz.lower():
            for f in ficheros:
                if f.lower().endswith(".json"):
                    indice[f] = os.path.join(raiz, f)

    rutas, etiquetas = [], []
    for elemento in entradas:
        candidato = os.path.normpath(elemento)
        if os.path.isfile(candidato):
            rutas.append(candidato)
            etiquetas.append(os.path.basename(candidato))
        else:
            base = os.path.basename(candidato)
            ruta = indice[base]  # asumimos que existe
            rutas.append(ruta)
            etiquetas.append(base)
    return etiquetas, rutas


def leer_hv_por_sujeto(ruta_absoluta):
    """Devuelve hv_por_sujeto del JSON de hipervolumen."""
    with open(ruta_absoluta, "r", encoding="utf-8") as fh:
        datos = json.load(fh)
    return datos["hv_por_sujeto"]


def alinear_seeds(lista_hv_a, lista_hv_b):
    """Alinea por seed y devuelve arrays A, B de HV en seeds comunes."""
    mapa_a = {int(x["seed"]): float(x["hv"]) for x in lista_hv_a}
    mapa_b = {int(x["seed"]): float(x["hv"]) for x in lista_hv_b}
    comunes = sorted(set(mapa_a) & set(mapa_b))
    return np.array([mapa_a[s] for s in comunes], dtype=float), np.array([mapa_b[s] for s in comunes], dtype=float)


def media_por_sujeto(lista_hv_por_metodo, nombres_metodos):
    """Matriz X (sujetos × métodos) con la media de HV por sujeto y método."""
    sujetos = sorted(set.intersection(*[set(d.keys()) for d in lista_hv_por_metodo]), key=int)
    X = np.zeros((len(sujetos), len(nombres_metodos)), dtype=float)
    for i, sid in enumerate(sujetos):
        for j, d in enumerate(lista_hv_por_metodo):
            valores = [float(x["hv"]) for x in d[sid]]
            X[i, j] = float(np.mean(valores))
    return sujetos, X


def wilcoxon_por_sujeto_par(nombre1, nombre2, hv1, hv2):
    """Wilcoxon por sujeto emparejando seeds entre dos métodos."""
    sujetos = sorted(set(hv1) & set(hv2), key=int)
    p_vals = []
    medianas = []
    n_fav1 = n_fav2 = n_emp = 0
    for sid in sujetos:
        A, B = alinear_seeds(hv1[sid], hv2[sid])
        _, p = stats.wilcoxon(A, B, zero_method='pratt')
        p_vals.append(float(p))
        md = float(np.median(A - B))
        medianas.append(md)
        if md > 0: n_fav1 += 1
        elif md < 0: n_fav2 += 1
        else: n_emp += 1
    _, p_comb = combine_pvalues(p_vals, method='fisher')
    mediana_global = float(np.median(medianas))
    ganador = nombre1 if mediana_global > 0 else (nombre2 if mediana_global < 0 else "Empate")
    texto = []
    texto.append(f"WILCOXON: {nombre1} vs {nombre2}\n")
    texto.append(f"  p_fisher={p_comb:.6f}  |  mediana(HV_{nombre1}-HV_{nombre2})={mediana_global:.6f}\n")
    texto.append(f"  sujetos_favorecen: {nombre1}={n_fav1}, {nombre2}={n_fav2}, empates={n_emp}\n")
    texto.append(f"  ganador_si_p<0.05: {ganador}\n\n")
    return "".join(texto)


def friedman_y_shaffer(nombres_metodos, X):
    """Aligned Friedman + Shaffer. Ranking por -HV si HV es mayor-mejor."""
    X_use = -X if METRICA_MAYOR_ES_MEJOR else X
    _, p_friedman, ranks, _ = friedman_aligned_ranks_test(*X_use.T)
    ranking = {m: r for m, r in zip(nombres_metodos, ranks)}
    texto = []
    texto.append("FRIEDMAN+SHAFFER (global)\n")
    texto.append(f"  p_friedman={p_friedman:.6f}\n")
    texto.append("  ranking (menor=mejor):\n")
    for m, r in sorted(ranking.items(), key=lambda t: t[1]):
        texto.append(f"    {m}: {r:.6f}\n")
    comparaciones, _, _, p_adj = shaffer_multitest(ranking)
    texto.append("  pares_significativos (p_adj<0.05):\n")
    for comp, ap in zip(comparaciones, p_adj):
        if ap < 0.05:
            A, _, B = comp.partition(" vs ")
            ganador = A if ranking[A] < ranking[B] else B
            texto.append(f"    {comp}  p_adj={ap:.6f}  ganador={ganador}\n")
    texto.append("\n")
    return "".join(texto)


def main():
    etiquetas, rutas = construir_rutas_archivos(ARCHIVOS_ENTRADA)
    hv_por_metodo = [leer_hv_por_sujeto(p) for p in rutas]

    informe = []
    informe.append("COMPARACIONES POR PARES (Wilcoxon por sujeto)\n\n")
    for i, j in itertools.combinations(range(len(etiquetas)), 2):
        informe.append(wilcoxon_por_sujeto_par(etiquetas[i], etiquetas[j], hv_por_metodo[i], hv_por_metodo[j]))

    sujetos, X = media_por_sujeto(hv_por_metodo, etiquetas)
    informe.append("ANÁLISIS GLOBAL (Aligned Friedman + Shaffer)\n\n")
    informe.append(friedman_y_shaffer(etiquetas, X))

    ruta_txt = os.path.join(CARPETA_SALIDA, "hv_tests.txt")
    with open(ruta_txt, "w", encoding="utf-8") as fh:
        fh.write("".join(informe))


if __name__ == "__main__":
    main()