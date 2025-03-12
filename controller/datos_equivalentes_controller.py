import re  # Importar la biblioteca re
from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
from model.data_manager import PandasModel  # Correct import
from model.database_manager import DataManager
from controller.chart_controller import ChartWindow

# Custom table model that supports group frames
class GroupedPandasModel(PandasModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(df, parent)
        self.group_rows = {}  # Dictionary to keep track of group boundaries
        self._setup_groups()
    
    def _setup_groups(self):
        # Identify groups: every 3 rows form a group, then there's an empty row
        row = 0
        while row < self.rowCount():
            if row + 2 < self.rowCount():
                # Mark these 3 rows as a group
                group_id = row // 4  # Each group has 3 data rows + 1 empty row
                for i in range(3):  # The 3 data rows in the group
                    self.group_rows[row + i] = group_id
            row += 4  # Move to next group (3 data rows + 1 empty row)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
            
        # For the empty rows, return empty string for display role
        if index.row() % 4 == 3 and role == QtCore.Qt.DisplayRole:  # Empty row
            return ""
            
        # For background colors, alternate between groups
        if role == QtCore.Qt.BackgroundRole:
            group_id = self.group_rows.get(index.row(), -1)
            if group_id != -1:
                # Alternate group colors
                if group_id % 2 == 0:
                    return QtGui.QColor("#F0F8FF")  # Light blue for even groups
                else:
                    return QtGui.QColor("#F0FFF0")  # Light green for odd groups
                    
        return super().data(index, role)

# Esta clase es para el modelo de tabla que soporta bordes de grupo
class GroupFrameDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(GroupFrameDelegate, self).__init__(parent)
        
    def paint(self, painter, option, index):
        super(GroupFrameDelegate, self).paint(painter, option, index)
        
        # Get the row and determine if it's the start, middle, or end of a group
        row = index.row()
        col = index.column()
        
        # Determine group boundaries (3 rows per group, followed by a blank row)
        group_start = (row // 4) * 4
        is_start_of_group = row == group_start
        is_end_of_group = row == group_start + 2
        is_in_group = row % 4 < 3  # First 3 rows of every 4 are part of a group
        
        if is_in_group:
            # Draw parts of the border based on position in group
            pen = QtGui.QPen(QtGui.QColor("#2c3e50"))  # Dark blue-gray border
            pen.setWidth(1)
            painter.setPen(pen)
            rect = option.rect
            
            # Left vertical border for all cells in the group
            if col == 0:
                painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())
                
            # Right vertical border for all cells in the group
            model = index.model()
            if col == model.columnCount() - 1:
                painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
                
            # Top border for first row in group
            if is_start_of_group:
                painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
                
            # Bottom border for last row in group
            if is_end_of_group:
                painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())

# Definir constantes para los nombres de las columnas
GOOGLE_FINANCE = "Google Finance"
MACROTRENDS = "Macrotrends"
YAHOO_FINANCE = "Yahoo Finance"
TIPO = "Tipo"
GOOGLE_INICIAL = "Google Inicial"
MACROTRENDS_INICIAL = "Macrotrends Inicial"
YAHOO_INICIAL = "Yahoo Inicial"

# Definir constante para el patrón de expresión regular
NON_NUMERIC_PATTERN = r'[^\d.-]'

def mostrar_datos_equivalentes(self):
    # Si hay un frame guardado de una búsqueda anterior, hacerlo visible nuevamente
    # Mostramos los controles si: 
    # 1. La búsqueda ha finalizado (trabajadores_finalizados = 3) o
    # 2. Estamos importando datos desde archivo (no hay trabajadores_finalizados pero hay datos)
    should_show_controls = (hasattr(self, 'trabajadores_finalizados') and self.trabajadores_finalizados == 3) or \
                           (hasattr(self, 'data_frames') and not all(df.empty for tipo in self.data_frames.values() 
                                                                   for df in tipo.values()))
    
    if hasattr(self, 'saved_filter_frame') and self.saved_filter_frame is not None:
        self.saved_filter_frame.setVisible(should_show_controls)
            
    # También revisar el combobox y label directamente
    if hasattr(self, 'year_filter_combobox') and self.year_filter_combobox is not None:
        self.year_filter_combobox.setVisible(should_show_controls)
        if hasattr(self, 'year_filter_label'):
            self.year_filter_label.setVisible(should_show_controls)
    
    # Verificar si el ComboBox de años ya existe, si no, crearlo
    if not hasattr(self, 'year_filter_combobox') or self.year_filter_combobox is None:
        # Crear un label con fuente más grande y en negrita
        self.year_filter_label = QtWidgets.QLabel("Filtrar años:", self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.year_filter_label.setFont(font)
        
        # Crear un ComboBox más grande y con mejor apariencia
        self.year_filter_combobox = QtWidgets.QComboBox(self.tab_2)
        self.year_filter_combobox.setMinimumHeight(30)  # Altura mínima para mejor visualización
        self.year_filter_combobox.setFont(QtGui.QFont("Arial", 10))
        self.year_filter_combobox.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: #f8f8f8;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #ccc;
            }
            QComboBox:hover {
                background-color: #e0e0e0;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ccc;
                selection-background-color: #4a90d9;
            }
        """)
        self.year_filter_combobox.addItems(["Todos los años", "2024", "2023", "2022", "2021"])
        self.year_filter_combobox.currentIndexChanged.connect(lambda: mostrar_datos_equivalentes(self))
        
        # Agregar un frame para contener el selector y darle un aspecto más destacado
        filter_frame = QtWidgets.QFrame(self.tab_2)
        filter_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        filter_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        filter_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")
        
        # Crear un layout para el frame
        filter_frame_layout = QtWidgets.QHBoxLayout(filter_frame)
        filter_frame_layout.addWidget(self.year_filter_label)
        filter_frame_layout.addWidget(self.year_filter_combobox)
        filter_frame_layout.addStretch()
        filter_frame_layout.setContentsMargins(10, 5, 10, 5)  # Añadir márgenes internos
        
        # Insertar el frame en el layout principal
        layout_index = self.tab_2_layout.indexOf(self.label_equivalentes)
        self.tab_2_layout.insertWidget(layout_index + 1, filter_frame)
        
        # Mejorar la apariencia de los labels de sección
        for label in [self.label_equivalentes, self.label_balance, self.label_cash_flow, self.label_income_statement]:
            font = QtGui.QFont()
            font.setPointSize(11)  # Aumentar tamaño de fuente
            font.setBold(True)     # Poner en negrita
            label.setFont(font)
            label.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")
            
        # Agregar un pequeño espacio después de la etiqueta principal
        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.tab_2_layout.insertItem(layout_index + 2, spacer)
    
    # Obtener el año seleccionado con manejo seguro
    selected_year = self.year_filter_combobox.currentText() if hasattr(self, 'year_filter_combobox') and self.year_filter_combobox else "Todos los años"
    
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

    # Determinar qué columnas mostrar según la selección del filtro de años
    selected_year = self.year_filter_combobox.currentText() if hasattr(self, 'year_filter_combobox') else "Todos los años"
    if selected_year == "Todos los años":
        years_columns = ["2024", "2023", "2022", "2021"]  # Actualizado para incluir 2024
    else:
        years_columns = [selected_year]

    # Crear las columnas base para los DataFrames intermedios
    base_columns = ["Fuente", "Datos"]
    display_columns = base_columns + years_columns

    # Interleave the values from Google, Yahoo, and Macrotrends for balance
    interleaved_balance = []
    for i in range(len(balance_df)):
        google_value = balance_df.iloc[i][GOOGLE_FINANCE]
        yahoo_value = balance_df.iloc[i][YAHOO_FINANCE]
        macrotrends_value = balance_df.iloc[i][MACROTRENDS]
        google_inicial = balance_df.iloc[i][GOOGLE_INICIAL]
        yahoo_inicial = balance_df.iloc[i][YAHOO_INICIAL]
        macrotrends_inicial = balance_df.iloc[i][MACROTRENDS_INICIAL]

        # Asegurar que self.data_frames existe antes de usarlo
        if not hasattr(self, 'data_frames'):
            # Si no existe, crear un diccionario vacío con la estructura necesaria
            self.data_frames = {
                'balance': {'google': pd.DataFrame(), 'yahoo': pd.DataFrame(), 'macrotrends': pd.DataFrame()},
                'cashflow': {'google': pd.DataFrame(), 'yahoo': pd.DataFrame(), 'macrotrends': pd.DataFrame()},
                'income': {'google': pd.DataFrame(), 'yahoo': pd.DataFrame(), 'macrotrends': pd.DataFrame()}
            }

        # Obtener todos los valores anuales primero, con manejo seguro de errores
        try:
            google_row_values = ["Google", google_value] + self.data_frames['balance']['google'].loc[self.data_frames['balance']['google']['Datos'] == google_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError, AttributeError):
            google_row_values = ["Google", google_value] + ["N/A", "N/A", "N/A", "N/A"]
        
        try:
            yahoo_row_values = ["Yahoo", yahoo_value] + self.data_frames['balance']['yahoo'].loc[self.data_frames['balance']['yahoo']['Datos'] == yahoo_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError, AttributeError):
            yahoo_row_values = ["Yahoo", yahoo_value] + ["N/A", "N/A", "N/A", "N/A"]
        
        try:
            macrotrends_row_values = ["Macrotrends", macrotrends_value] + self.data_frames['balance']['macrotrends'].loc[self.data_frames['balance']['macrotrends']['Datos'] == macrotrends_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError, AttributeError):
            macrotrends_row_values = ["Macrotrends", macrotrends_value] + ["N/A", "N/A", "N/A", "N/A"]

        # Asegurarse de que todos los rows tienen la longitud correcta antes de crear el diccionario
        all_years = ["2024", "2023", "2022", "2021"]
        
        # Asegurarse de que los valores tienen la longitud correcta antes de crear el diccionario
        while len(google_row_values) < 2 + len(all_years):
            google_row_values.append("N/A")
        while len(yahoo_row_values) < 2 + len(all_years):
            yahoo_row_values.append("N/A")
        while len(macrotrends_row_values) < 2 + len(all_years):
            macrotrends_row_values.append("N/A")
            
        # Limitar a la longitud máxima
        google_row_full = google_row_values[:2+len(all_years)]
        yahoo_row_full = yahoo_row_values[:2+len(all_years)]
        macrotrends_row_full = macrotrends_row_values[:2+len(all_years)]
        
        # Crear un diccionario de filas completas para buscar por año más tarde
        google_row_dict = dict(zip(["Fuente", "Datos"] + all_years, google_row_full))
        yahoo_row_dict = dict(zip(["Fuente", "Datos"] + all_years, yahoo_row_full))
        macrotrends_row_dict = dict(zip(["Fuente", "Datos"] + all_years, macrotrends_row_full))
        
        # Filtrar las filas según los años seleccionados, con manejo seguro de claves no encontradas
        google_row = []
        yahoo_row = []
        macrotrends_row = []
        
        for col in display_columns:
            google_row.append(google_row_dict.get(col, "N/A"))
            yahoo_row.append(yahoo_row_dict.get(col, "N/A"))
            macrotrends_row.append(macrotrends_row_dict.get(col, "N/A"))
        
        interleaved_balance.extend([google_row, yahoo_row, macrotrends_row, [""] * len(display_columns)])  # Add blank row

    interleaved_balance_df = pd.DataFrame(interleaved_balance, columns=display_columns)
    if not interleaved_balance_df.empty:
        interleaved_balance_df = interleaved_balance_df[:-1]  # Remove the last row

    # Process cashflow data
    # ...existing code for cashflow data processing...
    interleaved_cashflow = []
    for i in range(len(cashflow_df)):
        google_value = cashflow_df.iloc[i][GOOGLE_FINANCE]
        yahoo_value = cashflow_df.iloc[i][YAHOO_FINANCE]
        macrotrends_value = cashflow_df.iloc[i][MACROTRENDS]
        google_inicial = cashflow_df.iloc[i][GOOGLE_INICIAL]
        yahoo_inicial = cashflow_df.iloc[i][YAHOO_INICIAL]
        macrotrends_inicial = cashflow_df.iloc[i][MACROTRENDS_INICIAL]

        # Obtener todos los valores anuales primero, con manejo seguro de errores
        try:
            google_row_values = ["Google", google_value] + self.data_frames['cashflow']['google'].loc[self.data_frames['cashflow']['google']['Datos'] == google_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError):
            google_row_values = ["Google", google_value] + ["N/A", "N/A", "N/A", "N/A"]
        
        try:
            yahoo_row_values = ["Yahoo", yahoo_value] + self.data_frames['cashflow']['yahoo'].loc[self.data_frames['cashflow']['yahoo']['Datos'] == yahoo_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError):
            yahoo_row_values = ["Yahoo", yahoo_value] + ["N/A", "N/A", "N/A", "N/A"]
        
        try:
            macrotrends_row_values = ["Macrotrends", macrotrends_value] + self.data_frames['cashflow']['macrotrends'].loc[self.data_frames['cashflow']['macrotrends']['Datos'] == macrotrends_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError):
            macrotrends_row_values = ["Macrotrends", macrotrends_value] + ["N/A", "N/A", "N/A", "N/A"]

        # Asegurarse de que todos los rows tienen la longitud correcta
        all_years = ["2024", "2023", "2022", "2021"]
        
        # Asegurarse de que los valores tienen la longitud correcta antes de crear el diccionario
        while len(google_row_values) < 2 + len(all_years):
            google_row_values.append("N/A")
        while len(yahoo_row_values) < 2 + len(all_years):
            yahoo_row_values.append("N/A")
        while len(macrotrends_row_values) < 2 + len(all_years):
            macrotrends_row_values.append("N/A")
            
        # Limitar a la longitud máxima
        google_row_full = google_row_values[:2+len(all_years)]
        yahoo_row_full = yahoo_row_values[:2+len(all_years)]
        macrotrends_row_full = macrotrends_row_values[:2+len(all_years)]
        
        # Crear un diccionario de filas completas para buscar por año más tarde
        google_row_dict = dict(zip(["Fuente", "Datos"] + all_years, google_row_full))
        yahoo_row_dict = dict(zip(["Fuente", "Datos"] + all_years, yahoo_row_full))
        macrotrends_row_dict = dict(zip(["Fuente", "Datos"] + all_years, macrotrends_row_full))
        
        # Filtrar las filas según los años seleccionados, con manejo seguro de claves no encontradas
        google_row = []
        yahoo_row = []
        macrotrends_row = []
        
        for col in display_columns:
            google_row.append(google_row_dict.get(col, "N/A"))
            yahoo_row.append(yahoo_row_dict.get(col, "N/A"))
            macrotrends_row.append(macrotrends_row_dict.get(col, "N/A"))

        interleaved_cashflow.extend([google_row, yahoo_row, macrotrends_row, [""] * len(display_columns)])  # Add blank row

    interleaved_cashflow_df = pd.DataFrame(interleaved_cashflow, columns=display_columns)
    if not interleaved_cashflow_df.empty:
        interleaved_cashflow_df = interleaved_cashflow_df[:-1]  # Remove the last row

    # Process income data
    # ...existing code for income data processing...
    interleaved_income = []
    for i in range(len(income_df)):
        google_value = income_df.iloc[i][GOOGLE_FINANCE]
        yahoo_value = income_df.iloc[i][YAHOO_FINANCE]
        macrotrends_value = income_df.iloc[i][MACROTRENDS]
        google_inicial = income_df.iloc[i][GOOGLE_INICIAL]
        yahoo_inicial = income_df.iloc[i][YAHOO_INICIAL]
        macrotrends_inicial = income_df.iloc[i][MACROTRENDS_INICIAL]

        # Obtener todos los valores anuales primero, con manejo seguro de errores
        try:
            google_row_values = ["Google", google_value] + self.data_frames['income']['google'].loc[self.data_frames['income']['google']['Datos'] == google_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError):
            google_row_values = ["Google", google_value] + ["N/A", "N/A", "N/A", "N/A"]
        
        try:
            yahoo_row_values = ["Yahoo", yahoo_value] + self.data_frames['income']['yahoo'].loc[self.data_frames['income']['yahoo']['Datos'] == yahoo_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError):
            yahoo_row_values = ["Yahoo", yahoo_value] + ["N/A", "N/A", "N/A", "N/A"]
        
        try:
            macrotrends_row_values = ["Macrotrends", macrotrends_value] + self.data_frames['income']['macrotrends'].loc[self.data_frames['income']['macrotrends']['Datos'] == macrotrends_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError):
            macrotrends_row_values = ["Macrotrends", macrotrends_value] + ["N/A", "N/A", "N/A", "N/A"]

        # Asegurarse de que todos los rows tienen la longitud correcta
        all_years = ["2024", "2023", "2022", "2021"]
        
        # Asegurarse de que los valores tienen la longitud correcta antes de crear el diccionario
        while len(google_row_values) < 2 + len(all_years):
            google_row_values.append("N/A")
        while len(yahoo_row_values) < 2 + len(all_years):
            yahoo_row_values.append("N/A")
        while len(macrotrends_row_values) < 2 + len(all_years):
            macrotrends_row_values.append("N/A")
            
        # Limitar a la longitud máxima
        google_row_full = google_row_values[:2+len(all_years)]
        yahoo_row_full = yahoo_row_values[:2+len(all_years)]
        macrotrends_row_full = macrotrends_row_values[:2+len(all_years)]
        
        # Crear un diccionario de filas completas para buscar por año más tarde
        google_row_dict = dict(zip(["Fuente", "Datos"] + all_years, google_row_full))
        yahoo_row_dict = dict(zip(["Fuente", "Datos"] + all_years, yahoo_row_full))
        macrotrends_row_dict = dict(zip(["Fuente", "Datos"] + all_years, macrotrends_row_full))
        
        # Filtrar las filas según los años seleccionados, con manejo seguro de claves no encontradas
        google_row = []
        yahoo_row = []
        macrotrends_row = []
        
        for col in display_columns:
            google_row.append(google_row_dict.get(col, "N/A"))
            yahoo_row.append(yahoo_row_dict.get(col, "N/A"))
            macrotrends_row.append(macrotrends_row_dict.get(col, "N/A"))

        interleaved_income.extend([google_row, yahoo_row, macrotrends_row, [""] * len(display_columns)])  # Add blank row

    interleaved_income_df = pd.DataFrame(interleaved_income, columns=display_columns)
    if not interleaved_income_df.empty:
        interleaved_income_df = interleaved_income_df[:-1]  # Remove the last row

    # Mostrar los datos equivalentes en las tablas
    model_balance = GroupedPandasModel(interleaved_balance_df)
    self.tableView_balance.setModel(model_balance)
    self.tableView_balance.resizeColumnsToContents()
    self.tableView_balance.horizontalHeader().setStretchLastSection(True)
    self.tableView_balance.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    # Apply the delegate to draw the group frames
    balance_delegate = GroupFrameDelegate(self.tableView_balance)
    self.tableView_balance.setItemDelegate(balance_delegate)

    model_cashflow = GroupedPandasModel(interleaved_cashflow_df)
    self.tableView_cash_flow.setModel(model_cashflow)
    self.tableView_cash_flow.resizeColumnsToContents()
    self.tableView_cash_flow.horizontalHeader().setStretchLastSection(True)
    self.tableView_cash_flow.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    # Apply the delegate to draw the group frames
    cashflow_delegate = GroupFrameDelegate(self.tableView_cash_flow)
    self.tableView_cash_flow.setItemDelegate(cashflow_delegate)

    model_income = GroupedPandasModel(interleaved_income_df)
    self.tableView_income_statement.setModel(model_income)
    self.tableView_income_statement.resizeColumnsToContents()
    self.tableView_income_statement.horizontalHeader().setStretchLastSection(True)
    self.tableView_income_statement.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    # Apply the delegate to draw the group frames
    income_delegate = GroupFrameDelegate(self.tableView_income_statement)
    self.tableView_income_statement.setItemDelegate(income_delegate)

    # Store the dataframes for later use when clicking
    self.interleaved_balance_df = interleaved_balance_df
    self.interleaved_cashflow_df = interleaved_cashflow_df
    self.interleaved_income_df = interleaved_income_df
    
    # Ensure we start with no chart window reference
    if not hasattr(self, 'current_chart_window'):
        self.current_chart_window = None

    # Connect cell click events to a single handler
    try:
        # Disconnect existing connections first to prevent multiple handlers
        self.tableView_balance.clicked.disconnect()
        self.tableView_cash_flow.clicked.disconnect()
        self.tableView_income_statement.clicked.disconnect()
    except TypeError:
        # No previous connections
        pass
        
    # Connect new click handlers
    self.tableView_balance.clicked.connect(lambda index: handle_group_click(self, 'balance', index))
    self.tableView_cash_flow.clicked.connect(lambda index: handle_group_click(self, 'cashflow', index))
    self.tableView_income_statement.clicked.connect(lambda index: handle_group_click(self, 'income', index))

# Function to handle clicks and identify the group
def handle_group_click(self, data_type, index):
    # Get the appropriate dataframe based on the clicked table
    if data_type == 'balance':
        df = self.interleaved_balance_df
    elif data_type == 'cashflow':
        df = self.interleaved_cashflow_df
    elif data_type == 'income':
        df = self.interleaved_income_df
    else:
        return

    row = index.row()
    
    # Calculate the group (each group has 3 rows + 1 empty row)
    group_start = (row // 4) * 4
    
    # Make sure this is a valid group (we have 3 rows for the group)
    if group_start + 2 < df.shape[0]:
        # Get all rows in this group (3 rows, one for each source)
        group_data = df.iloc[group_start:group_start+3].copy()
        
        # Get the title from the data column (all rows in group have same concept, just take first)
        title = group_data.iloc[0]['Datos']
        
        # Close existing chart window if one is open
        if hasattr(self, 'current_chart_window') and self.current_chart_window is not None:
            try:
                self.current_chart_window.close()
            except:
                pass
        
        # Show a new chart and store a reference to it
        from controller.chart_controller import ChartWindow
        self.current_chart_window = ChartWindow(group_data, title, self)
        self.current_chart_window.show()

def limpiar_datos_equivalentes(self):
    """Limpia todas las tablas y contenido de la pestaña de datos equivalentes."""
    # Crear modelos vacíos para las tablas
    empty_model = PandasModel(pd.DataFrame())
    
    # Establecer los modelos vacíos en las tablas
    self.tableView_balance.setModel(empty_model)
    self.tableView_cash_flow.setModel(empty_model)
    self.tableView_income_statement.setModel(empty_model)
    
    # Restablecer los títulos de etiquetas
    _translate = QtCore.QCoreApplication.translate
    self.label_equivalentes.setText(_translate("MainWindow", "Datos Equivalentes"))
    self.label_balance.setText(_translate("MainWindow", "Datos de Balance"))
    self.label_cash_flow.setText(_translate("MainWindow", "Datos de Flujo de Caja"))
    self.label_income_statement.setText(_translate("MainWindow", "Cuenta de Pérdidas y Ganancias"))
    
    # Eliminar el selector de años si existe
    if hasattr(self, 'year_filter_combobox') and self.year_filter_combobox is not None:
        # Encontrar y eliminar el frame que contiene los controles
        for i in range(self.tab_2_layout.count()):
            item = self.tab_2_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), QtWidgets.QFrame):
                item.widget().setParent(None)
                break
        
        # Eliminar también el spacer que se añadió después
        for i in range(self.tab_2_layout.count()):
            item = self.tab_2_layout.itemAt(i)
            if item and not item.widget():  # Es un spacer
                self.tab_2_layout.removeItem(item)
                break
        
        # Limpiar las referencias a los objetos
        self.year_filter_label = None
        self.year_filter_combobox = None
    
    # Forzar la actualización visual
    self.tableView_balance.viewport().update()
    self.tableView_cash_flow.viewport().update()
    self.tableView_income_statement.viewport().update()
    
    # Close any open chart window
    if hasattr(self, 'current_chart_window') and self.current_chart_window is not None:
        try:
            self.current_chart_window.close()
        except:
            pass
        self.current_chart_window = None
