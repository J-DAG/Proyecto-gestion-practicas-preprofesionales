from PyQt6 import QtWidgets

from controlador.ControlOferta import ControlOferta
from modelo.Empresa import Empresa
from utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_crear_oferta import Ui_frmCrearOferta


class ControlVentanaCrearOferta(QtWidgets.QWidget, Ui_frmCrearOferta):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_controller = parent
        self.ofertas = ControlOferta()
        self.setupUi(self)
        self._cargar_empresas()
        self.sbxNumCupos.setMinimum(1)
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def guardar(self):
        try:
            self._validar_campos()
            oferta = self.ofertas.crear_oferta(
                str(self.cbxListaEmpresas.currentData()),
                self.txtTitulo.text().strip(),
                self.txtDescripcion.text().strip(),
                "",
                self.txtArea.text().strip(),
                self.sbxNumCupos.value(),
                self.dtFecha.selectedDate().toPyDate(),
            )
            QtWidgets.QMessageBox.information(
                self,
                "Oferta creada",
                f"Oferta registrada correctamente: {oferta.id_oferta}",
            )
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo crear", str(error))

    def _cargar_empresas(self):
        self.cbxListaEmpresas.clear()
        for empresa in Empresa.cargar_todos():
            self.cbxListaEmpresas.addItem(f"{empresa.id_empresa} - {empresa.nombre_empresa}", empresa.id_empresa)

    def _validar_campos(self):
        if self.cbxListaEmpresas.currentData() is None:
            raise ValidacionError("Debe seleccionar una empresa.")
        if not self.txtTitulo.text().strip():
            raise ValidacionError("El titulo de la oferta es obligatorio.")
        if not self.txtDescripcion.text().strip():
            raise ValidacionError("La descripcion de la oferta es obligatoria.")
        if not self.txtArea.text().strip():
            raise ValidacionError("El area de la oferta es obligatoria.")

    def _refrescar_padre(self):
        if self.parent_controller is not None and hasattr(self.parent_controller, "_refrescar_vistas"):
            self.parent_controller._refrescar_vistas()
