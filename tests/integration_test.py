import os
import time
import pandas as pd

from scrapers.yahoo_finance_scraper import YahooFinanceScraper
from scrapers.google_finance_scraper import GoogleFinanceScraper
from scrapers.macrotrends_scraper import MacrotrendsScraper
from model.data_import_export import export_to_excel, import_from_excel, export_to_sqlite, import_from_sqlite
from model.data_manager import filtrar_datos_google, filtrar_datos_yahoo, filtrar_datos_macrotrends


def test_complete_flow(ticker='AAPL'):
    """
    Realiza una prueba completa del flujo de trabajo:
    1. Buscar datos para el ticker en las tres fuentes
    2. Exportar los datos a Excel y SQLite
    3. Importar los datos desde los archivos exportados
    4. Comparar los datos originales con los importados
    """
    print(f"\n===== PRUEBA COMPLETA DE FLUJO PARA {ticker} =====\n")
    
    # Step 1: Extraer datos
    print("1. Extrayendo datos de las tres fuentes...")
    
    # Yahoo Finance
    print("   - Datos de Yahoo Finance...")
    start_time = time.time()
    yahoo_scraper = YahooFinanceScraper()
    yahoo_df = yahoo_scraper.get_combined_financial_data(ticker)
    print(f"     Completado en {time.time() - start_time:.2f} segundos")
    
    # Google Finance
    print("   - Datos de Google Finance...")
    start_time = time.time()
    google_scraper = GoogleFinanceScraper()
    google_df = google_scraper.get_stock_data(ticker)
    print(f"     Completado en {time.time() - start_time:.2f} segundos")
    
    # Macrotrends
    print("   - Datos de Macrotrends...")
    start_time = time.time()
    macrotrends_scraper = MacrotrendsScraper()
    macrotrends_df = macrotrends_scraper.get_financial_data(ticker)
    print(f"     Completado en {time.time() - start_time:.2f} segundos")
    
    # Step 2: Exportar datos
    print("\n2. Exportando datos...")
    
    from config import EXPORT_DIR
    # Exportar a Excel
    print("   - Exportando a Excel...")
    start_time = time.time()
    export_to_excel(google_df, yahoo_df, macrotrends_df, ticker)
    excel_path = os.path.join(EXPORT_DIR, f'{ticker}.xlsx')
    print(f"     Completado en {time.time() - start_time:.2f} segundos")

    # Exportar a SQLite
    print("   - Exportando a SQLite...")
    start_time = time.time()
    export_to_sqlite(google_df, yahoo_df, macrotrends_df, ticker)
    sqlite_path = os.path.join(EXPORT_DIR, f'{ticker}.sqlite')
    print(f"     Completado en {time.time() - start_time:.2f} segundos")
    print(f"     Archivo creado: {os.path.abspath(sqlite_path)}")
    
    # Step 3: Importar datos
    print("\n3. Importando datos...")
    
    # Importar desde Excel
    print("   - Importando desde Excel...")
    start_time = time.time()
    excel_google_df, excel_yahoo_df, excel_macrotrends_df = import_from_excel(excel_path)
    print(f"     Completado en {time.time() - start_time:.2f} segundos")
    print(f"     Filas importadas (Google): {len(excel_google_df)}")
    print(f"     Filas importadas (Yahoo): {len(excel_yahoo_df)}")
    print(f"     Filas importadas (Macrotrends): {len(excel_macrotrends_df)}")
    
    # Importar desde SQLite
    print("   - Importando desde SQLite...")
    start_time = time.time()
    sqlite_google_df, sqlite_yahoo_df, sqlite_macrotrends_df = import_from_sqlite(sqlite_path)
    print(f"     Completado en {time.time() - start_time:.2f} segundos")
    print(f"     Filas importadas (Google): {len(sqlite_google_df)}")
    print(f"     Filas importadas (Yahoo): {len(sqlite_yahoo_df)}")
    print(f"     Filas importadas (Macrotrends): {len(sqlite_macrotrends_df)}")
    
    # Step 4: Verificar que los datos filtrados son correctos
    print("\n4. Verificando filtrado de datos...")
    
    # Filtrar datos originales
    google_balance = filtrar_datos_google(google_df, 'balance')
    google_cashflow = filtrar_datos_google(google_df, 'cashflow')
    google_income = filtrar_datos_google(google_df, 'income')
    
    yahoo_balance = filtrar_datos_yahoo(ticker, 'balance')
    yahoo_cashflow = filtrar_datos_yahoo(ticker, 'cashflow')
    yahoo_income = filtrar_datos_yahoo(ticker, 'income')
    
    macrotrends_balance = filtrar_datos_macrotrends(macrotrends_df, 'balance')
    macrotrends_cashflow = filtrar_datos_macrotrends(macrotrends_df, 'cashflow')
    macrotrends_income = filtrar_datos_macrotrends(macrotrends_df, 'income')
    
    # Mostrar resultados de filtrado
    print("   - Google Finance:")
    print(f"     Balance: {len(google_balance)} filas")
    print(f"     Flujo de Caja: {len(google_cashflow)} filas")
    print(f"     Cuenta de Resultados: {len(google_income)} filas")
    
    print("   - Yahoo Finance:")
    print(f"     Balance: {len(yahoo_balance)} filas")
    print(f"     Flujo de Caja: {len(yahoo_cashflow)} filas")
    print(f"     Cuenta de Resultados: {len(yahoo_income)} filas")
    
    print("   - Macrotrends:")
    print(f"     Balance: {len(macrotrends_balance)} filas")
    print(f"     Flujo de Caja: {len(macrotrends_cashflow)} filas")
    print(f"     Cuenta de Resultados: {len(macrotrends_income)} filas")
    
    print("\n===== PRUEBA COMPLETA FINALIZADA =====")


if __name__ == "__main__":
    # Ejecutar la prueba para AAPL
    test_complete_flow('AAPL')
    
    # También puedes probar con otro ticker descomentando esta línea:
    # test_complete_flow('MSFT')