# Jeśli to nie da zadawalających rezultatów warto przed puszczeniem algorytmu genetycznego uzupełnić niektóre pola za pomocą prostych zasad logicznych
# - patrz artykuł J.M.Weiss, Genetic Algorithms and Sudoku, 2009

import random
from random import sample
import numpy as np
from typing import List
from numpy import random
from copy import deepcopy
from input_sudoku import *


# TODO: parametry do zmiany
N_POPULATION = 200  # rozmiar populacji
MAX_ITERATIONS = 200  # maksymalna liczba iteracji dla algorytmu genetycznego
MUTATION_PROB = 0.1  # prawdopodobieństwo mutacji
CROSSOVER_PROB = 1  # prawdopodobieństwo krzyżowania

iterations = 0


class Sudoku:
    def __init__(self, puzzle, level=1) -> None:
        """
            - puzzle (List[List[int]]): plansza sudoku z częściowym wypełnieniem; puste pola wypełniane zerami
            - level (int): poziom trudności sudoku w skali 1-5 (albo inna skala)
        """
        self.grid = puzzle
        self.level = level

    def __str__(self) -> str:
        separator_line = "+-------+------+------+"
        rows = []
        for i in range(9):
            if i % 3 == 0:
                rows.append(separator_line)
            row = "|"
            for j in range(9):
                if j % 3 == 0:
                    row += " "
                if self.grid[i][j] == 0:
                    row += "."
                else:
                    row += str(self.grid[i][j])
                row += " "
            row += "|"
            rows.append(row)
        rows.append(separator_line)
        
        # Informacja o poziomie trudności:
        level_info = f"Difficulty Level: {self.level}"
        rows.insert(0, level_info)
        
        return '\n'.join(rows)

class Solution:
    def __init__(self, grid) -> None:
        self.grid = grid
        self.fitness = self.get_fitness(grid)

    def get_fitness(self, grid: List[List[int]]) -> int:
        """
        Funkcja zwracająca dopasowanie rozwiązania, przy czym fitness == 0 oznacza rozwiązanie poprawne

        - grid (List[List[int]]): plansza sudoku

        """
        fitness_value = 0

        # Sprawdzenie wierszy i kolumn
        for i in range(9):
            row = grid[i]
            col = [grid[j][i] for j in range(9)]
            fitness_value += (9 - len(set(row)))
            fitness_value += (9 - len(set(col)))

        # Sprawdzenie bloków 3x3
        subgrids = giveSubgrids(grid)
        for subgrid in subgrids:
            flat_subgrid = [elem for row in subgrid for elem in row]
            fitness_value += (9 - len(set(flat_subgrid)))

        return fitness_value


def GA(sudoku: Sudoku) -> Sudoku:
    """
    Funkcja algorytmu genetycznego do znajdowania rozwiązania sudoku

        - sudoku (Sudoku): zagadka sudoku, dla której chcemy otrzymać rozwiązanie

    """
    global iterations
    
    P = createPopulation(sudoku)
    while not converge(P) and iterations < MAX_ITERATIONS:  # wykonujemy dopóki nie znaleziono dokładnego rozwiązania lub nie wykonano określonej liczby iteracji
        PP = crossover(P)
        PPP = mutation(PP, prob=MUTATION_PROB, sudoku=sudoku)
        P = select(P, PPP)
        iterations += 1
    return best(P)


def giveSubgrids(grid: List[List[int]]) -> List[List[List[int]]]:
    """
    Funkcja zwracająca listę bloków 3x3 utworzoną z zadanej planszy sudoku

        - grid (List[List[int]]): plansza sudoku

    """
    subgrids = []

    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            subgrid = [row[j:j + 3] for row in grid[i:i + 3]]
            subgrids.append(subgrid)

    return subgrids


def joinSubgrids(subgrids) -> List[List[int]]:
    """
    Funkcja zwracająca planszę sudoku utworzoną z listy kolejnych bloków 3x3

        - subgrids (List[List[List[int]]]): lista kolejnych bloków 3x3 planszy

    """
    grid9x9 = [[] * 9 for _ in range(9)]

    for i, subgrid in enumerate(subgrids):

        for j, row in enumerate(subgrid):
            grid9x9[i // 3 * 3 + j] += row

    return grid9x9


def createPopulation(sudoku: Sudoku) -> List[Solution]:
    """
    Funkcja zwracająca populację przypadkowych rozwiązań sudoku zadanej wielkości

        - sudoku (Sudoku): zagadka sudoku, dla której chcemy otrzymać rozwiązanie

    """
    P = []
    for _ in range(N_POPULATION):
        new_grid = deepcopy(sudoku.grid)
        subgrids = giveSubgrids(new_grid)
        for subgrid in subgrids:
            nums = set(range(1, 10))
            for row in subgrid:
                for elem in row:
                    if elem in nums:
                        nums.remove(elem)
            nums = list(nums)
            random.shuffle(nums)
            for i, row in enumerate(subgrid):
                for j, elem in enumerate(row):
                    if elem == 0:
                        subgrid[i][j] = nums.pop()
        new_grid = joinSubgrids(subgrids)
        P.append(Solution(new_grid))
    return P


def mutation(P, prob, sudoku: Sudoku) -> List[Solution]:
    """
    Funckja zwracająca populację rozwiązań sudoku poddanych operacji mutacji z zadanym prawdopodobieństwem mutacji


P (List[Solution]): populacja początkowa
prob (float): prawdopodobieństwo mutacji

    """
    PP = []
    initial_positions = []
    for i in range(9):
        for j in range(9):
            if sudoku.grid[i][j] != 0:
                initial_positions += (i, j)
    for solution in P:
        subgrids = giveSubgrids(solution.grid)
        for i, subgrid in enumerate(subgrids):
            if random.random() < prob:  # czy zachodzi mutacja
                # Pobieranie możliwych do zamiany pozycji, z wykluczeniem pozycji ustalonych na początku
                mutable_positions = [(r, c) for r in range(3) for c in range(3) if not ((i // 3 * 3 + r, i % 3 * 3 + c) in initial_positions)]
                if len(mutable_positions) > 1:
                    a, b = sample(range(len(mutable_positions)), 2)
                    ra, ca = mutable_positions[a]
                    rb, cb = mutable_positions[b]
                    subgrid[ra][ca], subgrid[rb][cb] = subgrid[rb][cb], subgrid[ra][ca]

        mutatedGrid = joinSubgrids(subgrids)
        PP.append(Solution(mutatedGrid))
    return PP


def crossover(P, crossover_probability=CROSSOVER_PROB) -> List[Solution]:
    """
    Funkcja zwracająca populację rozwiązań sudoku poddanych operacji krzyżowania

        - P (List[Solution]): populacja początkowa
        - crossover_probabilty (float): prawdopodobieństwo krzyżowania

    """
    PP = []

    # trzeba wybrać rodziców o najmniejszych dopasowaniach, a następnie przypadkowo wybrać punkt krzyżowania (jeśli jest 9 subgridów to takich punktów będzie 8)
    # sama operacja krzyżowania to połączenie odpowiedniej ilości bloków 3x3 z jednego i drugiego rodzica - w ten sposób powstanie dwóch potomków, których trzeba dodać do populacji

    P = sorted(P, key=lambda s: (s.fitness, random.random()))  # sortowanie rozwiązań według ich dopasowania (rosnąco), jeśli dopasowanie jest takie samo, to kolejność przypadkowa
    n = (N_POPULATION * (N_POPULATION + 1)) / 2  # ilość możliwych par rodziców jakie można wybrać z danej populacji
    prob = [i / n for i in range(1, N_POPULATION + 1)]  # lista prawdopodobieństw - większe prawdopodobieństwo dla rozwiązań o większym dopasowaniu
    for _ in range(N_POPULATION):
        parent1, parent2 = random.choice(P, p=prob, replace=False, size=2)  # wybieranie dwóch różnych losowych rodziców z populacji z uwzględnieniem prawdopodobieństwa dopasowań
        if random.random() < crossover_probability:
            parent1 = giveSubgrids(parent1.grid)
            parent2 = giveSubgrids(parent2.grid)
            crossover_point = random.choice(range(1, 9))
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            PP += [Solution(joinSubgrids(child1)), Solution(joinSubgrids(child2))]
        else:
            PP += [parent1, parent2]

    return PP


def converge(P) -> bool:
    """
    Funkcja sprawdzająca czy należy przerwać algorytm genetyczny

        - P (List[Solution]): populacja początkowa

    """
    for solution in P:
        if solution.fitness == 0:
            return True

    # wszystkie rozwiązania takie same
    for i in range(len(P) - 1):
        if P[i].grid != P[i + 1].grid:
            return False

    return True


def select(P, PP) -> List[Solution]:
    """
    Funkcja wybierająca kolejną populację

        - P (List[Solution]): populacja początkowa
        - PP (List[Solution]): populacja po operacjach krzyżowania i mutacji

    """
    P = sorted(P, key=lambda s: (s.fitness, random.random()), reverse=False)
    PP = sorted(PP, key=lambda s: (s.fitness, random.random()), reverse=False)

    # TODO: parametry do dobrania

    nParents = int(2 * N_POPULATION / 10) + 1  # 20% populacji rodziców + 1
    nChildren = int(5 * N_POPULATION / 10) + 1  # 50% populacji potomków + 1
    nRandom = N_POPULATION - nChildren - nParents  # reszta populacji przypadkowo

    bestOnes = P[:nParents] + PP[:nChildren]  # najlepsze rozwiązania
    others = P[nParents:] + PP[nChildren:]  # pozostałe przypadkowo

    # następna populacja
    nextP = bestOnes + np.ndarray.tolist(random.choice(others, size=nRandom, replace=False))

    return nextP


def best(P) -> Sudoku:
    """
    Funkcja zwracająca najlepsze rozwiązanie z populacji

        - P (List[Solution]): populacja początkowa

    """
    for solution in P:
        if solution.fitness == 0:
            return Sudoku(solution.grid)
    return Sudoku(P[0].grid)


def main() -> None:
    '''
    Main pipeline
    '''
    print('Initial sudoku fitness:', Solution(INPUT_GRID).fitness)

    result = GA(Sudoku(INPUT_GRID, level=DIFFICULTY))

    print(result)
    print('Final fitness:', Solution(result.grid).fitness)


if __name__ == "__main__":
    main()
