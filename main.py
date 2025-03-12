import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtGui import QIcon
from view.main_view import Ui_MainWindow
from view.equivalencias_view import EquivalenciasWindowUI
from view.ayuda_view import Ui_AyudaWindow  
from model.database_setup import initialize_database  

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('resources/icon.ico'))
        self.actionEquivalencias.triggered.connect(self.open_equivalencias_window)
        self.actionAcerca_de.triggered.connect(lambda: self.open_ayuda_window('acerca_de'))
        self.actionDocumentaci_n.triggered.connect(lambda: self.open_ayuda_window('documentacion'))  
        self.actionSalir.triggered.connect(self.close_application)
        self.showMaximized()

    def open_equivalencias_window(self):
        self.equivalencias_window = QDialog()
        self.ui = EquivalenciasWindowUI()
        self.ui.setupUi(self.equivalencias_window)
        self.equivalencias_window.exec_()

    def open_ayuda_window(self, tab_name):
        self.ayuda_window = QDialog()
        self.ui = Ui_AyudaWindow()
        self.ui.setupUi(self.ayuda_window, tab_name)
        self.ayuda_window.exec_()

    def close_application(self):
        QApplication.quit()

def main():
    # Initialize the database
    initialize_database()
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('resources/icon.ico'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
