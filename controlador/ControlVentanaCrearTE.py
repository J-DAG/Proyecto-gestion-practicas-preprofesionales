from PyQt6 import QtWidgets

from controlador.ControlUsuario import ControlUsuario
from controlador._formularios_usuario import llenar_combo_empresas, refrescar_padre, validar_basicos, validar_password, valor_combo
from utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_crear_cuenta_TE import Ui_frmCrearCuentaTA


class ControlVentanaCrearTE(QtWidgets.QWidget, Ui_frmCrearCuentaTA):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_controller = parent
        self.usuarios = ControlUsuario()
        self.setupUi(self)
        llenar_combo_empresas(self.cbxListaEmpresa)
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

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
            validar_password(self.txtContrasenia.text(), self.txtConfirmarContrasenia.text(), True)
            if not id_empresa:
                raise ValidacionError("Debe seleccionar una empresa.")
            if not cargo:
                raise ValidacionError("El cargo es obligatorio.")
            self.usuarios.registrar_tutor_empresarial(
                self.txtNombres.text().strip(),
                self.txtApellidos.text().strip(),
                self.txtCedula.text().strip(),
                self.txtCorreoElectronico.text().strip(),
                self.txtContrasenia.text(),
                id_empresa,
                cargo,
            )
            QtWidgets.QMessageBox.information(self, "Tutor creado", "Tutor empresarial registrado correctamente.")
            refrescar_padre(self.parent_controller)
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo crear", str(error))
