import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

class ChartWindow(QtWidgets.QWidget):  # Cambiado de QDialog a QWidget
    def __init__(self, data, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Comparativa: {title}")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.data = data
        self.title = title
        self._main_window = parent  # Guardar referencia al padre (no usar self.parent para no sobreescribir el método Qt)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
                min-height: 25px;
            }
        """)
        
        # Extraer valores numéricos y manejar diferentes formatos
        self._normalize_data()
        self._hide_secondary_search_buttons()  # Ocultar botones al importar datos
        self.init_ui()
    
    def _hide_secondary_search_buttons(self):
        """Oculta los botones de búsqueda secundaria de la ventana principal al importar datos de archivo"""
        if self._main_window and hasattr(self._main_window, 'hide_secondary_search_buttons'):
            try:
                self._main_window.hide_secondary_search_buttons()
            except Exception:
                pass  # La ventana principal puede no tener este método en todos los contextos
    
    def _normalize_data(self):
        # Normalizar y limpiar datos para graficar
        self.plot_data = {
            'years': [],
            'google': [],
            'yahoo': [],
            'macrotrends': []
        }
        
        years_cols = [col for col in self.data.columns if col not in ['Fuente', 'Datos']]
        self.plot_data['years'] = years_cols
        
        for provider in ['Google', 'Yahoo', 'Macrotrends']:
            provider_rows = self.data[self.data['Fuente'] == provider]
            
            if not provider_rows.empty:
                row_data = provider_rows.iloc[0]
                values = []
                
                for year in years_cols:
                    try:
                        value = row_data[year]
                        
                        if isinstance(value, str):
                            if provider == 'Google':
                                value = self._normalize_google_value(value)
                            elif provider == 'Macrotrends':
                                value = self._normalize_macrotrends_value(value)
                            else:  # Yahoo u otro proveedor
                                value = self._normalize_yahoo_value(value)
                        elif pd.isna(value) or value == 'N/A':
                            value = 0
                        
                    except (ValueError, TypeError) as e:
                        value = 0
                    
                    values.append(value)
                
                self.plot_data[provider.lower()] = values
    
    def _normalize_google_value(self, value_str):
        """Normaliza valores de Google Finance (formato: XX,XX mil M o X.XXX,XX M)"""
        
        if pd.isna(value_str) or value_str == 'N/A' or not isinstance(value_str, str):
            return 0
        
        # Eliminar espacios extra y normalizar (incluyendo espacios no separables \xa0)
        value_str = value_str.strip().replace('\xa0', ' ')
        
        # Patrón para formato "XX,XX mil M" (miles de millones)
        if 'mil M' in value_str:
            # Extraer la parte numérica antes de "mil M"
            number_part = value_str.replace('mil M', '').strip()
            
            # Reemplazar coma por punto para el separador decimal
            number_part = number_part.replace(',', '.')
            
            try:
                # Convertir a float y multiplicar por 1.000.000.000 (mil M = miles de millones)
                result = float(number_part) * 1_000_000_000
                return result
            except ValueError as e:
                return 0
        
        # Patrón para formato "X.XXX,XX M" (millones)
        elif value_str.endswith(' M'):
            # Extraer la parte numérica antes de " M"
            number_part = value_str.replace(' M', '').strip()
            
            # Manejar formato europeo: X.XXX,XX -> XXXX.XX
            if '.' in number_part and ',' in number_part:
                # Eliminar puntos (separador de miles) y reemplazar coma por punto (decimal)
                parts = number_part.split(',')
                if len(parts) == 2:
                    integer_part = parts[0].replace('.', '')
                    decimal_part = parts[1]
                    number_part = f"{integer_part}.{decimal_part}"
            
            try:
                # Convertir a float y multiplicar por 1.000.000 (M = millones)
                result = float(number_part) * 1_000_000
                return result
            except ValueError as e:
                return 0
        
        return 0
    
    def _normalize_macrotrends_value(self, value_str):
        """Normaliza valores de Macrotrends (formato: $XX.XXX o $XX.XXX,XX)"""
        
        if pd.isna(value_str) or value_str == 'N/A' or not isinstance(value_str, str):
            return 0
        
        # Eliminar símbolo de dólar y espacios
        value_str = value_str.strip().replace('$', '')
        
        try:
            # Manejar formato europeo: XX.XXX,YY donde . es miles y , es decimal
            if '.' in value_str and ',' in value_str:
                # Formato europeo: eliminar puntos (miles) y reemplazar coma por punto (decimal)
                parts = value_str.split(',')
                if len(parts) == 2:
                    integer_part = parts[0].replace('.', '')
                    decimal_part = parts[1]
                    clean_value = f"{integer_part}.{decimal_part}"
                else:
                    clean_value = value_str.replace('.', '').replace(',', '.')
            elif '.' in value_str and ',' not in value_str:
                # Separador de miles solo si sigue el patrón X.XXX (grupos de 3 dígitos)
                # Evitar tratar "1.5" (decimal) como "15"
                import re as _re
                if _re.match(r'^\d{1,3}(\.\d{3})+$', value_str):
                    clean_value = value_str.replace('.', '')
                else:
                    clean_value = value_str  # tratar el punto como decimal
            elif ',' in value_str and '.' not in value_str:
                # Solo coma, tratar como decimal
                clean_value = value_str.replace(',', '.')
            else:
                # No necesita formato especial
                clean_value = value_str
            
            result = float(clean_value) * 1_000_000
            return result
        except ValueError as e:
            return 0
    
    def _normalize_yahoo_value(self, value_str):
        """Normaliza valores de Yahoo Finance (formato: XX,XXX,XXX,XXX.XX)"""
        
        if pd.isna(value_str) or value_str == 'N/A':
            return 0
        
        if isinstance(value_str, (int, float)):
            # Ya está en formato correcto
            result = float(value_str)
            return result
        
        if isinstance(value_str, str):
            # Eliminar comas y convertir a float
            try:
                clean_value = value_str.replace(',', '')
                result = float(clean_value)
                return result
            except ValueError as e:
                return 0
        
        return 0
    
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(f"<h2>{self.title}</h2>")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        plot_type_label = QtWidgets.QLabel("Tipo de gráfico:")
        self.plot_type_selector = QtWidgets.QComboBox()
        self.plot_type_selector.addItems(["Líneas", "Barras", "Áreas"])
        self.plot_type_selector.setCurrentIndex(0)
        self.plot_type_selector.currentIndexChanged.connect(self.update_chart)
        
        plot_selector_layout = QtWidgets.QHBoxLayout()
        plot_selector_layout.addWidget(plot_type_label)
        plot_selector_layout.addWidget(self.plot_type_selector)
        
        self.scale_toggle = QtWidgets.QCheckBox("Escalar datos para mejor comparación")
        self.scale_toggle.setChecked(False)
        self.scale_toggle.stateChanged.connect(self.update_chart)

        # Añadir botón para guardar gráfico
        self.save_button = QtWidgets.QPushButton("Guardar gráfico")
        self.save_button.clicked.connect(self.save_chart)
        self.save_button.setStyleSheet("color: black;")  # Cambia el color del texto a negro

        control_panel = QtWidgets.QFrame()
        control_panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        control_panel.setStyleSheet("background-color: #eaeaea; border-radius: 5px; padding: 5px;")
        control_layout = QtWidgets.QHBoxLayout(control_panel)
        control_layout.addLayout(plot_selector_layout)
        control_layout.addStretch()
        control_layout.addWidget(self.scale_toggle)
        control_layout.addWidget(self.save_button)  # Añadir el botón al panel de control

        self.figure, self.ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(400)
        
        self.data_table = QtWidgets.QTableWidget()
        self.data_table.setColumnCount(4)  
        self.data_table.setHorizontalHeaderLabels(["Año", "Google", "Yahoo", "Macrotrends"])
        self.data_table.setMinimumHeight(150)
        self.data_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        self._populate_table()
        
        layout.addLayout(header_layout)
        layout.addWidget(control_panel)
        layout.addWidget(self.canvas)
        layout.addWidget(self.data_table)
        
        self.update_chart()

    def save_chart(self):
        """Abre un diálogo para guardar la imagen del gráfico."""
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Guardar gráfico como imagen",
            "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;Todos los archivos (*)",
            options=options
        )
        if file_path:
            self.figure.savefig(file_path)
    
    def _populate_table(self):
        years = self.plot_data['years']
        self.data_table.setRowCount(len(years))
        
        for i, year in enumerate(years):
            self.data_table.setItem(i, 0, QtWidgets.QTableWidgetItem(year))
            
            for j, source in enumerate(['google', 'yahoo', 'macrotrends']):
                value = self.plot_data[source][i]
                # Si el valor es string, mostrarlo tal como está
                if isinstance(value, str):
                    formatted_value = value
                else:
                    formatted_value = f"{value:,.2f}"
                self.data_table.setItem(i, j+1, QtWidgets.QTableWidgetItem(formatted_value))
        
        # Ajustar columnas para ocupar todo el ancho disponible
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
    
    def update_chart(self):
        self.ax.clear()
        
        years = self.plot_data['years']
        google_data = np.array(self.plot_data['google'])
        yahoo_data = np.array(self.plot_data['yahoo'])
        macrotrends_data = np.array(self.plot_data['macrotrends'])
        
        if self.scale_toggle.isChecked():
            google_max = max(google_data) if any(google_data) else 1
            yahoo_max = max(yahoo_data) if any(yahoo_data) else 1
            macrotrends_max = max(macrotrends_data) if any(macrotrends_data) else 1
            
            google_data = google_data / google_max if google_max != 0 else google_data
            yahoo_data = yahoo_data / yahoo_max if yahoo_max != 0 else yahoo_data
            macrotrends_data = macrotrends_data / macrotrends_max if macrotrends_max != 0 else macrotrends_data
        
        plot_type = self.plot_type_selector.currentText()
        
        if plot_type == "Líneas":
            self.ax.plot(years, google_data, 'b-o', label='Google Finance', linewidth=2)
            self.ax.plot(years, yahoo_data, 'g-s', label='Yahoo Finance', linewidth=2)
            self.ax.plot(years, macrotrends_data, 'r-^', label='Macrotrends', linewidth=2)
        
        elif plot_type == "Barras":
            x = np.arange(len(years))
            width = 0.25
            
            self.ax.bar(x - width, google_data, width, label='Google Finance', color='royalblue')
            self.ax.bar(x, yahoo_data, width, label='Yahoo Finance', color='forestgreen')
            self.ax.bar(x + width, macrotrends_data, width, label='Macrotrends', color='firebrick')
            
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(years)
        
        elif plot_type == "Áreas":
            self.ax.fill_between(years, google_data, alpha=0.3, color='royalblue', label='Google Finance')
            self.ax.fill_between(years, yahoo_data, alpha=0.3, color='forestgreen', label='Yahoo Finance')
            self.ax.fill_between(years, macrotrends_data, alpha=0.3, color='firebrick', label='Macrotrends')
        
        self.ax.set_title(f"Comparación de {self.title} por fuente", fontsize=14)
        self.ax.set_xlabel('Año', fontsize=12)
        
        if self.scale_toggle.isChecked():
            self.ax.set_ylabel('Valores Normalizados', fontsize=12)
        else:
            self.ax.set_ylabel('Valor', fontsize=12)
        
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Usar posicionamiento automático de la leyenda para evitar solapamientos
        self.ax.legend(loc='best', frameon=True, framealpha=0.9, fancybox=True, shadow=True)
        
        self.figure.tight_layout()
        self.canvas.draw()
