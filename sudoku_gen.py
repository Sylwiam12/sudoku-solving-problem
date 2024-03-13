# Jeśli to nie da zadawalających rezultatów warto przed puszczeniem algorytmu genetycznego uzupełnić niektóre pola za pomocą prostych zasad logicznych
# - patrz artykuł J.M.Weiss, Genetic Algorithms and Sudoku, 2009

import random
import numpy as np
from typing import List

# TODO: parametry do zmiany
N_POPULATION = 100  # rozmiar populacji
MAX_ITERATIONS = 200  # maksymalna liczba iteracji dla algorytmu genetycznego
MUTATION_PROB = 0.04  # prawdopodobieństwo mutacji

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


def fitness(grid) -> int:
    """ 
    Funkcja zwracająca dopasowanie rozwiązania, przy czym fitness == 0 oznacza rozwiązanie poprawne

        - grid (List[List[int]]): plansza sudoku

    """
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
    # TODO: połączyć bloki 3x3 z danej listy (9 elementów) w jedną planszę
    pass


def createPopulation(sudoku: Sudoku) -> List[Solution]:
    """
    Funkcja zwracająca populację przypadkowych rozwiązań sudoku zadanej wielkości

        - sudoku (Sudoku): zagadka sudoku, dla której chcemy otrzymać rozwiązanie

    """
    P = []
    for _ in range(N_POPULATION):
        grid = []
        # TODO: tam gdzie są zera w planszy (czyli pola puste) przypisujemy przypadkowe wartości z zakresu 1-9, ale tak żeby w każdym bloku 3x3 nie było powtórzeń
        P += (Solution(grid))
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
                # TODO: zamiana ze sobą dwóch przypadkowych elementów bloku 3x3 (swap) - nie można zamieniać pól, które były dane na początku
                pass
        mutatedGrid = joinSubgrids(subgrids)
        PP += (Solution(mutatedGrid))
    return PP


def crossover(P) -> List[Solution]:  # Dodać parametr prob? (prawdopodobieństwo krzyżowania)
    """
    Funkcja zwracająca populację rozwiązań sudoku poddanych operacji krzyżowania

        - P (List[Solution]): populacja początkowa

    """
    PP = []
    P = sorted(P, key=lambda s: (s.fitness, random.random()))  # sortowanie rozwiązań według ich dopasowania (rosnąco), jeśli dopasowanie jest takie samo, to kolejność przypadkowa
    # TODO: do przemyślenia jak to zrobić
    # prawdopodobnie trzeba wybrać rodziców o najmniejszych dopasowaniach, a następnie przypadkowo wybrać punkt krzyżowania (jeśli jest 9 subgridów to takich punktów będzie 8)
    # sama operacja krzyżowania to połączenie odpowiedniej ilości bloków 3x3 z jednego i drugiego rodzica - w ten sposób powstanie dwóch potomków, których trzeba dodać do populacji
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


if __name__ == "__main__":
    main()
