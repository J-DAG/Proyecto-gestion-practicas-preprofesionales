from PyQt6 import QtWidgets

from controlador.ControlUsuario import ControlUsuario
from controlador._formularios_usuario import (
    llenar_combo_carreras,
    llenar_combo_ciclos,
    refrescar_padre,
    validar_basicos,
    validar_password,
    valor_combo,
)
from utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_crear_cuenta_estudiante import Ui_frmCrearCuentaEstudiante


class ControlVentanaCrearEstudiante(QtWidgets.QWidget, Ui_frmCrearCuentaEstudiante):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_controller = parent
        self.usuarios = ControlUsuario()
        self.setupUi(self)
        llenar_combo_carreras(self.cbxCarrera)
        llenar_combo_ciclos(self.cbsCicloActual)
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def guardar(self):
        try:
            password = self.txtContrasenia.text()
            confirmar = self.txtConfirmarContrasenia.text()
            validar_basicos(
                self.txtNombres.text(),
                self.txtApellidos.text(),
                self.txtCedula.text(),
                self.txtCorreoElectronico.text(),
            )
            validar_password(password, confirmar, True)
            carrera = self.cbxCarrera.currentText().strip()
            if not carrera:
                raise ValidacionError("La carrera es obligatoria.")
            self.usuarios.registrar_estudiante(
                self.txtNombres.text().strip(),
                self.txtApellidos.text().strip(),
                self.txtCedula.text().strip(),
                self.txtCorreoElectronico.text().strip(),
                password,
                carrera,
                int(valor_combo(self.cbsCicloActual)),
                True,
            )
            QtWidgets.QMessageBox.information(self, "Estudiante creado", "Estudiante registrado correctamente.")
            refrescar_padre(self.parent_controller)
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo crear", str(error))
