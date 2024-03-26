from typing import List

N_SWARM = 100
N_ITERATIONS = 100
W1 = 0.3
W2 = 0.4
W3 = 0.3

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

    def get_mask(self, weights) -> List[int]:

        """"
        Funkcja do wylosowania maski z uwzględnieniem prawdopodobieństw w postacji wag
        
        """
        #TODO: stworzenie listy stanowaiącej maskę z uwzględnieniem podanych wag (watośći w liście są z zakresu 1-3)
        pass

    def crossover1(self, global_best, weights) -> None:
        """
        Funkcja krzyżowania - pierwsza wersja
        Na podstawie maski, obecnej pozycji, najlepszej lokalnej pozycji oraz najlepszej globalnej pozycji aktualizujemy obecną pozycję (patrz artykuł sekcja 4.2.)
        
        Pierwsze podejście zakłada krzyżowanie po wierszach - kolejne elementy maski odpowiadają kolejnym wierszom planszy. Od razu zwracana jest cała plansza.

        """
        # TODO: implementacja pierwszej wersji krzyżowania
        next_pos = []
        self.update_curr_pos(next_pos)

    def crossover2(self, global_best, weights) -> None:
        """
        Funkcja krzyżowania - druga wersja
        Na podstawie maski, obecnej pozycji, najlepszej lokalnej pozycji oraz najlepszej globalnej pozycji aktualizujemy obecną pozycję (patrz artykuł sekcja 4.2.)
        
        Drugie podejście zakłada krzyżowanie po elementach - kolejne elementy maski odpowiadają kolejnym elementom w danym wierszu. Operację powtarzamy dla wszystkich wierszy 
        i dopiero wtedy zwracana jest cała plansza.
         
        """
        # TODO: implementacja drugiej wersji krzyżowania
        next_pos = []
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
