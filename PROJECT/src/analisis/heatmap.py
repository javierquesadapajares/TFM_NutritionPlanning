# heatmap.py - Heatmap de 10 alimentos (matriz de coseno).

import os
import sys
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


AQUI = os.path.dirname(__file__)
PROJECT = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))  # .../PROJECT
if PROJECT not in sys.path:
    sys.path.insert(0, PROJECT)

from src.utilidades.carga_nutrientes import preparar_datos


RUTA_MATRIZ = os.path.join(PROJECT, "data", "procesado", "matrices", "matriz_coseno.npy")
DIR_SALIDA = os.path.join(PROJECT, "figures", "matrices")
os.makedirs(DIR_SALIDA, exist_ok=True)


nombres, _, _ = preparar_datos()                 
M = np.load(RUTA_MATRIZ).astype(np.float32)

# selecciona 10 alimentos
rng = np.random.default_rng(42)
idx = rng.choice(len(nombres), size=10, replace=False)
nombres_sel = [str(n).split(",", 1)[0].strip() for n in np.array(nombres)[idx]]
M_sel = M[np.ix_(idx, idx)]

conteo = {}
for i, n in enumerate(nombres_sel):
    conteo[n] = conteo.get(n, 0) + 1
    if conteo[n] > 1:
        nombres_sel[i] = f"{n} ({conteo[n]})"

def dibujar_guardar(matriz, etiquetas, anotar):
    """Dibuja y guarda el heatmap con seaborn."""
    plt.figure(figsize=(7, 6))
    ax = sns.heatmap(
        matriz,
        cmap="viridis",
        vmin=0.0, vmax=1.0,
        square=True,
        annot=anotar,
        fmt=".2f" if anotar else "",
        xticklabels=etiquetas,
        yticklabels=etiquetas,
        cbar_kws={"shrink": 0.85}
    )
    ax.set_title("Similitud (coseno) entre 10 alimentos", pad=10)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()

    nombre = "matriz_coseno_10alimentos_annot.png" if anotar else "matriz_coseno_10alimentos_clean.png"
    plt.savefig(os.path.join(DIR_SALIDA, nombre), dpi=300)
    plt.close()

# genera ambas versione
dibujar_guardar(M_sel, nombres_sel, anotar=False)
dibujar_guardar(M_sel, nombres_sel, anotar=True)