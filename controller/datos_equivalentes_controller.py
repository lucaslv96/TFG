import re  # Importar la biblioteca re
from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
from model.pandas_model import PandasModel  # Import PandasModel from the new module
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from model.data_manager import DataManager

class ChartWindow(QtWidgets.QWidget):
    def __init__(self, data, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        self.data = data
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.year_selector = QtWidgets.QComboBox(self)
        self.year_selector.addItems(["Todos los años", "2023", "2022", "2021", "2020"])
        self.year_selector.currentIndexChanged.connect(self.update_chart)
        layout.addWidget(self.year_selector)

        figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        layout.addWidget(self.canvas)

        self.update_chart()

    def update_chart(self):
        selected_year = self.year_selector.currentText()
        self.ax.clear()

        if selected_year == "Todos los años":
            self.ax.plot(self.data['Year'], pd.to_numeric(self.data['Google']), label='Google Finance', marker='o')
            self.ax.plot(self.data['Year'], pd.to_numeric(self.data['Yahoo']), label='Yahoo Finance', marker='o')
            self.ax.plot(self.data['Year'], pd.to_numeric(self.data['Macrotrends']), label='Macrotrends', marker='o')
        else:
            year_data = self.data[self.data['Year'] == selected_year]
            self.ax.plot(year_data['Year'], pd.to_numeric(year_data['Google']), label='Google Finance', marker='o')
            self.ax.plot(year_data['Year'], pd.to_numeric(year_data['Yahoo']), label='Yahoo Finance', marker='o')
            self.ax.plot(year_data['Year'], pd.to_numeric(year_data['Macrotrends']), label='Macrotrends', marker='o')

        self.ax.set_title(self.windowTitle())
        self.ax.set_xlabel('Year')
        self.ax.set_ylabel('Value')
        self.ax.legend()
        self.canvas.draw()

# Definir constantes para los nombres de las columnas
GOOGLE_FINANCE = "Google Finance"
MACROTRENDS = "Macrotrends"
YAHOO_FINANCE = "Yahoo Finance"
TIPO = "Tipo"
GOOGLE_INICIAL = "Google Inicial"
MACROTRENDS_INICIAL = "Macrotrends Inicial"
YAHOO_INICIAL = "Yahoo Inicial"
RELACION = "Relación"

# Definir constante para el patrón de expresión regular
NON_NUMERIC_PATTERN = r'[^\d.-]'

def mostrar_datos_equivalentes(self):
    data_manager = DataManager()
    query = '''
        SELECT 
            google_finance.dato_actual AS google,
            macrotrends.dato_actual AS macrotrends, 
            yahoo_finance.dato_actual AS yahoo,
            equivalencias.tipo_dato AS tipo,
            google_finance.dato_inicial AS google_inicial,
            macrotrends.dato_inicial AS macrotrends_inicial,
            yahoo_finance.dato_inicial AS yahoo_inicial
        FROM equivalencias
        JOIN google_finance ON equivalencias.google_finance_id = google_finance.id
        JOIN macrotrends ON equivalencias.macrotrends_id = macrotrends.id
        JOIN yahoo_finance ON equivalencias.yahoo_finance_id = yahoo_finance.id
        WHERE google_finance.dato_actual IS NOT NULL
    '''
    datos_equivalentes = data_manager.fetch_data(query)

    if not datos_equivalentes:
        datos_equivalentes = [("Test Google", "Test Macrotrends", "Test Yahoo", "test", "Test Google Inicial", "Test Macrotrends Inicial", "Test Yahoo Inicial")]

    # Crear DataFrame para los datos equivalentes
    df_equivalentes = pd.DataFrame(datos_equivalentes, columns=[GOOGLE_FINANCE, MACROTRENDS, YAHOO_FINANCE, TIPO, GOOGLE_INICIAL, MACROTRENDS_INICIAL, YAHOO_INICIAL])

    if df_equivalentes.empty:
        df_equivalentes = pd.DataFrame([["Test Google", "Test Macrotrends", "Test Yahoo", "test", "Test Google Inicial", "Test Macrotrends Inicial", "Test Yahoo Inicial"]],
                                       columns=[GOOGLE_FINANCE, MACROTRENDS, YAHOO_FINANCE, TIPO, GOOGLE_INICIAL, MACROTRENDS_INICIAL, YAHOO_INICIAL])

    # Separar los datos por tipo
    balance_df = df_equivalentes[df_equivalentes[TIPO] == "balance"].drop(columns=[TIPO])
    cashflow_df = df_equivalentes[df_equivalentes[TIPO] == "cashflow"].drop(columns=[TIPO])
    income_df = df_equivalentes[df_equivalentes[TIPO] == "income"].drop(columns=[TIPO])

    # Interleave the values from Google, Yahoo, and Macrotrends for balance
    interleaved_balance = []
    for i in range(len(balance_df)):
        google_value = balance_df.iloc[i][GOOGLE_FINANCE]
        yahoo_value = balance_df.iloc[i][YAHOO_FINANCE]
        macrotrends_value = balance_df.iloc[i][MACROTRENDS]
        google_inicial = balance_df.iloc[i][GOOGLE_INICIAL]
        yahoo_inicial = balance_df.iloc[i][YAHOO_INICIAL]
        macrotrends_inicial = balance_df.iloc[i][MACROTRENDS_INICIAL]

        google_row = ["Google", google_value, f"Yahoo: {yahoo_value}, Macrotrends: {macrotrends_value}"] + self.data_frames['balance']['google'].loc[self.data_frames['balance']['google']['Datos'] == google_inicial].values.flatten().tolist()[1:]
        yahoo_row = ["Yahoo", yahoo_value, f"Google: {google_value}, Macrotrends: {macrotrends_value}"] + self.data_frames['balance']['yahoo'].loc[self.data_frames['balance']['yahoo']['Datos'] == yahoo_inicial].values.flatten().tolist()[1:]
        macrotrends_row = ["Macrotrends", macrotrends_value, f"Google: {google_value}, Yahoo: {yahoo_value}"] + self.data_frames['balance']['macrotrends'].loc[self.data_frames['balance']['macrotrends']['Datos'] == macrotrends_inicial].values.flatten().tolist()[1:]

        interleaved_balance.extend([google_row, yahoo_row, macrotrends_row, [""] * 7])  # Add blank row

    interleaved_balance_df = pd.DataFrame(interleaved_balance, columns=["Fuente", "Datos", RELACION, "2023", "2022", "2021", "2020"])
    interleaved_balance_df = interleaved_balance_df[:-1]  # Remove the last row

    # Interleave the values from Google, Yahoo, and Macrotrends for cashflow
    interleaved_cashflow = []
    for i in range(len(cashflow_df)):
        google_value = cashflow_df.iloc[i][GOOGLE_FINANCE]
        yahoo_value = cashflow_df.iloc[i][YAHOO_FINANCE]
        macrotrends_value = cashflow_df.iloc[i][MACROTRENDS]
        google_inicial = cashflow_df.iloc[i][GOOGLE_INICIAL]
        yahoo_inicial = cashflow_df.iloc[i][YAHOO_INICIAL]
        macrotrends_inicial = cashflow_df.iloc[i][MACROTRENDS_INICIAL]

        google_row = ["Google", google_value, f"Yahoo: {yahoo_value}, Macrotrends: {macrotrends_value}"] + self.data_frames['cashflow']['google'].loc[self.data_frames['cashflow']['google']['Datos'] == google_inicial].values.flatten().tolist()[1:]
        yahoo_row = ["Yahoo", yahoo_value, f"Google: {google_value}, Macrotrends: {macrotrends_value}"] + self.data_frames['cashflow']['yahoo'].loc[self.data_frames['cashflow']['yahoo']['Datos'] == yahoo_inicial].values.flatten().tolist()[1:]
        macrotrends_row = ["Macrotrends", macrotrends_value, f"Google: {google_value}, Yahoo: {yahoo_value}"] + self.data_frames['cashflow']['macrotrends'].loc[self.data_frames['cashflow']['macrotrends']['Datos'] == macrotrends_inicial].values.flatten().tolist()[1:]

        interleaved_cashflow.extend([google_row, yahoo_row, macrotrends_row, [""] * 7])  # Add blank row

    interleaved_cashflow_df = pd.DataFrame(interleaved_cashflow, columns=["Fuente", "Datos", RELACION, "2023", "2022", "2021", "2020"])
    interleaved_cashflow_df = interleaved_cashflow_df[:-1]  # Remove the last row

    # Interleave the values from Google, Yahoo, and Macrotrends for income
    interleaved_income = []
    for i in range(len(income_df)):
        google_value = income_df.iloc[i][GOOGLE_FINANCE]
        yahoo_value = income_df.iloc[i][YAHOO_FINANCE]
        macrotrends_value = income_df.iloc[i][MACROTRENDS]
        google_inicial = income_df.iloc[i][GOOGLE_INICIAL]
        yahoo_inicial = income_df.iloc[i][YAHOO_INICIAL]
        macrotrends_inicial = income_df.iloc[i][MACROTRENDS_INICIAL]

        google_row = ["Google", google_value, f"Yahoo: {yahoo_value}, Macrotrends: {macrotrends_value}"] + self.data_frames['income']['google'].loc[self.data_frames['income']['google']['Datos'] == google_inicial].values.flatten().tolist()[1:]
        yahoo_row = ["Yahoo", yahoo_value, f"Google: {google_value}, Macrotrends: {macrotrends_value}"] + self.data_frames['income']['yahoo'].loc[self.data_frames['income']['yahoo']['Datos'] == yahoo_inicial].values.flatten().tolist()[1:]
        macrotrends_row = ["Macrotrends", macrotrends_value, f"Google: {google_value}, Yahoo: {yahoo_value}"] + self.data_frames['income']['macrotrends'].loc[self.data_frames['income']['macrotrends']['Datos'] == macrotrends_inicial].values.flatten().tolist()[1:]

        interleaved_income.extend([google_row, yahoo_row, macrotrends_row, [""] * 7])  # Add blank row

    interleaved_income_df = pd.DataFrame(interleaved_income, columns=["Fuente", "Datos", RELACION, "2023", "2022", "2021", "2020"])
    interleaved_income_df = interleaved_income_df[:-1]  # Remove the last row

    # Mostrar los datos equivalentes en las tablas
    model_balance = PandasModel(interleaved_balance_df)
    self.tableView_balance.setModel(model_balance)
    self.tableView_balance.resizeColumnsToContents()
    self.tableView_balance.horizontalHeader().setStretchLastSection(True)
    self.tableView_balance.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    model_cashflow = PandasModel(interleaved_cashflow_df)
    self.tableView_cash_flow.setModel(model_cashflow)
    self.tableView_cash_flow.resizeColumnsToContents()
    self.tableView_cash_flow.horizontalHeader().setStretchLastSection(True)
    self.tableView_cash_flow.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    model_income = PandasModel(interleaved_income_df)
    self.tableView_income_statement.setModel(model_income)
    self.tableView_income_statement.resizeColumnsToContents()
    self.tableView_income_statement.horizontalHeader().setStretchLastSection(True)
    self.tableView_income_statement.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    # Alternar colores de fila para las filas relacionadas
    def set_row_color(table_view, model):
        for row in range(model.rowCount()):
            if row % 6 < 3:
                color = QtGui.QColor("#f0f0f0")
            else:
                color = QtGui.QColor("#ffffff")
            for col in range(model.columnCount()):
                table_view.model().setData(table_view.model().index(row, col), color, QtCore.Qt.BackgroundRole)

    set_row_color(self.tableView_balance, model_balance)
    set_row_color(self.tableView_cash_flow, model_cashflow)
    set_row_color(self.tableView_income_statement, model_income)

    # Initialize chart_windows list to keep references to chart windows
    self.chart_windows = []

    # Connect cell click event to show chart
    self.tableView_balance.clicked.connect(lambda index: show_chart(self, interleaved_balance_df, index))
    self.tableView_cash_flow.clicked.connect(lambda index: show_chart(self, interleaved_cashflow_df, index))
    self.tableView_income_statement.clicked.connect(lambda index: show_chart(self, interleaved_income_df, index))

def show_chart(self, df, index):
    row = index.row()
    data = df.iloc[row]
    title = data['Datos']
    related_data = data[RELACION].split(", ")
    
    def get_related_value(related_data, index):
        try:
            return related_data[index].split(": ")[1]
        except IndexError:
            return ""
    
    google_value = get_related_value(related_data, 0)
    yahoo_value = get_related_value(related_data, 1)
    macrotrends_value = get_related_value(related_data, 2)
    
    google_values = self.df.loc[self.df['Datos'] == google_value].values.flatten().tolist()[1:] if google_value and google_value != "None" else []
    yahoo_values = self.df_yahoo.loc[self.df_yahoo['Datos'] == yahoo_value].values.flatten().tolist()[1:] if yahoo_value and yahoo_value != "None" else []
    macrotrends_values = self.df_macrotrends.loc[self.df_macrotrends['Datos'] == macrotrends_value].values.flatten().tolist()[1:] if macrotrends_value and macrotrends_value != "None" else []
    
    max_length = max(len(google_values), len(yahoo_values), len(macrotrends_values))
    google_values += [0] * (max_length - len(google_values))
    yahoo_values += [0] * (max_length - len(yahoo_values))
    macrotrends_values += [0] * (max_length - len(macrotrends_values))
    
    # Limpiar los valores antes de convertir a números
    def clean_values(values):
        cleaned_values = []
        for value in values:
            value = str(value).replace('$', '').replace('.', '').replace(',', '.').replace('%', '').replace('á', '').strip()
            if value.endswith('M'):
                value = value[:-1] + '000000'  # Convertir millones a unidades
            cleaned_values.append(value)
        return cleaned_values
    
    google_values = clean_values(google_values)
    yahoo_values = clean_values(yahoo_values)
    macrotrends_values = clean_values(macrotrends_values)
    
    # Eliminar cualquier carácter no numérico restante
    google_values = [re.sub(NON_NUMERIC_PATTERN, '', value) for value in google_values]
    yahoo_values = [re.sub(NON_NUMERIC_PATTERN, '', value) for value in yahoo_values]
    macrotrends_values = [re.sub(NON_NUMERIC_PATTERN, '', value) for value in macrotrends_values]
    
    chart_data = pd.DataFrame({
        'Year': ['2023', '2022', '2021', '2020'][:max_length],
        'Google': pd.to_numeric(google_values),
        'Yahoo': pd.to_numeric(yahoo_values),
        'Macrotrends': pd.to_numeric(macrotrends_values)
    })
    
    # Buscar y agregar valores relacionados
    related_titles = [title]
    for related in related_data:
        related_value = related.split(": ")[1] if ": " in related else ""
        if related_value and related_value != "None":
            related_titles.append(related_value)
            related_google_values = self.df.loc[self.df['Datos'] == related_value].values.flatten().tolist()[1:]
            related_yahoo_values = self.df_yahoo.loc[self.df_yahoo['Datos'] == related_value].values.flatten().tolist()[1:]
            related_macrotrends_values = self.df_macrotrends.loc[self.df_macrotrends['Datos'] == related_value].values.flatten().tolist()[1:]
            
            max_length = max(len(related_google_values), len(related_yahoo_values), len(related_macrotrends_values))
            related_google_values += [0] * (max_length - len(related_google_values))
            related_yahoo_values += [0] * (max_length - len(related_yahoo_values))
            related_macrotrends_values += [0] * (max_length - len(related_macrotrends_values))
            
            # Limpiar los valores antes de convertir a números
            related_google_values = clean_values(related_google_values)
            related_yahoo_values = clean_values(related_yahoo_values)
            related_macrotrends_values = clean_values(related_macrotrends_values)
            
            # Eliminar cualquier carácter no numérico restante
            related_google_values = [re.sub(NON_NUMERIC_PATTERN, '', value) for value in related_google_values]
            related_yahoo_values = [re.sub(NON_NUMERIC_PATTERN, '', value) for value in related_yahoo_values]
            related_macrotrends_values = [re.sub(NON_NUMERIC_PATTERN, '', value) for value in related_macrotrends_values]
            
            related_chart_data = pd.DataFrame({
                'Year': ['2023', '2022', '2021', '2020'][:max_length],
                'Google': pd.to_numeric(related_google_values),
                'Yahoo': pd.to_numeric(related_yahoo_values),
                'Macrotrends': pd.to_numeric(related_macrotrends_values)
            })
            
            chart_data = pd.concat([chart_data, related_chart_data], ignore_index=True)
    
    # Cerrar la ventana de gráfico actual si existe
    if hasattr(self, 'current_chart_window') and self.current_chart_window is not None:
        self.current_chart_window.close()
    
    # Concatenar los títulos relacionados para el título de la gráfica
    chart_title = " - ".join(related_titles)
    
    chart_window = ChartWindow(chart_data, chart_title)
    chart_window.show()
    self.current_chart_window = chart_window  # Mantener una referencia a la ventana de gráfico actual
