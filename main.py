import matplotlib.pyplot as plt
import numpy as np


class SudokuSolver:
    def __init__(self, file_location: str):
        self.file_location = file_location
        self.grid = []

    def generate_grid(self):
        self.grid = [
            4, 1, 0, 0, 0, 0, 0, 6, 8,
            6, 0, 0, 0, 0, 0, 0, 2, 0,
            0, 0, 0, 0, 0, 0, 5, 1, 0,
            0, 0, 0, 2, 4, 0, 6, 9, 0,
            3, 0, 0, 0, 5, 0, 0, 0, 0,
            4, 0, 6, 0, 0, 9, 0, 0, 1,
            0, 0, 0, 7, 0, 0, 3, 0, 0,
            9, 0, 2, 0, 6, 4, 0, 0, 0,
            0, 0, 7, 9, 0, 8, 0, 5, 0,
        ]

    def display_grid(self):
        grid_2d = np.array(self.grid).reshape(9, 9)

        plt.figure(figsize=(6, 6))
        plt.imshow(grid_2d, cmap="gray", vmin=0, vmax=9)

        for i in range(10):
            plt.axhline(i - 0.5, color="black", linewidth=2)
            plt.axvline(i - 0.5, color="black", linewidth=2)

        plt.xticks(range(9), range(1, 10))
        plt.yticks(range(9), range(1, 10))
        plt.gca().invert_yaxis()

        for (i, j), value in np.ndenumerate(grid_2d):
            if value != 0:
                plt.text(j, i, str(int(value)), ha='center', va='center', fontsize=20, color='black')

        plt.title("Sudoku Grid")
        plt.show()

    def run(self):
        self.generate_grid()
        self.display_grid()


if __name__ == "__main__":
    solver = SudokuSolver("sudoku.jpg")
    solver.run()
