import pandas as pd
import sqlite3
import os
from config import EXPORT_DIR

def export_to_excel(google_df, yahoo_df, macrotrends_df, ticker):
    # Crear el directorio de exportación si no existe
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    filepath = os.path.join(EXPORT_DIR, f'{ticker}.xlsx')
    with pd.ExcelWriter(filepath) as writer:
        if google_df is not None and not google_df.empty:
            # Para Google Finance, siempre preservar la estructura del índice convirtiéndolo en una columna 'Datos'
            google_export = google_df.copy()
            # Restablecer el índice para convertir los nombres de las filas en una columna
            google_export.reset_index(inplace=True)
            google_export.rename(columns={'index': 'Datos'}, inplace=True)
            # Limpiar los prefijos de la columna 'Datos'
            google_export['Datos'] = google_export['Datos'].str.replace(r'^(Income_|Balance_|Cashflow_)', '', regex=True)
            google_export.to_excel(writer, sheet_name='Google Finance', index=False)
        if yahoo_df is not None and not yahoo_df.empty:
            yahoo_export = yahoo_df.copy()
            yahoo_export.to_excel(writer, sheet_name='Yahoo Finance', index=False)
        if macrotrends_df is not None and not macrotrends_df.empty:
            macrotrends_df.to_excel(writer, sheet_name='Macrotrends', index=False)

def import_from_excel(filepath):
    try:
        google_df = pd.DataFrame()
        yahoo_df = pd.DataFrame()
        macrotrends_df = pd.DataFrame()
        
        with pd.ExcelFile(filepath) as xls:
            # Intentar leer cada hoja, si no existe, usar DataFrame vacío
            try:
                google_df = pd.read_excel(xls, sheet_name='Google Finance')
            except ValueError:
                pass
            
            try:
                yahoo_df = pd.read_excel(xls, sheet_name='Yahoo Finance')
            except ValueError:
                pass
            
            try:
                macrotrends_df = pd.read_excel(xls, sheet_name='Macrotrends')
            except ValueError:
                pass
        
        return google_df, yahoo_df, macrotrends_df
    except Exception as e:
        raise ValueError(f"Error al importar archivo Excel: {str(e)}")

def export_to_sqlite(google_df, yahoo_df, macrotrends_df, ticker):
    # Crear el directorio de exportación si no existe
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    filepath = os.path.join(EXPORT_DIR, f'{ticker}.sqlite')
    conn = sqlite3.connect(filepath)
    if google_df is not None and not google_df.empty:
        # Para Google Finance, siempre preservar la estructura del índice convirtiéndolo en una columna 'Datos'
        google_export = google_df.copy()
        # Restablecer el índice para convertir los nombres de las filas en una columna
        google_export.reset_index(inplace=True)
        google_export.rename(columns={'index': 'Datos'}, inplace=True)
        # Limpiar los prefijos de la columna 'Datos'
        google_export['Datos'] = google_export['Datos'].str.replace(r'^(Income_|Balance_|Cashflow_)', '', regex=True)
        google_export.to_sql('google_finance', conn, if_exists='replace', index=False)
    if yahoo_df is not None and not yahoo_df.empty:
        yahoo_export = yahoo_df.copy()
        yahoo_export.to_sql('yahoo_finance', conn, if_exists='replace', index=False)
    if macrotrends_df is not None and not macrotrends_df.empty:
        macrotrends_df.to_sql('macrotrends', conn, if_exists='replace', index=False)
    conn.close()

def import_from_sqlite(filepath):
    try:
        google_df = pd.DataFrame()
        yahoo_df = pd.DataFrame()
        macrotrends_df = pd.DataFrame()
        
        conn = sqlite3.connect(filepath)
        
        # Intentar leer cada tabla, si no existe, usar DataFrame vacío
        try:
            google_df = pd.read_sql_query("SELECT * FROM google_finance", conn)
        except pd.io.sql.DatabaseError:
            pass
        
        try:
            yahoo_df = pd.read_sql_query("SELECT * FROM yahoo_finance", conn)
        except pd.io.sql.DatabaseError:
            pass
        
        try:
            macrotrends_df = pd.read_sql_query("SELECT * FROM macrotrends", conn)
        except pd.io.sql.DatabaseError:
            pass
        
        conn.close()
        return google_df, yahoo_df, macrotrends_df
    except Exception as e:
        raise ValueError(f"Error al importar archivo SQLite: {str(e)}")
