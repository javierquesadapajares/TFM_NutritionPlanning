#ag_nsga2_metodo_separatista.py

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.operators.crossover.pntx import SinglePointCrossover, TwoPointCrossover
from pymoo.config import Config

from src.utilidades.funciones_auxiliares import calculo_macronutrientes, filtrar_comida
from src.utilidades.database import comida_basedatos
from src.utilidades.constantes import *
from src.utilidades.operadores_custom import CustomIntegerRandomSampling, CustomMutation

Config.warnings['not_compiled'] = False

comida_bd = comida_basedatos()


def objetivo_calorias(calorias_diarias, objetivo_calorico):
    """Calcula la desviacion entre las calorias diarias consumidas y el objetivo calorico."""

    desviacion_objetivo_calorias = abs(objetivo_calorico - calorias_diarias)

    return desviacion_objetivo_calorias

def restriccion_calorias(calorias_diarias, objetivo_calorico):
    """Aplica penalizacion si las calorias diarias estan fuera del rango aceptable en relacion con el objetivo."""

    limite_inferior = objetivo_calorico * 0.9
    limite_superior = objetivo_calorico * 1.1

    if calorias_diarias < limite_inferior or calorias_diarias > limite_superior:
        penalizacion_calorias = abs(objetivo_calorico - calorias_diarias)
    else:
        penalizacion_calorias = 0

    return penalizacion_calorias


def objetivo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias):
    """Calcula la desviacion de los macronutrientes respecto a los porcentajes ideales."""

    porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)

    desviacion_objetivo_proteinas = abs(porcentaje_proteinas - OBJETIVO_PROTEINAS)
    desviacion_objetivo_carbohidratos = abs(porcentaje_carbohidratos - OBJETIVO_CARBOHIDRATOS)
    desviacion_objetivo_grasas = abs(porcentaje_grasas - OBJETIVO_GRASAS)

    desviacion_macronutrientes = desviacion_objetivo_proteinas + desviacion_objetivo_carbohidratos + desviacion_objetivo_grasas

    return desviacion_macronutrientes

def restriccion_macronutrientes (proteinas_diarias, carbohidratos_diarias, grasas_diarias):
    """Aplica penalizacion si algun macronutriente esta fuera de los limites establecidos."""

    porcentaje_proteinas, porcentaje_carbohidratos, porcentaje_grasas = calculo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)

    penalizacion_macronutrientes = 0

    if porcentaje_proteinas < LIMITE_PROTEINAS[0] or porcentaje_proteinas > LIMITE_PROTEINAS[1]:
        penalizacion_macronutrientes += abs(porcentaje_proteinas - OBJETIVO_PROTEINAS)

    if porcentaje_carbohidratos < LIMITE_CARBOHIDRATOS[0] or porcentaje_carbohidratos > LIMITE_CARBOHIDRATOS[1]:
        penalizacion_macronutrientes += abs(porcentaje_carbohidratos - OBJETIVO_CARBOHIDRATOS)

    if porcentaje_grasas < LIMITE_GRASAS[0] or porcentaje_grasas > LIMITE_GRASAS[1]:
        penalizacion_macronutrientes += abs(porcentaje_grasas - OBJETIVO_GRASAS)

    return penalizacion_macronutrientes


def objetivo_preferencia_grupo(alimento, grupos_gusta, grupos_no_gusta):
    """Calcula la penalizacion de preferencia segun el grupo alimenticio del alimento."""

    penalizacion = 0

    if alimento["grupo"] in grupos_gusta:
        penalizacion = -PENALIZACION_PREFERENCIA
    if alimento["grupo"] in grupos_no_gusta:
        penalizacion = PENALIZACION_PREFERENCIA

    return penalizacion


def restriccion_alergia(alimento, grupos_alergia):
    """Aplica penalizacion cuadratica si el alimento pertenece a un grupo alergico."""

    if alimento["grupo"] in grupos_alergia:
        return (PENALIZACION_ALERGIA)**2
    else:
        return 0
    

class PlanningComida(ElementwiseProblem):
    """Clase que define el problema de planificacion de comida en base a objetivos y restricciones."""
    
    def __init__(self, comida_bd, objetivo_calorias, edad, grupos_alergia, grupos_gusta, grupos_no_gusta):

        super().__init__(n_var=NUM_GENES, n_obj=3, n_constr=3, xl=0, xu=len(comida_bd)-1)  
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

        total_desviaciones_calorias = 0
        total_penalizaciones_calorias = 0

        total_desviaciones_macronutrientes = 0
        total_penalizaciones_macronutrientes = 0

        total_penalizaciones_preferencia = 0
        total_penalizaciones_alergia = 0

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

                    alimento = self.comida_bd[int(x[(dia * NUM_ALIMENTOS_DIARIO) + suma_num_alimentos + indice_alimento])]

                    # Suma las calorias y macronutrientes del alimento actual
                    calorias_diarias += alimento["calorias"]
                    proteinas_diarias += alimento["proteinas"]
                    carbohidratos_diarias += alimento["carbohidratos"]
                    grasas_diarias += alimento["grasas"]

                    # Calcula penalizaciones por preferencia y alergia
                    total_penalizaciones_preferencia += objetivo_preferencia_grupo(alimento, self.grupos_gusta, self.grupos_no_gusta)
                    total_penalizaciones_alergia += restriccion_alergia(alimento, self.grupos_alergia)
                
                # Agrega el numero de alimentos de esta comida al total del dia
                suma_num_alimentos = suma_num_alimentos + num_alimentos
    
            # Calcula desviaciones y penalizaciones
            desviacion_objetivo_calorias = objetivo_calorias(calorias_diarias, self.objetivo_calorias)
            total_desviaciones_calorias += desviacion_objetivo_calorias

            penalizacion_objetivo_calorias = restriccion_calorias(calorias_diarias, self.objetivo_calorias)
            total_penalizaciones_calorias += penalizacion_objetivo_calorias

            desviacion_objetivo_macronutrientes = objetivo_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)
            total_desviaciones_macronutrientes += desviacion_objetivo_macronutrientes

            penalizacion_objetivo_macronutriente = restriccion_macronutrientes(proteinas_diarias, carbohidratos_diarias, grasas_diarias)
            total_penalizaciones_macronutrientes += penalizacion_objetivo_macronutriente

        # Calcula fitness
        fitness_objetivo_calorias = total_desviaciones_calorias
        fitness_objetivo_macronutrientes = total_desviaciones_macronutrientes
        fitness_objetivo_preferencia = total_penalizaciones_preferencia

        fitness_restriccion_alergia = total_penalizaciones_alergia
        fitness_restriccion_calorias = total_penalizaciones_calorias
        fitness_restriccion_macronutrientes = total_penalizaciones_macronutrientes

        # Establece objetivos y restricciones a minimizar
        out["F"] = np.column_stack([fitness_objetivo_calorias, fitness_objetivo_macronutrientes, fitness_objetivo_preferencia])
        out["G"] = np.column_stack([fitness_restriccion_alergia, fitness_restriccion_calorias, fitness_restriccion_macronutrientes])


    def filtrar_comida(self, tipo):
        """Filtra la base de datos de comida segun el tipo de comida."""
        return filtrar_comida(self.comida_bd, tipo, self.edad)
            

def ejecutar_algoritmo_genetico(comida_bd, objetivo_calorico, edad, grupos_alergia, grupos_gusta, grupos_no_gusta, seed,
                                n_gen=100, pop_size=100, prob_cruce=0.9, prob_mut=1/77):

    problema = PlanningComida(comida_bd, objetivo_calorico, edad, grupos_alergia, grupos_gusta, grupos_no_gusta)

    algoritmo = NSGA2(
        pop_size=pop_size,  # Tamaño de la poblacion
        sampling=CustomIntegerRandomSampling(problema),  # Inicializacion personalizada
        crossover=TwoPointCrossover(prob=prob_cruce),  # Cruzamiento
        mutation=CustomMutation(problema, prob_mutation=prob_mut),  # Mutacion personalizada
        eliminate_duplicates=True,
        seed=seed   # Semilla
    )

    resultado = minimize(
        problema,
        algoritmo,
        ('n_gen', n_gen),  # Numero de generaciones
        verbose=True,
        save_history=True
    )
    
    return resultado