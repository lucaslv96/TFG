from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import pandas as pd
import os
from model.data_manager import filtrar_datos_google, filtrar_datos_yahoo, filtrar_datos_macrotrends, PandasModel, filtrar_datos_yahoo_importados
from model.data_import_export import export_to_excel, import_from_excel, export_to_sqlite, import_from_sqlite
from scrapers.macrotrends_scraper import MacrotrendsScraper
from scrapers.yahoo_finance_scraper import YahooFinanceScraper
from controller.datos_equivalentes_controller import mostrar_datos_equivalentes


class Worker(QThread):
    result = pyqtSignal(pd.DataFrame)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker

    def run(self):
        from scrapers.google_finance_scraper import GoogleFinanceScraper
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


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

_ALT_BUTTON_STYLE = """
    background-color: #FF0000;
    color: white;
    font-weight: bold;
    border-radius: 3px;
    padding: 5px;
"""


def _set_table_model(table_view, df):
    """Asigna un PandasModel a table_view y configura el encabezado en modo stretch."""
    table_view.setModel(PandasModel(df))
    table_view.resizeColumnsToContents()
    table_view.horizontalHeader().setStretchLastSection(True)
    table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


def _on_worker_result(self, df, attr):
    """Recibe el DataFrame de un worker, actualiza el estado y comprueba si todos terminaron."""
    setattr(self, f'{attr}_df', df)
    self.trabajadores_finalizados += 1
    self.statusLabel.setText(f"{self.trabajadores_finalizados}/3 búsquedas completadas")
    self.progressBar.setValue(int((self.trabajadores_finalizados / 3) * 100))
    verificar_datos(self)


def _mostrar_interfaz_alt(self, source, df, text, search_func, table_view):
    """Crea o muestra/oculta la interfaz de búsqueda alternativa de una fuente."""
    label_attr  = f'{source}_alt_label'
    edit_attr   = f'{source}_alt_edit'
    button_attr = f'{source}_alt_button'

    if df.empty:
        if not hasattr(self, label_attr):
            label  = QtWidgets.QLabel(text, self.tab)
            label.setStyleSheet("color: #FF0000; font-weight: bold;")
            edit   = QtWidgets.QLineEdit(self.tab)
            edit.setStyleSheet("border: 1px solid #FF0000;")
            button = QtWidgets.QPushButton("Buscar", self.tab)
            button.setStyleSheet(_ALT_BUTTON_STYLE)
            button.clicked.connect(lambda: search_func(self, edit.text()))

            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(label)
            layout.addWidget(edit)
            layout.addWidget(button)

            index = self.tabLayout.indexOf(table_view)
            self.tabLayout.insertLayout(index, layout)

            setattr(self, label_attr,             label)
            setattr(self, edit_attr,              edit)
            setattr(self, button_attr,            button)
            setattr(self, f'{source}_alt_layout', layout)
        else:
            getattr(self, label_attr).setVisible(True)
            getattr(self, edit_attr).setVisible(True)
            getattr(self, button_attr).setVisible(True)
    elif hasattr(self, label_attr):
        getattr(self, label_attr).setVisible(False)
        getattr(self, edit_attr).setVisible(False)
        getattr(self, button_attr).setVisible(False)


def _actualizar_etiquetas(self, company_name):
    """Actualiza las etiquetas de fuente con el nombre de empresa si está disponible."""
    _translate = QtCore.QCoreApplication.translate
    sources = [
        (self.df,             self.label_2, "Datos de Google Finance"),
        (self.df_yahoo,       self.label_4, "Datos de Yahoo Finance"),
        (self.df_macrotrends, self.label_5, "Datos de Macrotrends"),
    ]
    for df, label, base in sources:
        text = f"{base} - {company_name}" if (company_name and not df.empty) else base
        label.setText(_translate("MainWindow", text))

    any_data = not self.df.empty or not self.df_yahoo.empty or not self.df_macrotrends.empty
    eq_text = f"Datos Equivalentes - {company_name}" if (company_name and any_data) else "Datos Equivalentes"
    self.label_equivalentes.setText(_translate("MainWindow", eq_text))


def _construir_data_frames(self, ticker=None, importados=False):
    """Construye self.data_frames filtrando cada fuente por tipo (balance/cashflow/income)."""
    self.data_frames = {}
    for dt in ('balance', 'cashflow', 'income'):
        if importados:
            yahoo_df = filtrar_datos_yahoo_importados(self.df_yahoo, dt) if not self.df_yahoo.empty else pd.DataFrame()
        else:
            yahoo_df = filtrar_datos_yahoo(ticker, dt) if (not self.df_yahoo.empty and ticker) else pd.DataFrame()

        self.data_frames[dt] = {
            'google':      filtrar_datos_google(self.df, dt)                  if not self.df.empty else pd.DataFrame(),
            'yahoo':       yahoo_df,
            'macrotrends': filtrar_datos_macrotrends(self.df_macrotrends, dt) if not self.df_macrotrends.empty else pd.DataFrame(),
        }


def _get_company_name(ticker):
    """Obtiene el nombre de la empresa desde Yahoo Finance; devuelve None si no está disponible."""
    try:
        name = YahooFinanceScraper().get_company_name(ticker)
        return name if name and name != "Nombre de la empresa no disponible" else None
    except Exception:
        return None


# ------------------------------------------------------------------
# Funciones principales
# ------------------------------------------------------------------

def buscar_datos(self):
    ticker = self.lineEdit.text().strip().upper()
    if ticker:
        self.statusLabel.setText("Estado: Buscando datos...")
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        ocultar_interfaces_alternativas(self)

        self.search_google.setVisible(True)
        self.search_yahoo.setVisible(True)
        self.search_macrotrends.setVisible(True)
        self.search_google.setEnabled(True)
        self.search_yahoo.setEnabled(True)
        self.search_macrotrends.setEnabled(True)

        self.tableView.setModel(PandasModel(pd.DataFrame()))
        self.tableView_3.setModel(PandasModel(pd.DataFrame()))
        self.tableView_4.setModel(PandasModel(pd.DataFrame()))

        self.tableView_balance.setModel(PandasModel(pd.DataFrame()))
        self.tableView_cash_flow.setModel(PandasModel(pd.DataFrame()))
        self.tableView_income_statement.setModel(PandasModel(pd.DataFrame()))

        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("MainWindow", "Datos de Google Finance"))
        self.label_4.setText(_translate("MainWindow", "Datos de Yahoo Finance"))
        self.label_5.setText(_translate("MainWindow", "Datos de Macrotrends"))
        self.label_equivalentes.setText(_translate("MainWindow", "Datos Equivalentes"))
        self.label_balance.setText(_translate("MainWindow", "Datos de Balance"))
        self.label_cash_flow.setText(_translate("MainWindow", "Datos de Flujo de Caja"))
        self.label_income_statement.setText(_translate("MainWindow", "Cuenta de Pérdidas y Ganancias"))

        # Ocultar temporalmente el selector de años durante la búsqueda
        self.saved_filter_frame = None
        for i in range(self.tab_2_layout.count()):
            item = self.tab_2_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QtWidgets.QFrame):
                self.saved_filter_frame = item.widget()
                self.saved_filter_frame.setVisible(False)
                break

        if hasattr(self, 'year_filter_combobox') and self.year_filter_combobox is not None:
            self.year_filter_combobox.setVisible(False)

        if hasattr(self, 'year_filter_label') and self.year_filter_label is not None:
            self.year_filter_label.setVisible(False)

        self.tableView.viewport().update()
        self.tableView_3.viewport().update()
        self.tableView_4.viewport().update()
        self.tableView_balance.viewport().update()
        self.tableView_cash_flow.viewport().update()
        self.tableView_income_statement.viewport().update()

        self.lineEdit.setEnabled(False)
        self.pushButton.setEnabled(False)

        self.google_df = pd.DataFrame()
        self.yahoo_df = pd.DataFrame()
        self.macrotrends_df = pd.DataFrame()

        self.trabajadores_finalizados = 0

        self.balanceButton.setVisible(False)
        self.flujoCajaButton.setVisible(False)
        self.perdidasGananciasButton.setVisible(False)

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
    _on_worker_result(self, df, 'google')


def mostrar_datos_yahoo(self, df):
    _on_worker_result(self, df, 'yahoo')


def mostrar_datos_macrotrends(self, df):
    _on_worker_result(self, df, 'macrotrends')


def verificar_datos(self):
    if self.trabajadores_finalizados < 3:
        return

    mostrar_interfaces_alternativas(self)

    if hasattr(self, 'saved_filter_frame') and self.saved_filter_frame is not None:
        self.saved_filter_frame.setVisible(True)

    mostrar_todos_los_datos(self)
    self.statusLabel.setText("Búsqueda completada")
    self.progressBar.setVisible(False)


def mostrar_interfaces_alternativas(self):
    """Muestra las interfaces de búsqueda alternativa solo después de completar toda la búsqueda."""
    _mostrar_interfaz_alt(
        self, 'google', self.google_df,
        "No se encontraron datos para Google Finance. Intente con otro ticker:",
        buscar_google_alternativo, self.tableView,
    )
    _mostrar_interfaz_alt(
        self, 'yahoo', self.yahoo_df,
        "No se encontraron datos para Yahoo Finance. Intente con otro ticker:",
        buscar_yahoo_alternativo, self.tableView_3,
    )
    _mostrar_interfaz_alt(
        self, 'macrotrends', self.macrotrends_df,
        "No se encontraron datos para Macrotrends. Intente con otro ticker:",
        buscar_macrotrends_alternativo, self.tableView_4,
    )


def mostrar_todos_los_datos(self):
    self.lineEdit.setEnabled(True)
    self.pushButton.setEnabled(True)

    self.df             = self.google_df      if hasattr(self, 'google_df')      and not self.google_df.empty      else pd.DataFrame()
    self.df_yahoo       = self.yahoo_df       if hasattr(self, 'yahoo_df')       and not self.yahoo_df.empty       else pd.DataFrame()
    self.df_macrotrends = self.macrotrends_df if hasattr(self, 'macrotrends_df') and not self.macrotrends_df.empty else pd.DataFrame()

    ticker = self.lineEdit.text().strip()
    _construir_data_frames(self, ticker=ticker, importados=False)

    self.balanceButton.setVisible(True)
    self.flujoCajaButton.setVisible(True)
    self.perdidasGananciasButton.setVisible(True)

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
        _set_table_model(self.tableView, self.data_frames['balance']['google'])

    if not self.data_frames['balance']['yahoo'].empty:
        _set_table_model(self.tableView_3, self.data_frames['balance']['yahoo'])

    if not self.data_frames['balance']['macrotrends'].empty:
        _set_table_model(self.tableView_4, self.data_frames['balance']['macrotrends'])

    _actualizar_etiquetas(self, _get_company_name(ticker))

    mostrar_datos_equivalentes(self)

    self.search_google.setVisible(True)
    self.search_yahoo.setVisible(True)
    self.search_macrotrends.setVisible(True)


def mostrar_datos_filtrados(self, data_type):
    if self.df.empty:
        return
    _set_table_model(self.tableView, filtrar_datos_google(self.df, data_type))
    display_selected_data(self, data_type)


def mostrar_datos_filtrados_macrotrends(self, data_type):
    if self.df_macrotrends.empty:
        return
    _set_table_model(self.tableView_4, filtrar_datos_macrotrends(self.df_macrotrends, data_type))


def mostrar_balance(self):
    mostrar_datos_filtrados(self, 'balance')


def display_selected_data(self, data_type):
    if self.df_yahoo.empty:
        return
    _set_table_model(self.tableView_3, filtrar_datos_yahoo(self.lineEdit.text().strip(), data_type))


def exportar_datos(self):
    if not hasattr(self, 'df') or self.df.empty:
        QtWidgets.QMessageBox.warning(None, "Exportar", "No hay datos para exportar.")
        return

    google_df = self.df if not self.df.empty else None

    yahoo_df = self.df_yahoo if not self.df_yahoo.empty else None
    if yahoo_df is not None and 'Datos' in yahoo_df.columns:
        needs_prefix = not any(
            str(val).startswith(('Income_', 'Cashflow_', 'Balance_'))
            for val in yahoo_df['Datos'].head(10)
        )
        if needs_prefix:
            ticker = self.lineEdit.text().strip()
            yahoo_df = YahooFinanceScraper().get_combined_financial_data(ticker)

    macrotrends_df = self.df_macrotrends if not self.df_macrotrends.empty else None
    ticker = self.lineEdit.text().strip().upper()

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
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Importar archivo", "",
        "Excel Files (*.xlsx);;SQLite Files (*.sqlite)", options=options,
    )
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

        self.df             = google_df      if not google_df.empty      else pd.DataFrame()
        self.df_yahoo       = yahoo_df       if not yahoo_df.empty       else pd.DataFrame()
        self.df_macrotrends = macrotrends_df if not macrotrends_df.empty else pd.DataFrame()

        ticker = os.path.basename(filename).split('.')[0]

        _construir_data_frames(self, importados=True)

        if not self.data_frames['balance']['google'].empty:
            _set_table_model(self.tableView, self.data_frames['balance']['google'])

        if not self.data_frames['balance']['yahoo'].empty:
            _set_table_model(self.tableView_3, self.data_frames['balance']['yahoo'])

        if not self.data_frames['balance']['macrotrends'].empty:
            _set_table_model(self.tableView_4, self.data_frames['balance']['macrotrends'])

        self.search_google.setVisible(True)
        self.search_yahoo.setVisible(True)
        self.search_macrotrends.setVisible(True)
        self.search_google.setEnabled(True)
        self.search_yahoo.setEnabled(True)
        self.search_macrotrends.setEnabled(True)

        self.balanceButton.setVisible(True)
        self.flujoCajaButton.setVisible(True)
        self.perdidasGananciasButton.setVisible(True)

        try:
            self.balanceButton.clicked.disconnect()
            self.flujoCajaButton.clicked.disconnect()
            self.perdidasGananciasButton.clicked.disconnect()
        except TypeError:
            pass

        self.balanceButton.clicked.connect(lambda: mostrar_datos_filtrados_importados(self, 'balance'))
        self.flujoCajaButton.clicked.connect(lambda: mostrar_datos_filtrados_importados(self, 'cashflow'))
        self.perdidasGananciasButton.clicked.connect(lambda: mostrar_datos_filtrados_importados(self, 'income'))

        _actualizar_etiquetas(self, _get_company_name(ticker))

        self.statusLabel.setText("Datos cargados con éxito")
        self.trabajadores_finalizados = 3

        mostrar_datos_equivalentes(self)

        if hasattr(self, 'saved_filter_frame') and self.saved_filter_frame is not None:
            self.saved_filter_frame.setVisible(True)

        if hasattr(self, 'year_filter_combobox') and self.year_filter_combobox is not None:
            self.year_filter_combobox.setVisible(True)

        if hasattr(self, 'year_filter_label') and self.year_filter_label is not None:
            self.year_filter_label.setVisible(True)

        QtWidgets.QMessageBox.information(None, "Importar", "Datos importados exitosamente.")


def mostrar_datos_filtrados_importados(self, data_type):
    """Muestra datos filtrados de archivos importados."""
    if not hasattr(self, 'data_frames') or data_type not in self.data_frames:
        return

    if not self.data_frames[data_type]['google'].empty:
        _set_table_model(self.tableView, self.data_frames[data_type]['google'])

    yahoo_df_filtrado = self.data_frames[data_type]['yahoo']
    if not yahoo_df_filtrado.empty:
        _set_table_model(self.tableView_3, yahoo_df_filtrado)
    elif hasattr(self, 'df_yahoo') and not self.df_yahoo.empty:
        _set_table_model(self.tableView_3, self.df_yahoo.head(10))

    if not self.data_frames[data_type]['macrotrends'].empty:
        _set_table_model(self.tableView_4, self.data_frames[data_type]['macrotrends'])

    mostrar_datos_equivalentes(self)


# ------------------------------------------------------------------
# Búsqueda con tickers alternativos
# ------------------------------------------------------------------

def buscar_google_alternativo(self, ticker):
    if not ticker.strip():
        return
    self.statusLabel.setText("Buscando datos de Google Finance...")
    try:
        self.google_alt_worker = Worker(ticker.strip())
        self.google_alt_worker.result.connect(lambda df: actualizar_datos_google(self, df))
        if hasattr(self, 'google_alt_button'):
            self.google_alt_button.setEnabled(False)
            self.google_alt_button.setText("Buscando...")
        self.google_alt_worker.start()
    except Exception as e:
        self.statusLabel.setText(f"Error al buscar: {str(e)}")
        if hasattr(self, 'google_alt_button'):
            self.google_alt_button.setEnabled(True)
            self.google_alt_button.setText("Buscar")


def buscar_yahoo_alternativo(self, ticker):
    if not ticker.strip():
        return
    self.statusLabel.setText("Buscando datos de Yahoo Finance...")
    try:
        self.yahoo_alt_worker = YahooWorker(ticker.strip(), 'balance')
        self.yahoo_alt_worker.result.connect(lambda df: actualizar_datos_yahoo(self, df))
        if hasattr(self, 'yahoo_alt_button'):
            self.yahoo_alt_button.setEnabled(False)
            self.yahoo_alt_button.setText("Buscando...")
        self.yahoo_alt_worker.start()
    except Exception as e:
        self.statusLabel.setText(f"Error al buscar: {str(e)}")
        if hasattr(self, 'yahoo_alt_button'):
            self.yahoo_alt_button.setEnabled(True)
            self.yahoo_alt_button.setText("Buscar")


def buscar_macrotrends_alternativo(self, ticker):
    if not ticker.strip():
        return
    self.statusLabel.setText("Buscando datos de Macrotrends...")
    try:
        self.macrotrends_alt_worker = MacrotrendsWorker(ticker.strip())
        self.macrotrends_alt_worker.result.connect(lambda df: actualizar_datos_macrotrends(self, df))
        if hasattr(self, 'macrotrends_alt_button'):
            self.macrotrends_alt_button.setEnabled(False)
            self.macrotrends_alt_button.setText("Buscando...")
        self.macrotrends_alt_worker.start()
    except Exception as e:
        self.statusLabel.setText(f"Error al buscar: {str(e)}")
        if hasattr(self, 'macrotrends_alt_button'):
            self.macrotrends_alt_button.setEnabled(True)
            self.macrotrends_alt_button.setText("Buscar")


# ------------------------------------------------------------------
# Actualización con resultados de búsqueda alternativa
# ------------------------------------------------------------------

def actualizar_datos_google(self, df):
    try:
        if hasattr(self, 'google_alt_button'):
            self.google_alt_button.setEnabled(True)
            self.google_alt_button.setText("Buscar")

        if not df.empty:
            self.google_df = df

            if hasattr(self, 'data_frames'):
                self.data_frames['balance']['google']  = filtrar_datos_google(df, 'balance')
                self.data_frames['cashflow']['google'] = filtrar_datos_google(df, 'cashflow')
                self.data_frames['income']['google']   = filtrar_datos_google(df, 'income')

                filtered_df = filtrar_datos_google(df, 'balance')
                if not filtered_df.empty:
                    _set_table_model(self.tableView, filtered_df)

            if hasattr(self, 'google_alt_label'):
                self.google_alt_label.setVisible(False)
                self.google_alt_edit.setVisible(False)
                self.google_alt_button.setVisible(False)

            mostrar_datos_equivalentes(self)
            self.statusLabel.setText("Datos de Google Finance actualizados")
        else:
            self.statusLabel.setText("No se encontraron datos para el ticker alternativo de Google Finance")
    except Exception as e:
        self.statusLabel.setText(f"Error: {str(e)}")


def actualizar_datos_yahoo(self, df):
    try:
        if hasattr(self, 'yahoo_alt_button'):
            self.yahoo_alt_button.setEnabled(True)
            self.yahoo_alt_button.setText("Buscar")

        if not df.empty:
            self.yahoo_df = df
            self.yahoo_alt_ticker = self.yahoo_alt_edit.text().strip() if hasattr(self, 'yahoo_alt_edit') else ""

            if hasattr(self, 'data_frames'):
                self.data_frames['balance']['yahoo']  = filtrar_datos_yahoo(self.yahoo_alt_ticker, 'balance')
                self.data_frames['cashflow']['yahoo'] = filtrar_datos_yahoo(self.yahoo_alt_ticker, 'cashflow')
                self.data_frames['income']['yahoo']   = filtrar_datos_yahoo(self.yahoo_alt_ticker, 'income')

                filtered_df = filtrar_datos_yahoo(self.yahoo_alt_ticker, 'balance')
                if not filtered_df.empty:
                    _set_table_model(self.tableView_3, filtered_df)

            if hasattr(self, 'yahoo_alt_label'):
                self.yahoo_alt_label.setVisible(False)
                self.yahoo_alt_edit.setVisible(False)
                self.yahoo_alt_button.setVisible(False)

            mostrar_datos_equivalentes(self)
            self.statusLabel.setText("Datos de Yahoo Finance actualizados")
        else:
            self.statusLabel.setText("No se encontraron datos para el ticker alternativo de Yahoo Finance")
    except Exception as e:
        self.statusLabel.setText(f"Error: {str(e)}")


def actualizar_datos_macrotrends(self, df):
    try:
        if hasattr(self, 'macrotrends_alt_button'):
            self.macrotrends_alt_button.setEnabled(True)
            self.macrotrends_alt_button.setText("Buscar")

        if not df.empty:
            self.macrotrends_df = df

            if hasattr(self, 'data_frames'):
                self.data_frames['balance']['macrotrends']  = filtrar_datos_macrotrends(df, 'balance')
                self.data_frames['cashflow']['macrotrends'] = filtrar_datos_macrotrends(df, 'cashflow')
                self.data_frames['income']['macrotrends']   = filtrar_datos_macrotrends(df, 'income')

                filtered_df = filtrar_datos_macrotrends(df, 'balance')
                if not filtered_df.empty:
                    _set_table_model(self.tableView_4, filtered_df)

            if hasattr(self, 'macrotrends_alt_label'):
                self.macrotrends_alt_label.setVisible(False)
                self.macrotrends_alt_edit.setVisible(False)
                self.macrotrends_alt_button.setVisible(False)

            mostrar_datos_equivalentes(self)
            self.statusLabel.setText("Datos de Macrotrends actualizados")
        else:
            self.statusLabel.setText("No se encontraron datos para el ticker alternativo de Macrotrends")
    except Exception as e:
        self.statusLabel.setText(f"Error: {str(e)}")


def ocultar_interfaces_alternativas(self):
    """Oculta todas las interfaces de búsqueda alternativa."""
    for source in ('google', 'yahoo', 'macrotrends'):
        for suffix in ('_alt_label', '_alt_edit', '_alt_button'):
            widget = getattr(self, f'{source}{suffix}', None)
            if widget is not None:
                widget.setVisible(False)
    if hasattr(self, 'tab') and self.tab is not None:
        self.tab.update()
