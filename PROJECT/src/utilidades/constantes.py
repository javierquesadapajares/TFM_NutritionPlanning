# constantes.py — Parámetros globales y catálogos del problema
# Contiene:
# - Umbrales y objetivos nutricionales.
# - Penalizaciones del modelo.
# - Tipos de comida, mapa de componentes por comida y calendario básico.
# - Tamaños del problema (días, genes).
# - Niveles de actividad (Enum) con utilidades.
# - Semillas fijas para reproducibilidad.
# - Grupos de comida (catálogo jerárquico).

from enum import Enum

# Umbrales de binarización nutricional (bajo, alto)
UMBRAL_BINARIZACION = {
    "calorias": (150, 400),
    "proteinas": (1.6, 8),
    "carbohidratos": (5, 22.5),
    "grasas": (3, 17.5),
}

# Porcentajes objetivo de macronutrientes (sobre calorías totales)
OBJETIVO_PROTEINAS = 22.5
OBJETIVO_CARBOHIDRATOS = 55.0
OBJETIVO_GRASAS = 27.5

# Límites aceptables de macronutrientes (porcentaje)
LIMITE_PROTEINAS = (10.0, 35.0)
LIMITE_CARBOHIDRATOS = (45.0, 65.0)
LIMITE_GRASAS = (20.0, 35.0)

# Factores de penalización
PENALIZACION_CALORIAS = 500
PENALIZACION_MACRONUTRIENTES = 300
PENALIZACION_ALERGIA = 1000
PENALIZACION_PREFERENCIA = 50

# Tipos de comida utilizados en el plan
class TipoComida:
    DESAYUNO = "desayuno"
    BEBIDA_DESAYUNO = "bebida_desayuno"
    SNACKS = "snacks"
    ALMUERZO_CENA = "almuerzo_cena"
    BEBIDAS = "bebidas"

# Calendario y definición de comidas del día
DIAS_SEMANA = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

# Cada comida indica cuántos alimentos tiene
COMIDAS = [
    {"nombre": "Desayuno", "num_alimentos": 3},
    {"nombre": "Tentempie", "num_alimentos": 1},
    {"nombre": "Almuerzo", "num_alimentos": 3},
    {"nombre": "Merienda", "num_alimentos": 1},
    {"nombre": "Cena", "num_alimentos": 3},
]

# Para cada comida, el tipo de cada componente en orden
MAPA_COMPONENTES_POR_COMIDA = {
    "Desayuno":  [TipoComida.DESAYUNO, TipoComida.DESAYUNO, TipoComida.BEBIDA_DESAYUNO],
    "Tentempie": [TipoComida.SNACKS],
    "Almuerzo":  [TipoComida.ALMUERZO_CENA, TipoComida.ALMUERZO_CENA, TipoComida.BEBIDAS],
    "Merienda":  [TipoComida.SNACKS],
    "Cena":      [TipoComida.ALMUERZO_CENA, TipoComida.ALMUERZO_CENA, TipoComida.BEBIDAS],
}

# Tamaños del problema
NUM_DIAS = 7
NUM_COMIDAS = len(COMIDAS)
NUM_ALIMENTOS_DIARIO = sum(c["num_alimentos"] for c in COMIDAS)  # 11 alimentos por día
NUM_GENES = NUM_DIAS * NUM_ALIMENTOS_DIARIO                       # 77 genes por menú semanal

# Niveles de actividad con factor multiplicador
class NivelActividad(Enum):
    SEDENTARIO = ("Sedentario (poco o ningun ejercicio)", 1.2)
    POCO_ACTIVO = ("Poco activo (ejercicio ligero/deportes 1-3 dias a la semana)", 1.375)
    MODERADAMENTE_ACTIVO = ("Moderadamente activo (ejercicio moderado/deportes 3-5 dias a la semana)", 1.55)
    ACTIVO = ("Activo (ejercicio duro/deportes 6-7 días a la semana)", 1.725)
    MUY_ACTIVO = ("Muy activo (ejercicio muy duro/deportes y un trabajo físico)", 1.9)

    @classmethod
    def descripciones(cls):
        """Devuelve la lista de descripciones de actividad."""
        return [x.value[0] for x in cls]

    @classmethod
    def factor_por_descripcion(cls, descripcion: str) -> float:
        """Devuelve el factor multiplicador a partir de la descripción exacta."""
        for x in cls:
            if x.value[0] == descripcion:
                return x.value[1]
        raise ValueError("Nivel de actividad no valido")

    # Aliases para compatibilidad si en algún sitio anterior se usaron nombres en inglés
    get_descriptions = descripciones
    get_value = factor_por_descripcion

# # 31 semillas para reproducibilidad (se usan en todos los sujetos)
# SEEDS = [
#     6, 26, 59, 60,
#     79, 93, 489, 608,
#     634, 684, 784, 930,
#     3364, 3608, 4845, 5375,
#     8542, 9397, 11320, 14648,
#     39843, 73886, 83186, 97870,
#     152822, 211193, 226880, 315529,
#     428397, 489166, 526568,
# ]

SEEDS = [42]

# Catálogo de grupos de comida (códigos y descripciones)
class GruposComida:
    class Cereales:
        CEREALES = ("A", "Cereals and cereal products")
        SANDWICHES = ("AB", "Sandwiches")
        ARROZ = ("AC", "Rice")
        PASTA = ("AD", "Pasta")
        PIZZAS = ("AE", "Pizzas")
        PANES = ("AF", "Breads")
        ROLLOS = ("AG", "Rolls")
        CEREALES_DESAYUNO = ("AI", "Breakfast cereals")
        ALIMENTOS_INFANTILES = ("AK", "Infant cereal foods")
        GALLETAS = ("AM", "Biscuits")
        PASTELES = ("AN", "Cakes")
        PASTELERIA = ("AO", "Pastry")
        BOLLOS = ("AP", "Buns and pastries")
        POSTRES = ("AS", "Puddings")
        APERITIVOS = ("AT", "Savouries")

    class Lacteos:
        LACTEOS = ("B", "Milk and milk products")
        class LecheVaca:
            LECHE_VACA = ("BA", "Cows milk")
            LECHE_DESAYUNO = ("BAB", "Breakfast milk")
            LECHE_DESCREMADA = ("BAE", "Skimmed milk")
            LECHE_SEMIDESCREMADA = ("BAH", "Semi-skimmed milk")
            LECHE_ENTERA = ("BAK", "Whole milk")
            LECHES_PROCESADAS = ("BAR", "Processed milks")
        BEBIDAS_LACTEAS = ("BH", "Milk-based drinks")
        class Cremas:
            CREMAS = ("BJ", "Creams")
            CREMAS_FRESCAS = ("BJC", "Fresh creams (pasteurised)")
            CREMAS_UHT = ("BJP", "UHT creams")
            CREMAS_IMITACION = ("BJS", "Imitation creams")
        QUESOS = ("BL", "Cheeses")
        class Yogures:
            YOGURES = ("BN", "Yogurts")
            YOGURES_ENTEROS = ("BNE", "Whole milk yogurts")
            YOGURES_DESNATADOS = ("BNH", "Low fat yogurts")
            OTROS_YOGURES = ("BNS", "Other yogurts")
        HELADOS = ("BP", "Ice creams")
        POSTRES_REFRIGERADOS = ("BR", "Puddings and chilled desserts")
        PLATOS_SALADOS_SALSAS = ("BV", "Savoury dishes and sauces")

    class Huevos:
        HUEVOS = ("C", "Eggs")
        HUEVOS_GENERALES = ("CA", "Eggs")
        class PlatosDeHuevos:
            PLATOS_DE_HUEVOS = ("CD", "Egg dishes")
            PLATOS_DE_HUEVOS_SALADOS = ("CDE", "Savoury egg dishes")
            PLATOS_DE_HUEVOS_DULCES = ("CDH", "Sweet egg dishes")

    class Vegetales:
        VEGETALES = ("D", "Vegetables")
        class Patatas:
            PATATAS = ("DA", "Potatoes")
            PATATAS_TEMPRANAS = ("DAE", "Early potatoes")
            PATATAS_PRINCIPALES = ("DAM", "Main crop potatoes")
            PATATAS_FRITAS = ("DAP", "Chipped old potatoes")
            PRODUCTOS_DE_PATATA = ("DAR", "Potato products")
        FRIJOLES_LENTEJAS = ("DB", "Beans and lentils")
        GUISANTES = ("DF", "Peas")
        VEGETALES_GENERALES = ("DG", "Vegetables, general")
        VEGETALES_SECOS = ("DI", "Vegetables, dried")
        PLATOS_DE_VEGETALES = ("DR", "Vegetable dishes")

    class Frutas:
        FRUTAS = ("F", "Fruit")
        FRUTAS_GENERALES = ("FA", "Fruit, general")
        JUGOS_DE_FRUTAS = ("FC", "Fruit juices")
        ZUMOS = ("FE", "Juices")

    class NuecesYSemillas:
        NUECES_SEMILLAS = ("G", "Nuts and seeds")
        NUECES_SEMILLAS_GENERALES = ("GA", "Nuts and seeds, general")

    class Pescado:
        PESCADO = ("J", "Fish and fish products")
        PESCADO_BLANCO = ("JA", "White fish")
        PESCADO_GRASO = ("JC", "Fatty fish")
        CRUSTACEOS = ("JK", "Crustacea")
        MOLUSCOS = ("JM", "Molluscs")
        PRODUCTOS_PLATOS_DE_PESCADO = ("JR", "Fish products and dishes")

    class Carne:
        CARNE = ("M", "Meat and meat products")
        class CarneGeneral:
            CARNE_GENERAL = ("MA", "Meat")
            BACON = ("MAA", "Bacon")
            CARNE_DE_RES = ("MAC", "Beef")
            CARNE_DE_CORDERO = ("MAE", "Lamb")
            CARNE_DE_CERDO = ("MAG", "Pork")
            CARNE_DE_TERNERA = ("MAI", "Veal")
        class Aves:
            AVES = ("MC", "Poultry")
            POLLO = ("MCA", "Chicken")
            PATO = ("MCC", "Duck")
            GANSO = ("MCE", "Goose")
            UROGALLO = ("MCG", "Grouse")
            PERDIZ = ("MCI", "Partridge")
            FAISAN = ("MCK", "Pheasant")
            PALOMA = ("MCM", "Pigeon")
            PAVO = ("MCO", "Turkey")
        class Caza:
            CAZA = ("ME", "Game")
            LIEBRE = ("MEA", "Hare")
            CONEJO = ("MEC", "Rabbit")
            VENADO = ("MEE", "Venison")
        DESPOJOS = ("MG", "Offal")
        HAMBURGUESAS_Y_PARRILLAS = ("MB", "Burgers and grillsteaks")
        class ProductosCarnicos:
            PRODUCTOS_CARNICOS = ("MI", "Meat products")
            OTROS_PRODUCTOS_CARNICOS = ("MIG", "Other meat products")
        PLATOS_DE_CARNE = ("MR", "Meat dishes")

    class Bebidas:
        BEBIDAS = ("P", "Beverages")
        class BebidasEnPolvoEsenciasInfusiones:
            BEBIDAS_EN_POLVO_ESENCIAS_INFUSIONES = ("PA", "Powdered drinks, essences and infusions")
            BEBIDAS_EN_POLVO = ("PAA", "Powdered drinks and essences")
            INFUSIONES = ("PAC", "Infusions")
        class BebidasSuaves:
            BEBIDAS_SUAVES = ("PC", "Soft drinks")
            BEBIDAS_CARBONATADAS = ("PCA", "Carbonated drinks")
            CALABAZA = ("PCC", "Squash and cordials")

    class Alcohol:
        ALCOHOL = ("Q", "Alcoholic beverages")
        CERVEZAS = ("QA", "Beers")
        SIDRAS = ("QC", "Ciders")
        VINOS = ("QE", "Wines")

    class Azucares:
        AZUCARES = ("S", "Sugars, preserves and snacks")
        class Confiteria:
            CONFITERIA = ("SE", "Confectionery")
            CONFITERIA_DE_CHOCOLATE = ("SEA", "Chocolate confectionery")
            CONFITERIA_NO_DE_CHOCOLATE = ("SEC", "Non-chocolate confectionery")
        class AperitivosSalados:
            APERITIVOS_SALADOS = ("SN", "Savoury snacks")
            APERITIVOS_DE_PATATA = ("SNA", "Potato-based snacks")
            APERITIVOS_NO_DE_PATATA = ("SNC", "Non-potato snacks")

    class SopasSalsas:
        SOPA_SALSAS = ("W", "Soups, sauces and miscellaneous foods")
        class Sopas:
            SOPAS = ("WA", "Soups")
            SOPAS_CASERAS = ("WAA", "Homemade soups")
            SOPAS_ENVASADAS = ("WAC", "Canned soups")
            SOPAS_EN_POLVO = ("WAE", "Packet soups")
        ENCURTIDOS = ("WE", "Pickles and chutneys")