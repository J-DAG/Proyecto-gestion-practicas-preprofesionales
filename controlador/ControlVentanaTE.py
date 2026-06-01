from PyQt6 import QtWidgets

from modelo.Usuario import TutorEmpresarial
from vista.ui_main_window_TE import Ui_MainWindowTE


class ControlVentanaTE(QtWidgets.QMainWindow, Ui_MainWindowTE):
    def __init__(self, usuario: TutorEmpresarial, login=None, parent=None):
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
