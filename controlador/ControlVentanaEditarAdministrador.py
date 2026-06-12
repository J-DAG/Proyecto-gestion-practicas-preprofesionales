from PyQt6 import QtWidgets

from controlador._formularios_usuario import refrescar_padre, validar_basicos, validar_password, validar_unicos_edicion
from modelo.Usuario import Administrador
from utilidades.Excepciones import SistemaPracticasError


class ControlVentanaEditarAdministrador(QtWidgets.QWidget):
    def __init__(self, usuario: Administrador, parent=None):
        super().__init__()
        self.usuario = usuario
        self.parent_controller = parent
        self.setWindowTitle("Editar administrador")
        self._construir_formulario()
        self._cargar_usuario()

    def _construir_formulario(self):
        layout = QtWidgets.QFormLayout(self)
        self.txtNombres = QtWidgets.QLineEdit()
        self.txtApellidos = QtWidgets.QLineEdit()
        self.txtCedula = QtWidgets.QLineEdit()
        self.txtCorreoElectronico = QtWidgets.QLineEdit()
        self.txtContrasenia = QtWidgets.QLineEdit()
        self.txtConfirmarContrasenia = QtWidgets.QLineEdit()
        self.txtContrasenia.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtConfirmarContrasenia.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtContrasenia.setPlaceholderText("Dejar vacio para conservar")
        self.btnCancelar = QtWidgets.QPushButton("Cancelar")
        self.btnGuardar = QtWidgets.QPushButton("Guardar cambios")
        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btnCancelar)
        botones.addWidget(self.btnGuardar)
        layout.addRow("Nombres:", self.txtNombres)
        layout.addRow("Apellidos:", self.txtApellidos)
        layout.addRow("Cedula:", self.txtCedula)
        layout.addRow("Correo electronico:", self.txtCorreoElectronico)
        layout.addRow("Contraseña:", self.txtContrasenia)
        layout.addRow("Confirmar contraseña:", self.txtConfirmarContrasenia)
        layout.addRow(botones)
        self.btnCancelar.clicked.connect(self.close)
        self.btnGuardar.clicked.connect(self.guardar)

    def _cargar_usuario(self):
        self.txtNombres.setText(self.usuario.nombres)
        self.txtApellidos.setText(self.usuario.apellidos)
        self.txtCedula.setText(self.usuario.cedula)
        self.txtCorreoElectronico.setText(self.usuario.email)

    def guardar(self):
        try:
            validar_basicos(
                self.txtNombres.text(),
                self.txtApellidos.text(),
                self.txtCedula.text(),
                self.txtCorreoElectronico.text(),
            )
            validar_password(self.txtContrasenia.text(), self.txtConfirmarContrasenia.text(), False)
            cedula = validar_unicos_edicion(
                self.usuario.id_usuario,
                self.txtCorreoElectronico.text().strip(),
                self.txtCedula.text().strip(),
            )
            self.usuario.nombres = self.txtNombres.text().strip()
            self.usuario.apellidos = self.txtApellidos.text().strip()
            self.usuario.cedula = cedula
            self.usuario.email = self.txtCorreoElectronico.text().strip()
            if self.txtContrasenia.text():
                self.usuario.password = self.usuario.encriptar_password(self.txtContrasenia.text())
            self.usuario.guardar()
            QtWidgets.QMessageBox.information(self, "Administrador actualizado", "Cambios guardados correctamente.")
            refrescar_padre(self.parent_controller)
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))
