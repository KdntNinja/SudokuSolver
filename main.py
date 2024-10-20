import logging

from matplotlib import pyplot as plt
import numpy as np


class SudokuSolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.grid = []

    def generate_grid(self) -> None:
        # fmt: off
        self.grid = [
            [0, 0, 0, 0, 0, 0, 0, 7, 0],
            [0, 7, 8, 0, 0, 0, 2, 0, 0],
            [0, 0, 6, 0, 0, 5, 0, 8, 0],
            [5, 0, 0, 0, 6, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 4, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 4, 0, 9],
            [0, 0, 0, 8, 7, 6, 0, 0, 0],
            [0, 0, 0, 2, 0, 0, 0, 0, 3],
            [0, 0, 0, 5, 0, 0, 0, 1, 2]
        ]
        # fmt: on

    def display_grid(self) -> None:
        if not self.grid:
            self.logger.error("The grid is empty. Cannot display.")
            return

        self.logger.info(f"Displaying the grid. {self.grid}")
        grid_2d = np.array(self.grid)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(np.ones((9, 9)), cmap="gray", vmin=0, vmax=1)

        for (i, j), value in np.ndenumerate(grid_2d):
            if value != 0:
                ax.text(
                    j,
                    i,
                    str(int(value)),
                    ha="center",
                    va="center",
                    fontsize=20,
                    color="black",
                )

        for i in range(10):
            if i % 3 == 0:
                ax.axhline(i - 0.5, color="black", linewidth=3)
                ax.axvline(i - 0.5, color="black", linewidth=3)
            else:
                ax.axhline(i - 0.5, color="black", linewidth=1)
                ax.axvline(i - 0.5, color="black", linewidth=1)

        ax.set_title("Sudoku Grid")
        ax.set_xticks([])
        ax.set_yticks([])

        plt.show()

    def check_row(self, row: int) -> bool:
        self.logger.debug(f"Checking row {row} for uniqueness.")
        numbers = self.grid[row]
        return self._check_unique(numbers)

    def check_column(self, col: int) -> bool:
        self.logger.debug(f"Checking column {col} for uniqueness.")
        numbers = [self.grid[row][col] for row in range(9)]
        return self._check_unique(numbers)

    @staticmethod
    def _check_unique(numbers: list) -> bool:
        seen = set()
        for number in numbers:
            if number != 0:
                if number in seen:
                    return False
                seen.add(number)
        return True

    def solve(self):
        if not self.grid:
            self.logger.error("The grid is empty. Cannot solve.")
            return

        self.logger.info("Solving...")
        solved = self._solve(self.grid)
        if solved:
            self.logger.info("Solved!")
            self.display_grid()
        else:
            self.logger.error("Could not solve the Sudoku puzzle.")

    def _solve(self, grid: list) -> bool:
        empty = self._find_empty(grid)
        if not empty:
            return True
        row, col = empty
        for number in range(1, 10):
            if self._is_valid(grid, (row, col), number):
                grid[row][col] = number
                if self._solve(grid):
                    return True
                grid[row][col] = 0
        return False

    @staticmethod
    def _find_empty(grid: list) -> None | tuple:
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    return i, j
        return None

    @staticmethod
    def _is_valid(grid: list, position: tuple, number: int) -> bool:
        row, col = position
        if number in grid[row]:
            return False

        if number in [grid[r][col] for r in range(9)]:
            return False

        box_row_start = (row // 3) * 3
        box_col_start = (col // 3) * 3
        for r in range(box_row_start, box_row_start + 3):
            for c in range(box_col_start, box_col_start + 3):
                if grid[r][c] == number:
                    return False
        return True

    def run(self):
        self.generate_grid()
        self.solve()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    solver = SudokuSolver()
    solver.run()
