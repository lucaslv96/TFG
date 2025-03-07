import sqlite3
import os
from model.data_manager import filtrar_datos_google, filtrar_datos_yahoo, filtrar_datos_macrotrends
import pandas as pd

# Definir constantes para las consultas SQL
INSERT_GOOGLE_FINANCE = 'INSERT INTO google_finance (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)'
INSERT_YAHOO_FINANCE = 'INSERT INTO yahoo_finance (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)'
INSERT_MACROTRENDS = 'INSERT INTO macrotrends (tipo_dato, dato_inicial, dato_actual) VALUES (?, ?, ?)'

def initialize_database():
    db_filename = 'bbdd/equivalencias.sqlite'
    
    if not os.path.exists('bbdd'):
        os.makedirs('bbdd')
    
    if not os.path.exists(db_filename):
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        
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
                FOREIGN KEY (yahoo_finance_id) REFERENCES yahoo_finance(id),
                FOREIGN KEY (macrotrends_id) REFERENCES macrotrends(id)
            )
        ''')
        
        # Load data from data_filter.py
        load_data(cursor)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    else:
        print("Database already exists.")

def load_data(cursor):
    # Load data from data_filter.py
    google_income_data = filtrar_datos_google(pd.DataFrame({'Datos': [
        'Ingresos', 'Gastos operativos', 'Ingresos netos', 'Margen de beneficio neto',
        'Beneficios por acción', 'EBITDA', 'Tipo impositivo efectivo'
    ]}), 'income')
    
    google_balance_data = filtrar_datos_google(pd.DataFrame({'Datos': [
        'Efectivo y a corto plazo', 'Activos totales', 'Responsabilidades totales',
        'Patrimonio total', 'Acciones en circulación', 'Precio-valor contable',
        'Rentabilidad económica', 'Retorno sobre capital'
    ]}), 'balance')
    
    google_cashflow_data = filtrar_datos_google(pd.DataFrame({'Datos': [
        'Ingresos netos', 'Efectivo de operaciones', 'Efectivo de inversión',
        'Efectivo de financiación', 'Variación neta del flujo de caja', 'Flujo de caja libre'
    ]}), 'cashflow')
    
    yahoo_income_data = filtrar_datos_yahoo('AAPL', 'income')  # Example ticker
    yahoo_income_data['tipo_dato'] = 'income'
    yahoo_balance_data = filtrar_datos_yahoo('AAPL', 'balance')
    yahoo_balance_data['tipo_dato'] = 'balance'
    yahoo_cashflow_data = filtrar_datos_yahoo('AAPL', 'cashflow')
    yahoo_cashflow_data['tipo_dato'] = 'cashflow'
    
    macrotrends_income_data = filtrar_datos_macrotrends(pd.DataFrame({'Datos': [
        'Revenue', 'Cost Of Goods Sold', 'Gross Profit', 'Research And Development Expenses', 'SG&A Expenses', 
        'Other Operating Income Or Expenses', 'Operating Expenses', 'Operating Income', 'Total Non-Operating Income/Expense',
        'Pre-Tax Income', 'Income Taxes', 'Income After Taxes', 'Other Income', 'Income From Continuous Operations',
        'Income From Discontinued Operations', 'Net Income', 'EBITDA', 'EBIT', 'Basic Shares Outstanding', 'Shares Outstanding',
        'Basic EPS', 'EPS - Earnings Per Share'
    ]}), 'income')
    
    macrotrends_balance_data = filtrar_datos_macrotrends(pd.DataFrame({'Datos': [
        'Cash On Hand', 'Receivables', 'Inventory', 'Pre-Paid Expenses', 'Other Current Assets', 'Total Current Assets', 
        'Property, Plant, And Equipment', 'Long-Term Investments', 'Goodwill And Intangible Assets', 'Other Long-Term Assets', 
        'Total Long-Term Assets', 'Total Assets', 'Total Current Liabilities', 'Long Term Debt', 'Other Non-Current Liabilities', 
        'Total Long Term Liabilities', 'Total Liabilities', 'Common Stock Net', 'Retained Earnings (Accumulated Deficit)', 
        'Comprehensive Income', 'Other Share Holders Equity', 'Share Holder Equity', 'Total Liabilities And Share Holders Equity'
    ]}), 'balance')
    
    macrotrends_cashflow_data = filtrar_datos_macrotrends(pd.DataFrame({'Datos': [
        'Net Income/Loss', 'Total Depreciation And Amortization - Cash Flow', 'Other Non-Cash Items', 'Total Non-Cash Items', 
        'Change In Accounts Receivable', 'Change In Inventories', 'Change In Accounts Payable', 'Change In Assets/Liabilities', 
        'Total Change In Assets/Liabilities', 'Cash Flow From Operating Activities', 'Net Change In Property, Plant, And Equipment',
        'Net Change In Intangible Assets', 'Net Acquisitions/Divestitures', 'Net Change In Short-term Investments', 'Net Change In Long-Term Investments',
        'Net Change In Investments - Total', 'Investing Activities - Other', 'Cash Flow From Investing Activities', 'Net Long-Term Debt', 
        'Net Current Debt', 'Debt Issuance/Retirement Net - Total', 'Net Common Equity Issued/Repurchased', 'Net Total Equity Issued/Repurchased',
        'Total Common And Preferred Stock Dividends Paid', 'Financial Activities - Other', 'Cash Flow From Financial Activities', 
        'Net Cash Flow', 'Stock-Based Compensation', 'Common Stock Dividends Paid'
    ]}), 'cashflow')
    
    # Insert data into google_finance table
    for index, row in google_income_data.iterrows():
        cursor.execute(INSERT_GOOGLE_FINANCE, ('income', row['Datos'], row['Datos']))
    for index, row in google_balance_data.iterrows():
        cursor.execute(INSERT_GOOGLE_FINANCE, ('balance', row['Datos'], row['Datos']))
    for index, row in google_cashflow_data.iterrows():
        cursor.execute(INSERT_GOOGLE_FINANCE, ('cashflow', row['Datos'], row['Datos']))
    
    # Insert data into yahoo_finance table
    yahoo_data = pd.concat([yahoo_income_data, yahoo_balance_data, yahoo_cashflow_data]).drop_duplicates()
    for index, row in yahoo_data.iterrows():
        cursor.execute(INSERT_YAHOO_FINANCE, (row['tipo_dato'], row['Datos'], row['Datos']))
    
    # Insert data into macrotrends table
    for index, row in macrotrends_income_data.iterrows():
        cursor.execute(INSERT_MACROTRENDS, ('income', row['Datos'], row['Datos']))
    for index, row in macrotrends_balance_data.iterrows():
        cursor.execute(INSERT_MACROTRENDS, ('balance', row['Datos'], row['Datos']))
    for index, row in macrotrends_cashflow_data.iterrows():
        cursor.execute(INSERT_MACROTRENDS, ('cashflow', row['Datos'], row['Datos']))
    
    # Insert default values into equivalencias table
    default_equivalencias = [
        ('income',1 ,38 , 1 ),
        ('income',6 , 7, 17 ),
        ('balance',8 , 103 , 23 ),
        ('balance',11 , 52 , 44 ),
        ('cashflow',16 ,160 ,46 ),
        ('cashflow', 17,142 ,55 )
    ]
    cursor.executemany('INSERT INTO equivalencias (tipo_dato, google_finance_id, yahoo_finance_id, macrotrends_id) VALUES (?, ?, ?, ?)', default_equivalencias)
