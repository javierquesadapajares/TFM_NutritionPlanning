# carga_datos_csv.py - Carga las comidas y los sujetos de los CSV

import os
import pandas as pd
import numpy as np

AQUI = os.path.dirname(__file__)                                
PROJECT_DIR = os.path.abspath(os.path.join(AQUI, "..", ".."))   
BASE = os.path.join(PROJECT_DIR, "data", "raw") 

RUTA_COMIDA     = os.path.join(BASE, "comida.csv")
RUTA_SUJ_CAL    = os.path.join(BASE, "sujetos_calorias.csv")    # columnas: id, edad, calorias
RUTA_GUSTOS     = os.path.join(BASE, "sujetos_gustos.csv")      # columnas: sujeto_id, grupo
RUTA_DISGUSTOS  = os.path.join(BASE, "sujetos_disgustos.csv")   # columnas: sujeto_id, grupo
RUTA_ALERGIAS   = os.path.join(BASE, "sujetos_alergias.csv")    # columnas: sujeto_id, grupo


def leer_comidas():
    """
    Devuelve lista de datos de los alimentos:
    id, nombre, grupo, calorias, grasas, proteinas, carbohidratos.
    """
    df = pd.read_csv(RUTA_COMIDA)  # separador por defecto = ','
    # Reordenar si existen:
    orden = ["id", "nombre", "grupo", "calorias", "grasas", "proteinas", "carbohidratos"]
    df = df[[c for c in orden if c in df.columns]]
    return df.to_dict(orient="records")


def agrupar_por_sujeto(ruta_csv):
    """
    Agrupa las listas de sujetos.
    """
    df = pd.read_csv(ruta_csv)
    g = df.groupby("sujeto_id")["grupo"].apply(list).reset_index()
    return g.rename(columns={"grupo": "lista"})


def leer_sujetos_con_preferencias():
    """
    Devuelve lista de fatos de los sujetos:
    calorias, edad, gustos, disgustos, alergias.
    """
    base = pd.read_csv(RUTA_SUJ_CAL).rename(columns={"id": "sujeto_id"})
    base = base[["sujeto_id", "edad", "calorias"]]

    g_gustos = agrupar_por_sujeto(RUTA_GUSTOS).rename(columns={"lista": "gustos"})
    g_disg   = agrupar_por_sujeto(RUTA_DISGUSTOS).rename(columns={"lista": "disgustos"})
    g_alerg  = agrupar_por_sujeto(RUTA_ALERGIAS).rename(columns={"lista": "alergias"})

    out = (base
           .merge(g_gustos, on="sujeto_id", how="left")
           .merge(g_disg,   on="sujeto_id", how="left")
           .merge(g_alerg,  on="sujeto_id", how="left"))

    for c in ["gustos", "disgustos", "alergias"]:
        out[c] = out[c].apply(lambda x: x if isinstance(x, list) else [])

    return out[["calorias", "edad", "gustos", "disgustos", "alergias"]].to_dict(orient="records")


if __name__ == "__main__":

    dfc = pd.read_csv(RUTA_COMIDA)
    f, c = dfc.shape
    print(f"\nCOMIDAS: {f} x {c}\n")

    rng = np.random.default_rng(42)
    muestra = dfc.iloc[rng.choice(f, size=min(10, f), replace=False)].copy()
    orden = [x for x in ["id", "nombre", "grupo", "calorias", "proteinas", "grasas", "carbohidratos"] if x in muestra.columns]
    if orden:
        muestra = muestra[orden]
    print("10 ALIMENTOS ALEATORIOS")
    print(muestra.to_string(index=False))

    sujetos = leer_sujetos_con_preferencias()
    dfs = pd.DataFrame(sujetos)
    print(f"\nSUJETOS: {dfs.shape[0]} x {dfs.shape[1]}\n")
    print("SUJETOS:")
    print(dfs.to_string(index=False))