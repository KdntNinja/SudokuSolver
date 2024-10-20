import matplotlib.pyplot as plt
import numpy as np
import os

os.environ["QT_QPA_PLATFORM"] = "x11"


class SudokuSolver:
    def __init__(self, file_location: str):
        self.image_location = file_location
        self.grid = []

    def generate_grid(self):
        # fmt: off
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
        # fmt: on

    def display_grid(self):
        if len(self.grid) == 0:
            print("Error: The grid is empty. Cannot display.")
            return

        grid_2d = np.array(self.grid).reshape(9, 9)

        plt.figure(figsize=(6, 6))
        plt.imshow(np.ones((9, 9)), cmap="gray", vmin=0, vmax=1)

        for (i, j), value in np.ndenumerate(grid_2d):
            if value != 0:
                plt.text(
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
                plt.axhline(i - 0.5, color="black", linewidth=3)
                plt.axvline(i - 0.5, color="black", linewidth=3)
            else:
                plt.axhline(i - 0.5, color="black", linewidth=1)
                plt.axvline(i - 0.5, color="black", linewidth=1)

        plt.title("Sudoku Grid")
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])
        plt.show()

    def solve(self):
        pass

    def run(self):
        self.generate_grid()
        self.display_grid()


if __name__ == "__main__":
    solver = SudokuSolver("sudoku.jpg")
    solver.run()
