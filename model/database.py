import sqlite3
import os
import logging
import pandas as pd
from config import DB_PATH, DB_DIR
from model.data_manager import filtrar_datos_google, filtrar_datos_yahoo, filtrar_datos_macrotrends

# ---------------------------------------------------------------------------
# Constantes SQL
# ---------------------------------------------------------------------------
_INSERT_GOOGLE   = 'INSERT INTO google_finance (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)'
_INSERT_YAHOO    = 'INSERT INTO yahoo_finance  (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)'
_INSERT_MACRO    = 'INSERT INTO macrotrends    (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)'


# ---------------------------------------------------------------------------
# Inicialización (se llama una sola vez al arrancar la app)
# ---------------------------------------------------------------------------

def initialize_database():
    """Crea el esquema y carga los datos por defecto si la BD no existe."""
    db_filename = str(DB_PATH)

    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    if not os.path.exists(db_filename):
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        _create_tables(cursor)
        _load_default_data(cursor)
        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.")


def _create_tables(cursor):
    cursor.execute('''
        CREATE TABLE google_finance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_dato TEXT NOT NULL,
            dato_inicial TEXT NOT NULL,
            dato_actual TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE yahoo_finance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_dato TEXT NOT NULL,
            dato_inicial TEXT NOT NULL,
            dato_actual TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE macrotrends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_dato TEXT NOT NULL,
            dato_inicial TEXT NOT NULL,
            dato_actual TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE equivalencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_dato TEXT NOT NULL,
            google_finance_id INTEGER,
            yahoo_finance_id INTEGER,
            macrotrends_id INTEGER,
            FOREIGN KEY (google_finance_id) REFERENCES google_finance(id),
            FOREIGN KEY (yahoo_finance_id)  REFERENCES yahoo_finance(id),
            FOREIGN KEY (macrotrends_id)    REFERENCES macrotrends(id)
        )
    ''')


def _load_default_data(cursor):
    google_income = filtrar_datos_google(pd.DataFrame({'Datos': [
        'Ingresos', 'Gastos operativos', 'Ingresos netos', 'Margen de beneficio neto',
        'Beneficios por acción', 'EBITDA', 'Tipo impositivo efectivo',
    ]}), 'income')
    google_balance = filtrar_datos_google(pd.DataFrame({'Datos': [
        'Efectivo y a corto plazo', 'Activos totales', 'Responsabilidades totales',
        'Patrimonio total', 'Acciones en circulación', 'Precio-valor contable',
        'Rentabilidad económica', 'Retorno sobre capital',
    ]}), 'balance')
    google_cashflow = filtrar_datos_google(pd.DataFrame({'Datos': [
        'Ingresos netos', 'Efectivo de operaciones', 'Efectivo de inversión',
        'Efectivo de financiación', 'Variación neta del flujo de caja', 'Flujo de caja libre',
    ]}), 'cashflow')

    yahoo_income   = filtrar_datos_yahoo('AAPL', 'income')
    yahoo_income['tipo_dato'] = 'income'
    yahoo_balance  = filtrar_datos_yahoo('AAPL', 'balance')
    yahoo_balance['tipo_dato'] = 'balance'
    yahoo_cashflow = filtrar_datos_yahoo('AAPL', 'cashflow')
    yahoo_cashflow['tipo_dato'] = 'cashflow'

    macro_income = filtrar_datos_macrotrends(pd.DataFrame({'Datos': [
        'Revenue', 'Cost Of Goods Sold', 'Gross Profit', 'Research And Development Expenses',
        'SG&A Expenses', 'Other Operating Income Or Expenses', 'Operating Expenses',
        'Operating Income', 'Total Non-Operating Income/Expense', 'Pre-Tax Income',
        'Income Taxes', 'Income After Taxes', 'Other Income', 'Income From Continuous Operations',
        'Income From Discontinued Operations', 'Net Income', 'EBITDA', 'EBIT',
        'Basic Shares Outstanding', 'Shares Outstanding', 'Basic EPS', 'EPS - Earnings Per Share',
    ]}), 'income')
    macro_balance = filtrar_datos_macrotrends(pd.DataFrame({'Datos': [
        'Cash On Hand', 'Receivables', 'Inventory', 'Pre-Paid Expenses', 'Other Current Assets',
        'Total Current Assets', 'Property, Plant, And Equipment', 'Long-Term Investments',
        'Goodwill And Intangible Assets', 'Other Long-Term Assets', 'Total Long-Term Assets',
        'Total Assets', 'Total Current Liabilities', 'Long Term Debt', 'Other Non-Current Liabilities',
        'Total Long Term Liabilities', 'Total Liabilities', 'Common Stock Net',
        'Retained Earnings (Accumulated Deficit)', 'Comprehensive Income',
        'Other Share Holders Equity', 'Share Holder Equity', 'Total Liabilities And Share Holders Equity',
    ]}), 'balance')
    macro_cashflow = filtrar_datos_macrotrends(pd.DataFrame({'Datos': [
        'Net Income/Loss', 'Total Depreciation And Amortization - Cash Flow', 'Other Non-Cash Items',
        'Total Non-Cash Items', 'Change In Accounts Receivable', 'Change In Inventories',
        'Change In Accounts Payable', 'Change In Assets/Liabilities', 'Total Change In Assets/Liabilities',
        'Cash Flow From Operating Activities', 'Net Change In Property, Plant, And Equipment',
        'Net Change In Intangible Assets', 'Net Acquisitions/Divestitures',
        'Net Change In Short-term Investments', 'Net Change In Long-Term Investments',
        'Net Change In Investments - Total', 'Investing Activities - Other',
        'Cash Flow From Investing Activities', 'Net Long-Term Debt', 'Net Current Debt',
        'Debt Issuance/Retirement Net - Total', 'Net Common Equity Issued/Repurchased',
        'Net Total Equity Issued/Repurchased', 'Total Common And Preferred Stock Dividends Paid',
        'Financial Activities - Other', 'Cash Flow From Financial Activities',
        'Net Cash Flow', 'Stock-Based Compensation', 'Common Stock Dividends Paid',
    ]}), 'cashflow')

    for row in google_income.itertuples():
        cursor.execute(_INSERT_GOOGLE, ('income', row.Datos, row.Datos))
    for row in google_balance.itertuples():
        cursor.execute(_INSERT_GOOGLE, ('balance', row.Datos, row.Datos))
    for row in google_cashflow.itertuples():
        cursor.execute(_INSERT_GOOGLE, ('cashflow', row.Datos, row.Datos))

    yahoo_all = pd.concat([yahoo_income, yahoo_balance, yahoo_cashflow]).drop_duplicates()
    for row in yahoo_all.itertuples():
        cursor.execute(_INSERT_YAHOO, (row.tipo_dato, row.Datos, row.Datos))

    for row in macro_income.itertuples():
        cursor.execute(_INSERT_MACRO, ('income', row.Datos, row.Datos))
    for row in macro_balance.itertuples():
        cursor.execute(_INSERT_MACRO, ('balance', row.Datos, row.Datos))
    for row in macro_cashflow.itertuples():
        cursor.execute(_INSERT_MACRO, ('cashflow', row.Datos, row.Datos))

    cursor.executemany(
        'INSERT INTO equivalencias (tipo_dato, google_finance_id, yahoo_finance_id, macrotrends_id) VALUES (?, ?, ?, ?)',
        [
            ('income',   1,  38,  1),
            ('income',   6,   7, 17),
            ('balance',  8, 103, 23),
            ('balance', 11,  52, 44),
            ('cashflow', 16, 160, 46),
            ('cashflow', 17, 142, 55),
        ]
    )


# ---------------------------------------------------------------------------
# DataManager — acceso a la BD en tiempo de ejecución
# ---------------------------------------------------------------------------

class DataManager:
    def __init__(self, db_filename=None):
        self.db_filename = db_filename or str(DB_PATH)
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)
        self._connect()

    def _connect(self):
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
        self.conn = sqlite3.connect(self.db_filename)
        self.cursor = self.conn.cursor()

    def fetch_data(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
