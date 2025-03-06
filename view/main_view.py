# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_view.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made a este archivo will be lost cuando pyuic5 es
# run again.  Do not edit este archivo unless you know lo que estás haciendo.

from PyQt5 import QtCore, QtGui, QtWidgets
from controller.main_controller import buscar_datos, exportar_datos, importar_datos
from controller.datos_equivalentes_controller import mostrar_datos_equivalentes

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        
        # Calculate screen size
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        width = screen_size.width()
        height = screen_size.height()
        
        MainWindow.resize(int(width * 0.8), int(height * 0.8))  # Set initial window size to 80% of screen size
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))  # Set minimum window size
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.centralwidget.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #e0e0e0;
                color: #333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QTableView {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.verticalLayout.setSpacing(0)  # Remove spacing
        
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        
        # Mejorar la apariencia de las pestañas
        tab_font = QtGui.QFont()
        tab_font.setBold(True)
        tab_font.setPointSize(8)  # Aumentar tamaño de fuente de las pestañas
        self.tabWidget.setFont(tab_font)
        
        # Estilizar las pestañas para que sean más atractivas
        self.tabWidget.setStyleSheet("""
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)
        
        self.verticalLayout.addWidget(self.tabWidget, stretch=1)  # Ensure the tab widget occupies maximum space
        
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabLayout = QtWidgets.QVBoxLayout(self.tab)
        self.tabLayout.setObjectName("tabLayout")
        self.tabLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.tabLayout.setSpacing(0)  # Remove spacing
        self.tab.setLayout(self.tabLayout)  # Ensure the layout is set for the tab
        
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setSpacing(10)
        
        # Mejorar la apariencia de los labels principales
        self.label = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Aumentar tamaño de fuente a 10pt
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label.setStyleSheet("color: #2c3e50; padding: 5px;")  # Añadir color y padding
        self.horizontalLayout.addWidget(self.label)
        
        # Mejorar la apariencia del campo de texto
        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setPlaceholderText("Ingrese el símbolo del ticker")
        self.lineEdit.setMinimumHeight(30)  # Aumentar altura
        self.lineEdit.setFont(QtGui.QFont("Arial", 10))  # Establecer fuente más grande
        self.lineEdit.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 1px solid #4a90d9;
                background-color: #ffffff;
            }
        """)
        self.horizontalLayout.addWidget(self.lineEdit)
        
        # Mejorar la apariencia del botón de búsqueda, pero conservando el color original
        self.pushButton = QtWidgets.QPushButton(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Aumentar tamaño de fuente a 10pt
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setFixedSize(120, 35)  # Aumentar tamaño
        self.pushButton.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #e0e0e0;
                color: #333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        self.pushButton.clicked.connect(self.on_search_clicked)
        self.horizontalLayout.addWidget(self.pushButton)
        
        self.tabLayout.addLayout(self.horizontalLayout)
        
        self.progressBar = QtWidgets.QProgressBar(self.tab)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)  # Initially hidden
        self.tabLayout.addWidget(self.progressBar)
        
        self.label_2 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Aumentar tamaño de fuente a 10pt
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_2.setStyleSheet("color: #2c3e50; margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")

        # Update the search fields to be visible but disabled by default
        self.search_google = QtWidgets.QLineEdit(self.tab)
        self.search_google.setPlaceholderText("Buscar en Google Finance")
        self.search_google.setObjectName("search_google")
        self.search_google.textChanged.connect(lambda: self.filter_table(self.tableView, self.search_google.text()))
        self.search_google.setVisible(True)  # Make visible by default
        self.search_google.setEnabled(False)  # But disabled by default until search completes
        self.search_google.setMinimumHeight(28)  # Altura mínima
        self.search_google.setFont(QtGui.QFont("Arial", 9))
        self.search_google.setStyleSheet("""
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 1px solid #4a90d9;
                background-color: #ffffff;
            }
            QLineEdit:disabled {
                background-color: #e9e9e9;
                color: #888888;
            }
        """)

        self.google_layout = QtWidgets.QHBoxLayout()
        self.google_layout.addWidget(self.label_2)
        self.google_layout.addWidget(self.search_google)
        self.tabLayout.addLayout(self.google_layout)

        self.tableView = QtWidgets.QTableView(self.tab)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)  # Adjust size to contents
        self.tableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Remove horizontal scroll
        self.tabLayout.addWidget(self.tableView)
        
        # Set the header labels to bold
        header = self.tableView.horizontalHeader()
        header_font = header.font()
        header_font.setBold(True)
        header.setFont(header_font)
        
        self.label_4 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Aumentar tamaño de fuente a 10pt
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_4.setStyleSheet("color: #2c3e50; margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")

        self.search_yahoo = QtWidgets.QLineEdit(self.tab)
        self.search_yahoo.setPlaceholderText("Buscar en Yahoo Finance")
        self.search_yahoo.setObjectName("search_yahoo")
        self.search_yahoo.textChanged.connect(lambda: self.filter_table(self.tableView_3, self.search_yahoo.text()))
        self.search_yahoo.setVisible(True)  # Make visible by default
        self.search_yahoo.setEnabled(False)  # But disabled by default until search completes
        self.search_yahoo.setMinimumHeight(28)  # Altura mínima
        self.search_yahoo.setFont(QtGui.QFont("Arial", 9))
        self.search_yahoo.setStyleSheet("""
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 1px solid #4a90d9;
                background-color: #ffffff;
            }
            QLineEdit:disabled {
                background-color: #e9e9e9;
                color: #888888;
            }
        """)

        self.yahoo_layout = QtWidgets.QHBoxLayout()
        self.yahoo_layout.addWidget(self.label_4)
        self.yahoo_layout.addWidget(self.search_yahoo)
        self.tabLayout.addLayout(self.yahoo_layout)
        
        self.tableView_3 = QtWidgets.QTableView(self.tab)
        self.tableView_3.setObjectName("tableView_3")
        self.tableView_3.horizontalHeader().setStretchLastSection(True)
        self.tableView_3.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)  # Adjust size to contents
        self.tableView_3.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Remove horizontal scroll
        self.tabLayout.addWidget(self.tableView_3)
        
        # Set the header labels to bold
        header_3 = self.tableView_3.horizontalHeader()
        header_font_3 = header_3.font()
        header_font_3.setBold(True)
        header_3.setFont(header_font_3)
        
        self.label_5 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Aumentar tamaño de fuente a 10pt
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_5.setStyleSheet("color: #2c3e50; margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")

        self.search_macrotrends = QtWidgets.QLineEdit(self.tab)
        self.search_macrotrends.setPlaceholderText("Buscar en Macrotrends")
        self.search_macrotrends.setObjectName("search_macrotrends")
        self.search_macrotrends.textChanged.connect(lambda: self.filter_table(self.tableView_4, self.search_macrotrends.text()))
        self.search_macrotrends.setVisible(True)  # Make visible by default
        self.search_macrotrends.setEnabled(False)  # But disabled by default until search completes
        self.search_macrotrends.setMinimumHeight(28)  # Altura mínima
        self.search_macrotrends.setFont(QtGui.QFont("Arial", 9))
        self.search_macrotrends.setStyleSheet("""
            QLineEdit {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f8f8;
            }
            QLineEdit:focus {
                border: 1px solid #4a90d9;
                background-color: #ffffff;
            }
            QLineEdit:disabled {
                background-color: #e9e9e9;
                color: #888888;
            }
        """)

        self.macrotrends_layout = QtWidgets.QHBoxLayout()
        self.macrotrends_layout.addWidget(self.label_5)
        self.macrotrends_layout.addWidget(self.search_macrotrends)
        self.tabLayout.addLayout(self.macrotrends_layout)
        
        self.tableView_4 = QtWidgets.QTableView(self.tab)
        self.tableView_4.setObjectName("tableView_4")
        self.tableView_4.horizontalHeader().setStretchLastSection(True)
        self.tableView_4.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)  # Adjust size to contents
        self.tableView_4.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Remove horizontal scroll
        self.tabLayout.addWidget(self.tableView_4)
        
        # Set the header labels to bold
        header_4 = self.tableView_4.horizontalHeader()
        header_font_4 = header_4.font()
        header_font_4.setBold(True)
        header_4.setFont(header_font_4)
        
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.buttonLayout.setContentsMargins(10, 10, 10, 10)
        self.buttonLayout.setSpacing(10)
        
        self.balanceButton = QtWidgets.QPushButton("Balance", self.tab)
        self.balanceButton.setFixedHeight(30)  # Maintain button height
        self.balanceButton.setFont(font)  # Set font to bold
        self.balanceButton.setStyleSheet("padding: 5px;")  # Add padding for better readability
        self.flujoCajaButton = QtWidgets.QPushButton("Flujo de Caja", self.tab)
        self.flujoCajaButton.setFixedHeight(30)  # Maintain button height
        self.flujoCajaButton.setFont(font)  # Set font to bold
        self.flujoCajaButton.setStyleSheet("padding: 5px;")  # Add padding for better readability
        self.perdidasGananciasButton = QtWidgets.QPushButton("Cuenta de Pérdidas y Ganancias", self.tab)
        self.perdidasGananciasButton.setFixedHeight(30)  # Maintain button height
        self.perdidasGananciasButton.setFont(font)  # Set font to bold
        self.perdidasGananciasButton.setStyleSheet("padding: 5px;")  # Add padding for better readability
        
        self.buttonLayout.addWidget(self.balanceButton)
        self.buttonLayout.addWidget(self.flujoCajaButton)
        self.buttonLayout.addWidget(self.perdidasGananciasButton)
        
        self.balanceButton.setVisible(False)
        self.flujoCajaButton.setVisible(False)
        self.perdidasGananciasButton.setVisible(False)
        
        self.tabLayout.addLayout(self.buttonLayout)
        
        # Mejorar la apariencia del indicador de estado
        self.statusLabel = QtWidgets.QLabel(self.tab)
        self.statusLabel.setObjectName("statusLabel")
        self.statusLabel.setText("Esperando búsqueda")
        self.statusLabel.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
        self.statusLabel.setStyleSheet("color: #555; padding: 5px; font-style: italic;")
        self.tabLayout.addWidget(self.statusLabel, alignment=QtCore.Qt.AlignLeft)
        
        self.tabLayout.setContentsMargins(10, 10, 10, 0)  # Adjust bottom margin to 0
        self.tabLayout.setSpacing(10)
        
        self.tabWidget.addTab(self.tab, "")
        
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab_2_layout = QtWidgets.QVBoxLayout(self.tab_2)
        self.tab_2_layout.setObjectName("tab_2_layout")
        self.tab_2_layout.setContentsMargins(10, 10, 10, 10)  # Add margins
        self.tab_2_layout.setSpacing(10)  # Add spacing
        
        self.label_equivalentes = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Increase font size
        self.label_equivalentes.setFont(font)
        self.label_equivalentes.setObjectName("label_equivalentes")
        self.label_equivalentes.setStyleSheet("color: #2c3e50; margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        self.tab_2_layout.addWidget(self.label_equivalentes)
        
        self.label_balance = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Increase font size
        self.label_balance.setFont(font)
        self.label_balance.setObjectName("label_balance")
        self.label_balance.setStyleSheet("color: #2c3e50; margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        self.tab_2_layout.addWidget(self.label_balance)
        
        self.tableView_balance = QtWidgets.QTableView(self.tab_2)
        self.tableView_balance.setObjectName("tableView_balance")
        self.tableView_balance.horizontalHeader().setStretchLastSection(True)
        self.tableView_balance.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)  # Adjust size to contents
        self.tableView_balance.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Remove horizontal scroll
        self.tab_2_layout.addWidget(self.tableView_balance)
        
        # Set the header labels to bold
        header_balance = self.tableView_balance.horizontalHeader()
        header_font_balance = header_balance.font()
        header_font_balance.setBold(True)
        header_balance.setFont(header_font_balance)
        
        self.label_cash_flow = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Increase font size
        self.label_cash_flow.setFont(font)
        self.label_cash_flow.setObjectName("label_cash_flow")
        self.label_cash_flow.setStyleSheet("color: #2c3e50; margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        self.tab_2_layout.addWidget(self.label_cash_flow)
        
        self.tableView_cash_flow = QtWidgets.QTableView(self.tab_2)
        self.tableView_cash_flow.setObjectName("tableView_cash_flow")
        self.tableView_cash_flow.horizontalHeader().setStretchLastSection(True)
        self.tableView_cash_flow.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)  # Adjust size to contents
        self.tableView_cash_flow.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Remove horizontal scroll
        self.tab_2_layout.addWidget(self.tableView_cash_flow)
        
        # Set the header labels to bold
        header_cash_flow = self.tableView_cash_flow.horizontalHeader()
        header_font_cash_flow = header_cash_flow.font()
        header_font_cash_flow.setBold(True)
        header_cash_flow.setFont(header_font_cash_flow)
        
        self.label_income_statement = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)  # Increase font size
        self.label_income_statement.setFont(font)
        self.label_income_statement.setObjectName("label_income_statement")
        self.label_income_statement.setStyleSheet("color: #2c3e50; margin-top: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        self.tab_2_layout.addWidget(self.label_income_statement)
        
        self.tableView_income_statement = QtWidgets.QTableView(self.tab_2)
        self.tableView_income_statement.setObjectName("tableView_income_statement")
        self.tableView_income_statement.horizontalHeader().setStretchLastSection(True)
        self.tableView_income_statement.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)  # Adjust size to contents
        self.tableView_income_statement.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # Remove horizontal scroll
        self.tab_2_layout.addWidget(self.tableView_income_statement)
        
        # Set the header labels to bold
        header_income_statement = self.tableView_income_statement.horizontalHeader()
        header_font_income_statement = header_income_statement.font()
        header_font_income_statement.setBold(True)
        header_income_statement.setFont(header_font_income_statement)
        
        self.tabWidget.addTab(self.tab_2, "")
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, int(width * 0.8), 26))  # Adjust the menu bar width
        self.menubar.setObjectName("menubar")
        self.menuArchivo = QtWidgets.QMenu(self.menubar)
        self.menuArchivo.setObjectName("menuArchivo")
        self.menuAyuda = QtWidgets.QMenu(self.menubar)
        self.menuAyuda.setObjectName("menuAyuda")
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.actionExportar = QtWidgets.QAction(MainWindow)
        self.actionExportar.setObjectName("actionExportar")
        self.actionExportar.triggered.connect(lambda: exportar_datos(self))
        self.actionImportar = QtWidgets.QAction(MainWindow)
        self.actionImportar.setObjectName("actionImportar")
        self.actionImportar.triggered.connect(lambda: importar_datos(self))
        self.actionEquivalencias = QtWidgets.QAction(MainWindow)
        self.actionEquivalencias.setObjectName("actionEquivalencias")
        self.actionSalir = QtWidgets.QAction(MainWindow)
        self.actionSalir.setObjectName("actionSalir")
        self.actionSalir.triggered.connect(lambda: QtWidgets.QApplication.quit())
        self.actionDocumentaci_n = QtWidgets.QAction(MainWindow)
        self.actionDocumentaci_n.setObjectName("actionDocumentaci_n")
        self.actionAcerca_de = QtWidgets.QAction(MainWindow)
        self.actionAcerca_de.setObjectName("actionAcerca_de")
        
        self.menuArchivo.addAction(self.actionExportar)
        self.menuArchivo.addAction(self.actionImportar)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.actionEquivalencias)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.actionSalir)
        self.menuAyuda.addAction(self.actionDocumentaci_n)
        self.menuAyuda.addAction(self.actionAcerca_de)
        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Scrapper de datos financieros"))
        self.label_2.setText(_translate("MainWindow", "Datos de Google Finance"))
        self.label.setText(_translate("MainWindow", "Ticket:"))
        self.label_4.setText(_translate("MainWindow", "Datos de Yahoo Finance"))
        self.label_5.setText(_translate("MainWindow", "Datos de Macrotrends"))
        self.pushButton.setText(_translate("MainWindow", "Buscar"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Ingrese el símbolo del ticker"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Principal"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Datos equivalentes"))
        self.menuArchivo.setTitle(_translate("MainWindow", "Archivo"))
        self.menuAyuda.setTitle(_translate("MainWindow", "Ayuda"))
        self.actionExportar.setText(_translate("MainWindow", "Exportar"))
        self.actionImportar.setText(_translate("MainWindow", "Importar"))
        self.actionEquivalencias.setText(_translate("MainWindow", "Equivalencias"))
        self.actionSalir.setText(_translate("MainWindow", "Salir"))
        self.actionDocumentaci_n.setText(_translate("MainWindow", "Documentación"))
        self.actionAcerca_de.setText(_translate("MainWindow", "Acerca de")) 
        self.label_equivalentes.setText(_translate("MainWindow", "Datos Equivalentes"))
        self.label_cash_flow.setText(_translate("MainWindow", "Datos de Flujo de Caja"))
        self.label_income_statement.setText(_translate("MainWindow", "Cuenta de Pérdidas y Ganancias"))
        self.label_balance.setText(_translate("MainWindow", "Datos de Balance"))

    def filter_table(self, table_view, text):
        model = table_view.model()
        if model is None:
            return
        for row in range(model.rowCount()):
            match = False
            for col in range(model.columnCount()):
                item = model.index(row, col).data()
                if text.lower() in item.lower():
                    match = True
                    break
            table_view.setRowHidden(row, not match)

    def on_search_clicked(self):
        # Deshabilitar los campos de búsqueda al inicio de la búsqueda
        self.search_google.setEnabled(False)
        self.search_yahoo.setEnabled(False)
        self.search_macrotrends.setEnabled(False)
        
        # Iniciar la búsqueda
        buscar_datos(self)
        # After a successful search, make the search boxes visible
        self.search_google.setVisible(True)
        self.search_yahoo.setVisible(True)
        self.search_macrotrends.setVisible(True)