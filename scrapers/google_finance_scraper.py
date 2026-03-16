import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd


class GoogleFinanceScraper:
    # Selectores CSS
    TABLE_SELECTOR      = "table.slpEwd"
    VALUE_CELL_SELECTOR = "td.QXDnM"
    NAME_CELL_SELECTOR  = "td.J9Jhg"
    TABLIST_SELECTOR    = "div.zsnTKc[role='tablist']"

    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--window-size=1920,1080")
        self.exchanges = [
            'NASDAQ', 'NYSE', 'AMEX', 'OTCMKTS', 'BME', 'XMAD',
            'LON', 'XLON', 'XPAR', 'Euronext', 'ETR', 'FWB',
            'MIL', 'MIB', 'XAMS', 'SWX', 'TSX', 'BMV', 'BVMF',
            'HKEX', 'SEHK', 'TSE', 'ASX', 'SGX', 'BSE', 'NSE', 'SSE', 'SZSE',
        ]
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Punto de entrada público
    # ------------------------------------------------------------------

    def get_stock_data(self, ticker):
        driver = webdriver.Firefox(options=self.options)
        try:
            exchange = self._find_exchange(driver, ticker)
            if not exchange:
                self.logger.warning("No se encontraron datos para %s en los exchanges disponibles.", ticker)
                return pd.DataFrame()

            url = f"https://www.google.com/finance/quote/{ticker}:{exchange}?hl=es"
            driver.get(url)

            datos_financieros = self._extraer_estados_financieros(driver)
            datos_balance     = self._extraer_balance_general(driver)
            datos_cashflow    = self._extraer_flujo_caja(driver)

            return self._combinar_dataframes(datos_financieros, datos_balance, datos_cashflow)

        except Exception as e:
            self.logger.error("Error al procesar los datos de Google Finance: %s", e)
            return pd.DataFrame()
        finally:
            driver.quit()

    # ------------------------------------------------------------------
    # Detección del exchange (usa Selenium para que se ejecute el JS)
    # ------------------------------------------------------------------

    def _find_exchange(self, driver, ticker):
        """Prueba cada exchange con Selenium hasta encontrar la tabla financiera."""
        cookies_accepted = False
        for exchange in self.exchanges:
            url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
            driver.get(url)
            if not cookies_accepted:
                self._aceptar_cookies(driver)
                cookies_accepted = True
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.TABLE_SELECTOR))
                )
                return exchange
            except Exception:
                continue
        return None

    # ------------------------------------------------------------------
    # Helpers de navegación y extracción
    # ------------------------------------------------------------------

    def _aceptar_cookies(self, driver):
        try:
            boton = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Aceptar todo')]"))
            )
            boton.click()
        except Exception:
            pass  # El diálogo no apareció; se continúa normalmente

    def _extraer_estados_financieros(self, driver):
        anios_config = {
            "2024": "annual2",
            "2023": "option-1",
            "2022": "option-2",
            "2021": "option-3",
        }
        datos_por_anio = {
            anio: self._extraer_datos_anio_financiero(driver, anio, boton_id)
            for anio, boton_id in anios_config.items()
        }
        return self._crear_dataframe_desde_dict(datos_por_anio)

    def _extraer_datos_anio_financiero(self, driver, anio, boton_id):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, boton_id))
            ).click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.TABLE_SELECTOR))
            )
            tabla_html = driver.find_element(By.CSS_SELECTOR, self.TABLE_SELECTOR).get_attribute("outerHTML")
            soup  = BeautifulSoup(tabla_html, "html.parser")
            filas = soup.find_all("tr", class_="roXhBd")

            datos      = {}
            seen_names = set()
            for fila in filas:
                celdas = fila.find_all("td")
                if len(celdas) >= 2:
                    nombre_div = celdas[0].find("div", class_="rsPbEe")
                    nombre = nombre_div.get_text(strip=True) if nombre_div else celdas[0].get_text(strip=True)
                    valor  = celdas[1].get_text(strip=True)
                    if nombre and valor != '—' and nombre not in seen_names:
                        datos[nombre] = valor
                        seen_names.add(nombre)
            return datos
        except Exception as e:
            self.logger.warning("Error extrayendo datos financieros para %s: %s", anio, e)
            return {}

    def _extraer_balance_general(self, driver):
        try:
            self._navegar_a_seccion(driver, "Balance general")
            tablists = driver.find_elements(By.CSS_SELECTOR, self.TABLIST_SELECTOR)
            if len(tablists) < 2:
                self.logger.warning("No se encontró el tablist de balance general.")
                return pd.DataFrame()
            datos = self._extraer_datos_por_anios(driver, tablists[1], 7, 16)
            return self._crear_dataframe_desde_dict(datos)
        except Exception as e:
            self.logger.error("Error extrayendo datos de balance general: %s", e)
            return pd.DataFrame()

    def _extraer_flujo_caja(self, driver):
        try:
            self._navegar_a_seccion(driver, "Flujo de caja")
            tablists = driver.find_elements(By.CSS_SELECTOR, self.TABLIST_SELECTOR)
            if len(tablists) < 3:
                self.logger.warning("No se encontró el tablist de flujo de caja.")
                return pd.DataFrame()
            datos = self._extraer_datos_por_anios(driver, tablists[2], 15, 21)
            return self._crear_dataframe_desde_dict(datos)
        except Exception as e:
            self.logger.error("Error extrayendo datos de flujo de caja: %s", e)
            return pd.DataFrame()

    def _navegar_a_seccion(self, driver, nombre_seccion):
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//span[contains(text(), '{nombre_seccion}')]/parent::div[@role='button']")
            )
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.TABLE_SELECTOR))
        )

    def _extraer_datos_por_anios(self, driver, tablist, inicio_slice, fin_slice):
        datos_por_anio = {}
        for anio in ["2024", "2023", "2022", "2021"]:
            try:
                self._seleccionar_anio(driver, tablist, anio)
                datos_por_anio[anio] = self._extraer_datos_tabla(driver, inicio_slice, fin_slice)
            except Exception as e:
                self.logger.warning("Error extrayendo datos para %s: %s", anio, e)
                datos_por_anio[anio] = {}
        return datos_por_anio

    def _seleccionar_anio(self, driver, tablist, anio):
        for boton in tablist.find_elements(By.CSS_SELECTOR, "button[role='tab']"):
            span = boton.find_element(By.CSS_SELECTOR, "span.VfPpkd-vQzf8d")
            if span.text.strip() == anio:
                boton.click()
                break
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.VALUE_CELL_SELECTOR))
        )

    def _extraer_datos_tabla(self, driver, inicio_slice, fin_slice):
        valores = driver.find_elements(By.CSS_SELECTOR, self.VALUE_CELL_SELECTOR)[inicio_slice:fin_slice]
        nombres = driver.find_elements(By.CSS_SELECTOR, self.NAME_CELL_SELECTOR)[inicio_slice:fin_slice]

        datos      = {}
        seen_names = set()
        for nombre_el, valor_el in zip(nombres, valores):
            nombre = nombre_el.text.strip()
            valor  = valor_el.text.strip()
            if nombre and valor and valor != '—' and nombre not in seen_names:
                datos[nombre] = valor
                seen_names.add(nombre)
        return datos

    def _crear_dataframe_desde_dict(self, datos_por_anio):
        if not datos_por_anio:
            return pd.DataFrame()

        todos_nombres = set()
        for d in datos_por_anio.values():
            todos_nombres.update(d.keys())
        if not todos_nombres:
            return pd.DataFrame()

        df = pd.DataFrame(index=sorted(todos_nombres))
        for anio, datos in datos_por_anio.items():
            for nombre, valor in datos.items():
                df.at[nombre, anio] = valor

        df = df[~df.index.duplicated(keep='first')]
        df = df.dropna(how='all')
        return df

    # ------------------------------------------------------------------
    # Combinación de secciones
    # ------------------------------------------------------------------

    def _combinar_dataframes(self, income, balance, cashflow):
        dataframes    = []
        seen_names    = set()

        def _add_section(df, prefix):
            if df.empty:
                return
            df = df[~df.index.duplicated(keep='first')]
            unique = df[~df.index.isin(seen_names)]
            if not unique.empty:
                prefixed = unique.copy()
                prefixed.index = [prefix + str(idx) for idx in unique.index]
                dataframes.append(prefixed)
                seen_names.update(unique.index)

        _add_section(income,   'Income_')
        _add_section(balance,  'Balance_')
        _add_section(cashflow, 'Cashflow_')

        if not dataframes:
            return pd.DataFrame()

        combined = pd.concat(dataframes, sort=False)
        combined = combined[~combined.index.duplicated(keep='first')]
        combined = combined.dropna(how='all')
        return combined
