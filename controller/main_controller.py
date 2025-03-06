from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import os
from model.data_manager import filtrar_datos_google, filtrar_datos_yahoo, filtrar_datos_macrotrends, PandasModel
from model.data_import_export import export_to_excel, import_from_excel, export_to_sqlite, import_from_sqlite
from model.database_manager import DataManager
from scrappers.macrotrends_scraper import MacrotrendsScraper
from scrappers.yahoo_finance_scraper import YahooFinanceScraper
from controller.datos_equivalentes_controller import mostrar_datos_equivalentes

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
        
        # Vaciar todas las tablas antes de realizar una nueva búsqueda
        self.tableView.setModel(PandasModel(pd.DataFrame()))
        self.tableView_3.setModel(PandasModel(pd.DataFrame()))
        self.tableView_4.setModel(PandasModel(pd.DataFrame()))
        
        # También vaciar las tablas de la pestaña de datos equivalentes
        self.tableView_balance.setModel(PandasModel(pd.DataFrame()))
        self.tableView_cash_flow.setModel(PandasModel(pd.DataFrame()))
        self.tableView_income_statement.setModel(PandasModel(pd.DataFrame()))
        
        # Restablecer los títulos de las etiquetas a sus valores por defecto
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("MainWindow", "Datos de Google Finance"))
        self.label_4.setText(_translate("MainWindow", "Datos de Yahoo Finance"))
        self.label_5.setText(_translate("MainWindow", "Datos de Macrotrends"))
        self.label_equivalentes.setText(_translate("MainWindow", "Datos Equivalentes"))
        self.label_balance.setText(_translate("MainWindow", "Datos de Balance"))
        self.label_cash_flow.setText(_translate("MainWindow", "Datos de Flujo de Caja"))
        self.label_income_statement.setText(_translate("MainWindow", "Cuenta de Pérdidas y Ganancias"))
        
        # Ocultar temporalmente el selector de años durante la búsqueda
        # Primero buscar y ocultar frame existente si existe
        self.saved_filter_frame = None
        for i in range(self.tab_2_layout.count()):
            item = self.tab_2_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QtWidgets.QFrame):
                self.saved_filter_frame = item.widget()
                self.saved_filter_frame.setVisible(False)
                break
        
        # También ocultar el combobox directamente si existe
        if hasattr(self, 'year_filter_combobox') and self.year_filter_combobox is not None:
            self.year_filter_combobox.setVisible(False)
            
        # Si hay una etiqueta del filtro, también ocultarla
        if hasattr(self, 'year_filter_label') and self.year_filter_label is not None:
            self.year_filter_label.setVisible(False)
        
        # Forzar actualización visual
        self.tableView.viewport().update()
        self.tableView_3.viewport().update()
        self.tableView_4.viewport().update()
        self.tableView_balance.viewport().update()
        self.tableView_cash_flow.viewport().update()
        self.tableView_income_statement.viewport().update()

        # Desactivar controles para evitar múltiples búsquedas simultáneas
        self.lineEdit.setEnabled(False)
        self.pushButton.setEnabled(False)
        
        # Reiniciar los dataframes
        self.google_df = pd.DataFrame()
        self.yahoo_df = pd.DataFrame()
        self.macrotrends_df = pd.DataFrame()

        # Inicializar el contador de trabajadores finalizados
        self.trabajadores_finalizados = 0
        
        # Ocultar los botones de navegación
        self.balanceButton.setVisible(False)
        self.flujoCajaButton.setVisible(False)
        self.perdidasGananciasButton.setVisible(False)
        
        # Iniciar los trabajadores para obtener datos
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
    #print("Mostrando datos de Google:", df)
    self.google_df = df
    self.trabajadores_finalizados += 1  # Incrementar contador
    self.statusLabel.setText(f"{self.trabajadores_finalizados}/3 búsquedas completadas")
    self.progressBar.setValue(int((self.trabajadores_finalizados / 3) * 100))  # Convert to int
    verificar_datos(self)

def mostrar_datos_yahoo(self, df):
    #print("Mostrando datos de Yahoo:", df)
    self.yahoo_df = df
    self.trabajadores_finalizados += 1  # Incrementar contador
    self.statusLabel.setText(f"{self.trabajadores_finalizados}/3 búsquedas completadas")
    self.progressBar.setValue(int((self.trabajadores_finalizados / 3) * 100))  # Convert to int
    verificar_datos(self)

def mostrar_datos_macrotrends(self, df):
    #print("Mostrando datos de Macrotrends:", df)
    self.macrotrends_df = df
    self.trabajadores_finalizados += 1  # Incrementar contador
    self.statusLabel.setText(f"{self.trabajadores_finalizados}/3 búsquedas completadas")
    self.progressBar.setValue(int((self.trabajadores_finalizados / 3) * 100))  # Convert to int
    verificar_datos(self)

def verificar_datos(self):
    # Solo proceder cuando los tres trabajadores hayan terminado
    if self.trabajadores_finalizados < 3:
        return

    # Una vez completada la búsqueda, hacer visible el frame si existe
    if hasattr(self, 'saved_filter_frame') and self.saved_filter_frame is not None:
        self.saved_filter_frame.setVisible(True)

    mostrar_todos_los_datos(self)
    self.statusLabel.setText("Búsqueda completada")
    self.progressBar.setVisible(False)  # Hide the progress bar after completion

def mostrar_todos_los_datos(self):
    print("Mostrando todos los datos")
    self.lineEdit.setEnabled(True)
    self.pushButton.setEnabled(True)
    
    self.df = self.google_df if not self.google_df.empty else pd.DataFrame()
    self.df_yahoo = self.yahoo_df if not self.yahoo_df.empty else pd.DataFrame()
    self.df_macrotrends = self.macrotrends_df if not self.macrotrends_df.empty else pd.DataFrame()
    
    # Definir self.data_frames
    self.data_frames = {
        'balance': {
            'google': filtrar_datos_google(self.df, 'balance') if not self.df.empty else pd.DataFrame(),
            'yahoo': filtrar_datos_yahoo(self.lineEdit.text().strip(), 'balance') if not self.df_yahoo.empty else pd.DataFrame(),
            'macrotrends': filtrar_datos_macrotrends(self.df_macrotrends, 'balance') if not self.df_macrotrends.empty else pd.DataFrame()
        },
        'cashflow': {
            'google': filtrar_datos_google(self.df, 'cashflow') if not self.df.empty else pd.DataFrame(),
            'yahoo': filtrar_datos_yahoo(self.lineEdit.text().strip(), 'cashflow') if not self.df_yahoo.empty else pd.DataFrame(),
            'macrotrends': filtrar_datos_macrotrends(self.df_macrotrends, 'cashflow') if not self.df_macrotrends.empty else pd.DataFrame()
        },
        'income': {
            'google': filtrar_datos_google(self.df, 'income') if not self.df.empty else pd.DataFrame(),
            'yahoo': filtrar_datos_yahoo(self.lineEdit.text().strip(), 'income') if not self.df_yahoo.empty else pd.DataFrame(),
            'macrotrends': filtrar_datos_macrotrends(self.df_macrotrends, 'income') if not self.df_macrotrends.empty else pd.DataFrame()
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
    
    if not self.data_frames['balance']['google'].empty:
        model_google = PandasModel(self.data_frames['balance']['google'])
        self.tableView.setModel(model_google)
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    if not self.data_frames['balance']['yahoo'].empty:
        model_yahoo = PandasModel(self.data_frames['balance']['yahoo'])
        self.tableView_3.setModel(model_yahoo)
        self.tableView_3.resizeColumnsToContents()
        self.tableView_3.horizontalHeader().setStretchLastSection(True)
        self.tableView_3.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    if not self.data_frames['balance']['macrotrends'].empty:
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
    
    google_df = self.df if not self.df.empty else None
    yahoo_df = self.df_yahoo if not self.df_yahoo.empty else None
    macrotrends_df = self.df_macrotrends if not self.df_macrotrends.empty else None
    ticker = self.lineEdit.text().strip().upper()
    
    # Call the export function from import_export_handler
    try:
        if google_df is not None or yahoo_df is not None or macrotrends_df is not None:
            export_to_sqlite(google_df, yahoo_df, macrotrends_df, ticker)
            export_to_excel(google_df, yahoo_df, macrotrends_df, ticker)
    except Exception as e:
        QtWidgets.QMessageBox.warning(None, "Exportar", f"Error al exportar datos: {str(e)}")
        return
    
    QtWidgets.QMessageBox.information(None, "Exportar", "Datos exportados exitosamente.")

def importar_datos(self):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Importar archivo", "", "Excel Files (*.xlsx);;SQLite Files (*.sqlite)", options=options)
    if filename:
        try:
            if filename.endswith('.xlsx'):
                google_df, yahoo_df, macrotrends_df = import_from_excel(filename)
            elif filename.endswith('.sqlite'):
                google_df, yahoo_df, macrotrends_df = import_from_sqlite(filename)
            else:
                raise ValueError("Formato de archivo no soportado.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "Importar", f"Error al importar archivo: {str(e)}")
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
        
        # Hacer visibles y habilitar las casillas de búsqueda
        self.search_google.setVisible(True)
        self.search_yahoo.setVisible(True)
        self.search_macrotrends.setVisible(True)
        self.search_google.setEnabled(True)
        self.search_yahoo.setEnabled(True)
        self.search_macrotrends.setEnabled(True)
        
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
        
        # Actualizar el mensaje de estado para indicar que los datos se han cargado exitosamente
        self.statusLabel.setText("Datos cargados con éxito")
        
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
    
