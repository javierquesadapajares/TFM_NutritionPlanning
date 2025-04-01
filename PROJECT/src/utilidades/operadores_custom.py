# operadores_custom.py

import numpy as np

from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.core.mutation import Mutation

from src.utilidades.constantes import *


class CustomIntegerRandomSampling(IntegerRandomSampling):
    """Clase personalizada para la inicializacion de los alimentos"""
    def __init__(self, problem):
        super().__init__()
        self.problem = problem

    def _do(self, problem, n_samples, **kwargs):

        # Inicializacion poblacion (NUM_POB * NUM_GEN)
        poblacion = np.full((n_samples, problem.n_var), np.nan)    

        for indice_individuo in range(n_samples):            
            for dia in range(NUM_DIAS):

                # Posicion inicial del dia
                indice_dia = dia * NUM_ALIMENTOS_DIARIO  

                for comida in COMIDAS:
                    num_alimentos = comida["num_alimentos"]

                    for indice_alimento in range(num_alimentos):
                        
                        match comida["nombre"]:

                            case "Tentempie" | "Merienda":
                                poblacion[indice_individuo, indice_dia] = np.random.choice(self.problem.snacks)

                            case "Desayuno":
                                if indice_alimento == 2:
                                    poblacion[indice_individuo, indice_dia] = np.random.choice(self.problem.bebida_desayuno)
                                else:
                                    poblacion[indice_individuo, indice_dia] = np.random.choice(self.problem.desayuno)

                            case _:
                                if indice_alimento == 2:
                                    poblacion[indice_individuo, indice_dia] = np.random.choice(self.problem.bebidas)
                                else:
                                    poblacion[indice_individuo, indice_dia] = np.random.choice(self.problem.almuerzo_cena)

                        indice_dia += 1
        
        return poblacion



class CustomMutation(Mutation):
    """Clase personalizada para la mutacion de los alimentos"""
    def __init__(self, problem, prob_mutation):
        super().__init__()
        self.problem = problem
        self.prob_mutation = prob_mutation

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            for dia in range(NUM_DIAS):
                
                # Posicion inicial del dia
                indice_dia = dia * NUM_ALIMENTOS_DIARIO

                for comida in COMIDAS:
                    num_alimentos = comida["num_alimentos"]

                    for indice_alimento in range(num_alimentos):
                        if np.random.rand() < self.prob_mutation:

                            match comida["nombre"]:

                                case "Tentempie" | "Merienda":
                                    X[i, indice_dia] = np.random.choice(problem.snacks)

                                case "Desayuno":
                                    if indice_alimento == 2:
                                        X[i, indice_dia] = np.random.choice(problem.bebida_desayuno)

                                    else:
                                        X[i, indice_dia] = np.random.choice(problem.desayuno)

                                case _:
                                    if indice_alimento == 2:
                                        X[i, indice_dia] = np.random.choice(problem.bebidas)
                                        
                                    else:
                                        X[i, indice_dia] = np.random.choice(problem.almuerzo_cena)

                        indice_dia += 1

        return X