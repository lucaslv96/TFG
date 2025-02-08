from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from controller.equivalencias_controller import confirmar_restauracion, actualizar_valor_inmediato, populate_mappings, previous_values  # Importar la función
from controller.equivalencias_controller import populate_table
from controller.datos_equivalentes_controller import mostrar_datos_equivalentes, show_chart  # Importar las nuevas funciones

class EquivalenciasWindowUI(object):
    def setupUi(self, EquivalenciasWindow):
        EquivalenciasWindow.setObjectName("EquivalenciasWindow")
        EquivalenciasWindow.resize(800, 600)
        
        EquivalenciasWindow.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QTableView {
                background-color: white;
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
            QPushButton#restoreButton {
                background-color: #e0e0e0;
            }
            QPushButton#restoreButton:hover {
                background-color: #d0d0d0;
            }
        """)

        self.verticalLayout = QtWidgets.QVBoxLayout(EquivalenciasWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(10)

        self.label = QtWidgets.QLabel("Establece equivalencias", EquivalenciasWindow)
        self.label.setMinimumHeight(50)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.label.setFont(font)
        self.verticalLayout.addWidget(self.label)

        # Crear el modelo para la tabla
        self.tableModel = QtGui.QStandardItemModel()
        self.tableModel.setHorizontalHeaderLabels(["Google Finance", "Macrotrends", "Yahoo Finance"])

        # Configurar la tabla con el modelo
        self.tableView = QtWidgets.QTableView(EquivalenciasWindow)
        self.tableView.setModel(self.tableModel)
        self.tableView.verticalHeader().setVisible(False)  # Ocultar la numeración de las filas

        # Ajustar el tamaño de las columnas para que ocupen todo el ancho
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Estilo de las cabeceras: negrita
        self.tableView.setStyleSheet("""
            QHeaderView::section {
                font-weight: bold;
                font-size: 10pt;
                text-align: center;
            }
        """)

        self.verticalLayout.addWidget(self.tableView)

        self.statusbar = QtWidgets.QStatusBar(EquivalenciasWindow)
        self.statusbar.showMessage("")

        button_font = QtGui.QFont()
        button_font.setBold(True)

        self.balanceButton = QtWidgets.QPushButton("Balance", EquivalenciasWindow)
        self.balanceButton.setFont(button_font)

        self.cashflowButton = QtWidgets.QPushButton("Flujo de Caja", EquivalenciasWindow)
        self.cashflowButton.setFont(button_font)

        self.incomeButton = QtWidgets.QPushButton("Cuenta de Pérdidas y Ganancias", EquivalenciasWindow)
        self.incomeButton.setFont(button_font)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(10, 10, 10, 10)
        self.buttons_layout.setSpacing(10)
        self.buttons_layout.addWidget(self.balanceButton)
        self.buttons_layout.addWidget(self.cashflowButton)
        self.buttons_layout.addWidget(self.incomeButton)
        self.verticalLayout.addLayout(self.buttons_layout)

        self.restoreButton = QtWidgets.QPushButton("Restaurar Valores por Defecto", EquivalenciasWindow)
        self.restoreButton.setFont(button_font)
        self.restoreButton.setObjectName("restoreButton")
        self.verticalLayout.addWidget(self.restoreButton)

        self.balanceButton.clicked.connect(lambda: self.set_data_type_and_populate('balance'))
        self.cashflowButton.clicked.connect(lambda: self.set_data_type_and_populate('cashflow'))
        self.incomeButton.clicked.connect(lambda: self.set_data_type_and_populate('income'))

        # Evento para restaurar valores por defecto
        self.restoreButton.clicked.connect(lambda: confirmar_restauracion(self))

        # Populate the mappings for initial values to IDs
        populate_mappings()

        # Conectar la señal de cambio de datos a la función de actualización inmediata
        self.tableModel.itemChanged.connect(lambda item: actualizar_valor_inmediato(self, item))

        # Populate the table with balance data initially
        self.current_data_type = 'balance'
        populate_table(self, 'balance')

        # Store initial values in the previous_values mapping
        for row in range(self.tableModel.rowCount()):
            for col in range(self.tableModel.columnCount()):
                previous_values[(row, col)] = self.tableModel.item(row, col).text()

        self.retranslateUi(EquivalenciasWindow)
        QtCore.QMetaObject.connectSlotsByName(EquivalenciasWindow)

    def set_data_type_and_populate(self, data_type):
        self.current_data_type = data_type
        populate_table(self, data_type)
        for row in range(self.tableModel.rowCount()):
            for col in range(self.tableModel.columnCount()):
                previous_values[(row, col)] = self.tableModel.item(row, col).text()

    def retranslateUi(self, EquivalenciasWindow):
        _translate = QtCore.QCoreApplication.translate
        EquivalenciasWindow.setWindowTitle(_translate("EquivalenciasWindow", "Equivalencias"))
