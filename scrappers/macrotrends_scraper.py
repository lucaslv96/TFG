import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

class MacrotrendsScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")  # Ensure the browser runs in headless mode
        self.options.add_argument("--window-size=1920,1080")  # Set window size to avoid issues with headless mode
        self.driver = None
        self.button_accepted = False

    def start_driver(self):
        if (self.driver is None):
            try:
                self.driver = webdriver.Firefox(options=self.options)
            except Exception as e:
                print(f"Error initializing WebDriver: {e}")
                self.driver = None

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def extract_table_data(self, url):
        self.start_driver()
        if not self.driver:
            return pd.DataFrame()

        self.driver.get(url)

        # Solo intentar hacer clic en el botón 'Aceptar todo' si no se ha hecho antes
        if not self.button_accepted:
            try:
                accept_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar todo')]"))
                )
                accept_button.click()
                self.button_accepted = True  # Marcar que ya se hizo clic
            except:
                print("El botón 'Aceptar todo' no se encontró, continuando con la extracción.")

        # Esperar para asegurar que la tabla esté cargada
        time.sleep(5)

        # Obtener el HTML después de la carga
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extraer las cabeceras de la columna (fechas)
        column_headers_div = soup.find('div', id='columntablejqxgrid')
        if column_headers_div is None:
            print("No se encontraron datos en la URL proporcionada.")
            return pd.DataFrame()

        column_headers = column_headers_div.find_all('div', role='columnheader')
        dates = [header.text.strip() for header in column_headers]

        # Extraer la tabla de la sección con id 'contentjqxgrid'
        table = soup.find('div', id='contentjqxgrid')
        rows = table.find_all('div', role='row')

        # Extraer los datos de cada fila
        data = []
        for row in rows:
            cols = row.find_all('div', class_='jqx-grid-cell')
            data.append([col.text.strip() for col in cols])

        # Crear un DataFrame con las fechas como columnas y los valores como filas
        if not data:
            print("No se encontraron datos en la tabla.")
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=dates)
        if not df.empty:
            df = df.drop(df.columns[1], axis=1)  # Eliminar la segunda columna
            df = df.iloc[:, :-2]  # Eliminar las dos últimas columnas
            df.columns.values[0] = "Datos"  # Renombrar la primera columna a "Datos"
            if len(df.columns) > 1:
                df.columns.values[1] = "2024"  # Renombrar la tercera columna a "2023"
            if len(df.columns) > 2:
                df.columns.values[2] = "2023"  # Renombrar la cuarta columna a "2022"
            if len(df.columns) > 3:
                df.columns.values[3] = "2022"  # Renombrar la quinta columna a "2021"
            if len(df.columns) > 4:
                df.columns.values[4] = "2021"  # Renombrar la sexta columna a "2020"
        return df

    def get_financial_data(self, ticker):
        self.start_driver()
        if not self.driver:
            return pd.DataFrame()

        # Construir la URL base
        base_url = f"https://www.macrotrends.net/stocks/charts/{ticker}"

        # Obtener la URL de la empresa
        self.driver.get(base_url)

        # Esperar y obtener la URL completa de la empresa
        time.sleep(5)
        current_url = self.driver.current_url

        # Obtener la tabla de Income Statement
        income_statement_url = f"{current_url}income-statement"
        df_income_statement = self.extract_table_data(income_statement_url)

        # Obtener la tabla de Balance Sheet
        balance_sheet_url = f"{current_url}balance-sheet"
        df_balance_sheet = self.extract_table_data(balance_sheet_url)

        # Obtener la tabla de Cash Flow Statement
        cash_flow_url = f"{current_url}cash-flow-statement"
        df_cash_flow = self.extract_table_data(cash_flow_url)

        # Concatenar las tablas
        combined_df = pd.concat([df_income_statement, df_balance_sheet, df_cash_flow], axis=0)

        # Reset index to ensure proper formatting
        combined_df.reset_index(drop=True, inplace=True)

        self.stop_driver()
        return combined_df

    def close(self):
        self.stop_driver()