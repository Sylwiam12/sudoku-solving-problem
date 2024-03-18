from typing import List

class Sudoku:
    def __init__(self, puzzle: List[List[int]], level: int = 1) -> None:
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

# Przykład:
puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]
sudoku = Sudoku(puzzle)
print("Sudoku Puzzle:")
print(sudoku)