from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests

class GoogleFinanceScraper:
    # Constantes para selectores CSS
    TABLE_SELECTOR = "table.slpEwd"
    VALUE_CELL_SELECTOR = "td.QXDnM"
    NAME_CELL_SELECTOR = "td.J9Jhg"
    TABLIST_SELECTOR = "div.zsnTKc[role='tablist']"
    
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless") 
        self.options.add_argument("--window-size=1920,1080")  
        self.exchanges = ['NASDAQ', 'NYSE', 'AMEX', 'OTCMKTS', 'BME', 'XMAD', 'LON', 'XLON', 'XPAR', 'Euronext', 'ETR', 'FWB', 'MIL', 'MIB', 'XAMS', 'SWX', 'TSX', 'BMV', 'BVMF', 'HKEX', 'SEHK', 'TSE', 'ASX', 'SGX', 'BSE', 'NSE', 'SSE', 'SZSE']

    def verify_exchange(self, ticker):
        for exchange in self.exchanges:
            url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                if soup.find_all('td', class_='QXDnM'):
                    return exchange
        return None

    def get_stock_data(self, ticker):
        exchange = self.verify_exchange(ticker)
        if not exchange:
            print(f"No se encontraron datos para el ticker {ticker} en los exchanges disponibles.")
            return pd.DataFrame()  
        
        try:
            driver = webdriver.Firefox(options=self.options)
            
            url = f"https://www.google.com/finance/quote/{ticker}:{exchange}?hl=es"
            driver.get(url)

            self._aceptar_cookies(driver)

            # Extraer datos de estados financieros (primera pestaña)
            datos_financieros = self._extraer_estados_financieros(driver)
            
            # Extraer datos de balance general
            datos_balance = self._extraer_balance_general(driver)
            
            # Extraer datos de flujo de caja
            datos_cashflow = self._extraer_flujo_caja(driver)
            
            # Combinar todos los DataFrames evitando duplicados y preservando nombres
            dataframes = []
            all_seen_names = set()  # Para evitar duplicados entre secciones
            
            if not datos_financieros.empty:
                # Agregar prefijo para evitar duplicados pero mantener nombres legibles
                datos_financieros_prefixed = datos_financieros.copy()
                # Filtrar duplicados dentro de la propia sección
                datos_financieros_prefixed = datos_financieros_prefixed[~datos_financieros_prefixed.index.duplicated(keep='first')]
                datos_financieros_prefixed.index = ['Income_' + str(idx) for idx in datos_financieros_prefixed.index]
                dataframes.append(datos_financieros_prefixed)
                all_seen_names.update(datos_financieros.index)
                
            if not datos_balance.empty:
                # Filtrar duplicados dentro de la propia sección
                datos_balance = datos_balance[~datos_balance.index.duplicated(keep='first')]
                # Solo agregar nombres que no hayamos visto antes
                unique_balance = datos_balance[~datos_balance.index.isin(all_seen_names)]
                if not unique_balance.empty:
                    datos_balance_prefixed = unique_balance.copy()
                    datos_balance_prefixed.index = ['Balance_' + str(idx) for idx in unique_balance.index]
                    dataframes.append(datos_balance_prefixed)
                    all_seen_names.update(unique_balance.index)
                
            if not datos_cashflow.empty:
                # Filtrar duplicados dentro de la propia sección
                datos_cashflow = datos_cashflow[~datos_cashflow.index.duplicated(keep='first')]
                # Solo agregar nombres que no hayamos visto antes
                unique_cashflow = datos_cashflow[~datos_cashflow.index.isin(all_seen_names)]
                if not unique_cashflow.empty:
                    datos_cashflow_prefixed = unique_cashflow.copy()
                    datos_cashflow_prefixed.index = ['Cashflow_' + str(idx) for idx in unique_cashflow.index]
                    dataframes.append(datos_cashflow_prefixed)
            
            # Combinar solo si hay DataFrames para combinar
            if dataframes:
                combined_df = pd.concat(dataframes, sort=False)
                # Eliminar cualquier duplicado que pudiera quedar por índice
                combined_df = combined_df[~combined_df.index.duplicated(keep='first')]
                # Eliminar filas con todos los valores NaN
                combined_df = combined_df.dropna(how='all')
                return combined_df
            else:
                return pd.DataFrame()

        except Exception as e:
            print(f"Error al procesar los datos de Google Finance: {e}")
            return pd.DataFrame()  

        finally:
            driver.quit()

    def _aceptar_cookies(self, driver):
        """Acepta las cookies si aparece el botón"""
        try:
            boton_aceptar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Aceptar todo')]"))
            )
            boton_aceptar.click()
        except Exception as e:
            print(f"Aviso: No se pudo encontrar el botón 'Aceptar todo': {e}")

    def _extraer_estados_financieros(self, driver):
        """Extrae los datos de estados financieros para todos los años"""
        anios_config = {
            "2024": "annual2",
            "2023": "option-1", 
            "2022": "option-2",
            "2021": "option-3"
        }
        
        datos_por_anio = {}
        for anio, boton_id in anios_config.items():
            datos_por_anio[anio] = self._extraer_datos_anio_financiero(driver, anio, boton_id)

        return self._crear_dataframe_desde_dict(datos_por_anio)

    def _extraer_datos_anio_financiero(self, driver, anio, boton_id):
        """Extrae los datos financieros de un año específico"""
        try:
            # Click en el botón del año
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, boton_id))
            ).click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.TABLE_SELECTOR))
            )

            tabla_html = driver.find_element(By.CSS_SELECTOR, self.TABLE_SELECTOR).get_attribute("outerHTML")
            soup = BeautifulSoup(tabla_html, "html.parser")
            filas = soup.find_all("tr", class_="roXhBd")

            datos = {}
            seen_names = set()  # Para evitar duplicados dentro del mismo año
            
            for fila in filas:
                celdas = fila.find_all("td")
                if len(celdas) >= 2:
                    nombre_div = celdas[0].find("div", class_="rsPbEe")
                    nombre = nombre_div.get_text(strip=True) if nombre_div else celdas[0].get_text(strip=True)
                    valor = celdas[1].get_text(strip=True)
                    
                    # Solo agregar si el nombre no está vacío, el valor no es '—' y no lo hemos visto antes
                    if nombre and valor != '—' and nombre not in seen_names:
                        datos[nombre] = valor
                        seen_names.add(nombre)

            return datos
        except Exception as e:
            print(f"Error extrayendo datos financieros para {anio}: {e}")
            return {}

    def _extraer_balance_general(self, driver):
        """Extrae los datos de balance general para todos los años"""
        try:
            self._navegar_a_seccion(driver, "Balance general")
            tablists = driver.find_elements(By.CSS_SELECTOR, self.TABLIST_SELECTOR)
            
            if len(tablists) < 2:
                print("No se encontró el tablist de balance general")
                return pd.DataFrame()
                
            tablist_balance = tablists[1]  # El segundo tablist corresponde a balance general
            datos_balance_por_anio = self._extraer_datos_por_anios(driver, tablist_balance, 7, 16)
            
            return self._crear_dataframe_desde_dict(datos_balance_por_anio)
            
        except Exception as e:
            print(f"Error extrayendo datos de balance general: {e}")
            return pd.DataFrame()

    def _extraer_flujo_caja(self, driver):
        """Extrae los datos de flujo de caja para todos los años"""
        try:
            self._navegar_a_seccion(driver, "Flujo de caja")
            tablists = driver.find_elements(By.CSS_SELECTOR, self.TABLIST_SELECTOR)
            
            if len(tablists) < 3:
                print("No se encontró el tablist de flujo de caja")
                return pd.DataFrame()
                
            tablist_cashflow = tablists[2]  # El tercer tablist corresponde a flujo de caja
            datos_cashflow_por_anio = self._extraer_datos_por_anios(driver, tablist_cashflow, 15, 21)
            
            return self._crear_dataframe_desde_dict(datos_cashflow_por_anio)
            
        except Exception as e:
            print(f"Error extrayendo datos de flujo de caja: {e}")
            return pd.DataFrame()

    def _navegar_a_seccion(self, driver, nombre_seccion):
        """Navega a una sección específica (Balance general o Flujo de caja)"""
        seccion_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{nombre_seccion}')]/parent::div[@role='button']"))
        )
        seccion_btn.click()

        # Esperar a que aparezca la tabla
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.TABLE_SELECTOR))
        )

    def _extraer_datos_por_anios(self, driver, tablist, inicio_slice, fin_slice):
        """Extrae datos para todos los años de una sección específica"""
        datos_por_anio = {}
        
        for anio in ["2024", "2023", "2022", "2021"]:
            try:
                self._seleccionar_anio(driver, tablist, anio)
                datos_por_anio[anio] = self._extraer_datos_tabla(driver, inicio_slice, fin_slice)
            except Exception as e:
                print(f"Error extrayendo datos para {anio}: {e}")
                datos_por_anio[anio] = {}
                
        return datos_por_anio

    def _seleccionar_anio(self, driver, tablist, anio):
        """Selecciona un año específico en el tablist"""
        botones = tablist.find_elements(By.CSS_SELECTOR, "button[role='tab']")
        for boton in botones:
            span = boton.find_element(By.CSS_SELECTOR, "span.VfPpkd-vQzf8d")
            if span.text.strip() == anio:
                boton.click()
                break
        
        # Esperar a que se carguen los datos
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.VALUE_CELL_SELECTOR))
        )

    def _extraer_datos_tabla(self, driver, inicio_slice, fin_slice):
        """Extrae datos de la tabla usando los índices especificados"""
        valores = driver.find_elements(By.CSS_SELECTOR, self.VALUE_CELL_SELECTOR)[inicio_slice:fin_slice]
        nombres = driver.find_elements(By.CSS_SELECTOR, self.NAME_CELL_SELECTOR)[inicio_slice:fin_slice]
        
        datos = {}
        seen_names = set()  # Para evitar duplicados
        
        for i in range(min(len(nombres), len(valores))):
            nombre = nombres[i].text.strip()
            valor = valores[i].text.strip()
            # Solo agregar si el nombre y valor no están vacíos, el valor no es '—' y no lo hemos visto antes
            if nombre and valor and valor != '—' and nombre not in seen_names:
                datos[nombre] = valor
                seen_names.add(nombre)
        
        return datos

    def _crear_dataframe_desde_dict(self, datos_por_anio):
        """Crea un DataFrame a partir de un diccionario de datos por año"""
        if not datos_por_anio:
            return pd.DataFrame()
            
        # Obtener todos los nombres únicos
        todos_nombres = set()
        for d in datos_por_anio.values():
            todos_nombres.update(d.keys())

        if not todos_nombres:
            return pd.DataFrame()

        # Crear DataFrame con índices ordenados usando los nombres reales
        df = pd.DataFrame(index=sorted(list(todos_nombres)))

        # Rellenar DataFrame con datos por año
        for anio, datos in datos_por_anio.items():
            for nombre in datos:
                if nombre in df.index:  # Verificar que el índice existe
                    df.at[nombre, anio] = datos[nombre]

        # Eliminar duplicados en el índice si los hay
        df = df[~df.index.duplicated(keep='first')]
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        return df
