from PyQt6 import QtCore, QtWidgets

from controlador.ControlUsuario import ControlUsuario
from controlador._formularios_usuario import refrescar_padre, validar_basicos, validar_password
from modelo.utilidades.Excepciones import SistemaPracticasError


class ControlVentanaCrearCoordinador(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_controller = parent
        self.usuarios = ControlUsuario()
        self.setWindowTitle("Registrar coordinador")
        self.resize(520, 340)
        self.setMinimumSize(QtCore.QSize(520, 340))
        self.setMaximumSize(QtCore.QSize(520, 340))
        self._construir_formulario()

    def _construir_formulario(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(12)
        self.txtNombres = QtWidgets.QLineEdit()
        self.txtApellidos = QtWidgets.QLineEdit()
        self.txtCedula = QtWidgets.QLineEdit()
        self.txtCorreoElectronico = QtWidgets.QLineEdit()
        self.txtContrasenia = QtWidgets.QLineEdit()
        self.txtConfirmarContrasenia = QtWidgets.QLineEdit()
        self.txtContrasenia.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.txtConfirmarContrasenia.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.btnCancelar = QtWidgets.QPushButton("Cancelar")
        self.btnGuardar = QtWidgets.QPushButton("Guardar y registrar")

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btnCancelar)
        botones.addWidget(self.btnGuardar)

        layout.addRow("Nombres:", self.txtNombres)
        layout.addRow("Apellidos:", self.txtApellidos)
        layout.addRow("Cedula:", self.txtCedula)
        layout.addRow("Correo electronico:", self.txtCorreoElectronico)
        layout.addRow("ContraseÃ±a:", self.txtContrasenia)
        layout.addRow("Confirmar contraseÃ±a:", self.txtConfirmarContrasenia)
        layout.addRow(botones)

        self.btnCancelar.clicked.connect(self.close)
        self.btnGuardar.clicked.connect(self.guardar)

    def guardar(self):
        try:
            validar_basicos(
                self.txtNombres.text(),
                self.txtApellidos.text(),
                self.txtCedula.text(),
                self.txtCorreoElectronico.text(),
            )
            validar_password(self.txtContrasenia.text(), self.txtConfirmarContrasenia.text(), True)
            self.usuarios.registrar_coordinador(
                self.txtNombres.text().strip(),
                self.txtApellidos.text().strip(),
                self.txtCedula.text().strip(),
                self.txtCorreoElectronico.text().strip(),
                self.txtContrasenia.text(),
            )
            QtWidgets.QMessageBox.information(self, "Coordinador creado", "Coordinador registrado correctamente.")
            refrescar_padre(self.parent_controller)
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo crear", str(error))

