from PyQt6 import QtCore, QtWidgets

from controlador.ControlPractica import ControlPractica
from modelo.Practica import Actividad, Practica
from modelo.Usuario import TutorEmpresarial, Usuario
from modelo.utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.ui_TE__actividades import Ui_FormTEListaActividades


class ControlVentanaTEActividades(QtWidgets.QWidget, Ui_FormTEListaActividades):
    def __init__(self, practica: Practica, usuario: TutorEmpresarial, ventana_anterior=None):
        super().__init__()
        self.practica = practica
        self.usuario = usuario
        self.ventana_anterior = ventana_anterior
        self.control_practica = ControlPractica()
        self.subventana = None
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
        self.btnNuevaActividad.clicked.connect(self.nueva_actividad)
        self.btnEditar.clicked.connect(self.editar_actividad)
        self.btnEliminar.clicked.connect(self.eliminar_actividad)
        self.btnMarcarCompletada.clicked.connect(self.marcar_completada)
        self.btnMarcarIncompletada.clicked.connect(self.marcar_incompletada)

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
        self.practica = Practica.obtener_por_id(self.practica.id_practica)
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

    def nueva_actividad(self):
        self._abrir_formulario(ControlVentanaCrearActividadTE(self.practica, self.usuario, self))

    def editar_actividad(self):
        actividad = self._actividad_seleccionada()
        if actividad is None:
            return
        self._abrir_formulario(ControlVentanaEditarActividadTE(actividad, self.usuario, self))

    def eliminar_actividad(self):
        actividad = self._actividad_seleccionada()
        if actividad is None:
            return
        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Eliminar actividad",
            f"Se eliminara la actividad {actividad.id_actividad}. Desea continuar?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            self.control_practica.eliminar_actividad(actividad.id_actividad, self.usuario.id_usuario)
            QtWidgets.QMessageBox.information(self, "Actividad eliminada", "La actividad fue eliminada.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo eliminar", str(error))

    def marcar_completada(self):
        actividad = self._actividad_seleccionada()
        if actividad is None:
            return
        try:
            self.control_practica.cambiar_completado_actividad(
                actividad.id_actividad,
                True,
                self.usuario.id_usuario,
            )
            QtWidgets.QMessageBox.information(self, "Actividad completada", "La actividad fue marcada como completada.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo completar", str(error))

    def marcar_incompletada(self):
        actividad = self._actividad_seleccionada()
        if actividad is None:
            return
        try:
            self.control_practica.cambiar_completado_actividad(
                actividad.id_actividad,
                False,
                self.usuario.id_usuario,
            )
            QtWidgets.QMessageBox.information(self, "Actividad pendiente", "La actividad fue marcada como pendiente.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))

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

    def _abrir_formulario(self, ventana):
        self.subventana = ventana
        self.subventana.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.subventana.destroyed.connect(self._volver_desde_formulario)
        self.subventana.show()
        self.hide()

    def _volver_desde_formulario(self):
        self.subventana = None
        self._refrescar_vistas()
        self.show()
        self.raise_()
        self.activateWindow()

    def _refrescar_vistas(self):
        self.cargar_datos()
        if self.ventana_anterior is not None:
            self.ventana_anterior.cargar_datos()
            if hasattr(self.ventana_anterior, "ventana_te") and self.ventana_anterior.ventana_te is not None:
                self.ventana_anterior.ventana_te.cargar_datos()
                self.ventana_anterior.ventana_te.cargar_resumen()


class ControlVentanaCrearActividadTE(QtWidgets.QWidget):
    def __init__(self, practica: Practica, usuario: TutorEmpresarial, parent_controller=None):
        super().__init__()
        from vista.ui_registrar_actividad import Ui_frmNuevaActividad

        self.practica = practica
        self.usuario = usuario
        self.parent_controller = parent_controller
        self.control_practica = ControlPractica()
        self.ui = Ui_frmNuevaActividad()
        self.ui.setupUi(self)
        self.setWindowTitle("Nueva actividad")
        self.ui.sbxHoras.setMinimum(1)
        self.ui.btnGuardar.clicked.connect(self.guardar)
        self.ui.btnCancelar.clicked.connect(self.close)

    def guardar(self):
        try:
            descripcion = self.ui.txtDescripcion.text().strip()
            horas = self.ui.sbxHoras.value()
            if not descripcion:
                raise ValidacionError("La descripcion de la actividad es obligatoria.")
            if self.practica.tutor_empresarial != self.usuario.id_usuario:
                raise ValidacionError("Solo el tutor empresarial asignado puede registrar actividades.")
            actividad = self.control_practica.registrar_actividad(self.practica.id_practica, descripcion, horas)
            QtWidgets.QMessageBox.information(
                self,
                "Actividad registrada",
                f"Actividad registrada correctamente: {actividad.id_actividad}",
            )
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo registrar", str(error))

    def _refrescar_padre(self):
        if self.parent_controller is not None and hasattr(self.parent_controller, "_refrescar_vistas"):
            self.parent_controller._refrescar_vistas()


class ControlVentanaEditarActividadTE(QtWidgets.QWidget):
    def __init__(self, actividad: Actividad, usuario: TutorEmpresarial, parent_controller=None):
        super().__init__()
        from vista.ui_editar_actividad import Ui_frmEditarActividad

        self.actividad = actividad
        self.usuario = usuario
        self.parent_controller = parent_controller
        self.control_practica = ControlPractica()
        self.ui = Ui_frmEditarActividad()
        self.ui.setupUi(self)
        self.setWindowTitle("Editar actividad")
        self.ui.txtDescripcion.setText(self.actividad.descripcion)
        self.ui.sbxHoras.setMinimum(1)
        self.ui.sbxHoras.setValue(self.actividad.horas)
        self.ui.btnGuardar.clicked.connect(self.guardar)
        self.ui.btnCancelar.clicked.connect(self.close)

    def guardar(self):
        try:
            descripcion = self.ui.txtDescripcion.text().strip()
            horas = self.ui.sbxHoras.value()
            if not descripcion:
                raise ValidacionError("La descripcion de la actividad es obligatoria.")
            self.control_practica.editar_actividad(
                self.actividad.id_actividad,
                descripcion,
                horas,
                self.usuario.id_usuario,
            )
            QtWidgets.QMessageBox.information(self, "Actividad actualizada", "Cambios guardados correctamente.")
            self._refrescar_padre()
            self.close()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))

    def _refrescar_padre(self):
        if self.parent_controller is not None and hasattr(self.parent_controller, "_refrescar_vistas"):
            self.parent_controller._refrescar_vistas()

