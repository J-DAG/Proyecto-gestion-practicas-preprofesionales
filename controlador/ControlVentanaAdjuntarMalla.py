from PyQt6 import QtWidgets

from controlador.ControlPostulacion import ControlPostulacion
from modelo.Oferta import Oferta
from modelo.Usuario import Estudiante
from utilidades.Excepciones import SistemaPracticasError, ValidacionError


class ControlVentanaAdjuntarMalla(QtWidgets.QWidget):
    def __init__(self, estudiante: Estudiante, oferta: Oferta, parent_controller=None):
        super().__init__()
        self.estudiante = estudiante
        self.oferta = oferta
        self.parent_controller = parent_controller
        self.postulaciones = ControlPostulacion()
        self.ruta_pdf = ""
        self.setWindowTitle("Adjuntar avance de malla")
        self.resize(560, 190)
        self._construir_interfaz()

    def _construir_interfaz(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.lblInformacion = QtWidgets.QLabel(
            "Para continuar con la postulacion adjunte el avance de malla en formato PDF."
        )
        self.lblOferta = QtWidgets.QLabel(f"Oferta: {self.oferta.id_oferta} - {self.oferta.titulo}")
        self.txtRuta = QtWidgets.QLineEdit(self)
        self.txtRuta.setReadOnly(True)
        self.txtRuta.setPlaceholderText("Seleccione un archivo PDF")

        fila_archivo = QtWidgets.QHBoxLayout()
        fila_archivo.addWidget(self.txtRuta)
        self.btnSeleccionar = QtWidgets.QPushButton("Seleccionar PDF", self)
        fila_archivo.addWidget(self.btnSeleccionar)

        fila_botones = QtWidgets.QHBoxLayout()
        fila_botones.addStretch()
        self.btnCancelar = QtWidgets.QPushButton("Cancelar", self)
        self.btnGuardar = QtWidgets.QPushButton("Continuar postulacion", self)
        fila_botones.addWidget(self.btnCancelar)
        fila_botones.addWidget(self.btnGuardar)

        layout.addWidget(self.lblInformacion)
        layout.addWidget(self.lblOferta)
        layout.addLayout(fila_archivo)
        layout.addLayout(fila_botones)

        self.btnSeleccionar.clicked.connect(self.seleccionar_pdf)
        self.btnCancelar.clicked.connect(self.close)
        self.btnGuardar.clicked.connect(self.guardar)

    def seleccionar_pdf(self):
        ruta, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Seleccionar avance de malla",
            "",
            "Archivos PDF (*.pdf)",
        )
        if ruta:
            self.ruta_pdf = ruta
            self.txtRuta.setText(ruta)

    def guardar(self):
        try:
            if not self.ruta_pdf:
                raise ValidacionError("Debe seleccionar el PDF del avance de malla.")
            postulacion = self.postulaciones.crear_postulacion(
                self.estudiante.id_usuario,
                self.oferta.id_oferta,
                self.ruta_pdf,
            )
            QtWidgets.QMessageBox.information(
                self,
                "Postulacion registrada",
                f"Postulacion creada correctamente: {postulacion.id_postulacion}",
            )
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo postular", str(error))

    def _refrescar_padre(self):
        if self.parent_controller is not None and hasattr(self.parent_controller, "_refrescar_vistas"):
            self.parent_controller._refrescar_vistas()
