import os
import sys
import time
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Añadir el directorio raíz al path para poder importar los módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrappers.yahoo_finance_scraper import YahooFinanceScraper
from scrappers.google_finance_scraper import GoogleFinanceScraper
from scrappers.macrotrends_scraper import MacrotrendsScraper
from model.data_import_export import export_to_excel, import_from_excel, export_to_sqlite, import_from_sqlite

def run_performance_test(function, args, name, iterations=10):
    """
    Ejecuta una función múltiples veces y mide su rendimiento
    
    Args:
        function: La función a probar
        args: Argumentos para la función (como tupla)
        name: Nombre descriptivo para los informes
        iterations: Número de ejecuciones para obtener un promedio
    
    Returns:
        Dict con resultados (tiempo promedio, desviación estándar, tiempos individuales)
    """
    print(f"\nPueba de rendimiento para: {name}")
    times = []
    
    # Ejecutar las pruebas sin mostrar progreso detallado
    for i in range(iterations):
        try:
            start_time = time.time()
            result = function(*args)
            end_time = time.time()
            elapsed = end_time - start_time
            times.append(elapsed)
        except Exception as e:
            print(f"Error en {name}: {str(e)}")
            times.append(None)
    
    # Calcular estadísticas (excluyendo los None)
    valid_times = [t for t in times if t is not None]
    if valid_times:
        avg_time = statistics.mean(valid_times)
        if len(valid_times) > 1:
            std_dev = statistics.stdev(valid_times)
        else:
            std_dev = 0
            
        print(f"Resultado para {name}:")
        print(f"  Tiempo promedio: {avg_time:.2f} segundos")
        print(f"  Desviación estándar: {std_dev:.2f} segundos")
        
        return {
            'name': name,
            'avg_time': avg_time,
            'std_dev': std_dev,
            'times': valid_times
        }
    else:
        print(f"No se pudieron obtener tiempos válidos para {name}")
        return {
            'name': name,
            'avg_time': None,
            'std_dev': None,
            'times': []
        }

def test_search_performance(tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']):
    """Prueba el rendimiento de búsqueda de datos para varios tickers"""
    results = {
        'yahoo': [],
        'google': [],
        'macrotrends': []
    }
    
    # Crear los scrapers
    yahoo_scraper = YahooFinanceScraper()
    google_scraper = GoogleFinanceScraper()
    macrotrends_scraper = MacrotrendsScraper()
    
    print("\n===== PRUEBAS DE RENDIMIENTO DE BÚSQUEDA =====")
    
    for ticker in tickers:
        print(f"\n--- Probando ticker: {ticker} ---")
        
        # Probar Yahoo Finance
        result = run_performance_test(
            yahoo_scraper.get_combined_financial_data,
            (ticker,),
            f"Yahoo Finance - {ticker}"
        )
        results['yahoo'].append(result)
        
        # Probar Google Finance
        result = run_performance_test(
            google_scraper.get_stock_data,
            (ticker,),
            f"Google Finance - {ticker}"
        )
        results['google'].append(result)
        
        # Probar Macrotrends
        result = run_performance_test(
            macrotrends_scraper.get_financial_data,
            (ticker,),
            f"Macrotrends - {ticker}"
        )
        results['macrotrends'].append(result)
    
    return results

def test_export_import_performance(ticker='AAPL'):
    """Prueba el rendimiento de exportación e importación"""
    print("\n===== PRUEBAS DE RENDIMIENTO DE EXPORTACIÓN/IMPORTACIÓN =====")
    
    results = {}
    
    # Obtener datos para las pruebas
    yahoo_scraper = YahooFinanceScraper()
    google_scraper = GoogleFinanceScraper()
    macrotrends_scraper = MacrotrendsScraper()
    
    print(f"Obteniendo datos para {ticker} para las pruebas...")
    yahoo_df = yahoo_scraper.get_combined_financial_data(ticker)
    google_df = google_scraper.get_stock_data(ticker)
    macrotrends_df = macrotrends_scraper.get_financial_data(ticker)
    
    # Si no existe el directorio export, crearlo
    if not os.path.exists('export'):
        os.makedirs('export')
    
    # Probar exportación a Excel
    results['export_excel'] = run_performance_test(
        export_to_excel,
        (google_df, yahoo_df, macrotrends_df, ticker),
        "Exportar a Excel"
    )
    
    # Probar importación desde Excel
    excel_path = os.path.join('export', f'{ticker}.xlsx')
    if os.path.exists(excel_path):
        results['import_excel'] = run_performance_test(
            import_from_excel,
            (excel_path,),
            "Importar desde Excel"
        )
    
    # Probar exportación a SQLite
    results['export_sqlite'] = run_performance_test(
        export_to_sqlite,
        (google_df, yahoo_df, macrotrends_df, ticker),
        "Exportar a SQLite"
    )
    
    # Probar importación desde SQLite
    sqlite_path = os.path.join('export', f'{ticker}.sqlite')
    if os.path.exists(sqlite_path):
        results['import_sqlite'] = run_performance_test(
            import_from_sqlite,
            (sqlite_path,),
            "Importar desde SQLite"
        )
    
    return results

def generate_performance_report(search_results, export_import_results):
    """Genera un informe visual de los resultados de rendimiento"""
    
    report_folder = 'performance_reports'
    os.makedirs(report_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(report_folder, f'performance_report_{timestamp}.html')
    
    # Crear gráficos
    plt.figure(figsize=(12, 8))
    
    # Gráfico para búsquedas
    plt.subplot(2, 1, 1)
    
    yahoo_times = [r['avg_time'] for r in search_results['yahoo'] if r['avg_time'] is not None]
    google_times = [r['avg_time'] for r in search_results['google'] if r['avg_time'] is not None]
    macro_times = [r['avg_time'] for r in search_results['macrotrends'] if r['avg_time'] is not None]
    
    tickers = [r['name'].split(' - ')[1] for r in search_results['yahoo'] if r['avg_time'] is not None]
    
    x = range(len(tickers))
    bar_width = 0.25
    
    plt.bar([i - bar_width for i in x], yahoo_times, width=bar_width, label='Yahoo Finance', color='blue')
    plt.bar(x, google_times, width=bar_width, label='Google Finance', color='red')
    plt.bar([i + bar_width for i in x], macro_times, width=bar_width, label='Macrotrends', color='green')
    
    plt.xlabel('Ticker')
    plt.ylabel('Tiempo (segundos)')
    plt.title('Tiempo de búsqueda por fuente')
    plt.xticks(x, tickers)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Gráfico para exportación/importación
    plt.subplot(2, 1, 2)
    
    operations = []
    times = []
    err = []
    
    for key, result in export_import_results.items():
        if result['avg_time'] is not None:
            operations.append(key)
            times.append(result['avg_time'])
            err.append(result['std_dev'])
    
    plt.bar(operations, times, yerr=err, capsize=5)
    plt.xlabel('Operación')
    plt.ylabel('Tiempo (segundos)')
    plt.title('Tiempo de exportación/importación')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(report_folder, f'performance_chart_{timestamp}.png'))
    
    # Crear informe HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Informe de Rendimiento - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .chart-container {{ margin: 30px 0; }}
            .section {{ margin-bottom: 40px; }}
        </style>
    </head>
    <body>
        <h1>Informe de Rendimiento - {timestamp}</h1>
        
        <div class="section">
            <h2>Resumen de Resultados</h2>
            
            <h3>Tiempos de Búsqueda</h3>
            <table>
                <tr>
                    <th>Fuente</th>
                    <th>Ticker</th>
                    <th>Tiempo Promedio (s)</th>
                    <th>Desviación Estándar</th>
                </tr>
    """
    
    # Añadir resultados de búsqueda
    for source in ['yahoo', 'google', 'macrotrends']:
        for result in search_results[source]:
            if result['avg_time'] is not None:
                html_content += f"""
                <tr>
                    <td>{source.capitalize()}</td>
                    <td>{result['name'].split(' - ')[1]}</td>
                    <td>{result['avg_time']:.2f}</td>
                    <td>{result['std_dev']:.2f}</td>
                </tr>
                """
    
    html_content += """
            </table>
            
            <h3>Tiempos de Exportación/Importación</h3>
            <table>
                <tr>
                    <th>Operación</th>
                    <th>Tiempo Promedio (s)</th>
                    <th>Desviación Estándar</th>
                </tr>
    """
    
    # Añadir resultados de exportación/importación
    for key, result in export_import_results.items():
        if result['avg_time'] is not None:
            html_content += f"""
            <tr>
                <td>{result['name']}</td>
                <td>{result['avg_time']:.2f}</td>
                <td>{result['std_dev']:.2f}</td>
            </tr>
            """
    
    html_content += """
            </table>
        </div>
        
        <div class="chart-container">
            <h2>Gráficos de Rendimiento</h2>
            <img src="performance_chart_{}.png" alt="Performance Charts" style="max-width: 100%;">
        </div>
    </body>
    </html>
    """.format(timestamp)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nInforme generado: {report_file}")
    return report_file

if __name__ == "__main__":
    # Lista de tickers a probar (puedes modificarla)
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    # Ejecutar pruebas de rendimiento
    search_results = test_search_performance(test_tickers)
    export_import_results = test_export_import_performance('AAPL')
    
    # Generar informe
    report_path = generate_performance_report(search_results, export_import_results)
    
    print("\nPruebas de rendimiento completadas.")
    print(f"El informe se ha generado en: {report_path}")