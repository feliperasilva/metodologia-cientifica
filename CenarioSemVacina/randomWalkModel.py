import enum
import random
from PIL import Image
import os

class State(enum.Enum):
    healthy = 0
    sick = 1
    immune = 2
    recovered = 3
    dead = 4

class Individual:
    def __init__(self, state):
        self.state = state
        self.previous_state = state

class RandomWalkModel:
    def __init__(self, populationMatrixSize):
        self.population = []
        self.nextPopulation = []
        self.currentGeneration = 0
        self.total_cases = 0

        self.transitionProbabilities = [
            [1.00, 0.00, 0.00, 0.00, 0.00],
            [0.00, 0.18, 0.21, 0.60, 0.01],
            [0.00, 0.00, 0.98, 0.02, 0.00],
            [0.80, 0.20, 0.00, 0.00, 0.00],
            [0.00, 0.00, 0.00, 0.00, 1.00],
        ]

        self.contagionFactor = 0.18
        self.socialDistanceEffect = 0.0

        for i in range(populationMatrixSize):
            self.population.append([])
            self.nextPopulation.append([])
            for j in range(populationMatrixSize):
                self.population[i].append(Individual(State.healthy))
                self.nextPopulation[i].append(Individual(State.healthy))

        startIndex = int(populationMatrixSize / 2)
        self.population[startIndex][startIndex].state = State.sick
        self.population[startIndex][startIndex].previous_state = State.healthy
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
            neighbour.state = State.sick

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
        for i in range(len(self.population)):
            for j in range(len(self.population[i])):
                self.individualTransition(i, j)
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
                print(state, '\t', end = ' ')
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
        # Garante que a pasta img é relativa ao local deste script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(script_dir, "img")
        os.makedirs(img_dir, exist_ok=True)
        lines = len(self.population)
        columns = len(self.population[0])
        img = Image.new(mode="RGB", size=(columns, lines))
        for i in range(lines):
            for j in range(columns):
                state = self.population[i][j].state
                if state == State.healthy:
                    img.putpixel((j, i), (0, 255, 0))
                elif state == State.sick:
                    img.putpixel((j, i), (255, 0, 0))
                elif state == State.dead:
                    img.putpixel((j, i), (0, 0, 0))
                elif state == State.immune:
                    img.putpixel((j, i), (0, 255, 255))
                elif state == State.recovered:
                    img.putpixel((j, i), (255, 0, 255))
                else:
                    print("INVALID STATE")
        filename = os.path.join(img_dir, f"gen{name}.png")
        img.save(filename)
        # img.show()  # Descomente para visualizar a imagem após salvar
        print(f"Imagem salva em: {filename}")
        return filename

# MAIN PROGRAM

numberOfRuns = 10
gridSize = 166
numberOfGenerations = 52

for i in range(numberOfRuns):
    model = RandomWalkModel(gridSize)
    model.simulation(numberOfGenerations, False)
    print("Casos ocorridos:", model.total_cases)
    #model.printImage(i)