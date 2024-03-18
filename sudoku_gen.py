# Jeśli to nie da zadawalających rezultatów warto przed puszczeniem algorytmu genetycznego uzupełnić niektóre pola za pomocą prostych zasad logicznych
# - patrz artykuł J.M.Weiss, Genetic Algorithms and Sudoku, 2009

import random
import numpy as np
from typing import List
from numpy import random

# TODO: parametry do zmiany
N_POPULATION = 100  # rozmiar populacji
MAX_ITERATIONS = 200  # maksymalna liczba iteracji dla algorytmu genetycznego
MUTATION_PROB = 0.04  # prawdopodobieństwo mutacji
CROSSOVER_PROB = 1    # prawdopodobieństwo krzyżowania

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
        # TODO: wypisywanie planszy sudoku wraz z ich poziomem trudności
        pass


class Solution:
    def __init__(self, grid) -> None:
        self.grid = grid
        self.fitness = fitness(grid)
        # self.fitness = 10



    def fitness(grid: List[List[int]]) -> int:
    """
    Funkcja zwracająca dopasowanie rozwiązania, przy czym fitness == 0 oznacza rozwiązanie poprawne

    - grid (List[List[int]]): plansza sudoku

    """
    fitness_value = 0

    # Sprawdzenie wierszy i kolumn
    for i in range(9):
        row = grid[i]
        col = [grid[j][i] for j in range(9)]
        if len(set(row)) != 9 or len(set(col)) != 9:
            fitness_value += 1

    # Sprawdzenie bloków 3x3
    subgrids = giveSubgrids(grid)
    for subgrid in subgrids:
        flat_subgrid = [elem for row in subgrid for elem in row]
        if len(set(flat_subgrid)) != 9:
            fitness_value += 1

    return fitness_value

    # TODO: implementacja funkcji fitness: zliczanie duplikatów w każdej kolumnie, wierszu i bloku 3x3 - brak duplikatów oznacza dopasowanie równe zero, czyli poprawne rozwiązanie
    pass


def GA(sudoku: Sudoku) -> Sudoku:
    """
    Funkcja algorytmu genetycznego do znajdowania rozwiązania sudoku

        - sudoku (Sudoku): zagadka sudoku, dla której chcemy otrzymać rozwiązanie

    """
    global iterations

    P = createPopulation(sudoku)
    while not converge(P) and iterations < MAX_ITERATIONS:  # wykonujemy dopóki nie znaleziono dokładnego rozwiązania lub nie wykonano określonej liczby iteracji
        PP = crossover(P)
        PPP = mutation(PP, prob=MUTATION_PROB)
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
            subgrid = [row[j:j+3] for row in grid[i:i+3]]
            subgrids.append(subgrid)
    
    return subgrids


def joinSubgrids(subgrids) -> List[List[int]]:
    """
    Funkcja zwracająca planszę sudoku utworzoną z listy kolejnych bloków 3x3

        - subgrids (List[List[List[int]]]): lista kolejnych bloków 3x3 planszy

    """

    grid9x9 = [[0] * 9 for _ in range(9)]

    for i, grid3x3 in enumerate(subgrids):
        for j, row in enumerate(grid3x3):
            for k, elem in enumerate(row):
                grid9x9[j + i // 3 * 3][i % 3 * 3 + k] = elem

    return grid9x9


def createPopulation(sudoku: Sudoku) -> List[Solution]:
    """
    Funkcja zwracająca populację przypadkowych rozwiązań sudoku zadanej wielkości

        - sudoku (Sudoku): zagadka sudoku, dla której chcemy otrzymać rozwiązanie

    """
    P = []
    for _ in range(N_POPULATION):
        new_grid = np.copy(sudoku.grid)
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



def mutation(P, prob) -> List[Solution]:
    """
    Funckja zwracająca populację rozwiązań sudoku poddanych operacji mutacji z zadanym prawdopodobieństwem mutacji

        - P (List[Solution]): populacja początkowa
        - prob (float): prawdopodobieństwo mutacji

    """
    PP = []
    for solution in P:
        subgrids = giveSubgrids(solution.grid)
        for subgrid in subgrids:
            if random.random() < prob:  # czy zachodzi mutacja
                      # Pobieranie możliwych do zamiany pozycji, z wykluczeniem pozycji ustalonych na początku
                mutable_positions = [(r, c) for r in range(3) for c in range(3) if not ((i//3*3 + r, i%3*3 + c) in solution.initial_positions)]
                if len(mutable_positions) > 1:
                    a, b = random.choice(range(len(mutable_positions)), size=2, replace=False)
                    # Zamiana miejscami wartości
                    ra, ca = mutable_positions[a]
                    rb, cb = mutable_positions[b]
                    subgrid[ra][ca], subgrid[rb][cb] = subgrid[rb][cb], subgrid[ra][ca]
               
                
        mutatedGrid = joinSubgrids(subgrids)
        PP += (Solution(mutatedGrid))
    return PP


def crossover(P, crossover_probability = CROSSOVER_PROB) -> List[Solution]:  
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
        parent1, parent2 = random.choice(P, p=prob, replace=False, size=2) # wybieranie dwóch różnych losowych rodziców z populacji z uwzględnieniem prawdopodobieństwa dopasowań
        if random.random() < crossover_probability:
            parent1 = giveSubgrids(parent1.grid)
            parent2 = giveSubgrids(parent2.grid)
            crossover_point = random.choice(range(1,9))  
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


def main():
    print("Hello World!")

    # grid1 = [[6, 5, 0, 0 ,0, 7, 9, 0, 3], 
    #         [0, 0, 2, 1, 0, 0, 6, 0, 0],
    #         [9, 0, 0, 0, 6, 3, 0, 0, 4],
    #         [1, 2, 9, 0, 0, 0, 0, 0, 0],
    #         [3, 0, 4, 9, 0, 8, 1, 0, 0],
    #         [0, 0, 0, 3, 0, 0, 4, 7, 9],
    #         [0, 0, 6, 0, 8, 0, 3, 0, 5],
    #         [7, 4 ,0, 5, 0, 0, 0, 0, 1],
    #         [5, 8, 1, 4, 0, 0, 0, 2, 6]]
    # grid2 = [[0, 6, 0, 0, 1, 3, 5, 4, 0],
    #         [0, 8, 0, 0, 0, 0, 0, 1, 6],
    #         [1, 0, 4, 0, 6, 9, 2, 0, 0],
    #         [0, 0, 1, 0, 7, 0, 0, 6, 0],
    #         [0, 0, 6, 0, 2, 0, 3, 0, 0],
    #         [0, 9, 0, 0, 3, 0, 4, 0, 0],
    #         [0, 0, 8, 7, 4, 0, 6, 0, 3],
    #         [5, 3, 0, 0, 0, 0, 0, 9, 0],
    #         [0, 4, 2, 3, 9, 0, 0, 8, 0]]
    # sol1 = Solution(grid1)
    # sol2 = Solution(grid2)
    # P = [sol1, sol2]
    # PP = crossover(P)
    # for sol in PP:
    #     print(sol.grid)
    #     print(" ")

if __name__ == "__main__":
    main()
