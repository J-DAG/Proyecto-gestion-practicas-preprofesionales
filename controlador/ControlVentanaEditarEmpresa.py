from PyQt6 import QtWidgets

from modelo.Empresa import Empresa
from utilidades.Excepciones import SistemaPracticasError, ValidacionError
from utilidades.ManejoDatos import ManejoDatos
from vista.ui_editar_empresa import Ui_frmEditarEmpresa


class ControlVentanaEditarEmpresa(QtWidgets.QWidget, Ui_frmEditarEmpresa):
    def __init__(self, empresa: Empresa, parent=None):
        super().__init__()
        self.empresa = empresa
        self.parent_controller = parent
        self.setupUi(self)
        self._cargar_empresa()
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def _cargar_empresa(self):
        self.txtNombreEmpresa.setText(self.empresa.nombre_empresa)
        self.txtCorreoElectronico.setText(self.empresa.email)
        self.txtRuc.setText(self.empresa.ruc)
        self.txtRazonSocial.setText(self.empresa.razon_social)
        self.txtSector.setText(self.empresa.sector)
        self.txtUbicacion.setText(self.empresa.ubicacion)
        self.txtMision.setText(self.empresa.mision)
        self.txtVision.setText(self.empresa.vision)
        self.rbtSi.setChecked(self.empresa.convenio_vigente)
        self.rbtNo.setChecked(not self.empresa.convenio_vigente)

    def guardar(self):
        try:
            self._validar_campos()
            self._validar_ruc_unico()
            self.empresa.nombre_empresa = self.txtNombreEmpresa.text().strip()
            self.empresa.email = self.txtCorreoElectronico.text().strip()
            self.empresa.ruc = self.txtRuc.text().strip()
            self.empresa.razon_social = self.txtRazonSocial.text().strip()
            self.empresa.sector = self.txtSector.text().strip()
            self.empresa.ubicacion = self.txtUbicacion.text().strip()
            self.empresa.mision = self.txtMision.text().strip()
            self.empresa.vision = self.txtVision.text().strip()
            self.empresa.convenio_vigente = self.rbtSi.isChecked()
            self.empresa.guardar()
            QtWidgets.QMessageBox.information(self, "Empresa actualizada", "Cambios guardados correctamente.")
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))

    def _validar_campos(self):
        if not self.txtNombreEmpresa.text().strip():
            raise ValidacionError("El nombre de la empresa es obligatorio.")
        if "@" not in self.txtCorreoElectronico.text():
            raise ValidacionError("El email de la empresa no tiene un formato valido.")
        if not self.txtRuc.text().strip():
            raise ValidacionError("El RUC de la empresa es obligatorio.")

    def _validar_ruc_unico(self):
        empresa = ManejoDatos("empresas").buscar_por_campo("ruc", self.txtRuc.text().strip())
        if empresa is not None and empresa.id_empresa != self.empresa.id_empresa:
            raise ValidacionError(f"Ya existe una empresa con RUC {self.txtRuc.text().strip()}.")

    def _refrescar_padre(self):
        if self.parent_controller is not None and hasattr(self.parent_controller, "_refrescar_vistas"):
            self.parent_controller._refrescar_vistas()
