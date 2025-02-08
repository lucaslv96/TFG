from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import os
from model.data_filter import filtrar_datos_google, filtrar_datos_yahoo, filtrar_datos_macrotrends
from model.import_export_handler import export_to_excel, import_from_excel, export_to_sqlite, import_from_sqlite
from model.data_manager import DataManager
from scrappers.macrotrends_scraper import MacrotrendsScraper
from scrappers.yahoo_finance_scraper import YahooFinanceScraper
from controller.datos_equivalentes_controller import mostrar_datos_equivalentes
from model.pandas_model import PandasModel

class Worker(QThread):
    result = pyqtSignal(pd.DataFrame)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker

    def run(self):
        from scrappers.google_finance_scraper import GoogleFinanceScraper
        scraper = GoogleFinanceScraper()
        df = scraper.get_stock_data(self.ticker)
        self.result.emit(df)

class YahooWorker(QThread):
    result = pyqtSignal(pd.DataFrame)

    def __init__(self, ticker, data_type):
        super().__init__()
        self.ticker = ticker
        self.data_type = data_type

    def run(self):
        df = filtrar_datos_yahoo(self.ticker, self.data_type)
        self.result.emit(df)

class MacrotrendsWorker(QThread):
    result = pyqtSignal(pd.DataFrame)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker

    def run(self):
        scraper = MacrotrendsScraper()
        df = scraper.get_financial_data(self.ticker)
        self.result.emit(df)

def buscar_datos(self):
    ticker = self.lineEdit.text().strip().upper()
    if ticker:
        self.statusLabel.setText("Estado: Buscando datos...")
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)
        # Vaciar las tablas antes de realizar una nueva búsqueda
        self.tableView.setModel(PandasModel(pd.DataFrame()))
        self.tableView_3.setModel(PandasModel(pd.DataFrame()))
        self.tableView_4.setModel(PandasModel(pd.DataFrame()))
        self.tableView.viewport().update()
        self.tableView_3.viewport().update()
        self.tableView_4.viewport().update()

        self.lineEdit.setEnabled(False)
        self.pushButton.setEnabled(False)
        
        self.google_df = pd.DataFrame()
        self.yahoo_df = pd.DataFrame()
        self.macrotrends_df = pd.DataFrame()

        # Contador para rastrear los trabajadores que han terminado
        self.trabajadores_finalizados = 0
        
        # Ocultar los botones mientras se realiza la búsqueda
        self.balanceButton.setVisible(False)
        self.flujoCajaButton.setVisible(False)
        self.perdidasGananciasButton.setVisible(False)
        
        # Clear company name labels
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("MainWindow", "Datos de Google Finance"))
        self.label_4.setText(_translate("MainWindow", "Datos de Yahoo Finance"))
        self.label_5.setText(_translate("MainWindow", "Datos de Macrotrends"))
        
        self.google_worker = Worker(ticker)
        self.yahoo_worker = YahooWorker(ticker, 'balance')
        self.macrotrends_worker = MacrotrendsWorker(ticker)
        
        self.google_worker.result.connect(lambda df: mostrar_datos_google(self, df))
        self.yahoo_worker.result.connect(lambda df: mostrar_datos_yahoo(self, df))
        self.macrotrends_worker.result.connect(lambda df: mostrar_datos_macrotrends(self, df))
        
        self.google_worker.start()
        self.yahoo_worker.start()
        self.macrotrends_worker.start()

def mostrar_datos_google(self, df):
    self.google_df = df
    self.trabajadores_finalizados += 1  # Incrementar contador
    self.statusLabel.setText(f"{self.trabajadores_finalizados}/3 búsquedas completadas")
    self.progressBar.setValue(int((self.trabajadores_finalizados / 3) * 100))  # Convert to int
    verificar_datos(self)

def mostrar_datos_yahoo(self, df):
    self.yahoo_df = df
    self.trabajadores_finalizados += 1  # Incrementar contador
    self.statusLabel.setText(f"{self.trabajadores_finalizados}/3 búsquedas completadas")
    self.progressBar.setValue(int((self.trabajadores_finalizados / 3) * 100))  # Convert to int
    verificar_datos(self)

def mostrar_datos_macrotrends(self, df):
    self.macrotrends_df = df
    self.trabajadores_finalizados += 1  # Incrementar contador
    self.statusLabel.setText(f"{self.trabajadores_finalizados}/3 búsquedas completadas")
    self.progressBar.setValue(int((self.trabajadores_finalizados / 3) * 100))  # Convert to int
    verificar_datos(self)

def verificar_datos(self):
    # Solo proceder cuando los tres trabajadores hayan terminado
    if self.trabajadores_finalizados < 3:
        return

    if self.google_df.empty and self.yahoo_df.empty and self.macrotrends_df.empty:
        QtWidgets.QMessageBox.warning(None, "Error", "No se encontraron datos para el ticker en ninguna fuente.")
        self.lineEdit.setEnabled(True)
        self.pushButton.setEnabled(True)
        self.statusLabel.setText("No se encontraron datos")
    else:
        mostrar_todos_los_datos(self)
        self.statusLabel.setText("Búsqueda completada")
    
    self.progressBar.setVisible(False)  # Hide the progress bar after completion

def mostrar_todos_los_datos(self):
    self.lineEdit.setEnabled(True)
    self.pushButton.setEnabled(True)
    if not self.google_df.empty and not self.yahoo_df.empty and not self.macrotrends_df.empty:
        self.df = self.google_df
        self.df_yahoo = self.yahoo_df
        self.df_macrotrends = self.macrotrends_df
        
        # Definir self.data_frames
        self.data_frames = {
            'balance': {
                'google': filtrar_datos_google(self.df, 'balance'),
                'yahoo': filtrar_datos_yahoo(self.lineEdit.text().strip(), 'balance'),
                'macrotrends': filtrar_datos_macrotrends(self.df_macrotrends, 'balance')
            },
            'cashflow': {
                'google': filtrar_datos_google(self.df, 'cashflow'),
                'yahoo': filtrar_datos_yahoo(self.lineEdit.text().strip(), 'cashflow'),
                'macrotrends': filtrar_datos_macrotrends(self.df_macrotrends, 'cashflow')
            },
            'income': {
                'google': filtrar_datos_google(self.df, 'income'),
                'yahoo': filtrar_datos_yahoo(self.lineEdit.text().strip(), 'income'),
                'macrotrends': filtrar_datos_macrotrends(self.df_macrotrends, 'income')
            }
        }
        
        self.balanceButton.setVisible(True)
        self.flujoCajaButton.setVisible(True)
        self.perdidasGananciasButton.setVisible(True)
        
        # Desconectar señales previas para evitar duplicaciones
        try:
            self.balanceButton.clicked.disconnect()
            self.flujoCajaButton.clicked.disconnect()
            self.perdidasGananciasButton.clicked.disconnect()
        except TypeError:
            pass
        
        self.balanceButton.clicked.connect(lambda: mostrar_datos_filtrados(self, 'balance'))
        self.flujoCajaButton.clicked.connect(lambda: mostrar_datos_filtrados(self, 'cashflow'))
        self.perdidasGananciasButton.clicked.connect(lambda: mostrar_datos_filtrados(self, 'income'))
        
        self.balanceButton.clicked.connect(lambda: mostrar_datos_filtrados_macrotrends(self, 'balance'))
        self.flujoCajaButton.clicked.connect(lambda: mostrar_datos_filtrados_macrotrends(self, 'cashflow'))
        self.perdidasGananciasButton.clicked.connect(lambda: mostrar_datos_filtrados_macrotrends(self, 'income'))
        
        model_google = PandasModel(self.data_frames['balance']['google'])
        self.tableView.setModel(model_google)
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        model_yahoo = PandasModel(self.data_frames['balance']['yahoo'])
        self.tableView_3.setModel(model_yahoo)
        self.tableView_3.resizeColumnsToContents()
        self.tableView_3.horizontalHeader().setStretchLastSection(True)
        self.tableView_3.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        model_macrotrends = PandasModel(self.data_frames['balance']['macrotrends'])
        self.tableView_4.setModel(model_macrotrends)
        self.tableView_4.resizeColumnsToContents()
        self.tableView_4.horizontalHeader().setStretchLastSection(True)
        self.tableView_4.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Obtener el nombre de la empresa y actualizar las etiquetas
        yahoo_scraper = YahooFinanceScraper()
        company_name = yahoo_scraper.get_company_name(self.lineEdit.text().strip())
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("MainWindow", f"Datos de Google Finance - {company_name}"))
        self.label_4.setText(_translate("MainWindow", f"Datos de Yahoo Finance - {company_name}"))
        self.label_5.setText(_translate("MainWindow", f"Datos de Macrotrends - {company_name}"))
        self.label_equivalentes.setText(_translate("MainWindow", f"Datos Equivalentes - {company_name}"))

        # Mostrar datos equivalentes
        mostrar_datos_equivalentes(self)

        # Hacer visibles las casillas de búsqueda
        self.search_google.setVisible(True)
        self.search_yahoo.setVisible(True)
        self.search_macrotrends.setVisible(True)

def mostrar_datos_filtrados(self, data_type):
    if self.df.empty:
        return
    filtered_df = filtrar_datos_google(self.df, data_type)
    model = PandasModel(filtered_df)
    self.tableView.setModel(model)
    self.tableView.resizeColumnsToContents()
    self.tableView.horizontalHeader().setStretchLastSection(True)
    self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    display_selected_data(self, data_type)  # Mostrar también los datos de Yahoo Finance

def mostrar_datos_filtrados_macrotrends(self, data_type):
    if self.df_macrotrends.empty:
        return
    filtered_df = filtrar_datos_macrotrends(self.df_macrotrends, data_type)
    model = PandasModel(filtered_df)
    self.tableView_4.setModel(model)
    self.tableView_4.resizeColumnsToContents()
    self.tableView_4.horizontalHeader().setStretchLastSection(True)
    self.tableView_4.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

def mostrar_balance(self):
    mostrar_datos_filtrados(self, 'balance')

def display_selected_data(self, data_type):
    if self.df_yahoo.empty:
        return
    yahoo_data = filtrar_datos_yahoo(self.lineEdit.text().strip(), data_type)
    model = PandasModel(yahoo_data)
    self.tableView_3.setModel(model)
    self.tableView_3.resizeColumnsToContents()
    self.tableView_3.horizontalHeader().setStretchLastSection(True)
    self.tableView_3.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

def exportar_datos(self):
    if not hasattr(self, 'df') or self.df.empty:
        QtWidgets.QMessageBox.warning(None, "Exportar", "No hay datos para exportar.")
        return
    google_df = self.df
    yahoo_df = self.df_yahoo
    macrotrends_df = self.df_macrotrends
    ticker = self.lineEdit.text().strip().upper()
    
    # Call the export function from import_export_handler
    export_to_sqlite(google_df, yahoo_df, macrotrends_df, ticker)
    export_to_excel(google_df, yahoo_df, macrotrends_df, ticker)
    
    QtWidgets.QMessageBox.information(None, "Exportar", "Datos exportados exitosamente.")

def importar_datos(self):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Importar archivo", "", "Excel Files (*.xlsx);;SQLite Files (*.sqlite)", options=options)
    if filename:
        if filename.endswith('.xlsx'):
            google_df, yahoo_df, macrotrends_df = import_from_excel(filename)
        elif filename.endswith('.sqlite'):
            google_df, yahoo_df, macrotrends_df = import_from_sqlite(filename)
        else:
            QtWidgets.QMessageBox.warning(None, "Importar", "Formato de archivo no soportado.")
            return
        
        # Filtrar los valores de balance, flujo de caja y cuenta de pérdidas y ganancias
        google_df_balance = filtrar_datos_google(google_df, 'balance')
        yahoo_df_balance = filtrar_datos_yahoo(os.path.basename(filename).split('.')[0], 'balance')
        macrotrends_df_balance = filtrar_datos_macrotrends(macrotrends_df, 'balance')
        
        google_df_cashflow = filtrar_datos_google(google_df, 'cashflow')
        yahoo_df_cashflow = filtrar_datos_yahoo(os.path.basename(filename).split('.')[0], 'cashflow')
        macrotrends_df_cashflow = filtrar_datos_macrotrends(macrotrends_df, 'cashflow')
        
        google_df_income = filtrar_datos_google(google_df, 'income')
        yahoo_df_income = filtrar_datos_yahoo(os.path.basename(filename).split('.')[0], 'income')
        macrotrends_df_income = filtrar_datos_macrotrends(macrotrends_df, 'income')
        
        # Guardar los DataFrames filtrados en atributos de la clase
        self.data_frames = {
            'balance': {
                'google': google_df_balance,
                'yahoo': yahoo_df_balance,
                'macrotrends': macrotrends_df_balance
            },
            'cashflow': {
                'google': google_df_cashflow,
                'yahoo': yahoo_df_cashflow,
                'macrotrends': macrotrends_df_cashflow
            },
            'income': {
                'google': google_df_income,
                'yahoo': yahoo_df_income,
                'macrotrends': macrotrends_df_income
            }
        }
        
        # Mostrar los datos de balance importados en las tablas
        model_google = PandasModel(self.data_frames['balance']['google'])
        self.tableView.setModel(model_google)
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        model_yahoo = PandasModel(self.data_frames['balance']['yahoo'])
        self.tableView_3.setModel(model_yahoo)
        self.tableView_3.resizeColumnsToContents()
        self.tableView_3.horizontalHeader().setStretchLastSection(True)
        self.tableView_3.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        model_macrotrends = PandasModel(self.data_frames['balance']['macrotrends'])
        self.tableView_4.setModel(model_macrotrends)
        self.tableView_4.resizeColumnsToContents()
        self.tableView_4.horizontalHeader().setStretchLastSection(True)
        self.tableView_4.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        # Hacer visibles las casillas de búsqueda
        self.search_google.setVisible(True)
        self.search_yahoo.setVisible(True)
        self.search_macrotrends.setVisible(True)
        
        self.balanceButton.setVisible(True)
        self.flujoCajaButton.setVisible(True)
        self.perdidasGananciasButton.setVisible(True)
        
        # Conectar los botones para alternar entre los tipos de datos
        self.balanceButton.clicked.connect(lambda: mostrar_datos_filtrados(self, 'balance'))
        self.flujoCajaButton.clicked.connect(lambda: mostrar_datos_filtrados(self, 'cashflow'))
        self.perdidasGananciasButton.clicked.connect(lambda: mostrar_datos_filtrados(self, 'income'))
        
        # Definir self.df, self.df_yahoo y self.df_macrotrends
        self.df = self.data_frames['balance']['google']
        self.df_yahoo = self.data_frames['balance']['yahoo']
        self.df_macrotrends = self.data_frames['balance']['macrotrends']
        
        # Obtener el nombre de la empresa del nombre del archivo
        ticker = os.path.basename(filename).split('.')[0]
        yahoo_scraper = YahooFinanceScraper()
        company_name = yahoo_scraper.get_company_name(ticker)
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("MainWindow", f"Datos de Google Finance - {company_name}"))
        self.label_4.setText(_translate("MainWindow", f"Datos de Yahoo Finance - {company_name}"))
        self.label_5.setText(_translate("MainWindow", f"Datos de Macrotrends - {company_name}"))
        self.label_equivalentes.setText(_translate("MainWindow", f"Datos Equivalentes - {company_name}"))
        
        # Mostrar datos equivalentes
        mostrar_datos_equivalentes(self)
        
        QtWidgets.QMessageBox.information(None, "Importar", "Datos importados exitosamente.")
def mostrar_datos_filtrados(self, data_type):
    if self.data_frames[data_type]['google'].empty:
        return
    filtered_df_google = self.data_frames[data_type]['google']
    filtered_df_yahoo = self.data_frames[data_type]['yahoo']
    filtered_df_macrotrends = self.data_frames[data_type]['macrotrends']
    
    model_google = PandasModel(filtered_df_google)
    self.tableView.setModel(model_google)
    self.tableView.resizeColumnsToContents()
    self.tableView.horizontalHeader().setStretchLastSection(True)
    self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    model_yahoo = PandasModel(filtered_df_yahoo)
    self.tableView_3.setModel(model_yahoo)
    self.tableView_3.resizeColumnsToContents()
    self.tableView_3.horizontalHeader().setStretchLastSection(True)
    self.tableView_3.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    model_macrotrends = PandasModel(filtered_df_macrotrends)
    self.tableView_4.setModel(model_macrotrends)
    self.tableView_4.resizeColumnsToContents()
    self.tableView_4.horizontalHeader().setStretchLastSection(True)
    self.tableView_4.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
