from PyQt6 import QtWidgets

from controlador.ControlUsuario import ControlUsuario
from controlador._formularios_usuario import llenar_combo_carreras, refrescar_padre, validar_basicos, validar_password
from modelo.utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_crear_cuenta_TA import Ui_frmCrearCuentaTA


class ControlVentanaCrearTA(QtWidgets.QWidget, Ui_frmCrearCuentaTA):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_controller = parent
        self.usuarios = ControlUsuario()
        self.setupUi(self)
        if hasattr(self, "cbxCarrera"):
            llenar_combo_carreras(self.cbxCarrera)
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def guardar(self):
        try:
            carrera = self._carrera()
            validar_basicos(
                self.txtNombres.text(),
                self.txtApellidos.text(),
                self.txtCedula.text(),
                self.txtCorreoElectronico.text(),
            )
            validar_password(self.txtContrasenia.text(), self.txtConfirmarContrasenia.text(), True)
            if not carrera:
                raise ValidacionError("La carrera es obligatoria.")
            self.usuarios.registrar_tutor_academico(
                self.txtNombres.text().strip(),
                self.txtApellidos.text().strip(),
                self.txtCedula.text().strip(),
                self.txtCorreoElectronico.text().strip(),
                self.txtContrasenia.text(),
                carrera,
            )
            QtWidgets.QMessageBox.information(self, "Tutor creado", "Tutor academico registrado correctamente.")
            refrescar_padre(self.parent_controller)
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo crear", str(error))

    def _carrera(self) -> str:
        if hasattr(self, "txtCarrera"):
            return self.txtCarrera.text().strip()
        return self.cbxCarrera.currentText().strip()

