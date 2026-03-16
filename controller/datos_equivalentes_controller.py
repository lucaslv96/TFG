from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd
from model.data_manager import PandasModel
from model.database import DataManager
# ChartWindow se importa de forma lazy dentro de handle_group_click para evitar import circular

# Modelo de tabla personalizado que soporta grupos
class GroupedPandasModel(PandasModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(df, parent)
        self.group_rows = {}  # Diccionario para los límites de grupo
        self._setup_groups()
    
    def _setup_groups(self):
        # Identificar grupos: cada 3 filas forman un grupo, luego hay una fila vacía
        row = 0
        while row < self.rowCount():
            if row + 2 < self.rowCount():
                # Marcar estas 3 filas como un grupo
                group_id = row // 4  # Cada grupo tiene 3 filas de datos + 1 fila vacía
                for i in range(3):  # Las 3 filas de datos del grupo
                    self.group_rows[row + i] = group_id
            row += 4  # Pasar al siguiente grupo (3 filas de datos + 1 vacía)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
            
        # Para las filas vacías, devolver cadena vacía para el rol de display
        if index.row() % 4 == 3 and role == QtCore.Qt.DisplayRole:  # Fila vacía
            return ""
            
        # Para colores de fondo, alternar entre grupos
        if role == QtCore.Qt.BackgroundRole:
            group_id = self.group_rows.get(index.row(), -1)
            if group_id != -1:
                # Alternar colores de grupo
                if group_id % 2 == 0:
                    return QtGui.QColor("#F0F8FF")  # Azul claro para grupos pares
                else:
                    return QtGui.QColor("#F0FFF0")  # Verde claro para grupos impares
                    
        return super().data(index, role)

# Esta clase es para el modelo de tabla que soporta bordes de grupo
class GroupFrameDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(GroupFrameDelegate, self).__init__(parent)
        
    def paint(self, painter, option, index):
        super(GroupFrameDelegate, self).paint(painter, option, index)
        
        # Obtener la fila y determinar si es inicio, medio o fin de grupo
        row = index.row()
        col = index.column()
        
        # Determinar límites de grupo (3 filas por grupo, seguidas de una vacía)
        group_start = (row // 4) * 4
        is_start_of_group = row == group_start
        is_end_of_group = row == group_start + 2
        is_in_group = row % 4 < 3  # Primeras 3 filas de cada 4 son parte de un grupo
        
        if is_in_group:
            # Dibujar partes del borde según la posición en el grupo
            pen = QtGui.QPen(QtGui.QColor("#2c3e50"))  # Borde azul oscuro
            pen.setWidth(1)
            painter.setPen(pen)
            rect = option.rect
            
            # Borde vertical izquierdo para todas las celdas del grupo
            if col == 0:
                painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())
                
            # Borde vertical derecho para todas las celdas del grupo
            model = index.model()
            if col == model.columnCount() - 1:
                painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
                
            # Borde superior para la primera fila del grupo
            if is_start_of_group:
                painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
                
            # Borde inferior para la última fila del grupo
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

_ALL_YEARS = ["2024", "2023", "2022", "2021"]


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _lookup_yahoo_row(self, data_type, yahoo_value, yahoo_inicial):
    """Busca la fila de Yahoo para un concepto dado, con fallback a coincidencia parcial."""
    try:
        df_y = self.data_frames[data_type]['yahoo']
        match = df_y.loc[df_y['Datos'] == yahoo_inicial]
        if not match.empty:
            return ["Yahoo", yahoo_value] + match.iloc[0].values[1:5].tolist()

        if data_type != 'balance':
            partial = df_y[df_y['Datos'].str.lower().str.contains(str(yahoo_inicial).lower(), na=False)]
            if not partial.empty:
                nombre_real = partial.iloc[0].get('Datos', 'N/A') if 'Datos' in partial.columns else 'N/A'
                return ["Yahoo", nombre_real] + partial.iloc[0].values[1:5].tolist()
        elif hasattr(self, 'df_yahoo') and not self.df_yahoo.empty:
            muestra = self.df_yahoo.head(10).values.flatten().tolist()
            if len(muestra) >= 5:
                return ["Yahoo", yahoo_value] + muestra[1:5]
    except Exception:
        pass
    return ["Yahoo", yahoo_value] + ["N/A"] * 4


def _build_interleaved_df(self, source_df, data_type, display_columns):
    """Intercala filas de Google, Yahoo y Macrotrends para un tipo de dato."""
    interleaved = []
    for i in range(len(source_df)):
        row = source_df.iloc[i]
        g_value  = row[GOOGLE_FINANCE];      g_inicial = row[GOOGLE_INICIAL]
        y_value  = row[YAHOO_FINANCE];       y_inicial = row[YAHOO_INICIAL]
        m_value  = row[MACROTRENDS];         m_inicial = row[MACROTRENDS_INICIAL]

        try:
            df_g = self.data_frames[data_type]['google']
            g_vals = ["Google", g_value] + df_g.loc[df_g['Datos'] == g_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError, AttributeError):
            g_vals = ["Google", g_value] + ["N/A"] * 4

        y_vals = _lookup_yahoo_row(self, data_type, y_value, y_inicial)

        try:
            df_m = self.data_frames[data_type]['macrotrends']
            m_vals = ["Macrotrends", m_value] + df_m.loc[df_m['Datos'] == m_inicial].values.flatten().tolist()[1:]
        except (KeyError, IndexError, ValueError):
            m_vals = ["Macrotrends", m_value] + ["N/A"] * 4

        for vals in (g_vals, y_vals, m_vals):
            while len(vals) < 2 + len(_ALL_YEARS):
                vals.append("N/A")

        keys = ["Fuente", "Datos"] + _ALL_YEARS
        g_dict = dict(zip(keys, g_vals[:2 + len(_ALL_YEARS)]))
        y_dict = dict(zip(keys, y_vals[:2 + len(_ALL_YEARS)]))
        m_dict = dict(zip(keys, m_vals[:2 + len(_ALL_YEARS)]))

        interleaved.extend([
            [g_dict.get(c, "N/A") for c in display_columns],
            [y_dict.get(c, "N/A") for c in display_columns],
            [m_dict.get(c, "N/A") for c in display_columns],
            [""] * len(display_columns),
        ])

    df = pd.DataFrame(interleaved, columns=display_columns)
    return df[:-1] if not df.empty else df


def _set_grouped_table(table_view, df):
    """Asigna un GroupedPandasModel a una tabla y aplica el delegado de bordes."""
    model = GroupedPandasModel(df)
    table_view.setModel(model)
    table_view.resizeColumnsToContents()
    table_view.horizontalHeader().setStretchLastSection(True)
    table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    table_view.setItemDelegate(GroupFrameDelegate(table_view))


def _init_year_filter(self):
    """Crea el widget de filtro de años la primera vez. Solo debe llamarse una vez."""
    self.year_filter_label = QtWidgets.QLabel("Filtrar años:", self.tab_2)
    font = QtGui.QFont()
    font.setPointSize(10)
    font.setBold(True)
    self.year_filter_label.setFont(font)

    self.year_filter_combobox = QtWidgets.QComboBox(self.tab_2)
    self.year_filter_combobox.setMinimumHeight(30)
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
    self.year_filter_combobox.addItems(["Todos los años"] + _ALL_YEARS)
    self.year_filter_combobox.currentIndexChanged.connect(lambda: mostrar_datos_equivalentes(self))

    filter_frame = QtWidgets.QFrame(self.tab_2)
    filter_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    filter_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    filter_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")

    filter_frame_layout = QtWidgets.QHBoxLayout(filter_frame)
    filter_frame_layout.addWidget(self.year_filter_label)
    filter_frame_layout.addWidget(self.year_filter_combobox)
    filter_frame_layout.addStretch()
    filter_frame_layout.setContentsMargins(10, 5, 10, 5)

    layout_index = self.tab_2_layout.indexOf(self.label_equivalentes)
    self.tab_2_layout.insertWidget(layout_index + 1, filter_frame)

    for label in [self.label_equivalentes, self.label_balance, self.label_cash_flow, self.label_income_statement]:
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")

    spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
    self.tab_2_layout.insertItem(layout_index + 2, spacer)


def mostrar_datos_equivalentes(self):
    # Mostramos los controles si la búsqueda ha finalizado o hay datos cargados
    should_show_controls = (hasattr(self, 'trabajadores_finalizados') and self.trabajadores_finalizados == 3) or \
                           (hasattr(self, 'data_frames') and not all(df.empty for tipo in self.data_frames.values()
                                                                     for df in tipo.values()))

    if hasattr(self, 'saved_filter_frame') and self.saved_filter_frame is not None:
        self.saved_filter_frame.setVisible(should_show_controls)

    if hasattr(self, 'year_filter_combobox') and self.year_filter_combobox is not None:
        self.year_filter_combobox.setVisible(should_show_controls)
        if hasattr(self, 'year_filter_label'):
            self.year_filter_label.setVisible(should_show_controls)

    # Crear el filtro de años solo la primera vez
    if not hasattr(self, 'year_filter_combobox') or self.year_filter_combobox is None:
        _init_year_filter(self)

    # Obtener el año seleccionado
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

    # Crear DataFrame para los datos equivalentes
    df_equivalentes = pd.DataFrame(datos_equivalentes, columns=[GOOGLE_FINANCE, MACROTRENDS, YAHOO_FINANCE, TIPO, GOOGLE_INICIAL, MACROTRENDS_INICIAL, YAHOO_INICIAL])

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

    # Asegurar que self.data_frames existe antes de usarlo
    if not hasattr(self, 'data_frames'):
        self.data_frames = {
            t: {'google': pd.DataFrame(), 'yahoo': pd.DataFrame(), 'macrotrends': pd.DataFrame()}
            for t in ('balance', 'cashflow', 'income')
        }

    interleaved_balance_df  = _build_interleaved_df(self, balance_df,  'balance',  display_columns)
    interleaved_cashflow_df = _build_interleaved_df(self, cashflow_df, 'cashflow', display_columns)
    interleaved_income_df   = _build_interleaved_df(self, income_df,   'income',   display_columns)

    _set_grouped_table(self.tableView_balance,          interleaved_balance_df)
    _set_grouped_table(self.tableView_cash_flow,        interleaved_cashflow_df)
    _set_grouped_table(self.tableView_income_statement, interleaved_income_df)

    # Guardar los dataframes para uso posterior al hacer clic
    self.interleaved_balance_df = interleaved_balance_df
    self.interleaved_cashflow_df = interleaved_cashflow_df
    self.interleaved_income_df = interleaved_income_df
    
    # Asegurarse de empezar sin referencia a ventana de gráfico
    if not hasattr(self, 'current_chart_window'):
        self.current_chart_window = None

    # Conectar eventos de clic de celda a un único manejador
    try:
        # Desconectar conexiones existentes primero para evitar múltiples manejadores
        self.tableView_balance.clicked.disconnect()
        self.tableView_cash_flow.clicked.disconnect()
        self.tableView_income_statement.clicked.disconnect()
    except TypeError:
        # Sin conexiones previas
        pass
        
    # Conectar nuevos manejadores de clic
    self.tableView_balance.clicked.connect(lambda index: handle_group_click(self, 'balance', index))
    self.tableView_cash_flow.clicked.connect(lambda index: handle_group_click(self, 'cashflow', index))
    self.tableView_income_statement.clicked.connect(lambda index: handle_group_click(self, 'income', index))

# Función para manejar clics e identificar el grupo
def handle_group_click(self, data_type, index):
    # Obtener el dataframe apropiado según la tabla clicada
    if data_type == 'balance':
        df = self.interleaved_balance_df
    elif data_type == 'cashflow':
        df = self.interleaved_cashflow_df
    elif data_type == 'income':
        df = self.interleaved_income_df
    else:
        return

    row = index.row()
    
    # Calcular el grupo (cada grupo tiene 3 filas + 1 vacía)
    group_start = (row // 4) * 4
    
    # Asegurarse de que es un grupo válido (tenemos 3 filas para el grupo)
    if group_start + 2 < df.shape[0]:
        # Obtener todas las filas de este grupo (3 filas, una por fuente)
        group_data = df.iloc[group_start:group_start+3].copy()
        
        # Obtener el título de la columna de datos (todas las filas del grupo tienen el mismo concepto, tomar la primera)
        title = group_data.iloc[0]['Datos']
        
        # Cerrar ventana de gráfico existente si hay una abierta
        if hasattr(self, 'current_chart_window') and self.current_chart_window is not None:
            try:
                self.current_chart_window.close()
            except RuntimeError:
                pass  # La ventana ya fue destruida por Qt

        # Mostrar un nuevo gráfico y guardar referencia
        from controller.chart_controller import ChartWindow  # lazy import para evitar circular
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
    
    # Cerrar cualquier ventana de gráfico abierta
    if hasattr(self, 'current_chart_window') and self.current_chart_window is not None:
        try:
            self.current_chart_window.close()
        except:
            pass
        self.current_chart_window = None
