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
        self.options.add_argument("--headless")  
        self.options.add_argument("--window-size=1920,1080")  
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
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  

        self.driver.get(url)

        if not self.button_accepted:
            try:
                accept_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar todo')]"))
                )
                accept_button.click()
                self.button_accepted = True  
            except:
                print("El botón 'Aceptar todo' no se encontró, continuando con la extracción.")

        time.sleep(5)

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        column_headers_div = soup.find('div', id='columntablejqxgrid')
        if column_headers_div is None:
            print("No se encontraron datos en la URL proporcionada.")
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  

        column_headers = column_headers_div.find_all('div', role='columnheader')
        if not column_headers:
            print("No se encontraron encabezados de columna en la tabla.")
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  
            
        dates = [header.text.strip() for header in column_headers]

        table = soup.find('div', id='contentjqxgrid')
        if not table:
            print("No se encontró la tabla de contenido.")
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  

        rows = table.find_all('div', role='row')
        if not rows:
            print("No se encontraron filas en la tabla.")
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  

        data = []
        for row in rows:
            cols = row.find_all('div', class_='jqx-grid-cell')
            data.append([col.text.strip() for col in cols])

        if not data:
            print("No se encontraron datos en la tabla.")
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  

        df = pd.DataFrame(data, columns=dates)
        if df.empty:
            print("DataFrame vacío después de la creación.")
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  

        if len(df.columns) > 1:
            df = df.drop(df.columns[1], axis=1)  
        
        if len(df.columns) > 2: 
            df = df.iloc[:, :-2]  
        
        if len(df.columns) > 0:
            df.columns.values[0] = "Datos"  
        if len(df.columns) > 1:
            df.columns.values[1] = "2024" 
        if len(df.columns) > 2:
            df.columns.values[2] = "2023"  
        if len(df.columns) > 3:
            df.columns.values[3] = "2022"  
        if len(df.columns) > 4:
            df.columns.values[4] = "2021" 
        
        for col in ["Datos", "2024", "2023", "2022", "2021"]:
            if col not in df.columns:
                df[col] = "N/A"
                
        return df

    def get_financial_data(self, ticker):
        self.start_driver()
        if not self.driver:
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"]) 
        base_url = f"https://www.macrotrends.net/stocks/charts/{ticker}"

        try:
            self.driver.get(base_url)

            time.sleep(5)
            current_url = self.driver.current_url

            if "stocks/charts" not in current_url or ticker.lower() not in current_url.lower():
                print(f"No se encontró la empresa {ticker} en Macrotrends")
                self.stop_driver()
                return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])

            income_statement_url = f"{current_url}income-statement"
            df_income_statement = self.extract_table_data(income_statement_url)

            balance_sheet_url = f"{current_url}balance-sheet"
            df_balance_sheet = self.extract_table_data(balance_sheet_url)

            cash_flow_url = f"{current_url}cash-flow-statement"
            df_cash_flow = self.extract_table_data(cash_flow_url)

            if df_income_statement.empty and df_balance_sheet.empty and df_cash_flow.empty:
                print(f"No se encontraron datos financieros para {ticker}")
                self.stop_driver()
                return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])

            dfs_to_concat = []
            for df in [df_income_statement, df_balance_sheet, df_cash_flow]:
                if not df.empty:
                    for col in ["Datos", "2024", "2023", "2022", "2021"]:
                        if col not in df.columns:
                            df[col] = "N/A"
                    dfs_to_concat.append(df)
            
            if dfs_to_concat:
                combined_df = pd.concat(dfs_to_concat, axis=0)
                combined_df.reset_index(drop=True, inplace=True)
            else:
                combined_df = pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])

            self.stop_driver()
            return combined_df

        except Exception as e:
            print(f"Error al obtener datos de Macrotrends para {ticker}: {str(e)}")
            self.stop_driver()
            return pd.DataFrame(columns=["Datos", "2024", "2023", "2022", "2021"])  

    def close(self):
        self.stop_driver()