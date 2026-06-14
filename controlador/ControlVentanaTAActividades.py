from PyQt6 import QtWidgets

from controlador.ControlPractica import ControlPractica
from modelo.Practica import Actividad, Practica
from modelo.Usuario import TutorAcademico, Usuario
from modelo.utilidades.Excepciones import SistemaPracticasError
from vista.ui_TA__actividades import Ui_frmTAListaActividades


class ControlVentanaTAActividades(QtWidgets.QWidget, Ui_frmTAListaActividades):
    def __init__(self, practica: Practica, usuario: TutorAcademico, ventana_anterior=None):
        super().__init__()
        self.practica = practica
        self.usuario = usuario
        self.ventana_anterior = ventana_anterior
        self.control_practica = ControlPractica()
        self.volviendo = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnRegresar.clicked.connect(self.volver)
        self.btnInicio.clicked.connect(self.volver_inicio)
        self.btnBuscar.clicked.connect(self.buscar_actividades)
        self.txtBuscar.returnPressed.connect(self.buscar_actividades)
        self.txtBuscar.textChanged.connect(self.buscar_actividades)
        self.btnAprobar.clicked.connect(self.aprobar_actividad)
        self.btnNegar.clicked.connect(self.negar_actividad)

    def configurar_tabla(self):
        columnas = ["ID", "Descripcion", "Horas", "Fecha", "Aprobada", "Completada", "Estado"]
        self.tblActividades.setColumnCount(len(columnas))
        self.tblActividades.setHorizontalHeaderLabels(columnas)
        self.tblActividades.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblActividades.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblActividades.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblActividades.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblActividades.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        estudiante = Usuario.buscar_por_id(self.practica.id_estudiante)
        self.lblNombresEstudianteEditar.setText(estudiante.nombre if estudiante else self.practica.id_estudiante)
        self._llenar_tabla(self.control_practica.listar_actividades(self.practica.id_practica))

    def buscar_actividades(self):
        texto = self.txtBuscar.text().strip().lower()
        actividades = self.control_practica.listar_actividades(self.practica.id_practica)
        if texto:
            actividades = [
                actividad
                for actividad in actividades
                if texto in actividad.id_actividad.lower()
                or texto in actividad.descripcion.lower()
                or texto in actividad.obtener_estado().lower()
            ]
        self._llenar_tabla(actividades)

    def aprobar_actividad(self):
        actividad = self._actividad_seleccionada()
        if actividad is None:
            return
        try:
            self.control_practica.cambiar_aprobacion_actividad(
                actividad.id_actividad,
                True,
                self.usuario.id_usuario,
            )
            QtWidgets.QMessageBox.information(self, "Actividad aprobada", "La actividad fue aprobada.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo aprobar", str(error))

    def negar_actividad(self):
        actividad = self._actividad_seleccionada()
        if actividad is None:
            return
        try:
            self.control_practica.cambiar_aprobacion_actividad(
                actividad.id_actividad,
                False,
                self.usuario.id_usuario,
            )
            QtWidgets.QMessageBox.information(self, "Actividad pendiente", "La actividad quedo pendiente de aprobacion.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo negar", str(error))

    def volver_inicio(self):
        self.volviendo = True
        if self.ventana_anterior is not None and hasattr(self.ventana_anterior, "volver_inicio"):
            self.ventana_anterior.volver_inicio()
        self.close()

    def volver(self):
        self.volviendo = True
        if self.ventana_anterior is not None:
            self.ventana_anterior.cargar_datos()
            self.ventana_anterior.show()
            self.ventana_anterior.raise_()
            self.ventana_anterior.activateWindow()
        self.close()

    def closeEvent(self, event):
        if self.volviendo:
            super().closeEvent(event)
            return
        if self.ventana_anterior is not None:
            self.ventana_anterior.cargar_datos()
            self.ventana_anterior.show()
            self.ventana_anterior.raise_()
            self.ventana_anterior.activateWindow()
        super().closeEvent(event)

    def _llenar_tabla(self, actividades: list[Actividad]):
        self.tblActividades.setRowCount(len(actividades))
        for fila, actividad in enumerate(actividades):
            valores = [
                actividad.id_actividad,
                actividad.descripcion,
                actividad.horas,
                actividad.fecha,
                "Si" if actividad.aprobada_por_tutor_academico else "No",
                "Si" if actividad.completada_por_tutor_empresarial else "No",
                actividad.obtener_estado(),
            ]
            for columna, valor in enumerate(valores):
                self.tblActividades.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _actividad_seleccionada(self) -> Actividad | None:
        fila = self.tblActividades.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una actividad de la tabla.")
            return None
        item = self.tblActividades.item(fila, 0)
        if item is None:
            return None
        return Actividad.buscar_por_id(item.text())

    def _refrescar_vistas(self):
        self.cargar_datos()
        if self.ventana_anterior is not None:
            self.ventana_anterior.cargar_datos()

