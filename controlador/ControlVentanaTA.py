from PyQt6 import QtWidgets

from modelo.Usuario import TutorAcademico
from vista.ui_main_window_TA import Ui_MainWindowTA


class ControlVentanaTA(QtWidgets.QMainWindow, Ui_MainWindowTA):
    def __init__(self, usuario: TutorAcademico, login=None, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.login = login
        self.setupUi(self)
        self.btnCerrarSesion_2.clicked.connect(self.salir)
        self.btnCerrarSesion.triggered.connect(self.salir)

    def salir(self):
        self.close()
        if self.login is not None:
            self.login.volver_a_login()
