from PyQt6 import QtWidgets

from controlador._formularios_usuario import (
    llenar_combo_carreras,
    refrescar_padre,
    seleccionar_combo_por_texto,
    validar_basicos,
    validar_password,
    validar_unicos_edicion,
)
from modelo.Usuario import TutorAcademico
from utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_editar_cuenta_TA import Ui_frmEditarTA


class ControlVentanaEditarTA(QtWidgets.QWidget, Ui_frmEditarTA):
    def __init__(self, usuario: TutorAcademico, parent=None):
        super().__init__()
        self.usuario = usuario
        self.parent_controller = parent
        self.setupUi(self)
        llenar_combo_carreras(self.cbxCarrera)
        self._cargar_usuario()
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def _cargar_usuario(self):
        self.txtNombres.setText(self.usuario.nombres)
        self.txtApellidos.setText(self.usuario.apellidos)
        self.txtCedula.setText(self.usuario.cedula)
        self.txtCorreoElectronico.setText(self.usuario.email)
        seleccionar_combo_por_texto(self.cbxCarrera, self.usuario.carrera)

    def guardar(self):
        try:
            carrera = self.cbxCarrera.currentText().strip()
            validar_basicos(
                self.txtNombres.text(),
                self.txtApellidos.text(),
                self.txtCedula.text(),
                self.txtCorreoElectronico.text(),
            )
            validar_password(self.txtContrasenia.text(), self.txtConfirmarContrasenia.text(), False)
            if not carrera:
                raise ValidacionError("La carrera es obligatoria.")
            validar_unicos_edicion(
                self.usuario.id_usuario,
                self.txtCorreoElectronico.text().strip(),
                self.txtCedula.text().strip(),
            )
            self.usuario.nombres = self.txtNombres.text().strip()
            self.usuario.apellidos = self.txtApellidos.text().strip()
            self.usuario.cedula = self.txtCedula.text().strip()
            self.usuario.email = self.txtCorreoElectronico.text().strip()
            self.usuario.carrera = carrera
            if self.txtContrasenia.text():
                self.usuario.password = self.usuario.encriptar_password(self.txtContrasenia.text())
            self.usuario.guardar()
            QtWidgets.QMessageBox.information(self, "Tutor actualizado", "Cambios guardados correctamente.")
            refrescar_padre(self.parent_controller)
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))
