#
# Instituto Federal de Educação, Ciência e Tecnologia - IFPE
# Campus: Igarassu
# Course: Internet Systems
# Subject: Scientific Methodology
# Professor: Allan Lima - allan.lima@igarassu.ifpe.edu.br
#
# Public Domain Code: Feel free to use, modify, and redistribute it.
#

# Instructions for running the code:
# 1) If the interpreter does not recognize the enum class, install it using:
#    sudo pip install enum34
# 2) Ensure the code runs on Python 3:
#    python3 randomWalkModel.py

import enum
import random
from PIL import Image
import os

# for image generation:
# pip install Pillow 

# Enum class to represent the possible states of an individual in the simulation.
class State(enum.Enum):
    healthy = 0    # Saudável
    sick = 1       # Doente
    immune = 2     # Imune
    recovered = 3  # Recuperado
    dead = 4       # Morto

class RandomWalkModel:
    """
    Initializes the simulation's population grid and parameters.
    Args:
        populationMatrixSize (int): The size of the square population matrix.
    """
    def __init__(self, populationMatrixSize):
        self.population = []           # Current state of the population grid
        self.nextPopulation = []       # Next state of the population grid after interactions
        self.currentGeneration = 0     # Current generation count
        self.total_cases = 0           # Total number of case transitions (healthy/recovered -> sick)

        # NOVA MATRIZ DE PROBABILIDADES BASEADA NA IMAGEM 1 E ORDEM AJUSTADA
        # Ordem: Saudável, Doente, Imune, Recuperado, Morto
        self.transitionProbabilities = [
            [1.00, 0.00, 0.00, 0.00, 0.00],    # Saudável
            [0.00, 0.10, 0.25, 0.648, 0.002],  # Doente
            [0.00, 0.00, 0.995, 0.005, 0.00],  # Imune
            [0.90, 0.10, 0.00, 0.00, 0.00],    # Recuperado
            [0.00, 0.00, 0.00, 0.00, 1.00],    # Morto
        ]

        self.contagionFactor = 0.06  # Atualizado conforme imagem 
        self.socialDistanceEffect = 0.0 # Probability of avoiding contact because of social distancing


        # Initializes the population matrix with healthy individuals.
        for i in range(populationMatrixSize):
            self.population.append([])
            self.nextPopulation.append([])
            for j in range(populationMatrixSize):
                self.population[i].append(Individual(State.healthy))
                self.nextPopulation[i].append(Individual(State.healthy))

        # Sets the initial sick individual at the center of the matrix.
        startIndex = int(populationMatrixSize / 2)
        self.population[startIndex][startIndex].state = State.sick
        self.population[startIndex][startIndex].previous_state = State.healthy  # Initial transition
        self.nextPopulation[startIndex][startIndex].state = State.sick
        self.nextPopulation[startIndex][startIndex].previous_state = State.healthy

    """
    Determines the next state of an individual based on transition probabilities 
    and processes interactions if the individual is sick.
    
    Args:
        line (int): The row index of the individual.
        column (int): The column index of the individual.
    """
    def individualTransition(self, line, column):
        individual = self.population[line][column]

        if (individual.state == State.dead):  # Skips transitions for dead individuals
            return
        
        if (individual.state == State.healthy):  # Skips transitions for healthy individuals
            return
        
        if (individual.state == State.sick):  # Only sick individuals spread the virus
            self.computeSocialInteractions(line, column)

        # Determines the next state using probabilities for the current state
        probabilities = self.transitionProbabilities[individual.state.value]
        number = random.random()
        cumulativeProbability = 0

        for index in range(len(probabilities)):
            cumulativeProbability += probabilities[index]
            if number <= cumulativeProbability:
                self.nextPopulation[line][column].state = State(index)
                break

    """
    Simulates the possibility of a healthy individual becoming sick 
    after interacting with a sick individual.
    
    Args:
        neighbour (Individual): The healthy individual being evaluated.
    """
    def computeSickContact(self, neighbour):
        number = random.random()
        if (number <= self.contagionFactor):
            neighbour.state = State.sick  # an individual becomes sick

    """
    Evaluates interactions between a sick individual and its neighbors, 
    considering the possibility of contagion.
    
    Args:
        line (int): The row index of the sick individual.
        column (int): The column index of the sick individual.
    """
    def computeSocialInteractions(self, line, column):
        individual = self.population[line][column]
        initialLine = max(0, line - 1)
        finalLine = min(line + 2, len(self.population))

        for i in range(initialLine, finalLine):
            initialColumn = max(0, column - 1)
            finalColumn = min(column + 2, len(self.population[i]))

            for j in range(initialColumn, finalColumn):
                if (i == line and j == column): # Skips the individual itself
                    continue

                avoidContact = self.socialDistanceEffect >= random.random()

                if (not avoidContact):
                    neighbour = self.nextPopulation[i][j]
                    if (neighbour.state == State.healthy):
                        self.computeSickContact(neighbour)

    """
    Advances the simulation by transitioning all individuals 
    to their next state based on current conditions.
    Also counts the number of new cases occurred in this generation.
    """
    def nextGeneration(self):
        # Step 1: compute new states
        for i in range(len(self.population)):
            for j in range(len(self.population[i])):
                self.individualTransition(i, j)

        # Step 2: count new cases and update states & previous_states
        for i in range(len(self.population)):
            for j in range(len(self.population[i])):
                individual = self.population[i][j]
                next_individual = self.nextPopulation[i][j]
                # Count transition: healthy or recovered to sick
                if (individual.state in [State.healthy, State.recovered] and next_individual.state == State.sick):
                    self.total_cases += 1
                # Update previous_state before copying state
                individual.previous_state = individual.state
                # Copy next state to current
                individual.state = next_individual.state

    """Generates a report of the current state counts in the population."""
    def report(self):
        states = list(State)
        cases = [0] * len(states)

        for row in self.population:
            for individual in row:
                cases[individual.state.value] += 1

        return cases

    """Prints the simulation report to the console."""
    def printReport(self, report):
        for cases in report:
            print(cases, '\t', end=' ')
        print()

    """
    Logs column headers representing states if verbose mode is enabled.
    
    Args:
        verbose (bool): Whether to print the headers.
    """
    def logHeaders(self, verbose):
        if (verbose):
            states = list(State)
            for state in states:
                print(state, '\t', end = ' ')
            print()
	
    """
    Logs the simulation's current state counts if verbose mode is enabled.

    Args:
        verbose (bool): Whether to print the report.
    """
    def logReport(self, verbose):
        if (verbose):
            report = self.report()
            self.printReport(report)
	
    """
        Runs the simulation for the specified number of generations, 
        logging results if verbose mode is enabled.
        
        Args:
            generations (int): The number of generations to simulate.
            verbose (bool): Whether to print detailed simulation logs.
        """
    def simulation(self, generations, verbose):
        self.logHeaders(verbose)
        self.logReport(verbose)
        for i in range(generations):
            self.nextGeneration()
            self.logReport(verbose)

    """Prints the status of each individual in the population on the console, formatted in table form."""
    def logPopulation(self, population):
        for i in range(len(population)):
            for j in range(len(population)):
                print(population[i][j].state.value, '\t', end = ' ')
            print()
        print()

    """
        Creates and displays an image of the population after the end of the simulation.
        Pure colors:
        - Saudável (healthy):       verde puro      (0,255,0)
        - Doente (sick):           vermelho puro   (255,0,0)
        - Morto (dead):            preto puro      (0,0,0)
        - Imune (immune):          ciano puro      (0,255,255)
        - Recuperado (recovered):  magenta puro    (255,0,255)
        Salva na pasta img/
    """
    def printImage(self, name):
        # Garante que a pasta img existe
        os.makedirs("img", exist_ok=True)
        lines = len(self.population)
        columns = len(self.population[0])
        img = Image.new(mode="RGB", size=(columns, lines))
        for i in range(lines):
            for j in range(columns):
                state = self.population[i][j].state
                if state == State.healthy:
                    img.putpixel((i, j), (0, 255, 0))       # verde puro
                elif state == State.sick:
                    img.putpixel((i, j), (255, 0, 0))       # vermelho puro
                elif state == State.dead:
                    img.putpixel((i, j), (0, 0, 0))         # preto puro
                elif state == State.immune:
                    img.putpixel((i, j), (0, 255, 255))     # ciano puro
                elif state == State.recovered:
                    img.putpixel((i, j), (255, 0, 255))     # magenta puro
                else:
                    print("INVALID STATE")

        filename = os.path.join("img", f"gen{name}.png")
        img.save(filename)
        img.show()
        print(f"Imagem salva em: {os.path.abspath(filename)}")
        return os.path.abspath(filename)

# MAIN PROGRAM

numberOfRuns = 1000       # Number of simulation runs
gridSize = 166            # Size of the population grid
numberOfGenerations = 52  # Number of generations (iterations) per simulation run

# Run the simulation multiple times and print the number of cases after each run
for i in range(numberOfRuns):
    model = RandomWalkModel(gridSize)
    model.simulation(numberOfGenerations, False)
    print("Casos ocorridos:", model.total_cases)
    # Para salvar e mostrar a imagem final da simulação, descomente a linha abaixo:
    # model.printImage(i)