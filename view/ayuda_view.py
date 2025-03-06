from PyQt5 import QtCore, QtGui, QtWidgets
import os

class Ui_AyudaWindow(object):
    def setupUi(self, AyudaWindow, tab_name):
        AyudaWindow.setObjectName("AyudaWindow")
        AyudaWindow.resize(800, 600)  # Increased height for better appearance
        
        # Set a nicer application style and stylesheet
        AyudaWindow.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
                color: #444444;
                font-size: 10pt;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                color: #2c3e50;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d0d0d0;
            }
            QLabel {
                color: #333333;
                line-height: 140%;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 140%;
            }
        """)
        
        self.verticalLayout = QtWidgets.QVBoxLayout(AyudaWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)  # Add more padding
        
        self.tabWidget = QtWidgets.QTabWidget(AyudaWindow)
        self.tabWidget.setObjectName("tabWidget")
        
        # Improve about tab layout with better spacing and styling
        self.tab_acerca_de = QtWidgets.QWidget()
        self.tab_acerca_de.setObjectName("tab_acerca_de")
        
        # Create a better layout for the about page
        self.acerca_de_layout = QtWidgets.QVBoxLayout(self.tab_acerca_de)
        self.acerca_de_layout.setContentsMargins(20, 20, 20, 20)
        self.acerca_de_layout.setSpacing(20)
        
        # Create a top section with app icon and title
        self.top_section = QtWidgets.QHBoxLayout()
        self.top_section.setSpacing(20)
        
        # Add application icon
        icon_path = os.path.join("resources", "icon.ico")
        if os.path.exists(icon_path):
            self.iconLabel = QtWidgets.QLabel()
            self.iconLabel.setPixmap(QtGui.QPixmap(icon_path).scaled(
                128, 128, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            self.iconLabel.setFixedSize(128, 128)
            self.top_section.addWidget(self.iconLabel)
        else:
            # Create a placeholder or a text logo if icon doesn't exist
            self.app_logo = QtWidgets.QLabel()
            self.app_logo.setText("📊")
            font = QtGui.QFont()
            font.setPointSize(48)
            self.app_logo.setFont(font)
            self.app_logo.setFixedSize(128, 128)
            self.app_logo.setAlignment(QtCore.Qt.AlignCenter)
            self.top_section.addWidget(self.app_logo)
        
        # Add title and version section
        self.title_section = QtWidgets.QVBoxLayout()
        
        self.app_title = QtWidgets.QLabel("Scrapper de datos financieros")
        title_font = QtGui.QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.app_title.setFont(title_font)
        self.title_section.addWidget(self.app_title)
        
        self.app_version = QtWidgets.QLabel("Versión 1.0.0")
        version_font = QtGui.QFont()
        version_font.setPointSize(10)
        version_font.setItalic(True)
        self.app_version.setFont(version_font)
        self.title_section.addWidget(self.app_version)
        
        self.app_tagline = QtWidgets.QLabel("Una herramienta para análisis de datos financieros")
        tagline_font = QtGui.QFont()
        tagline_font.setPointSize(10)
        self.app_tagline.setFont(tagline_font)
        self.title_section.addWidget(self.app_tagline)
        
        self.title_section.addStretch()
        self.top_section.addLayout(self.title_section)
        self.top_section.addStretch()
        
        # Add the top section to the main layout
        self.acerca_de_layout.addLayout(self.top_section)
        
        # Horizontal line as separator
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.acerca_de_layout.addWidget(self.line)
        
        # Create a QScrollArea for the description section
        self.scroll_area = QtWidgets.QScrollArea(self.tab_acerca_de)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        
        # Create a widget to contain the content for the scroll area
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        
        # Description section - now inside the scroll area
        self.description = QtWidgets.QLabel()
        self.description.setWordWrap(True)
        description_font = QtGui.QFont()
        description_font.setPointSize(10)
        self.description.setFont(description_font)
        self.description.setText("""
        <p>Esta aplicación permite obtener y visualizar datos financieros de diferentes fuentes como Yahoo Finance, Macrotrends y Google Finance.</p>
        <p>Los datos se pueden buscar utilizando el símbolo del ticker de la empresa y se muestran en tablas correspondientes.</p>
        <p>Además, los datos se pueden exportar a archivo Excel o SQLite para su análisis posterior.</p>
        """)
        self.scroll_layout.addWidget(self.description)
        
        # Features section - also inside the scroll area
        self.features_title = QtWidgets.QLabel("Características principales:")
        features_title_font = QtGui.QFont()
        features_title_font.setPointSize(12)
        features_title_font.setBold(True)
        self.features_title.setFont(features_title_font)
        self.scroll_layout.addWidget(self.features_title)
        
        features_list = [
            "Búsqueda de datos financieros por ticker de empresa",
            "Visualización de Balance General, Estado de Resultados y Flujo de Caja",
            "Comparación de datos entre diferentes fuentes",
            "Exportación de datos a Excel y SQLite",
            "Personalización de equivalencias entre conceptos financieros"
        ]
        
        self.features = QtWidgets.QLabel()
        self.features.setWordWrap(True)
        self.features.setFont(description_font)
        features_text = "<ul>"
        for feature in features_list:
            features_text += f"<li>{feature}</li>"
        features_text += "</ul>"
        self.features.setText(features_text)
        self.scroll_layout.addWidget(self.features)
        
        # Add stretch to push content to the top
        self.scroll_layout.addStretch()
        
        # Set the content widget to the scroll area
        self.scroll_area.setWidget(self.scroll_content)
        
        # Add the scroll area to the main layout
        self.acerca_de_layout.addWidget(self.scroll_area, 1)  # Give it a stretch factor of 1
        
        # Remove author section and copyright notice
        # These sections are now removed as requested
        
        self.tab_guia_rapida = QtWidgets.QWidget()
        self.tab_guia_rapida.setObjectName("tab_guia_rapida")
        self.verticalLayout_guia_rapida = QtWidgets.QVBoxLayout(self.tab_guia_rapida)
        self.verticalLayout_guia_rapida.setObjectName("verticalLayout_guia_rapida")
        self.verticalLayout_guia_rapida.setContentsMargins(20, 20, 20, 20)  # Add more padding
        
        self.guiaRapidaTitle = QtWidgets.QLabel("Guía Rápida de Uso")
        guia_title_font = QtGui.QFont()
        guia_title_font.setPointSize(16)
        guia_title_font.setBold(True)
        self.guiaRapidaTitle.setFont(guia_title_font)
        self.verticalLayout_guia_rapida.addWidget(self.guiaRapidaTitle)
        
        self.guiaRapidaLabel = QtWidgets.QLabel()
        self.guiaRapidaLabel.setObjectName("guiaRapidaLabel")
        self.guiaRapidaLabel.setWordWrap(True)
        guide_font = QtGui.QFont()
        guide_font.setPointSize(10)
        self.guiaRapidaLabel.setFont(guide_font)
        self.verticalLayout_guia_rapida.addWidget(self.guiaRapidaLabel)
        
        # Remove the screenshots section as requested
        
        # Add stretch at the end to push content to the top
        self.verticalLayout_guia_rapida.addStretch(1)
        
        self.tab_autor = QtWidgets.QWidget()
        self.tab_autor.setObjectName("tab_autor")
        self.verticalLayout_autor = QtWidgets.QVBoxLayout(self.tab_autor)
        self.verticalLayout_autor.setObjectName("verticalLayout_autor")
        self.verticalLayout_autor.setContentsMargins(20, 20, 20, 20)  # Add more padding
        
        self.autorLabel = QtWidgets.QLabel()
        self.autorLabel.setObjectName("autorLabel")
        self.autorLabel.setWordWrap(True)
        self.autorLabel.setFont(guide_font)
        self.verticalLayout_autor.addWidget(self.autorLabel)
        self.verticalLayout_autor.addStretch(1)
        
        self.tab_documentacion = QtWidgets.QWidget()
        self.tab_documentacion.setObjectName("tab_documentacion")
        self.verticalLayout_documentacion = QtWidgets.QVBoxLayout(self.tab_documentacion)
        self.verticalLayout_documentacion.setObjectName("verticalLayout_documentacion")
        self.verticalLayout_documentacion.setContentsMargins(20, 20, 20, 20)  # Add more padding
        
        self.textEdit = QtWidgets.QTextEdit(self.tab_documentacion)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setReadOnly(True)
        self.verticalLayout_documentacion.addWidget(self.textEdit)
        
        # Add all tabs
        self.tabWidget.addTab(self.tab_acerca_de, "")
        self.tabWidget.addTab(self.tab_guia_rapida, "")
        self.tabWidget.addTab(self.tab_autor, "")
        self.tabWidget.addTab(self.tab_documentacion, "")
        
        # Apply bold font to tab text
        for i in range(self.tabWidget.count()):
            tab_font = QtGui.QFont()
            tab_font.setBold(True)
            tab_font.setPointSize(10)  # Larger font size
            self.tabWidget.tabBar().setTabTextColor(i, QtGui.QColor("#2c3e50"))  # Darker text color
            self.tabWidget.tabBar().setFont(tab_font)
        
        self.verticalLayout.addWidget(self.tabWidget)
        
        self.retranslateUi(AyudaWindow)
        
        # Show the appropriate tab and manage tab visibility based on tab_name parameter
        if tab_name == 'acerca_de':
            self.tabWidget.setCurrentIndex(0)
            AyudaWindow.resize(800, 600)  # Better size for about tab
        elif tab_name == 'documentacion':
            self.tabWidget.setCurrentIndex(3)
            AyudaWindow.resize(900, 700)  # Larger size for documentation
        
        QtCore.QMetaObject.connectSlotsByName(AyudaWindow)

    def retranslateUi(self, AyudaWindow):
        _translate = QtCore.QCoreApplication.translate
        AyudaWindow.setWindowTitle(_translate("AyudaWindow", "Ayuda"))
        
        self.guiaRapidaLabel.setText(_translate("AyudaWindow", 
            "<h2>Cómo utilizar la aplicación</h2>"
            "<ol>"
            "<li><strong>Buscar datos financieros:</strong> Ingrese el símbolo del ticker de la empresa en el campo de texto y haga clic en 'Buscar'.</li>"
            "<li><strong>Visualizar datos:</strong> Los datos se mostrarán en tablas separadas para cada fuente (Google Finance, Yahoo Finance, Macrotrends).</li>"
            "<li><strong>Filtrar datos:</strong> Utilice los campos de búsqueda encima de cada tabla para filtrar los resultados.</li>"
            "<li><strong>Cambiar tipo de datos:</strong> Use los botones 'Balance', 'Flujo de Caja' y 'Cuenta de Pérdidas y Ganancias' para ver diferentes tipos de informes.</li>"
            "<li><strong>Exportar resultados:</strong> Desde el menú 'Archivo', seleccione 'Exportar' para guardar los datos en Excel o SQLite.</li>"
            "<li><strong>Gestionar equivalencias:</strong> Seleccione 'Equivalencias' en el menú 'Archivo' para establecer correspondencias entre diferentes fuentes.</li>"
            "</ol>"
        
        ))
        
        self.autorLabel.setText(_translate("AyudaWindow", 
            "<h1 style='color: #2c3e50;'>Sobre el Autor</h1>"
            "<div style='display: flex;'>"
            "<div style='padding: 20px;'>"
            "<h2>Lucas Lubian de Vega</h2>"
            "<p>Estudiante de Ingeniería Informática en Tecnologías de la Información en la Escuela Politécnica de Ingeniería de Gijón.</p>"
            "<h3>Contacto</h3>"
            "<p><strong>Email:</strong> uo271365@uniovi.es</p>"
            "<p><strong>LinkedIn:</strong> <a href='https://www.linkedin.com/in/lucas-lubián-de-vega-229913273/'>linkedin.com/in/lucas-lubián-de-vega-229913273/</a></p>"
            "</div>"
            "</div>"
        ))
        
        self.textEdit.setHtml(_translate("AyudaWindow", r"""
        <h1>Documentación del Software</h1>

        <h2>Instalación</h2>
        <p>Para instalar el programa, siga los siguientes pasos:</p>
        <ol>
            <li>Clonar el repositorio: <code>git clone <URL_DEL_REPOSITORIO></code></li>
            <li>Navegar al directorio del proyecto: <code>cd <NOMBRE_DEL_REPOSITORIO></code></li>
            <li>Instalar las dependencias: <code>pip install -r requirements.txt</code></li>
        </ol>
        
        <h3>Si deseas modificar el código fuente o contribuir al desarrollo del proyecto, sigue estos pasos para descargar y configurar el entorno:</h3>
        <ol>
            <li>Clonar repositorio:
                <pre><code>git clone https://github.com/lucaslv96/TFG.git
cd TFG</code></pre>
            </li>
            <li>Verificar la versión de Python:
                <p>Asegúrate de tener instalada la versión mínima recomendada de Python:</p>
                <pre><code>Python 3.12.3</code></pre>
                <p>Puedes verificar la versión instalada con el siguiente comando:</p>
                <pre><code>python --version</code></pre>
            </li>
            <li>Crear un entorno virtual (Opcional, pero recomendable):
                <pre><code>python -m venv venv</code></pre>
                <p>Para activarlo:</p>
                <ul>
                    <li>Windows: <pre><code>venv\Scripts\activate</code></pre></li>
                    <li>Linux/Mac: <pre><code>source venv/bin/activate</code></pre></li>
                </ul>
            </li>
            <li>Instalar dependencias:
                <pre><code>pip install -r requirements.txt</code></pre>
            </li>
            <li>Ejecutar el programa desde código fuente:
                <pre><code>python main.py</code></pre>
            </li>
        </ol>
        
        <h2>Uso del Programa</h2>
        <p>Para ejecutar el programa, navegue al directorio del proyecto y ejecute el siguiente comando:</p>
        <pre><code>python main.py</code></pre>
        <p>Al iniciar el programa, se abrirá la ventana principal con las siguientes opciones:</p>
        <ul>
            <li><strong>Buscar Datos:</strong> Ingrese el símbolo del ticker de la empresa y haga clic en "Buscar" para obtener los datos financieros.</li>
            <li><strong>Exportar Datos:</strong> Exporte los datos obtenidos a un archivo Excel o SQLite.</li>
            <li><strong>Importar Datos:</strong> Importe datos desde un archivo Excel o SQLite.</li>
            <li><strong>Equivalencias:</strong> Abra la ventana de equivalencias para establecer relaciones entre los datos de diferentes fuentes.</li>
            <li><strong>Acerca de:</strong> Información sobre el programa y el autor.</li>
        </ul>
        
        <h2>Solución de Problemas</h2>
        <h3>Problema: No se encuentran datos para el ticker ingresado</h3>
        <ul>
            <li>Asegúrese de que el símbolo del ticker sea correcto y esté en mayúsculas.</li>
            <li>Verifique su conexión a Internet.</li>
        </ul>
        
        <h3>Problema: Error al exportar o importar datos</h3>
        <ul>
            <li>Asegúrese de que el archivo de destino no esté en uso por otra aplicación.</li>
            <li>Verifique que el archivo tenga el formato correcto (Excel o SQLite).</li>
        </ul>
        
        <h2>Contacto</h2>
        <p>Para más información o soporte, contacte al autor:</p>
        <ul>
            <li><strong>Nombre:</strong> Lucas Lubian de Vega</li>
            <li><strong>Email:</strong> uo271365@uniovi.es</li>
        </ul>
        """))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_acerca_de), _translate("AyudaWindow", "Acerca de"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_guia_rapida), _translate("AyudaWindow", "Guía rápida"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_autor), _translate("AyudaWindow", "Autor"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_documentacion), _translate("AyudaWindow", "Documentación"))
