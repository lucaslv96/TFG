import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

class ChartWindow(QtWidgets.QWidget):  # Changed from QDialog to QWidget
    def __init__(self, data, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Comparativa: {title}")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.data = data
        self.title = title
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
        
        # Extract numeric values and handle different formats
        self._normalize_data()
        self.init_ui()
    
    def _normalize_data(self):
        # Normalize and clean data for plotting
        self.plot_data = {
            'years': [],
            'google': [],
            'yahoo': [],
            'macrotrends': []
        }
        
        # Get the years columns
        years_cols = [col for col in self.data.columns if col not in ['Fuente', 'Datos']]
        self.plot_data['years'] = years_cols
        
        # For each provider, extract and normalize values
        for provider in ['Google', 'Yahoo', 'Macrotrends']:
            provider_rows = self.data[self.data['Fuente'] == provider]
            if not provider_rows.empty:
                row_data = provider_rows.iloc[0]
                values = []
                for year in years_cols:
                    try:
                        # Get the raw value
                        value = row_data[year]
                        
                        # Handle different formats
                        if isinstance(value, str):
                            # Remove currency symbols, commas as thousand separators, etc.
                            value = re.sub(r'[^\d.-]', '', value.replace(',', ''))
                            
                            # Handle percentages
                            if '%' in row_data[year]:
                                value = float(value) / 100 if value else 0
                            
                            # Handle millions/billions indicators
                            if 'M' in row_data[year]:
                                value = float(value) * 1000000 if value else 0
                            elif 'B' in row_data[year]:
                                value = float(value) * 1000000000 if value else 0
                            else:
                                value = float(value) if value else 0
                        elif pd.isna(value) or value == 'N/A':
                            value = 0
                    except (ValueError, TypeError):
                        value = 0
                    
                    values.append(value)
                
                self.plot_data[provider.lower()] = values
    
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Header with title
        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(f"<h2>{self.title}</h2>")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Plot type selector
        plot_type_label = QtWidgets.QLabel("Tipo de gráfico:")
        self.plot_type_selector = QtWidgets.QComboBox()
        self.plot_type_selector.addItems(["Líneas", "Barras", "Áreas"])
        self.plot_type_selector.setCurrentIndex(0)
        self.plot_type_selector.currentIndexChanged.connect(self.update_chart)
        
        plot_selector_layout = QtWidgets.QHBoxLayout()
        plot_selector_layout.addWidget(plot_type_label)
        plot_selector_layout.addWidget(self.plot_type_selector)
        
        # Data scaling toggle
        self.scale_toggle = QtWidgets.QCheckBox("Escalar datos para mejor comparación")
        self.scale_toggle.setChecked(False)
        self.scale_toggle.stateChanged.connect(self.update_chart)
        
        # Control panel
        control_panel = QtWidgets.QFrame()
        control_panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        control_panel.setStyleSheet("background-color: #eaeaea; border-radius: 5px; padding: 5px;")
        control_layout = QtWidgets.QHBoxLayout(control_panel)
        control_layout.addLayout(plot_selector_layout)
        control_layout.addStretch()
        control_layout.addWidget(self.scale_toggle)
        
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(400)
        
        # Data table showing the values
        self.data_table = QtWidgets.QTableWidget()
        self.data_table.setColumnCount(4)  # Year, Google, Yahoo, Macrotrends
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
        
        # Fill the data table
        self._populate_table()
        
        # Add components to layout
        layout.addLayout(header_layout)
        layout.addWidget(control_panel)
        layout.addWidget(self.canvas)
        layout.addWidget(self.data_table)
        
        # Update chart with default settings
        self.update_chart()
    
    def _populate_table(self):
        years = self.plot_data['years']
        self.data_table.setRowCount(len(years))
        
        # Vertical header with year numbers
        for i, year in enumerate(years):
            self.data_table.setItem(i, 0, QtWidgets.QTableWidgetItem(year))
            
            # Format values with thousand separators
            for j, source in enumerate(['google', 'yahoo', 'macrotrends']):
                value = self.plot_data[source][i]
                # Format the number with commas as thousand separators
                formatted_value = f"{value:,.2f}"
                self.data_table.setItem(i, j+1, QtWidgets.QTableWidgetItem(formatted_value))
        
        # Resize columns to content
        self.data_table.resizeColumnsToContents()
    
    def update_chart(self):
        self.ax.clear()
        
        years = self.plot_data['years']
        google_data = np.array(self.plot_data['google'])
        yahoo_data = np.array(self.plot_data['yahoo'])
        macrotrends_data = np.array(self.plot_data['macrotrends'])
        
        # Scale data if the toggle is checked
        if self.scale_toggle.isChecked():
            # Find max values for each data series
            google_max = max(google_data) if any(google_data) else 1
            yahoo_max = max(yahoo_data) if any(yahoo_data) else 1
            macrotrends_max = max(macrotrends_data) if any(macrotrends_data) else 1
            
            # Scale each series by its max value
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
        
        # Set chart title and labels
        self.ax.set_title(f"Comparación de {self.title} por fuente", fontsize=14)
        self.ax.set_xlabel('Año', fontsize=12)
        
        if self.scale_toggle.isChecked():
            self.ax.set_ylabel('Valores Normalizados', fontsize=12)
        else:
            self.ax.set_ylabel('Valor', fontsize=12)
        
        # Add grid for better readability
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        self.ax.legend(loc='upper left', frameon=True, framealpha=0.8)
        
        # Tight layout and redraw
        self.figure.tight_layout()
        self.canvas.draw()
