from PyQt6 import QtWidgets

from modelo.Usuario import Estudiante
from vista.ui_main_window_estudiante import Ui_MainWindowEstudiante


class ControlVentanaEstudiante(QtWidgets.QMainWindow, Ui_MainWindowEstudiante):
    def __init__(self, usuario: Estudiante, login=None, parent=None):
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
