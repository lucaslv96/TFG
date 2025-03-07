from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests

class GoogleFinanceScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")  # Ensure the browser runs in headless mode
        self.options.add_argument("--window-size=1920,1080")  # Set window size to avoid issues with headless mode
        self.exchanges = [
            'NASDAQ', 'NYSE', 'AMEX', 'TSX', 'LON', 'ASX', 'HKEX', 'TSE', 'BVMF', 'BSE', 'NSE', 'SGX', 
            'KRX', 'SSE', 'SZSE', 'TADAWUL', 'FWB', 'ETR', 'SWX', 'JSE', 'SEHK', 'BMV', 'MOEX', 'IDX',
            'BME', 'MIL', 'STO', 'HEL', 'CPH', 'ICE', 'VIE', 'WSE', 'BUD', 'ZSE', 'PSE', 'OSE', 'BCBA',
            'ASE', 'NZX', 'KLSE', 'SET', 'HNX', 'HOSE', 'TSXV', 'CSE', 'Euronext', 'EURONEXT', 'MIB',
            'ISE', 'BIST', 'XWAR', 'XSES', 'XBKK', 'XHKG', 'XNYS', 'XAMS', 'XBRU', 'XLON', 'XPAR',
            'XASX', 'XETR', 'XSTO', 'XCSE', 'XHEL', 'XICE', 'XOSL', 'XMAD', 'XLIS', 'XWBO', 'XBUE',
            'XJSE', 'XTSE', 'XTAE', 'XKAR', 'XMEX', 'XSGO', 'XPHL', 'XTNX', 'XJNB', 'XMAU', 'XBOM',
            'XNSE', 'XBOR', 'XNGO', 'XHSE', 'XLME', 'XBMS', 'XBKK', 'XBLA', 'XGSE', 'XNAF', 'XGAZ',
            'XCAI', 'XGHA', 'XRSE', 'XSRA', 'XNBO', 'XMAR', 'XTAB', 'XMON', 'XBEL', 'XCAI', 'XBUC',
            'XBKS', 'XKLS', 'XBLS', 'XHCM', 'XLON', 'XMTS', 'XJKT', 'XNEW', 'XCAR', 'XNIL', 'XMNG',
            'XBHR', 'XMNX', 'XDMX', 'XPTF', 'XGIB', 'XJMU', 'XBNK', 'XKBS', 'XMOL', 'XPAR', 'XROM',
            'XSPC', 'XSAI', 'XSOF', 'XSSX', 'XSWX', 'XTMB', 'XURA', 'XVIE', 'XWBO', 'XTWN', 'XTAS', 
            'OTCMKTS'
        ]

    def verify_exchange(self, ticker):
        for exchange in self.exchanges:
            url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Check if the necessary financial data is present
                if soup.find_all('td', class_='QXDnM'):
                    return exchange
        return None

    def get_stock_data(self, ticker):
        exchange = self.verify_exchange(ticker)
        if not exchange:
            print(f"No se encontraron datos para el ticker {ticker} en los exchanges disponibles.")
            return pd.DataFrame()  # Return an empty DataFrame if no valid exchange is found
        
        try:
            # Inicializar el driver
            driver = webdriver.Firefox(options=self.options)
            
            # URL de la página de Google Finance para el ticker
            url = f"https://www.google.com/finance/quote/{ticker}:{exchange}?hl=es"
            driver.get(url)

            # Esperar y hacer clic en el botón "Aceptar todo" si está presente
            try:
                boton_aceptar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Aceptar todo']"))
                )
                boton_aceptar.click()
            except Exception as e:
                # Si no encuentra el botón, continuar (puede que ya se hayan aceptado)
                print(f"Aviso: No se pudo encontrar el botón 'Aceptar todo': {e}")

            # Esperar a que el botón "Anual" esté presente y hacer clic en él
            boton_anual = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "annual2"))
            )
            boton_anual.click()

            # Esperar a que la tabla de datos financieros esté presente
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "zsnTKc"))
            )

            def extraer_datos():
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                fin_data = soup.find_all('td', class_='QXDnM')
                
                stock_data = {
                    'Ingresos': fin_data[0].text if len(fin_data) > 0 else 'N/A',
                    'Gastos operativos': fin_data[1].text if len(fin_data) > 1 else 'N/A',
                    'Ingresos netos': fin_data[2].text if len(fin_data) > 2 else 'N/A',
                    'Margen de beneficio neto': fin_data[3].text if len(fin_data) > 3 else 'N/A',
                    'Beneficios por acción': fin_data[4].text if len(fin_data) > 4 else 'N/A',
                    'EBITDA': fin_data[5].text if len(fin_data) > 5 else 'N/A',
                    'Tipo impositivo efectivo': fin_data[6].text if len(fin_data) > 6 else 'N/A',
                    'Efectivo y a corto plazo': fin_data[7].text if len(fin_data) > 7 else 'N/A',
                    'Activos totales': fin_data[8].text if len(fin_data) > 8 else 'N/A',
                    'Responsabilidades totales': fin_data[9].text if len(fin_data) > 9 else 'N/A',
                    'Patrimonio total': fin_data[10].text if len(fin_data) > 10 else 'N/A',
                    'Acciones en circulación': fin_data[11].text if len(fin_data) > 11 else 'N/A',
                    'Precio-valor contable': fin_data[12].text if len(fin_data) > 12 else 'N/A',
                    'Rentabilidad económica': fin_data[13].text if len(fin_data) > 13 else 'N/A',
                    'Retorno sobre capital': fin_data[14].text if len(fin_data) > 14 else 'N/A',
                    'Ingresos netos': fin_data[15].text if len(fin_data) > 15 else 'N/A',
                    'Efectivo de operaciones': fin_data[16].text if len(fin_data) > 16 else 'N/A',
                    'Efectivo de inversión': fin_data[17].text if len(fin_data) > 17 else 'N/A',
                    'Efectivo de financiación': fin_data[18].text if len(fin_data) > 18 else 'N/A',
                    'Variación neta del flujo de caja': fin_data[19].text if len(fin_data) > 19 else 'N/A',
                    'Flujo de caja libre': fin_data[20].text if len(fin_data) > 20 else 'N/A'
                }
                stock_data = {k: v for k, v in stock_data.items() if v != '—'}
                
                df = pd.DataFrame(list(stock_data.items()), columns=['Datos', 'Value'])
                return df

            # Extraer datos para el año actual (2024)
            df_2024 = extraer_datos()
            df_2024.columns = ['Datos', '2024']

            # Extraer datos para los años anteriores (2023, 2022, 2021)
            all_data = [df_2024]
            for i in range(1, 4):  # Ahora recogemos 2023, 2022 y 2021
                boton_anio = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, f"option-{i}"))
                )
                boton_anio.click()
                
                df_anio = extraer_datos()
                df_anio.columns = ['Datos', str(2024 - i)]  # Ahora empezamos desde 2024
                all_data.append(df_anio)

            # Combinar todos los datos en un solo DataFrame
            combined_df = pd.concat(all_data, axis=1)
            combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]  # Eliminar columnas duplicadas
            
            return combined_df

        except Exception as e:
            print(f"Error al procesar los datos de Google Finance: {e}")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

        finally:
            driver.quit()
