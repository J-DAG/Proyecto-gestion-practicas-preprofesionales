from PyQt6 import QtWidgets

from configuracion.ajustes import ROLES
from controlador.ControlUsuario import ControlUsuario
from controlador.ControlVentanaAdmin import ControlVentanaAdmin
from controlador.ControlVentanaCoordinador import ControlVentanaCoordinador
from controlador.ControlVentanaEstudiante import ControlVentanaEstudiante
from controlador.ControlVentanaTA import ControlVentanaTA
from controlador.ControlVentanaTE import ControlVentanaTE
from modelo.Usuario import Administrador, Coordinador, Estudiante, TutorAcademico, TutorEmpresarial
from utilidades.Excepciones import SistemaPracticasError
from vista.estilos import EstilosClase
from vista.ui_inicio_sesion import Ui_frmInicioSesion


class ControlPrincipal(QtWidgets.QWidget,Ui_frmInicioSesion,
):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.usuarios = ControlUsuario()
        self.ventana_usuario = None
        self.btnIniciarSesion.clicked.connect(self._login)
        self.btnCrearCuenta.clicked.connect(self.crear_cuenta)
        self.lblTitulo.setFont(EstilosClase.titulo())

    def _login(self) -> None:
        try:
            usuario = self.usuarios.login(
                self.txtUsuario.text().strip(),
                self.txtContrasenia.text().strip(),
            )
            if isinstance(usuario, Administrador) or usuario.rol == ROLES["ADMINISTRADOR"]:
                self.ventana_usuario = ControlVentanaAdmin(usuario, self)
            elif isinstance(usuario, Coordinador) or usuario.rol == ROLES["COORDINADOR"]:
                self.ventana_usuario = ControlVentanaCoordinador(usuario, self)
            elif isinstance(usuario, Estudiante) or usuario.rol == ROLES["ESTUDIANTE"]:
                self.ventana_usuario = ControlVentanaEstudiante(usuario, self)
            elif isinstance(usuario, TutorAcademico) or usuario.rol == ROLES["TUTOR_ACADEMICO"]:
                self.ventana_usuario = ControlVentanaTA(usuario, self)
            elif isinstance(usuario, TutorEmpresarial) or usuario.rol == ROLES["TUTOR_EMPRESARIAL"]:
                self.ventana_usuario = ControlVentanaTE(usuario, self)
            else:
                QtWidgets.QMessageBox.warning(self, "Rol no soportado", "Rol sin vista grafica asignada.")
                return

            self.ventana_usuario.show()
            self.hide()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "Error de inicio de sesion", str(error))
        except Exception as error:
            QtWidgets.QMessageBox.critical(self, "Error al abrir ventana", str(error))

    def volver_a_login(self) -> None:
        self.txtContrasenia.clear()
        self.show()

    def crear_cuenta(self) -> None:
        QtWidgets.QMessageBox.information(
            self,
            "Crear cuenta",
            "El registro de usuarios se gestiona desde el administrador.",
        )
