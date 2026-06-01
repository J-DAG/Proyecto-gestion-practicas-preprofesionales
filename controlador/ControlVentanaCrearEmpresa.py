from PyQt6 import QtWidgets

from controlador.ControlOferta import ControlOferta
from utilidades.Excepciones import SistemaPracticasError, ValidacionError


from vista.ui_crear_empresa import Ui_frmCrearEmpresa


class ControlVentanaCrearEmpresa(QtWidgets.QWidget, Ui_frmCrearEmpresa):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_controller = parent
        self.ofertas = ControlOferta()
        self.setupUi(self)
        self.rbtSi.setChecked(True)
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def guardar(self):
        try:
            self._validar_campos()
            empresa = self.ofertas.registrar_empresa(
                self.txtNombreEmpresa.text().strip(),
                self.txtCorreoElectronico.text().strip(),
                self.txtRazonSocial.text().strip(),
                self.txtRuc.text().strip(),
                self.txtSector.text().strip(),
                self.txtUbicacion.text().strip(),
                self.txtMision.text().strip(),
                self.txtVision.text().strip(),
                self.rbtSi.isChecked(),
            )
            QtWidgets.QMessageBox.information(
                self,
                "Empresa creada",
                f"Empresa registrada correctamente: {empresa.id_empresa}",
            )
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo crear", str(error))

    def _validar_campos(self):
        if not self.txtNombreEmpresa.text().strip():
            raise ValidacionError("El nombre de la empresa es obligatorio.")
        if "@" not in self.txtCorreoElectronico.text():
            raise ValidacionError("El email de la empresa no tiene un formato valido.")
        if not self.txtRuc.text().strip():
            raise ValidacionError("El RUC de la empresa es obligatorio.")

    def _refrescar_padre(self):
        if self.parent_controller is not None and hasattr(self.parent_controller, "_refrescar_vistas"):
            self.parent_controller._refrescar_vistas()
