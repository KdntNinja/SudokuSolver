import logging
import os

import pyautogui
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


class SudokuSolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.grid = []
        self.driver = None
        self.wait = None
        self.url = "https://www.livesudoku.com/en/sudoku/evil/"

    def setup_driver(self) -> None:
        self.logger.info("Setting up WebDriver")
        options = webdriver.FirefoxOptions()
        if os.getenv("HEADLESS") == "True":
            options.add_argument("--headless")

        service = Service("/usr/bin/geckodriver")
        try:
            self.driver = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 30)
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
            try:
                consent_button = WebDriverWait(self.driver, 3).until(
                    lambda driver: driver.find_element(
                        By.XPATH,
                        "//button[@class='fc-button fc-cta-consent fc-primary-button'][contains(., 'Consent')]",
                    )
                )
                consent_button.click()
            except TimeoutException:
                pass
            playarea = self.wait.until(
                lambda driver: driver.find_element(By.CSS_SELECTOR, "#playarea")
            )
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
        numbers = []

        for td in td_elements:
            span = td.find("span", class_="fixedcell")
            if span:
                numbers.append(int(span.text))
            else:
                numbers.append(0)

        return numbers

    def extract_cells(self) -> None:
        self.logger.info("Extracting Sudoku cells from HTML")
        with open("sudoku_grid.html") as file:
            html = file.read()
        self.grid = self.extract_numbers_from_html(html)
        self.logger.info("Cells extracted.")

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
        for number in range(1, 10):
            if self._is_valid(grid, (row, col), number):
                grid[row * 9 + col] = number
                if self._solve(grid):
                    return True
                grid[row * 9 + col] = 0
        return False

    @staticmethod
    def _find_empty(grid: list) -> None | tuple:
        for i in range(9):
            for j in range(9):
                if grid[i * 9 + j] == 0:
                    return i, j
        return None

    @staticmethod
    def _is_valid(grid: list, position: tuple, number: int) -> bool:
        row, col = position
        if number in [grid[row * 9 + c] for c in range(9)]:
            return False

        if number in [grid[r * 9 + col] for r in range(9)]:
            return False

        box_row_start = (row // 3) * 3
        box_col_start = (col // 3) * 3
        for r in range(box_row_start, box_row_start + 3):
            for c in range(box_col_start, box_col_start + 3):
                if grid[r * 9 + c] == number:
                    return False
        return True

    def _submit_solution(self) -> None:
        self.logger.info("Submitting solution")
        for i in range(9):
            for j in range(9):
                if self.grid[i * 9 + j] != 0:
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
            self.logger.info("Run method complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    solver = SudokuSolver()
    solver.run()
