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
        # TODO: wypisywanie planszy sudoku wraz z ich poziomem trudności
        pass

class Particle:
    """
    Klasa Particle opisująca cząstkę w roju
    """
    def __init__(self, sudoku: Sudoku) -> None:
        self.curr_pos = self.first_position(sudoku)
        self.local_best_position = self.curr_pos
        self.fitness = self.set_fitness()
        self.sudoku = sudoku
        
        """
            - curr_pos (List[List[int]]): aktualna pozycja
            - local_best_position (List[List[int]]): najlepsza pozycja cząstki lokalnie
            - fitness int: miara dopasowania
            - sudoku (List[List[int]]): plansza
        """
    def first_position(self, sudoku) -> None:
        """
        Funkcja ustalająca pierwszą pozycję cząstki

            - sudoku (List[List[int]]): plansza sudoku

        """
        # TODO: przypisywanie randomowych wartości z zakresu 1-9 pustym polom (nie ruszamy tego co było w podanej planszy) tak, żeby w każdym wierszu nie było powtórzeń
        pass

    def update_curr_pos(self, pos) -> None:
        self.set_local_best_pos(pos)
        self.curr_pos = pos

    def set_fitness(self) -> None:
        """
        Funkcja obliczająca dopasowanie cząstki: sum of number of unique elements in each row, plus, sum of number of unique elements in each column, plus, 
        sum of number of unique elements in each box (patrz artykuł, sekcja 4.1)
        
        """
        # TODO: implementacja jak w artykule
        pass

    def set_local_best_pos(self, next_pos) -> None:
        """
        Funkcja służąca do uaktualnienia najlepszej pozycji lokalnej
        
        """
        #TODO: porównanie local_best_position z curr_pos i uaktualnienie wartości local_best_position
        pass

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

            def get_mask() -> List[List[List[int]]]:
                """
                Funkcja zagnieżdzona, która jest dostępna do wywołania w trakcie działania funkcji crossover
                (może korzystać z parametrów "zamrożonych", stąd brak parametrów w nawiasach)

                """

                return rnd.choices(parent_tup, weights=weights_frozen, k=9)


            func(self, parent_tup, get_mask)  # wykonanie funkcji crossover

        return wrapper


    @decorate_crossover
    def crossover1(self, parent_tup, get_mask) -> None:
        """
        Funkcja krzyżowania - pierwsza wersja
        Na podstawie maski, obecnej pozycji, najlepszej lokalnej pozycji oraz najlepszej globalnej pozycji aktualizujemy obecną pozycję (patrz artykuł sekcja 4.2.)
        
        Pierwsze podejście zakłada krzyżowanie po wierszach - kolejne elementy maski odpowiadają kolejnym wierszom planszy. Od razu zwracana jest cała plansza.

        """
        # TODO: implementacja pierwszej wersji krzyżowania

        mask = get_mask()

        next_pos = []
        self.update_curr_pos(next_pos)

    @decorate_crossover
    def crossover2(self, parent_tup, get_mask):
        """
        Funkcja krzyżowania - druga wersja
        Na podstawie maski, obecnej pozycji, najlepszej lokalnej pozycji oraz najlepszej globalnej pozycji aktualizujemy obecną pozycję (patrz artykuł sekcja 4.2.)
        
        Drugie podejście zakłada krzyżowanie po elementach - kolejne elementy maski odpowiadają kolejnym elementom w danym wierszu. Operację powtarzamy dla wszystkich wierszy 
        i dopiero wtedy zwracana jest cała plansza.
         
        """
        
        for row in range(9):
            mask = get_mask()

            for pos, parent in enumerate(mask):
                choice = parent[row][pos]

                for other_parent in parent_tup:

                    if other_parent is not parent:
                        pos_choice = other_parent[row].index(choice)
                        swap_elements(other_parent[row], pos, pos_choice)
        
        # po operacji krzyżowania każda kopia z trzech cząstek zawiera ten sam wynik krzyżowania (każda jest sobie równa)
        next_pos = parent_tup[0]
        self.update_curr_pos(next_pos)
    
    def mutation(self) -> None:
        """
        Funkcja operacji mutacji:  swap two non-fixed elements in a row (patrz artykuł, sekcja 4.1.)
        """
        next_pos = []
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
        # TODO: należy ustalić parametr self.global_best_position, czyli wybierać spośród self.particles cząstkę o najlepszym dopasowaniu
        pass

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
    
    swarm2 = Swarm(w1=W1, w2=W2, w3=W3)
    
    while not converge(swarm) and iterations < N_ITERATIONS:
        for particle in swarm.particles:
            particle.crossover1(swarm.get_global_best(), swarm.get_weights())
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
    # TODO: czy jest jakaś cząstka z dopasowaniem 273
    pass

def main():
    pass

if __name__ == "__main__":
    main()
