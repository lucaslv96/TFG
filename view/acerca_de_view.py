from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AcercaDeWindow(object):
    def setupUi(self, AcercaDeWindow):
        AcercaDeWindow.setObjectName("AcercaDeWindow")
        AcercaDeWindow.resize(600, 300)
        
        self.verticalLayout = QtWidgets.QVBoxLayout(AcercaDeWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.tabWidget = QtWidgets.QTabWidget(AcercaDeWindow)
        self.tabWidget.setObjectName("tabWidget")
        
        self.tab_acerca_de = QtWidgets.QWidget()
        self.tab_acerca_de.setObjectName("tab_acerca_de")
        self.horizontalLayout_acerca_de = QtWidgets.QHBoxLayout(self.tab_acerca_de)
        self.horizontalLayout_acerca_de.setObjectName("horizontalLayout_acerca_de")
        
        self.iconLabel = QtWidgets.QLabel(self.tab_acerca_de)
        self.iconLabel.setPixmap(QtGui.QPixmap("resources/icon.ico").scaled(192, 192, QtCore.Qt.KeepAspectRatio))
        self.horizontalLayout_acerca_de.addWidget(self.iconLabel)
        
        self.textLabel = QtWidgets.QLabel(self.tab_acerca_de)
        self.textLabel.setObjectName("textLabel")
        self.textLabel.setWordWrap(True)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.textLabel.setFont(font)
        self.horizontalLayout_acerca_de.addWidget(self.textLabel)
        
        self.tabWidget.addTab(self.tab_acerca_de, "")
        
        self.tab_guia_rapida = QtWidgets.QWidget()
        self.tab_guia_rapida.setObjectName("tab_guia_rapida")
        self.verticalLayout_guia_rapida = QtWidgets.QVBoxLayout(self.tab_guia_rapida)
        self.verticalLayout_guia_rapida.setObjectName("verticalLayout_guia_rapida")
        
        self.guiaRapidaLabel = QtWidgets.QLabel(self.tab_guia_rapida)
        self.guiaRapidaLabel.setObjectName("guiaRapidaLabel")
        self.guiaRapidaLabel.setWordWrap(True)
        self.guiaRapidaLabel.setFont(font)
        self.verticalLayout_guia_rapida.addWidget(self.guiaRapidaLabel)
        
        self.tabWidget.addTab(self.tab_guia_rapida, "")
        
        self.tab_autor = QtWidgets.QWidget()
        self.tab_autor.setObjectName("tab_autor")
        self.verticalLayout_autor = QtWidgets.QVBoxLayout(self.tab_autor)
        self.verticalLayout_autor.setObjectName("verticalLayout_autor")
        
        self.autorLabel = QtWidgets.QLabel(self.tab_autor)
        self.autorLabel.setObjectName("autorLabel")
        self.autorLabel.setWordWrap(True)
        self.autorLabel.setFont(font)
        self.verticalLayout_autor.addWidget(self.autorLabel)
        
        self.tabWidget.addTab(self.tab_autor, "")
        
        self.verticalLayout.addWidget(self.tabWidget)
        
        self.retranslateUi(AcercaDeWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(AcercaDeWindow)

    def retranslateUi(self, AcercaDeWindow):
        _translate = QtCore.QCoreApplication.translate
        AcercaDeWindow.setWindowTitle(_translate("AcercaDeWindow", "Acerca de"))
        self.textLabel.setText(_translate("AcercaDeWindow", 
            "Esta aplicación permite obtener y visualizar datos financieros de diferentes fuentes como Yahoo Finance, Macrotrends y Google Finance.\n\n"
            "Los datos se pueden buscar utilizando el símbolo del ticker de la empresa y se muestran en tablas correspondientes.\n\n"
            "Además, los datos se pueden exportar a un archivo Excel para su análisis posterior."
        ))
        self.guiaRapidaLabel.setText(_translate("AcercaDeWindow", 
            "Para usar esta aplicación:\n\n"
            "1. Ingrese el símbolo del ticker de la empresa en el campo de texto.\n"
            "2. Haga clic en 'Buscar' para obtener los datos financieros.\n"
            "3. Los datos se mostrarán en las tablas correspondientes.\n"
            "4. Haga clic en 'Exportar Resultados' para guardar los datos en un archivo Excel."
        ))
        self.autorLabel.setText(_translate("AcercaDeWindow", 
            "Autor:\n\n"
            "Nombre: Lucas Lubian de Vega\n\n"
            "Email: uo271365@uniovi.es"
        ))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_acerca_de), _translate("AcercaDeWindow", "Acerca de"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_guia_rapida), _translate("AcercaDeWindow", "Guía rápida"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_autor), _translate("AcercaDeWindow", "Autor"))
