from PyQt6 import QtCore, QtWidgets

from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_editar_oferta import Ui_frmEditarOferta


class ControlVentanaEditarOferta(QtWidgets.QWidget, Ui_frmEditarOferta):
    def __init__(self, oferta: Oferta, parent=None):
        super().__init__()
        self.oferta = oferta
        self.parent_controller = parent
        self.setupUi(self)
        self._cargar_empresas()
        self._cargar_oferta()
        self.sbxNumCupos.setMinimum(1)
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnCancelar.clicked.connect(self.close)

    def guardar(self):
        try:
            self._validar_campos()
            self.oferta.id_empresa = str(self.cbxListaEmpresas.currentData())
            self.oferta.titulo = self.txtTitulo.text().strip()
            self.oferta.descripcion = self.txtDescripcion.text().strip()
            self.oferta.area = self.txtArea.text().strip()
            self.oferta.cupos = self.sbxNumCupos.value()
            self.oferta.fecha_cierre = self.dtFecha.selectedDate().toPyDate()
            self.oferta.guardar()
            QtWidgets.QMessageBox.information(self, "Oferta actualizada", "Cambios guardados correctamente.")
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))

    def _cargar_empresas(self):
        self.cbxListaEmpresas.clear()
        for empresa in Empresa.cargar_todos():
            self.cbxListaEmpresas.addItem(f"{empresa.id_empresa} - {empresa.nombre_empresa}", empresa.id_empresa)

    def _cargar_oferta(self):
        indice_empresa = self.cbxListaEmpresas.findData(self.oferta.id_empresa)
        if indice_empresa >= 0:
            self.cbxListaEmpresas.setCurrentIndex(indice_empresa)
        self.txtTitulo.setText(self.oferta.titulo)
        self.txtDescripcion.setText(self.oferta.descripcion)
        self.txtArea.setText(self.oferta.area)
        self.sbxNumCupos.setValue(self.oferta.cupos)
        self.dtFecha.setSelectedDate(QtCore.QDate(self.oferta.fecha_cierre.year, self.oferta.fecha_cierre.month, self.oferta.fecha_cierre.day))

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
