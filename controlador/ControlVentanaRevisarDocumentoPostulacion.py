from pathlib import Path
from PyQt6 import QtCore, QtGui, QtWidgets

from configuracion.ajustes import ROLES
from controlador.ControlPostulacion import ControlPostulacion
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Usuario import Usuario
from utilidades.Excepciones import SistemaPracticasError, ValidacionError


class ControlVentanaRevisarDocumentoPostulacion(QtWidgets.QWidget):
    def __init__(self, postulacion: Postulacion, coordinador: Usuario, parent_controller=None):
        super().__init__()
        self.postulacion = postulacion
        self.coordinador = coordinador
        self.parent_controller = parent_controller
        self.postulaciones = ControlPostulacion()
        self.practicas = ControlPractica()
        self.ruta_documento: Path | None = None
        self.oferta: Oferta | None = None
        self.setWindowTitle("Revisar documento de postulacion")
        self.resize(760, 430)
        self._construir_interfaz()
        self._cargar_datos()

    def _construir_interfaz(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.lblTitulo = QtWidgets.QLabel("Revision de avance de malla")
        self.lblTitulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.lblDetalle = QtWidgets.QLabel()
        self.lblRuta = QtWidgets.QLabel()
        self.lblRuta.setWordWrap(True)

        self.grpPractica = QtWidgets.QGroupBox("Datos para iniciar practica")
        formulario = QtWidgets.QFormLayout(self.grpPractica)
        self.dtpInicio = QtWidgets.QDateEdit(self.grpPractica)
        self.dtpInicio.setCalendarPopup(True)
        self.dtpInicio.setDate(QtCore.QDate.currentDate())
        self.dtpFin = QtWidgets.QDateEdit(self.grpPractica)
        self.dtpFin.setCalendarPopup(True)
        self.dtpFin.setDate(QtCore.QDate.currentDate().addMonths(3))
        self.cbxTutorAcademico = QtWidgets.QComboBox(self.grpPractica)
        self.cbxTutorEmpresarial = QtWidgets.QComboBox(self.grpPractica)
        self.lblEmpresa = QtWidgets.QLabel(self.grpPractica)
        formulario.addRow("Empresa:", self.lblEmpresa)
        formulario.addRow("Fecha inicio:", self.dtpInicio)
        formulario.addRow("Fecha fin:", self.dtpFin)
        formulario.addRow("Tutor academico:", self.cbxTutorAcademico)
        formulario.addRow("Tutor empresarial:", self.cbxTutorEmpresarial)

        fila_botones = QtWidgets.QHBoxLayout()
        fila_botones.addStretch()
        self.btnAbrirDocumento = QtWidgets.QPushButton("Ver documento", self)
        self.btnCancelar = QtWidgets.QPushButton("Cancelar", self)
        self.btnAprobar = QtWidgets.QPushButton("Aprobar e iniciar practica", self)
        fila_botones.addWidget(self.btnAbrirDocumento)
        fila_botones.addWidget(self.btnCancelar)
        fila_botones.addWidget(self.btnAprobar)

        layout.addWidget(self.lblTitulo)
        layout.addWidget(self.lblDetalle)
        layout.addWidget(self.lblRuta)
        layout.addWidget(self.grpPractica)
        layout.addStretch()
        layout.addLayout(fila_botones)

        self.btnAbrirDocumento.clicked.connect(self.abrir_documento)
        self.btnCancelar.clicked.connect(self.close)
        self.btnAprobar.clicked.connect(self.aprobar)

    def _cargar_datos(self):
        estudiante = Usuario.buscar_por_id(self.postulacion.id_estudiante)
        self.oferta = Oferta.buscar_por_id(self.postulacion.id_oferta)
        empresa = Empresa.buscar_por_id(self.oferta.id_empresa) if self.oferta else None
        self.lblDetalle.setText(
            "Postulacion: {id_pos}\nEstudiante: {estudiante}\nOferta: {oferta}".format(
                id_pos=self.postulacion.id_postulacion,
                estudiante=estudiante.nombre if estudiante else self.postulacion.id_estudiante,
                oferta=self.oferta.titulo if self.oferta else self.postulacion.id_oferta,
            )
        )
        self.lblEmpresa.setText(empresa.nombre_empresa if empresa else "Empresa no encontrada")
        self._cargar_tutores(empresa.id_empresa if empresa else "")
        try:
            self.ruta_documento = self.postulaciones.obtener_documento_malla(self.postulacion.id_postulacion)
            self.lblRuta.setText(f"Documento adjunto: {self.ruta_documento}")
        except SistemaPracticasError as error:
            self.lblRuta.setText(str(error))
            self.btnAbrirDocumento.setEnabled(False)
            self.btnAprobar.setEnabled(False)

    def _cargar_tutores(self, id_empresa: str):
        self.cbxTutorAcademico.clear()
        self.cbxTutorEmpresarial.clear()

        for usuario in Usuario.cargar_todos():
            if not getattr(usuario, "activo", True):
                continue
            if usuario.rol == ROLES["TUTOR_ACADEMICO"]:
                self.cbxTutorAcademico.addItem(f"{usuario.id_usuario} - {usuario.nombre}", usuario.id_usuario)
            if usuario.rol == ROLES["TUTOR_EMPRESARIAL"] and getattr(usuario, "id_empresa", "") == id_empresa:
                self.cbxTutorEmpresarial.addItem(f"{usuario.id_usuario} - {usuario.nombre}", usuario.id_usuario)

        if self.cbxTutorAcademico.count() == 0 or self.cbxTutorEmpresarial.count() == 0:
            self.btnAprobar.setEnabled(False)
            self.lblRuta.setText(
                self.lblRuta.text()
                + "\nNo hay tutores academicos activos o tutores empresariales activos para esta empresa."
            )

    def abrir_documento(self):
        if self.ruta_documento is None:
            return
        try:
            url = QtCore.QUrl.fromLocalFile(str(self.ruta_documento))
            if not QtGui.QDesktopServices.openUrl(url):
                raise RuntimeError("No se pudo abrir el PDF con la aplicacion predeterminada.")
        except Exception as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo abrir", str(error))

    def aprobar(self):
        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Aprobar postulacion",
            f"Desea aprobar la postulacion {self.postulacion.id_postulacion}?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            self._validar_datos_practica()
            postulacion = self.postulaciones.validar_postulacion(self.postulacion.id_postulacion, self.coordinador)
            postulacion = self.postulaciones.aceptar_postulacion(postulacion.id_postulacion)
            practica = self.practicas.crear_practica(
                postulacion.id_postulacion,
                self.dtpInicio.date().toPyDate(),
                self.dtpFin.date().toPyDate(),
                str(self.cbxTutorAcademico.currentData()),
                str(self.cbxTutorEmpresarial.currentData()),
            )
            QtWidgets.QMessageBox.information(
                self,
                "Practica iniciada",
                f"Postulacion {postulacion.id_postulacion} aprobada. Practica creada: {practica.id_practica}.",
            )
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo aprobar", str(error))

    def _validar_datos_practica(self):
        if self.cbxTutorAcademico.currentData() is None:
            raise ValidacionError("Debe seleccionar un tutor academico.")
        if self.cbxTutorEmpresarial.currentData() is None:
            raise ValidacionError("Debe seleccionar un tutor empresarial de la empresa.")
        if self.dtpFin.date().toPyDate() < self.dtpInicio.date().toPyDate():
            raise ValidacionError("La fecha de fin no puede ser anterior a la fecha de inicio.")

    def _refrescar_padre(self):
        if self.parent_controller is not None and hasattr(self.parent_controller, "_refrescar_vistas"):
            self.parent_controller._refrescar_vistas()
