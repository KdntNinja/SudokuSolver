import logging
import os

import pyautogui
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


class SudokuSolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pyautogui.PAUSE = 0
        self.grid = []
        self.fixed_cells = []
        self.driver = None
        self.wait = None
        self.url = "https://www.livesudoku.com/en/sudoku/evil/"
        self.row_cache = [set() for _ in range(9)]
        self.col_cache = [set() for _ in range(9)]
        self.box_cache = [set() for _ in range(9)]

    def download_ublock_origin(self) -> str:
        self.logger.info("Checking if uBlock Origin extension is already downloaded")
        xpi_path = "uBlock0.xpi"
        if not os.path.exists(xpi_path):
            self.logger.info("Downloading uBlock Origin extension")
            url = "https://github.com/gorhill/uBlock/releases/download/1.60.1b15/uBlock0_1.60.1b15.firefox.signed.xpi"
            response = requests.get(url)
            with open(xpi_path, "wb") as file:
                file.write(response.content)
            self.logger.info("uBlock Origin downloaded")
        else:
            self.logger.info(
                "uBlock Origin extension already exists, skipping download"
            )
        return xpi_path

    def setup_driver(self) -> None:
        self.logger.info("Setting up WebDriver")

        xpi_path = self.download_ublock_origin()

        options = FirefoxOptions()

        if os.getenv("HEADLESS") == "True":
            options.add_argument("--headless")

        service = Service("/usr/bin/geckodriver")

        try:
            self.driver = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 3)

            self.logger.info("Adding uBlock Origin extension")
            self.driver.install_addon(xpi_path, temporary=True)

            self.logger.info("WebDriver setup complete")
        except Exception as e:
            self.logger.error(
                f"Failed to set up WebDriver. Make sure geckodriver is installed and in your PATH: {e}"
            )
            raise

    def teardown_driver(self) -> None:
        self.logger.info("Tearing down WebDriver")
        if self.driver:
            self.driver.quit()
        self.logger.info("WebDriver teardown complete")
        os.system("pkill geckodriver")

    def get_html(self) -> None:
        try:
            self.logger.info("Loading Sudoku page")
            self.driver.get(self.url)
            self.logger.info("Page loaded.")
            playarea = self.driver.find_element(By.CSS_SELECTOR, "#playarea")
            playarea_html = playarea.get_attribute("innerHTML")
            self.logger.info("Getting all HTML in #playarea")
            with open("sudoku_grid.html", "w") as file:
                file.write(playarea_html)
            self.logger.info("HTML saved as 'sudoku_grid.html'.")
        except Exception as e:
            self.logger.error(f"An error occurred while getting the HTML: {e}")

    @staticmethod
    def extract_numbers_from_html(html):
        soup = BeautifulSoup(html, "html.parser")
        td_elements = soup.find_all("td")

        numbers = [
            (
                int(td.find("span", class_="fixedcell").text)
                if td.find("span", class_="fixedcell")
                else 0
            )
            for td in td_elements
        ]
        fixed_cells = [bool(td.find("span", class_="fixedcell")) for td in td_elements]

        return numbers, fixed_cells

    def extract_cells(self) -> None:
        self.logger.info("Extracting Sudoku cells from HTML")
        with open("sudoku_grid.html") as file:
            html = file.read()
        self.grid, self.fixed_cells = self.extract_numbers_from_html(html)
        self._initialize_caches()
        self.logger.info("Cells extracted.")

    def _initialize_caches(self):
        for i in range(9):
            for j in range(9):
                num = self.grid[i * 9 + j]
                if num != 0:
                    self.row_cache[i].add(num)
                    self.col_cache[j].add(num)
                    self.box_cache[(i // 3) * 3 + j // 3].add(num)

    def check_row(self, row: int) -> bool:
        self.logger.info(f"Checking row {row} for uniqueness.")
        numbers = self.grid[row * 9: (row + 1) * 9]
        return self._check_unique(numbers)

    def check_column(self, col: int) -> bool:
        self.logger.info(f"Checking column {col} for uniqueness.")
        numbers = [self.grid[row * 9 + col] for row in range(9)]
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

    def solve(self) -> None:
        if not self.grid:
            self.logger.error("The grid is empty. Cannot solve.")
            return

        self.logger.info("Solving...")
        solved = self._solve(self.grid)
        if solved:
            self.logger.info("Solved!")
            try:
                self._submit_solution()
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
        else:
            self.logger.error("Could not solve the Sudoku puzzle.")

    def _solve(self, grid: list) -> bool:
        empty = self._find_empty(grid)
        if not empty:
            return True
        row, col = empty
        box_index = (row // 3) * 3 + col // 3

        available_numbers = (
                set(range(1, 10))
                - self.row_cache[row]
                - self.col_cache[col]
                - self.box_cache[box_index]
        )

        for number in available_numbers:
            grid[row * 9 + col] = number
            self.row_cache[row].add(number)
            self.col_cache[col].add(number)
            self.box_cache[box_index].add(number)

            if self._solve(grid):
                return True

            grid[row * 9 + col] = 0
            self.row_cache[row].remove(number)
            self.col_cache[col].remove(number)
            self.box_cache[box_index].remove(number)

        return False

    def _find_empty(self, grid: list) -> None | tuple:
        for i in range(9):
            for j in range(9):
                if grid[i * 9 + j] == 0 and not self.fixed_cells[i * 9 + j]:
                    return i, j
        return None

    def _submit_solution(self) -> None:
        self.logger.info("Submitting solution")
        for i in range(9):
            for j in range(9):
                if self.grid[i * 9 + j] != 0 and not self.fixed_cells[i * 9 + j]:
                    try:
                        elem = self.wait.until(
                            lambda driver: driver.find_element(By.ID, f"td{i * 9 + j}")
                        )
                        elem.click()
                        pyautogui.press(str(self.grid[i * 9 + j]))
                    except Exception as e:
                        self.logger.error(f"An error occurred: {e}")
        self.logger.info("Solution submitted.")

    def run(self) -> None:
        self.logger.info("Starting run method")
        self.setup_driver()
        try:
            self.get_html()
            self.extract_cells()
            self.solve()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            self.teardown_driver()
        finally:
            with open("sudoku_grid.html", "w") as file:
                file.truncate(0)
            self.logger.info("Run method complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    solver = SudokuSolver()
    solver.run()