import pandas as pd
import sqlite3
import os

def export_to_excel(google_df, yahoo_df, macrotrends_df, ticker):
    # Create export directory if it does not exist
    if not os.path.exists('export'):
        os.makedirs('export')
    
    filepath = os.path.join('export', f'{ticker}.xlsx')
    with pd.ExcelWriter(filepath) as writer:
        if google_df is not None:
            google_df.to_excel(writer, sheet_name='Google Finance', index=False)
        if yahoo_df is not None:
            yahoo_df.to_excel(writer, sheet_name='Yahoo Finance', index=False)
        if macrotrends_df is not None:
            macrotrends_df.to_excel(writer, sheet_name='Macrotrends', index=False)

def import_from_excel(filepath):
    try:
        with pd.ExcelFile(filepath) as xls:
            google_df = pd.read_excel(xls, sheet_name='Google Finance')
            yahoo_df = pd.read_excel(xls, sheet_name='Yahoo Finance')
            macrotrends_df = pd.read_excel(xls, sheet_name='Macrotrends')
        # Check if the required columns are present
        required_columns = ['Datos']
        for df in [google_df, yahoo_df, macrotrends_df]:
            if not all(column in df.columns for column in required_columns):
                raise ValueError("El archivo Excel no contiene las columnas requeridas.")
        return google_df, yahoo_df, macrotrends_df
    except Exception as e:
        raise ValueError(f"Error al importar archivo Excel: {str(e)}")

def export_to_sqlite(google_df, yahoo_df, macrotrends_df, ticker):
    # Create export directory if it does not exist
    if not os.path.exists('export'):
        os.makedirs('export')
    
    filepath = os.path.join('export', f'{ticker}.sqlite')
    conn = sqlite3.connect(filepath)
    if google_df is not None:
        google_df.to_sql('google_finance', conn, if_exists='replace', index=False)
    if yahoo_df is not None:
        yahoo_df.to_sql('yahoo_finance', conn, if_exists='replace', index=False)
    if macrotrends_df is not None:
        macrotrends_df.to_sql('macrotrends', conn, if_exists='replace', index=False)
    conn.close()

def import_from_sqlite(filepath):
    try:
        conn = sqlite3.connect(filepath)
        google_df = pd.read_sql_query("SELECT * FROM google_finance", conn)
        yahoo_df = pd.read_sql_query("SELECT * FROM yahoo_finance", conn)
        macrotrends_df = pd.read_sql_query("SELECT * FROM macrotrends", conn)
        conn.close()
        # Check if the required columns are present
        required_columns = ['Datos']
        for df in [google_df, yahoo_df, macrotrends_df]:
            if not all(column in df.columns for column in required_columns):
                raise ValueError("El archivo SQLite no contiene las columnas requeridas.")
        return google_df, yahoo_df, macrotrends_df
    except Exception as e:
        raise ValueError(f"Error al importar archivo SQLite: {str(e)}")
