#
# Instituto Federal de Educação, Ciência e Tecnologia - IFPE
# Campus: Igarassu
# Curso: Sistemas para Internet
# Disciplina: Metodologia Científica
# Professor: Allan Lima - allan.lima@igarassu.ifpe.edu.br
#
# Código em Domínio Público: Sinta-se livre para usar, modificar e redistribuir.
#

# Instruções para execução:
# 1) Certifique-se de estar usando Python 3:
#    python3 randomWalkModel.py
# 2) Instale a biblioteca Pillow, se necessário:
#    pip3 install Pillow

import enum
import random
from PIL import Image
import os

# Classe para representar o estado de cada indivíduo na simulação.
class State(enum.Enum):
    healthy = 0    # Saudável
    sick = 1       # Doente
    immune = 2     # Imune
    recovered = 3  # Recuperado
    dead = 4       # Morto

# Classe que representa um indivíduo da população.
class Individual:
    def __init__(self, state):
        self.state = state
        self.previous_state = state

class RandomWalkModel:
    """
    Inicializa a grade da população e os parâmetros da simulação.
    Args:
        populationMatrixSize (int): Tamanho da matriz quadrada da população.
    """
    def __init__(self, populationMatrixSize):
        self.population = []           # Estado atual da população
        self.nextPopulation = []       # Próximo estado da população após interações
        self.currentGeneration = 0     # Contador de gerações
        self.total_cases = 0           # Total de casos (transições para doente)

        # Tabela de probabilidades de transição entre estados
        self.transitionProbabilities = [
            [1.00, 0.00, 0.00, 0.00, 0.00],    # Saudável
            [0.00, 0.10, 0.25, 0.648, 0.002],  # Doente
            [0.00, 0.00, 0.995, 0.005, 0.00],  # Imune
            [0.90, 0.10, 0.00, 0.00, 0.00],    # Recuperado
            [0.00, 0.00, 0.00, 0.00, 1.00],    # Morto
        ]

        self.contagionFactor = 0.06  # Fator de contágio ajustado
        self.socialDistanceEffect = 0.0 # Probabilidade de evitar contato (distanciamento)

        # Inicializa a população com indivíduos saudáveis.
        for i in range(populationMatrixSize):
            self.population.append([])
            self.nextPopulation.append([])
            for j in range(populationMatrixSize):
                self.population[i].append(Individual(State.healthy))
                self.nextPopulation[i].append(Individual(State.healthy))

        # Define um indivíduo doente no centro da matriz.
        startIndex = int(populationMatrixSize / 2)
        self.population[startIndex][startIndex].state = State.sick
        self.population[startIndex][startIndex].previous_state = State.healthy  # Transição inicial
        self.nextPopulation[startIndex][startIndex].state = State.sick
        self.nextPopulation[startIndex][startIndex].previous_state = State.healthy

    def individualTransition(self, line, column):
        individual = self.population[line][column]

        if individual.state == State.dead:
            return
        if individual.state == State.healthy:
            return
        if individual.state == State.sick:
            self.computeSocialInteractions(line, column)

        # Determina o próximo estado com base nas probabilidades
        probabilities = self.transitionProbabilities[individual.state.value]
        number = random.random()
        cumulativeProbability = 0

        for index in range(len(probabilities)):
            cumulativeProbability += probabilities[index]
            if number <= cumulativeProbability:
                self.nextPopulation[line][column].state = State(index)
                break

    def computeSickContact(self, neighbour):
        number = random.random()
        if number <= self.contagionFactor:
            neighbour.state = State.sick  # Indivíduo saudável fica doente

    def computeSocialInteractions(self, line, column):
        initialLine = max(0, line - 1)
        finalLine = min(line + 2, len(self.population))

        for i in range(initialLine, finalLine):
            initialColumn = max(0, column - 1)
            finalColumn = min(column + 2, len(self.population[i]))
            for j in range(initialColumn, finalColumn):
                if i == line and j == column:
                    continue
                avoidContact = self.socialDistanceEffect >= random.random()
                if not avoidContact:
                    neighbour = self.nextPopulation[i][j]
                    if neighbour.state == State.healthy:
                        self.computeSickContact(neighbour)

    def nextGeneration(self):
        # Etapa 1: calcula novos estados
        for i in range(len(self.population)):
            for j in range(len(self.population[i])):
                self.individualTransition(i, j)
        # Etapa 2: conta novos casos e atualiza estados
        for i in range(len(self.population)):
            for j in range(len(self.population[i])):
                individual = self.population[i][j]
                next_individual = self.nextPopulation[i][j]
                if (individual.state in [State.healthy, State.recovered] and next_individual.state == State.sick):
                    self.total_cases += 1
                individual.previous_state = individual.state
                individual.state = next_individual.state

    def report(self):
        states = list(State)
        cases = [0] * len(states)
        for row in self.population:
            for individual in row:
                cases[individual.state.value] += 1
        return cases

    def printReport(self, report):
        for cases in report:
            print(cases, '\t', end=' ')
        print()

    def logHeaders(self, verbose):
        if verbose:
            states = list(State)
            for state in states:
                print(state, '\t', end=' ')
            print()

    def logReport(self, verbose):
        if verbose:
            report = self.report()
            self.printReport(report)

    def simulation(self, generations, verbose):
        self.logHeaders(verbose)
        self.logReport(verbose)
        for _ in range(generations):
            self.nextGeneration()
            self.logReport(verbose)

    def logPopulation(self, population):
        for i in range(len(population)):
            for j in range(len(population)):
                print(population[i][j].state.value, '\t', end = ' ')
            print()
        print()

    def printImage(self, name):
        os.makedirs("img", exist_ok=True)
        lines = len(self.population)
        columns = len(self.population[0])
        img = Image.new(mode="RGB", size=(columns, lines))
        for i in range(lines):
            for j in range(columns):
                state = self.population[i][j].state
                if state == State.healthy:
                    img.putpixel((j, i), (0, 255, 0))       # verde puro
                elif state == State.sick:
                    img.putpixel((j, i), (255, 0, 0))       # vermelho puro
                elif state == State.dead:
                    img.putpixel((j, i), (0, 0, 0))         # preto puro
                elif state == State.immune:
                    img.putpixel((j, i), (0, 255, 255))     # ciano puro
                elif state == State.recovered:
                    img.putpixel((j, i), (255, 0, 255))     # magenta puro
                else:
                    print("INVALID STATE")
        filename = os.path.join("img", f"gen{name}.png")
        img.save(filename)
        img.show()
        print(f"Imagem salva em: {os.path.abspath(filename)}")
        return os.path.abspath(filename)

# PROGRAMA PRINCIPAL

numberOfRuns = 1000             # Quantidade de execuções da simulação
gridSize = 166                # Tamanho da matriz populacional
numberOfGenerations = 52      # Número de gerações/iterações por execução

# Executa a simulação e imprime o número de casos em cada execução
for i in range(numberOfRuns):
    model = RandomWalkModel(gridSize)
    model.simulation(numberOfGenerations, False)
    print(model.total_cases)
    # Para salvar e mostrar a imagem final da simulação, descomente a linha abaixo:
    #model.printImage(i)