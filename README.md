# TFM_NutritionPlanning
TFM de valuación de operadores evolutivos guiados por similitud en espacios vectorial, matricial y de grafos aplicados a la planificación nutricional multiobjetivo. Este TFM compara cuatro representaciones del espacio de búsqueda (discreto, vectores, matrices y grafos) sobre un mismo problema: generar menús semanales que cumplan objetivos y restricciones nutricionales (calorías, P/C/G, alergias, gustos, etc.). El algoritmo base es NSGA-III y se evalúan operadores guiados por similitud.

## Descarga

1) Clonar el repositorio:
    ```
    git clone https://github.com/javierquesadapajares/TFM_NutritionPlanning.git
    cd TFM_NutritionPlanning
    cd PROJECT
    git submodule update --init --recursive
    ```
2) Crear el entorno:
    - A) environment.yml
        ```
        conda env create -f environment.yml
        conda activate NOMBRE_ENTORNO   # sustituye por el 'name' del yml
        ```
    - B) requirements.txt
        ```
        conda create -n tfm python=3.10 -y
        conda activate tfm
        pip install -r requirements.txt
        ```
3) Asegurarse que los datos de entrada están en [`PROJECT/data/raw`]. Ejecuta para comprobar:
    ```
    python -m src.utilidades.carga_datos_csv
    ```

## Ejecución (desde `PROJECT/`)

### Construcción de artefactos
```
    # Matrices de similitud (coseno, braycurtis, jaccard)
    python -m src.espacios.matrices.construir_matrices

    # Grafos (3 métricas × 3 filtros × 5 tipos = 45)
    python -m src.espacios.grafos.construir_grafos
```
### Lotes de experimentos (5 sujetos × 31 seeds = 155)
```
    python -m src.espacios.vectores.ejecutar_vectores
    python -m src.espacios.matrices.ejecutar_matrices
    python -m src.espacios.grafos.ejecutar_grafos
```
### Análisis y figuras
```
    python -m src.analisis.heatmap
    python -m src.analisis.extraer_hipervolumen
    python -m src.analisis.boxplot_hv
    python -m src.analisis.tests_estadisticos
    python -m src.analisis.calcular_metricas_grafos
    python -m src.analisis.resumen_resultados
```
### GUI
```
    python -m src.GUI.ejecutor_aplicacion
```

## Estructura del Proyecto 
- 📄[`README.md`](README.md): Documentación principal del proyecto.
- 📄[`requirements.txt`](requirements.txt): Dependencias necesarias del proyecto. Ejecuta "pip install -r requirements.txt".
- 📂[`PROJECT/`](PROJECT/): Directorio en el que se encuentra todo el código correspondiente al TFM.

### **📂[`PROJECT/data`](PROJECT/data)**
- 📂[`raw/`](PROJECT/data/raw/): Ficheros de entrada.
    - 📄[`comida.csv`](PROJECT/data/raw/comida.csv): Catálogo de alimentos.
    - 📄[`sujetos_calorias.csv`](PROJECT/data/raw/sujetos_calorias.csv): Requerimientos calóricos por sujeto.
    - 📄[`sujetos_gustos.csv`](PROJECT/data/raw/sujetos_gustos.csv): Preferencias.
    - 📄[`sujetos_disgustos.csv`](PROJECT/data/raw/sujetos_disgustos.csv): Exclusiones.
    - 📄[`sujetos_alergias.csv`](PROJECT/data/raw/sujetos_alergias.csv): Alergias.
- 📂[`procesado/`](PROJECT/data/procesado/): Artefactos generados y resultados.
    - 📂[`analisis/`](PROJECT/data/procesado/analisis/): Salidas globales de análisis.
    - 📂[`vectores/`](PROJECT/data/procesado/vectores/): Resultados del espacio vectorial.
    - 📂[`matrices/`](PROJECT/data/procesado/matrices/): Resultados del espacio matricial.
    - 📂[`grafos/`](PROJECT/data/procesado/grafos/): Resultados del espacio de grafos.

### **📂[`PROJECT/external`](PROJECT/external)**
- 📂[`stac/`](PROJECT/external/): Este repositorio usa un submódulo llamado `stac`, que es una implementación personalizada basada en [`citiususc/stac`](https://github.com/citiususc/stac.git) con correcciones específicas. Actualmente, `stac` está fijado en el commit [`df5159c`](https://github.com/citiususc/stac/commit/df5159c).

### **📂[`PROJECT/src`](PROJECT/src/)**
- 📂[`algoritmo/`](PROJECT/src/algoritmo/): Núcleo del GA.
    - 📄[`ejecutor_ag.py`](PROJECT/src/algoritmo/ejecutor_ag.py): Ejecutor NSGA-III.
    - 📄[`inicializacion_mutacion.py`](PROJECT/src/algoritmo/inicializacion_mutacion.py): Inicialización y mutación por posición.
    - 📄[`problema.py`](PROJECT/src/algoritmo/problema.py): Definición del problema para Pymoo (objetivos y restricciones).
- 📂[`espacios/`](PROJECT/src/espacios/): Implementaciones por representación.
    - 📂[`vectores/`](PROJECT/src/espacios/vectores/): Vectores de nutrientes.
        - 📂[`operadores/`](PROJECT/src/espacios/vectores/operadores/)
            - 📄[`cruce.py`](PROJECT/src/espacios/vectores/operadores/cruce.py): Cruces en espacio vectorial.
            - 📄[`mutacion.py`](PROJECT/src/espacios/vectores/operadores/mutacion.py): Mutaciones en espacio vectorial.
        - 📄[`preparador_vectores.py`](PROJECT/src/espacios/vectores/preparador_vectores.py): Preparación y ejecución única en el espacio vectorial.
        - 📄[`ejecutar_vectores.py`](PROJECT/src/espacios/vectores/ejecutar_vectores.py): Ejecuta 155 veces en espacio vectorial (guarda JSON y gráficas).
    - 📂[`matrices/`](PROJECT/src/espacios/matrices/): Matrices de similitud.
        - 📂[`operadores/`](PROJECT/src/espacios/matrices/operadores/)
            - 📄[`cruce.py`](PROJECT/src/espacios/matrices/operadores/cruce.py): Cruces en espacio matricial.
            - 📄[`mutacion.py`](PROJECT/src/espacios/matrices/operadores/mutacion.py): Mutaciones en espacio matricial.
        - 📄[`construir_matrices.py`](PROJECT/src/espacios/matrices/construir_matrices.py): Calcula y guarda matrices de similitud.
        - 📄[`metricas_similitud.py`](PROJECT/src/espacios/matrices/metricas_similitud.py): Métricas de similitud entre alimentos.
        - 📄[`preparador_matrices.py`](PROJECT/src/espacios/matrices/preparador_matrices.py): Preparación y ejecución única en el espacio matricial.
        - 📄[`ejecutar_matrices.py`](PROJECT/src/espacios/matrices/ejecutar_matrices.py): Ejecuta 155 veces en espacio matricial (guarda JSON y gráficas).
    - 📂[`grafos/`](PROJECT/src/espacios/grafos/): Grafos de similitud.
        - 📂[`operadores/`](PROJECT/src/espacios/grafos/operadores/)
            - 📄[`cruce.py`](PROJECT/src/espacios/grafos/operadores/cruce.py): Cruces en espacio de grafos.
            - 📄[`mutacion.py`](PROJECT/src/espacios/grafos/operadores/mutacion.py): Mutaciones en espacio de grafos.
            - 📄[`precalculos.py`](PROJECT/src/espacios/grafos/operadores/precalculos.py): Precálculos básicos para trabajar con grafos (distancias, mapeos, vecinos, comunidades).
        - 📄[`construir_grafos.py`](PROJECT/src/espacios/grafos/construir_grafos.py): Genera grafos de similitud por tipo de gen (3×3×5=45).
        - 📄[`filtrado_artistas.py`](PROJECT/src/espacios/grafos/filtrado_aristas.py): Filtros de aristas para grafos de similitud.
        - 📄[`preparador_grafos.py`](PROJECT/src/espacios/grafos/preparador_grafos.py): Preparación y ejecución única en el espacio de grafos.
        - 📄[`ejecutar_grafos.py`](PROJECT/src/espacios/grafos/ejecutar_grafos.py): Ejecuta 155 veces en espacio de grafos (guarda JSON y gráficas).
- 📂[`utilidades/`](PROJECT/src/utilidades/): Helpers comunes.
    - 📄[`carga_datos_csv.py`](PROJECT/src/utilidades/carga_datos_csv.py): Carga las comidas y los sujetos de los CSV.
    - 📄[`carga_nutrientes.py`](PROJECT/src/utilidades/carga_nutrientes.py): Carga y prepara nutrientes.
    - 📄[`constantes.py`](PROJECT/src/utilidades/constantes.py): Parámetros globales y catálogos del problema.
    - 📄[`nutricion.py`](PROJECT/src/utilidades/nutricion.py): Utilidades nutricionales (P/C/G desde gramos, kcal totales, suma de nutrientes, desviaciones vs objetivos).
    - 📄[`planificacion.py`](PROJECT/src/utilidades/planificacion.py): Utilidades de planificación del menú y helpers comunes.
- 📂[`analisis/`](PROJECT/src/analisis/): Scripts de análisis.
    - 📄[`boxplot_hv.py`](PROJECT/src/analisis/boxplot_hv.py): Visualiza box-plot de hipervolumen entre espacios.
    - 📄[`calcular_metricas_grafos.py`](PROJECT/src/analisis/calcular_metricas_grafos.py): Lee los grafos y crea un CSV resumen
    - 📄[`extraer_hipervolumen.py`](PROJECT/src/analisis/extraer_hipervolumen.py): Extrae el HV por seed y por sujeto para cada método.
    - 📄[`heatmap.py`](PROJECT/src/analisis/heatmap.py): Heatmap de 10 alimentos (matriz de coseno).
    - 📄[`resumen_resultados.py`](PROJECT/src/analisis/resumen_resultados.py): Genera CSV con métricas por configuración y por sujeto.
    - 📄[`tests_estadisticos.py`](PROJECT/src/analisis/tests_estadisticos.py): Comparación de métodos con Wilcoxon (pares) y Friedman+Shaffer (global).
- 📂[`GUI/`](PROJECT/src/GUI/): Interfaz gráfica.
    - 📄[`ejecutor_aplicacion.py`](PROJECT/src/GUI/ejecutor_aplicacion.py): Lanza la aplicación para ejecutar el algoritmo evolutivo.
    - 📄[`estilos.py`](PROJECT/src/GUI/estilos.py): Estilos usados en la aplicación.
    - 📄[`ventana_comidas.py`](PROJECT/src/GUI/ventana_comidas.py): Muestra los alimentos y sus datos.
    - 📄[`ventana_configuracion_algoritmo.py`](PROJECT/src/GUI/ventana_configuracion_algoritmo.py): Permite elegir el espacio y sus hiperparámetros.
    - 📄[`ventana_menu.py`](PROJECT/src/GUI/ventana_menu.py): Muestra el menú generado.
    - 📄[`ventana_preguntasusuario.py`](PROJECT/src/GUI/ventana_preguntasusuario.py): Muestra formulario de datos del sujeto.
    - 📄[`ventana_principal.py`](PROJECT/src/GUI/ventana_principal.py): Ventana principal (orquestación).