import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


_YEAR_COLUMNS = ["Datos", "2024", "2023", "2022", "2021"]


class MacrotrendsScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--window-size=1920,1080")
        self.driver = None
        self.button_accepted = False
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Ciclo de vida del driver
    # ------------------------------------------------------------------

    def start_driver(self):
        if self.driver is None:
            try:
                self.driver = webdriver.Firefox(options=self.options)
            except Exception as e:
                self.logger.error("Error inicializando WebDriver: %s", e)
                self.driver = None

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def close(self):
        self.stop_driver()

    # ------------------------------------------------------------------
    # Punto de entrada público
    # ------------------------------------------------------------------

    def get_financial_data(self, ticker):
        self.start_driver()
        if not self.driver:
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        base_url = f"https://www.macrotrends.net/stocks/charts/{ticker}"
        try:
            self.driver.get(base_url)
            # Esperar a que la página redirija al nombre real de la empresa
            WebDriverWait(self.driver, 15).until(
                lambda d: ticker.lower() in d.current_url.lower() and "stocks/charts" in d.current_url
            )
            current_url = self.driver.current_url

            df_income  = self.extract_table_data(f"{current_url}income-statement")
            df_balance = self.extract_table_data(f"{current_url}balance-sheet")
            df_cashflow = self.extract_table_data(f"{current_url}cash-flow-statement")

            if df_income.empty and df_balance.empty and df_cashflow.empty:
                self.logger.warning("No se encontraron datos financieros para %s.", ticker)
                self.stop_driver()
                return pd.DataFrame(columns=_YEAR_COLUMNS)

            frames = [df for df in [df_income, df_balance, df_cashflow] if not df.empty]
            combined = pd.concat(frames, axis=0).reset_index(drop=True)
            self.stop_driver()
            return combined

        except Exception as e:
            self.logger.error("Error al obtener datos de Macrotrends para %s: %s", ticker, e)
            self.stop_driver()
            return pd.DataFrame(columns=_YEAR_COLUMNS)

    # ------------------------------------------------------------------
    # Extracción de una tabla individual
    # ------------------------------------------------------------------

    def extract_table_data(self, url):
        self.start_driver()
        if not self.driver:
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        self.driver.get(url)

        if not self.button_accepted:
            try:
                accept_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar todo')]"))
                )
                accept_button.click()
                self.button_accepted = True
            except Exception:
                pass  # El diálogo no apareció; se continúa normalmente

        # Esperar a que la tabla de contenido esté presente en lugar de un sleep fijo
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "contentjqxgrid"))
            )
        except Exception:
            self.logger.warning("Tiempo de espera agotado para la tabla en %s.", url)
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        column_headers_div = soup.find('div', id='columntablejqxgrid')
        if not column_headers_div:
            self.logger.warning("No se encontraron encabezados en %s.", url)
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        dates = [h.text.strip() for h in column_headers_div.find_all('div', role='columnheader')]
        if not dates:
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        table = soup.find('div', id='contentjqxgrid')
        if not table:
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        rows = table.find_all('div', role='row')
        if not rows:
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        data = [[col.text.strip() for col in row.find_all('div', class_='jqx-grid-cell')] for row in rows]
        df = pd.DataFrame(data, columns=dates)
        if df.empty:
            return pd.DataFrame(columns=_YEAR_COLUMNS)

        return self._normalizar_columnas(df)

    # ------------------------------------------------------------------
    # Helper: normaliza columnas al esquema estándar
    # ------------------------------------------------------------------

    @staticmethod
    def _normalizar_columnas(df):
        # Eliminar la segunda columna (vacía en Macrotrends) y las dos últimas
        if len(df.columns) > 1:
            df = df.drop(df.columns[1], axis=1)
        if len(df.columns) > 2:
            df = df.iloc[:, :-2]

        # Renombrar las columnas disponibles según _YEAR_COLUMNS
        rename_map = {old: new for old, new in zip(df.columns, _YEAR_COLUMNS)}
        df = df.rename(columns=rename_map)

        # Añadir columnas que falten como N/A
        for col in _YEAR_COLUMNS:
            if col not in df.columns:
                df[col] = "N/A"

        return df
