#ag_nsga2_reparacion.py

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.operators.crossover.pntx import SinglePointCrossover
from pymoo.config import Config

from utilidades.funciones_auxiliares import calculo_macronutrientes, filtrar_comida
from utilidades.database import comida_basedatos
from utilidades.constantes import *
from src.utilidades.operadores_custom import CustomIntegerRandomSampling, CustomMutation

Config.warnings['not_compiled'] = False

comida_bd = comida_basedatos()


def objetivo_calorias(calorias_diarias, objetivo_calorico):
    """Calcula la desviacion entre las calorias diarias consumidas y el objetivo calorico."""

    desviacion_objetivo_calorias = abs(objetivo_calorico - calorias_diarias)

    return desviacion_objetivo_calorias


def objetivo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias):
    """Calcula la desviacion de los macronutrientes respecto a los porcentajes ideales."""

    porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)

    desviacion_objetivo_proteinas = abs(porcentaje_proteinas - OBJETIVO_PROTEINAS)
    desviacion_objetivo_carbohidratos = abs(porcentaje_carbohidratos - OBJETIVO_CARBOHIDRATOS)
    desviacion_objetivo_grasas = abs(porcentaje_grasas - OBJETIVO_GRASAS)

    desviacion_macronutrientes = desviacion_objetivo_proteinas + desviacion_objetivo_carbohidratos + desviacion_objetivo_grasas

    return desviacion_macronutrientes


def objetivo_preferencia_grupo(alimento, grupos_gusta, grupos_no_gusta):
    """Calcula la penalizacion de preferencia segun el grupo alimenticio del alimento."""

    penalizacion = 0

    if alimento["grupo"] in grupos_gusta:
        penalizacion = -PENALIZACION_PREFERENCIA
    if alimento["grupo"] in grupos_no_gusta:
        penalizacion = PENALIZACION_PREFERENCIA

    return penalizacion


def reparar_solucion(solucion, problema, objetivo_calorico, grupos_alergia, num_intentos):
    
    solucion_reparada = solucion.copy()

    for dia in range(NUM_DIAS):
        calorias_diarias = 0
        proteinas_diarias = 0
        carbohidratos_diarias = 0
        grasas_diarias = 0

        inicio_dia = dia * NUM_ALIMENTOS_DIARIO

        # Calcula calorias y macronutrientes diarios
        for i in range(inicio_dia, inicio_dia + NUM_ALIMENTOS_DIARIO):

            alimento = problema.comida_bd[int(solucion_reparada[i])]

            calorias_diarias += alimento["calorias"]
            proteinas_diarias += alimento["proteinas"]
            carbohidratos_diarias += alimento["carbohidratos"]
            grasas_diarias += alimento["grasas"]

        # Calcula porcentajes de macronutrientes
        porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(
            proteinas_diarias, carbohidratos_diarias, grasas_diarias
        )

        intentos = 0
        # Ajusta calorias y macronutrientes si estan fuera del rango permitido
        while intentos < num_intentos and (
            not (objetivo_calorico * 0.9 <= calorias_diarias <= objetivo_calorico * 1.1) or \
            not (LIMITE_PROTEINAS[0] <= porcentaje_proteinas <= LIMITE_PROTEINAS[1]) or \
            not (LIMITE_CARBOHIDRATOS[0] <= porcentaje_carbohidratos <= LIMITE_CARBOHIDRATOS[1]) or \
            not (LIMITE_GRASAS[0] <= porcentaje_grasas <= LIMITE_GRASAS[1])):

            # Selecciona un indice aleatorio de un alimento en la solucion para reemplazarlo
            idx = np.random.randint(inicio_dia, inicio_dia + NUM_ALIMENTOS_DIARIO)
            alimento_actual = problema.comida_bd[int(solucion_reparada[idx])]

            # Selecciona un nuevo alimento para reemplazo
            nuevo_alimento_idx = seleccionar_nuevo_alimento(problema, idx, inicio_dia)
            nuevo_alimento = problema.comida_bd[nuevo_alimento_idx]

            if nuevo_alimento["grupo"] in grupos_alergia:
                intentos += 1
                continue
            
            # Actualiza los valores de calorias y macronutrientes tras el reemplazo del alimento
            calorias_diarias += nuevo_alimento["calorias"] - alimento_actual["calorias"]
            proteinas_diarias += nuevo_alimento["proteinas"] - alimento_actual["proteinas"]
            carbohidratos_diarias += nuevo_alimento["carbohidratos"] - alimento_actual["carbohidratos"]
            grasas_diarias += nuevo_alimento["grasas"] - alimento_actual["grasas"]

            # Reemplaza el alimento en la solucion reparada
            solucion_reparada[idx] = nuevo_alimento_idx

            # Recalcula porcentajes de macronutrientes
            porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(
                proteinas_diarias, carbohidratos_diarias, grasas_diarias
            )

    return solucion_reparada

def seleccionar_nuevo_alimento(problema, idx, inicio_dia):
    """Selecciona un nuevo alimento aleatorio para reemplazar en la solucion basado en el tipo de comida"""
    
    suma_num_alimentos = 0

    for comida in COMIDAS:
        num_alimentos = comida["num_alimentos"]

        for indice_alimento in range(num_alimentos):

            if (inicio_dia + suma_num_alimentos + indice_alimento) == idx:

                match comida["nombre"]:

                    case "Tentempie" | "Merienda":
                        return np.random.choice(problema.snacks)
                    
                    case "Desayuno":
                        if indice_alimento == 2:
                            return np.random.choice(problema.bebida_desayuno)
                        else:
                            return np.random.choice(problema.desayuno)
                        
                    case _:
                        if indice_alimento == 2:
                            return np.random.choice(problema.bebidas)
                        else:
                            return np.random.choice(problema.almuerzo_cena)
                        
        suma_num_alimentos += num_alimentos

    return -1


# Clase del problema de optimizacion
class PlanningComida(ElementwiseProblem):
    """Clase que define el problema de planificacion de comida en base a objetivos y restricciones."""
    
    def __init__(self, comida_bd, objetivo_calorico, edad, grupos_alergia, grupos_gusta, grupos_no_gusta):

        super().__init__(n_var=NUM_GENES, n_obj=3, n_constr=0, xl=0, xu=len(comida_bd)-1)  
        self.comida_bd = comida_bd
        self.objetivo_calorias = objetivo_calorias
        self.edad = edad
        self.grupos_alergia = grupos_alergia
        self.grupos_gusta = grupos_gusta
        self.grupos_no_gusta = grupos_no_gusta
            
        self.almuerzo_cena = self.filtrar_comida("almuerzo_cena")
        self.bebidas = self.filtrar_comida("bebidas")
        self.desayuno = self.filtrar_comida("desayuno")
        self.bebida_desayuno = self.filtrar_comida("bebida_desayuno") 
        self.snacks = self.filtrar_comida("snacks")


    def _evaluate(self, x, out, *args, **kwargs):
        """Evalua el plan de comidas generando los valores de los objetivos y las restricciones."""

        x_reparada = reparar_solucion(x, self, self.objetivo_calorias, self.grupos_alergia, 100)
        
        total_desviaciones_calorias = 0
        total_desviaciones_macronutrientes = 0
        total_penalizaciones_preferencia = 0

        # Evaluacion para cada dia
        for dia in range(NUM_DIAS):
            calorias_diarias = 0
            proteinas_diarias = 0
            carbohidratos_diarias = 0
            grasas_diarias = 0

            suma_num_alimentos = 0
            
            # Recorre cada tipo de comida en el dia
            for indice_comida, comida in enumerate(COMIDAS):
                num_alimentos = comida["num_alimentos"]

                # Itera sobre cada alimento en la comida actual
                for indice_alimento in range(num_alimentos):
                    idx = (dia * NUM_ALIMENTOS_DIARIO) + suma_num_alimentos + indice_alimento
                    alimento = self.comida_bd[int(x_reparada[idx])]

                    # Suma las calorias y macronutrientes del alimento actual
                    calorias_diarias += alimento["calorias"]
                    proteinas_diarias += alimento["proteinas"]
                    carbohidratos_diarias += alimento["carbohidratos"]
                    grasas_diarias += alimento["grasas"]

                    # Calcula penalizaciones por preferencia
                    total_penalizaciones_preferencia += objetivo_preferencia_grupo(alimento, self.grupos_gusta, self.grupos_no_gusta)
                
                # Agrega el numero de alimentos de esta comida al total del dia
                suma_num_alimentos += num_alimentos

            # Calcula desviaciones
            desviacion_objetivo_calorias = objetivo_calorias(calorias_diarias, self.objetivo_calorias)
            total_desviaciones_calorias += desviacion_objetivo_calorias

            desviacion_objetivo_macronutrientes = objetivo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)
            total_desviaciones_macronutrientes += desviacion_objetivo_macronutrientes

        # Calcula fitness
        fitness_objetivo_calorias = total_desviaciones_calorias
        fitness_objetivo_macronutrientes = total_desviaciones_macronutrientes
        fitness_objetivo_preferencia = total_penalizaciones_preferencia

        # Establece objetivos a minimizar
        out["F"] = np.array([fitness_objetivo_calorias, fitness_objetivo_macronutrientes, fitness_objetivo_preferencia])


    def filtrar_comida(self, tipo):
        """Filtra la base de datos de comida segun el tipo de comida."""
        return filtrar_comida(self.comida_bd, tipo, self.edad)


def ejecutar_algoritmo_genetico(comida_bd, objetivo_calorico, edad, grupos_alergia, grupos_gusta, grupos_no_gusta, seed):

    problema = PlanningComida(comida_bd, objetivo_calorico, edad, grupos_alergia, grupos_gusta, grupos_no_gusta)

    algoritmo = NSGA2(
        pop_size=100,  # Tamaño de la poblacion
        sampling=CustomIntegerRandomSampling(problema),  # Inicializacion personalizada
        crossover=SinglePointCrossover(prob=1),  # Cruzamiento
        mutation=CustomMutation(problema, prob_mutation=1/77),  # Mutacion personalizada
        eliminate_duplicates=True,
        seed=seed   # Semilla
    )

    resultado = minimize(
        problema,
        algoritmo,
        ('n_gen', 100),  # Numero de generaciones
        verbose=True,
        save_history=True
    )
    
    return resultado