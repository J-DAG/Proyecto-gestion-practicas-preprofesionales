from PyQt6 import QtWidgets

from controlador._formularios_usuario import (
    llenar_combo_empresas,
    refrescar_padre,
    seleccionar_combo_por_dato,
    validar_basicos,
    validar_password,
    validar_unicos_edicion,
    valor_combo,
)
from modelo.Empresa import Empresa
from modelo.Usuario import TutorEmpresarial
from utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_editar_cuenta_TE import Ui_frmEditarTE


class ControlVentanaEditarTE(QtWidgets.QWidget, Ui_frmEditarTE):
    def __init__(self, usuario: TutorEmpresarial, parent=None):
        super().__init__()
        self.usuario = usuario
        self.parent_controller = parent
        self.setupUi(self)
        llenar_combo_empresas(self.cbxListaEmpresa)
        self._cargar_usuario()
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def _cargar_usuario(self):
        self.txtNombres.setText(self.usuario.nombres)
        self.txtApellidos.setText(self.usuario.apellidos)
        self.txtCedula.setText(self.usuario.cedula)
        self.txtCorreoElectronico.setText(self.usuario.email)
        seleccionar_combo_por_dato(self.cbxListaEmpresa, self.usuario.id_empresa)
        self.txtCargo.setText(self.usuario.cargo)

    def guardar(self):
        try:
            id_empresa = str(valor_combo(self.cbxListaEmpresa))
            cargo = self.txtCargo.text().strip()
            validar_basicos(
                self.txtNombres.text(),
                self.txtApellidos.text(),
                self.txtCedula.text(),
                self.txtCorreoElectronico.text(),
            )
            validar_password(self.txtContrasenia.text(), self.txtConfirmarContrasenia.text(), False)
            if not id_empresa:
                raise ValidacionError("Debe seleccionar una empresa.")
            if not cargo:
                raise ValidacionError("El cargo es obligatorio.")
            Empresa.obtener_por_id(id_empresa)
            validar_unicos_edicion(
                self.usuario.id_usuario,
                self.txtCorreoElectronico.text().strip(),
                self.txtCedula.text().strip(),
            )
            self.usuario.nombres = self.txtNombres.text().strip()
            self.usuario.apellidos = self.txtApellidos.text().strip()
            self.usuario.cedula = self.txtCedula.text().strip()
            self.usuario.email = self.txtCorreoElectronico.text().strip()
            self.usuario.id_empresa = id_empresa
            self.usuario.cargo = cargo
            if self.txtContrasenia.text():
                self.usuario.password = self.usuario.encriptar_password(self.txtContrasenia.text())
            self.usuario.guardar()
            QtWidgets.QMessageBox.information(self, "Tutor actualizado", "Cambios guardados correctamente.")
            refrescar_padre(self.parent_controller)
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))
