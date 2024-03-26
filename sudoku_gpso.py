from typing import List, Callable, Tuple
import random as rnd
from copy import deepcopy



N_SWARM = 100
N_ITERATIONS = 100
W1 = 0.3    # waga obecnej pozycji curr_pos
W2 = 0.4    # waga najlepszej pozycji lokalnej
W3 = 0.3    # waga najlepszej pozycji globalnej global_best_position

iterations = 0


def swap_elements(lst: List[int], pos1: int, pos2: int) -> None:
    '''
    Funkcja zamieniająca miejscami wartości na pozycjach pos1 i pos2 w podanej liście lst
        - param lst: lista, w której następuje zamiana miejsc
        - param pos1: pierwsza pozycja zamiany
        - param pos2: druga pozycja zamiany
    '''
    lst[pos1], lst[pos2] = lst[pos2], lst[pos1]

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

class Particle:
    """
    Klasa Particle opisująca cząstkę w roju
    """
    def __init__(self, sudoku: Sudoku) -> None:
        self.curr_pos = self.first_position(sudoku)
        self.local_best_position = self.curr_pos
        self.fitness = self.set_fitness(self.curr_pos)
        self.sudoku = sudoku
        
        """
            - curr_pos (List[List[int]]): aktualna pozycja
            - local_best_position (List[List[int]]): najlepsza pozycja cząstki lokalnie
            - fitness int: miara dopasowania
            - sudoku (List[List[int]]): plansza
        """

    def first_position(self, sudoku: Sudoku) -> List[List[int]]:
        """
        Funkcja ustalająca pierwszą pozycję cząstki

            - sudoku (Sudoku): plansza sudoku

        """
        for row in sudoku.grid:
            empty_indices = [i for i, x in enumerate(row) if x == 0]
            possible_values = list(set(range(1, 10)) - set(row))
            rnd.shuffle(possible_values)
            for index in empty_indices:
                row[index] = possible_values.pop()

        return sudoku.grid

    def update_curr_pos(self, pos) -> None:
        self.set_local_best_pos(pos)
        self.curr_pos = pos

    @staticmethod
    def set_fitness(pos) -> int:
        """
        Funkcja obliczająca dopasowanie cząstki: sum of number of unique elements in each row, plus, sum of number of unique elements in each column, plus, 
        sum of number of unique elements in each box (patrz artykuł, sekcja 4.1)
        
        """

        # Suma unikalnych elementów w każdym wierszu
        row_fitness = sum(len(set(row)) for row in pos)

        # Suma unikalnych elementów w każdej kolumnie
        col_fitness = sum(len(set(col)) for col in zip(*pos))

        # Suma unikalnych elementów w każdym kwadracie 3x3
        box_fitness = 0
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                box = [pos[x][y] for x in range(i, i + 3) for y in range(j, j + 3)]
                box_fitness += len(set(box))

        # Sumowanie wartości fitness dla wierszy, kolumn i kwadratów
        total_fitness = row_fitness + col_fitness + box_fitness
        return total_fitness

    def set_local_best_pos(self, next_pos) -> None:
        """
        Funkcja służąca do uaktualnienia najlepszej pozycji lokalnej
        
        """
        if self.fitness < Particle.set_fitness(next_pos):
           self.local_best_position = next_pos
           self.fitness = self.set_fitness()

    @staticmethod
    def decorate_crossover(func) -> Callable[[List[List[int]], Tuple[List[List[int]]]], None]:
        """
        Dekorator funkcji crossover do zainicjalizowania tuple'a z rodzicami i udostępnienia funkcji do wylosowania
        maski z uwzględnieniem prawdopodobieństw w postacji wag

            - func: funkcja do wykonania (crossover1, bądź crossover2), której funkcjonalności mają zostać
            rozszerzone o to, co jest we wrapperze

        """

        def wrapper(self, global_best, weights) -> None:
            """
            Przy wywołaniu funkcji crossover następuje de facto wywołanie funkcji wrapper, stąd przy wywołaniu crossover
            podajemy tylko parametry wrappera, a nie funkcji crossover

            """

            parent_tup = (
                deepcopy(self.curr_pos),
                deepcopy(self.local_best_position),
                deepcopy(global_best)
            )

            weights_frozen = weights

            def gen_mask(loops: int) -> List[List[List[int]]]:
                """
                Funkcja zagnieżdzona, która jest dostępna do wywołania w trakcie działania funkcji crossover
                (może korzystać z parametrów "zamrożonych", stąd brak parametrów w nawiasach)

                """

                for _ in range(loops):
                    yield rnd.choices(parent_tup, weights=weights_frozen, k=9)


            next_pos = func(self, parent_tup, gen_mask)  # wykonanie funkcji crossover

            # po operacji krzyżowania każda kopia z trzech cząstek zawiera ten sam wynik krzyżowania (każda jest sobie równa)
            self.update_curr_pos(next_pos)

        return wrapper


    @decorate_crossover
    def crossover1(self, _, gen_mask) -> List[List[int]]:
        """
        Funkcja krzyżowania - pierwsza wersja
        Na podstawie maski, obecnej pozycji, najlepszej lokalnej pozycji oraz najlepszej globalnej pozycji aktualizujemy obecną pozycję (patrz artykuł sekcja 4.2.)
        
        Pierwsze podejście zakłada krzyżowanie po wierszach - kolejne elementy maski odpowiadają kolejnym wierszom planszy. Od razu zwracana jest cała plansza.

        """

        mask = next(gen_mask(1))
        result = []

        for row, parent in enumerate(mask):
            result.append(parent[row])

        return result

    @decorate_crossover
    def crossover2(self, parent_tup, gen_mask) -> List[List[int]]:
        """
        Funkcja krzyżowania - druga wersja
        Na podstawie maski, obecnej pozycji, najlepszej lokalnej pozycji oraz najlepszej globalnej pozycji aktualizujemy obecną pozycję (patrz artykuł sekcja 4.2.)
        
        Drugie podejście zakłada krzyżowanie po elementach - kolejne elementy maski odpowiadają kolejnym elementom w danym wierszu. Operację powtarzamy dla wszystkich wierszy 
        i dopiero wtedy zwracana jest cała plansza.
         
        """
        
        for row, mask in enumerate(gen_mask(9)):

            for pos, parent in enumerate(mask):
                choice = parent[row][pos]

                for other_parent in parent_tup:

                    if other_parent is not parent:
                        pos_choice = other_parent[row].index(choice)
                        swap_elements(other_parent[row], pos, pos_choice)

        return parent_tup[0]
    
    def mutation(self) -> None:
        """
        Funkcja operacji mutacji:  swap two non-fixed elements in a row (patrz artykuł, sekcja 4.1.)
        """

        next_pos = [row[:] for row in self.curr_pos]  # Tworzymy głęboką kopię obecnej pozycji
        for i in range(9):  # i - wiersz, j - kolumna
            # wyszukanie pozycji, które można zamienić
            non_fixed_positions = [j for j, val in enumerate(self.curr_pos[i]) if self.sudoku.grid[i][j] == 0]
            
            if len(non_fixed_positions) > 1:
                swap_positions = rnd.sample(non_fixed_positions, 2)

                next_pos[i][swap_positions[0]], next_pos[i][swap_positions[1]] = next_pos[i][swap_positions[1]], next_pos[i][swap_positions[0]]
        
        self.update_curr_pos(next_pos)


class Swarm:
    """
    Klasa Swarm opisująca rój cząstek
    """
    def __init__(self, w1, w2, w3) -> None:
        self.global_best_position = None
        self.particles = []
        self.size = len(self.particles)
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        
        """
            - global_best_position (List[List[int]]): najlepsza pozycja w roju
            - particles (List[Particle]): lista cząstek - rój
            - size int: rozmiar roju
            - w1, w2, w3 float:  parametr poznawczy, parametry zbiorowy, etc w1+w2+w3=1 oraz  w1, w2, w3>0
        """

    def add_particle(self, particle: Particle) -> None:
        self.particles.append(particle)

    def set_global_best(self) -> None:
        
        """
        Funkcja służąca do uaktualnienia najlepszej pozycji globalnej

        """
        best = self.particles[0]
        for particle in self.particles:
            if particle.fitness > best.fitness:
                best = particle
        self.global_best_position = best

    def get_global_best(self) -> List[List[int]]:
        return self.global_best_position
    
    def get_weights(self) -> tuple[float, float, float]:
        return self.w1, self.w2, self.w3


def GPSO(sudoku: Sudoku) -> Sudoku:
    global iterations

    swarm = Swarm(w1=W1, w2=W2, w3=W3)
    for _ in range(N_SWARM):
        swarm.add_particle(Particle(sudoku))
    
    swarm.set_global_best()

    while not converge(swarm) and iterations < N_ITERATIONS:
        swarm2 = Swarm(w1=W1, w2=W2, w3=W3)

        for particle in swarm.particles:

            particle.crossover1(swarm.get_global_best().curr_pos, swarm.get_weights())
            particle.mutation()
            swarm2.add_particle(particle)

        swarm = swarm2
        swarm.set_global_best() # TODO: omówić sposób updatowania global_best - czy po każdym krzyżowaniu cząstki? czy tak jak teraz, na nowym roju? 
          
        iterations += 1
        
    return Sudoku(swarm.get_global_best())

def converge(swarm: Swarm) -> bool: 
    """
    Funkcja sprawdzająca czy należy przerwać algorytm GPSO
    """
    for particle in swarm.particles:
        if particle.fitness == 273:
            return True
    return False

def main():
    grid1 = [[6, 5, 0, 0, 0, 7, 9, 0, 3],
             [0, 0, 2, 1, 0, 0, 6, 0, 0],
             [9, 0, 0, 0, 6, 3, 0, 0, 4],
             [1, 2, 9, 0, 0, 0, 0, 0, 0],
             [3, 0, 4, 9, 0, 8, 1, 0, 0],
             [0, 0, 0, 3, 0, 0, 4, 7, 9],
             [0, 0, 6, 0, 8, 0, 3, 0, 5],
             [7, 4, 0, 5, 0, 0, 0, 0, 1],
             [5, 8, 1, 4, 0, 0, 0, 2, 6]]
    # grid1 = [
    #     [9, 0, 2, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 1, 5],
    #     [7, 0, 0, 6, 0, 2, 0, 0, 0],
    #     [0, 0, 0, 7, 9, 0, 0, 0, 0],
    #     [0, 6, 1, 0, 8, 0, 0, 0, 2],
    #     [0, 0, 0, 0, 3, 0, 1, 0, 0],
    #     [0, 0, 7, 0, 0, 0, 9, 4, 0],
    #     [4, 0, 0, 0, 0, 0, 0, 2, 1],
    #     [0, 8, 0, 0, 0, 4, 6, 0, 0]
    # ]

    best_particle = GPSO(Sudoku(grid1))

    for row in best_particle.grid.sudoku.grid:
        print(row)

    print(best_particle.grid.fitness)


if __name__ == "__main__":
    main()
