"""
Tests unitarios que no requieren red, Firefox ni display.
Mockean selenium, yfinance y PyQt5 para probar solo la lógica pura.
"""
import sys
import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock

# --- Mockear dependencias pesadas ANTES de importar los módulos del proyecto ---
for _mod in [
    'selenium', 'selenium.webdriver', 'selenium.webdriver.common',
    'selenium.webdriver.common.by', 'selenium.webdriver.support',
    'selenium.webdriver.support.ui', 'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.firefox', 'selenium.webdriver.firefox.options',
    'bs4', 'yfinance',
    'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui',
    'matplotlib', 'matplotlib.backends', 'matplotlib.backends.backend_qt5agg',
    'matplotlib.figure',
]:
    sys.modules.setdefault(_mod, MagicMock())

from scrapers.macrotrends_scraper import MacrotrendsScraper, _YEAR_COLUMNS   # noqa: E402
from scrapers.yahoo_finance_scraper import YahooFinanceScraper                # noqa: E402
from model.data_manager import (                                               # noqa: E402
    filtrar_datos_google, filtrar_datos_yahoo_importados,
    filtrar_datos_macrotrends, _YAHOO_BALANCE_ITEMS,
    _YAHOO_INCOME_ITEMS, _YAHOO_CASHFLOW_ITEMS,
)


# ===========================================================================
# config.py
# ===========================================================================

class TestConfig:
    def test_paths_are_absolute(self):
        from config import ROOT, DB_PATH, EXPORT_DIR, RESOURCES_DIR
        assert ROOT.is_absolute()
        assert DB_PATH.is_absolute()
        assert EXPORT_DIR.is_absolute()
        assert RESOURCES_DIR.is_absolute()

    def test_db_path_is_sqlite(self):
        from config import DB_PATH
        assert DB_PATH.suffix == '.sqlite'

    def test_export_dir_inside_data(self):
        from config import EXPORT_DIR
        assert 'data' in EXPORT_DIR.parts

    def test_db_path_inside_data(self):
        from config import DB_PATH
        assert 'data' in DB_PATH.parts


# ===========================================================================
# MacrotrendsScraper._normalizar_columnas
# ===========================================================================

class TestMacrotrendsNormalizar:
    def _make_df(self, cols):
        """Crea un DataFrame de prueba con las columnas dadas."""
        return pd.DataFrame([['Revenue', '1000', '900', '800', '700', 'extra1', 'extra2']],
                            columns=cols)

    def test_columnas_renombradas(self):
        cols = ['Datos', 'Unused', '2024', '2023', '2022', '2021', 'Old1', 'Old2']
        df = pd.DataFrame([['Revenue', '', '1000', '900', '800', '700', 'x', 'y']], columns=cols)
        result = MacrotrendsScraper._normalizar_columnas(df)
        assert list(result.columns) == _YEAR_COLUMNS

    def test_columnas_faltantes_rellenadas_con_na(self):
        # Solo dos columnas: Datos y 2024
        df = pd.DataFrame([['Revenue', '1000']], columns=['Datos', '2024'])
        result = MacrotrendsScraper._normalizar_columnas(df)
        for col in _YEAR_COLUMNS:
            assert col in result.columns
        assert result.iloc[0]['2023'] == 'N/A'
        assert result.iloc[0]['2022'] == 'N/A'

    def test_year_columns_constante(self):
        assert _YEAR_COLUMNS == ['Datos', '2024', '2023', '2022', '2021']


# ===========================================================================
# YahooFinanceScraper._format_data
# ===========================================================================

class TestYahooFormatData:
    def _make_raw(self):
        """Simula el DataFrame crudo que devuelve yfinance."""
        cols = [
            datetime(2024, 12, 31),
            datetime(2023, 12, 31),
            datetime(2022, 12, 31),
            datetime(2021, 12, 31),
            datetime(2020, 12, 31),  # 5.ª columna — debe descartarse
        ]
        data = {c: [100, 200, 300] for c in cols}
        df = pd.DataFrame(data, index=['Total Revenue', 'Net Income', 'EBITDA'])
        return df

    def test_solo_cuatro_columnas(self):
        scraper = YahooFinanceScraper()
        result = scraper._format_data(self._make_raw())
        assert len(result.columns) == 5  # 'Datos' + 4 años

    def test_columna_datos_existe(self):
        scraper = YahooFinanceScraper()
        result = scraper._format_data(self._make_raw())
        assert 'Datos' in result.columns

    def test_columnas_son_años(self):
        scraper = YahooFinanceScraper()
        result = scraper._format_data(self._make_raw())
        year_cols = [c for c in result.columns if c != 'Datos']
        assert year_cols == ['2024', '2023', '2022', '2021']


# ===========================================================================
# filtrar_datos_yahoo_importados
# ===========================================================================

class TestFiltrarYahooImportados:
    def _make_yahoo_df(self):
        rows = (
            [{'Datos': item, '2024': 1, '2023': 2, '2022': 3, '2021': 4}
             for item in _YAHOO_BALANCE_ITEMS[:5]]
            + [{'Datos': item, '2024': 1, '2023': 2, '2022': 3, '2021': 4}
               for item in _YAHOO_INCOME_ITEMS[:5]]
            + [{'Datos': item, '2024': 1, '2023': 2, '2022': 3, '2021': 4}
               for item in _YAHOO_CASHFLOW_ITEMS[:5]]
        )
        return pd.DataFrame(rows)

    def test_filtro_balance_devuelve_solo_balance(self):
        df = self._make_yahoo_df()
        result = filtrar_datos_yahoo_importados(df, 'balance')
        assert not result.empty
        for val in result['Datos']:
            assert val in _YAHOO_BALANCE_ITEMS

    def test_filtro_income_devuelve_solo_income(self):
        df = self._make_yahoo_df()
        result = filtrar_datos_yahoo_importados(df, 'income')
        assert not result.empty
        for val in result['Datos']:
            assert val in _YAHOO_INCOME_ITEMS

    def test_filtro_tipo_invalido_devuelve_vacio(self):
        df = self._make_yahoo_df()
        result = filtrar_datos_yahoo_importados(df, 'inexistente')
        assert result.empty

    def test_df_vacio_devuelve_vacio(self):
        result = filtrar_datos_yahoo_importados(pd.DataFrame(), 'balance')
        assert result.empty


# ===========================================================================
# filtrar_datos_google
# ===========================================================================

class TestFiltrarGoogle:
    def _make_google_live_df(self):
        """Simula el DataFrame en vivo de GoogleFinanceScraper (índice = nombres)."""
        index = [
            'Ingresos', 'Gastos operativos', 'Ingresos netos',
            'Efectivo y a corto plazo', 'Activos totales',
            'Efectivo de operaciones', 'Flujo de caja libre', 'Otro dato',
        ]
        return pd.DataFrame(
            {'2024': [1]*len(index), '2023': [2]*len(index),
             '2022': [3]*len(index), '2021': [4]*len(index)},
            index=index,
        )

    def test_income_contiene_ingresos(self):
        result = filtrar_datos_google(self._make_google_live_df(), 'income')
        assert not result.empty
        assert 'Datos' in result.columns
        assert 'Ingresos' in result['Datos'].values

    def test_balance_contiene_activos(self):
        result = filtrar_datos_google(self._make_google_live_df(), 'balance')
        assert not result.empty
        assert 'Activos totales' in result['Datos'].values

    def test_cashflow_contiene_flujo(self):
        result = filtrar_datos_google(self._make_google_live_df(), 'cashflow')
        assert not result.empty
        assert 'Flujo de caja libre' in result['Datos'].values

    def test_df_vacio_devuelve_vacio(self):
        result = filtrar_datos_google(pd.DataFrame(), 'balance')
        assert result.empty

    def test_tipo_invalido_devuelve_vacio(self):
        result = filtrar_datos_google(self._make_google_live_df(), 'inexistente')
        assert result.empty


# ===========================================================================
# filtrar_datos_macrotrends
# ===========================================================================

class TestFiltrarMacrotrends:
    def _make_macro_df(self):
        items = ['Revenue', 'Net Income', 'Cash On Hand', 'Total Assets',
                 'Cash Flow From Operating Activities', 'Free Cash Flow', 'Dato raro']
        rows = [{'Datos': i, '2024': 1, '2023': 2, '2022': 3, '2021': 4} for i in items]
        return pd.DataFrame(rows)

    def test_income_devuelve_revenue(self):
        result = filtrar_datos_macrotrends(self._make_macro_df(), 'income')
        assert not result.empty
        assert 'Revenue' in result['Datos'].values

    def test_balance_devuelve_total_assets(self):
        result = filtrar_datos_macrotrends(self._make_macro_df(), 'balance')
        assert not result.empty
        assert 'Total Assets' in result['Datos'].values

    def test_cashflow_devuelve_operating(self):
        result = filtrar_datos_macrotrends(self._make_macro_df(), 'cashflow')
        assert not result.empty
        assert 'Cash Flow From Operating Activities' in result['Datos'].values

    def test_df_vacio_devuelve_vacio(self):
        result = filtrar_datos_macrotrends(pd.DataFrame(), 'balance')
        assert result.empty
