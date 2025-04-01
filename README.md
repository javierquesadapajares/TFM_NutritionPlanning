# NutritionPlanning
PFG de Planificación nutricional mediante algoritmos evolutivos. Este proyecto tiene como finalidad la creación de un menú semanal de comidas personalizado mediante algoritmos genéticos. Experimentando con diferentes algoritmos se busca crear un plan alimenticio que cumpla distintos objetivos nutricionales, como la ingesta calórica diaria o la proporción de macronutrientes tomados, a la vez que limitarse según las restricciones dadas.

## Estructura del Proyecto 
- 📄[`README.md`](README.md): Documentación principal del proyecto.
- 📄[`requirements.txt`](requirements.txt): Dependencias necesarias del proyecto. Ejecuta "pip install -r requirements.txt".
- 📂[`PROJECT/`](PROJECT/): Directorio en el que se encuentra todo el código correspondiente al PFG.

### **📂[`PROJECT/data`](PROJECT/data)**
- 📄[`food_database_dump.sql`](PROJECT/data/food_database_dump.sql): Contiene la base de datos exportada.

### **📂[`PROJECT/external`](PROJECT/external)**
- 📂[`stac/`](PROJECT/external/): Este repositorio usa un submódulo llamado `stac`, que es una implementación personalizada basada en [`citiususc/stac`](https://github.com/citiususc/stac.git) con correcciones específicas. Actualmente, `stac` está fijado en el commit [`df5159c`](https://github.com/citiususc/stac/commit/df5159c).

### **📂[`PROJECT/src`](PROJECT/src)**
- 📄[`__main__.py`](PROJECT/src/__main__.py): Archivo principal que inicia el proyecto.
- 📂[`algoritmos/`](PROJECT/src/algoritmos/): Contiene implementaciones de algoritmos genéticos multiobjetivo junto con variaciones y operadores personalizados para resolver el problema nutricional.
- 📂[`GUI/`](PROJECT/src/GUI/): Incluye la interfaz gráfica de usuario del proyecto, diseñada para la creación y visualización de un menú de comida personalizado.
- 📂[`utilidades/`](PROJECT/src/utilidades/): Reúne funciones auxiliares, constantes globales y herramientas para la conexión a la base de datos.
- 📂[`test/`](PROJECT/src/test/): Contiene scripts para la realización de pruebas y análisis de experimentos.

#### **📂[`algoritmos/`](PROJECT/src/algoritmos/)**
- 📂[`nsga2/`](PROJECT/src/algoritmos/nsga2/): Contiene diferentes implementaciones del algoritmo *Non-dominated Sorting Genetic Algorithm II* (NSGA-II) basándose en el manejo de restricciones.
- 📂[`nsga3/`](PROJECT/src/algoritmos/nsga3/): Contiene diferentes implementaciones del algoritmo *Non-dominated Sorting Genetic Algorithm III* (NSGA-III) basándose en el manejo de restricciones.
- 📂[`spea2/`](PROJECT/src/algoritmos/spea2/): Contiene diferentes implementaciones del algoritmo *Strength Pareto Evolutionary Algorithm 2* (SPEA2) basándose en el manejo de restricciones.
- 📂[`moead/`](PROJECT/src/algoritmos/moead/): Contiene implementación del algoritmo *Multi-Objective Evolutionary Algorithm based on Decomposition* (MOEA/D).

#### **📂[`GUI/`](PROJECT/src/GUI/)**
- 📄[`ventana_principal.py`](PROJECT/src/GUI/ventana_principal.py): Entrada a la interfaz al ejecutar el archivo [`__main__.py`](PROJECT/src/__main__.py). Presenta botones que dirigen a la ventana [`ventana_basedatos.py`](PROJECT/src/GUI/ventana_basedatos.py) o a [`ventana_preguntasusario.py`](PROJECT/src/GUI/ventana_preguntasusuario.py).
- 📄[`ventana_basedatos.py`](PROJECT/src/GUI/ventana_basedatos.py): Muestra en formato tabla los alimentos que se encuentran en la base de datos y sus correspondientes valores nutricionales.
- 📄[`ventana_preguntasusuario.py`](PROJECT/src/GUI/ventana_preguntasusuario.py): El usuario puede ingresar datos personales y preferencias alimenticias para personalizar la planificación nutricional. También permite configurar el algoritmo evolutivo. Presenta el botón que ejecuta genético.
- 📄[`ventana_configuracion_algoritmo.py`](PROJECT/src/GUI/ventana_configuracion_algoritmo.py): Panel en el que se puede cambiar los hiperparámetros del algoritmo evolutivo.
- 📄[`ventana_menu.py`](PROJECT/src/GUI/ventana_menu.py): Muestra el menú semanal resultado de la ejecución del algortimo evolutivo.

#### **📂[`utilidades/`](PROJECT/src/utilidades/)**
- 📄[`constantes.py`](PROJECT/src/utilidades/constantes.py): Se definen todas las variables globales que son usadas en el resto del proyecto.
- 📄[`database.py`](PROJECT/src/utilidades/database.py): Se realiza la conexión a la base de datos donde se encuentran los alimentos y los sujetos de prueba y se realiza una query para recoger estos datos.
- 📄[`funciones_auxiliares.py`](PROJECT/src/utilidades/funciones_auxiliares.py): Se codifican distintas funciones que ayudan en la ejecución del algoritmo evolutivo.
- 📄[`operadores_custom.py`](PROJECT/src/utilidades/operadores_custom.py): Se definen los operadores personalizados de inicialización y mutación.

#### **📂[`test/`](PROJECT/src/test/)**
- 📄[`ejecutar_guardar_resultados.py`](PROJECT/src/test/ejecutar_guardar_resultados.py): Se ejecuta el algoritmo 31 veces por cada sujeto y se guardan los resultados en [`resultados/tablas/`](PROJECT/src/test/resultados/tablas/) en formato JSON según el tipo de algoritmo y los hiperparámetros elegidos.
- 📄[`hipervolumen.py`](PROJECT/src/test/hipervolumen.py): Se calcula el hipervolumen a partir de los resultados guardados en [`resultados/tablas/`](PROJECT/src/test/resultados/tablas/) y se guardan en el directorio `resultados/tablas/xxx/hipervolumen/`, donde `xxx` representa el nombre de la carpeta correspondiente al algoritmo evaluado.
- 📄[`comparacion_algoritmos.py`](PROJECT/src/test/comparacion_algoritmos.py): Se codifican los test 1vs1 (Wilcoxon) y NvsN (Friedman-Schaffer) para la comparación de hipervolumenes.
- 📄[`grafica_fitness.py`](PROJECT/src/test/grafica_fitness.py): Se crean gráficas de la evolución del fitness de cada objetivo tras la ejecución del algoritmo. Los resultados se guardan en el directorio [`resultados/graficas`](PROJECT/src/test/resultados/graficas/)
- 📂[`resultados/`](PROJECT/src/test/resultados/): Directorio en el que se encuentran los resultados de ejecutar los diferentes tipos de algoritmo.

##### **📂[`resultados/`](PROJECT/src/test/resultados/)**
- 📂[`tablas`](PROJECT/src/test/resultados/tablas/): Almacena los resultados de ejecutar los scripts [`ejecutar_guardar_resultados.py`](PROJECT/src/test/ejecutar_guardar_resultados.py) y [`hipervolumen.py`](PROJECT/src/test/hipervolumen.py)
- 📂[`graficas/`](PROJECT/src/test/resultados/graficas/): Almacena los resultados de ejecutar [`grafica_fitness.py`](PROJECT/src/test/grafica_fitness.py).
