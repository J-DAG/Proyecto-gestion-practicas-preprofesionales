from PyQt6 import QtWidgets

from configuracion.ajustes import HORAS_MAXIMAS_PRACTICA
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Practica import Actividad
from modelo.Usuario import Estudiante, Usuario
from vista.ui_EST_practicas import Ui_FormPracticaEstudiante


class ControlVentanaEstudiantePractica(QtWidgets.QWidget, Ui_FormPracticaEstudiante):
    def __init__(self, usuario: Estudiante, ventana_estudiante=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_estudiante = ventana_estudiante
        self.login = login
        self.practicas = ControlPractica()
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.rbtAprobadas.setAutoExclusive(False)
        self.rbtAprobadas_2.setAutoExclusive(False)
        self.rbtAprobadas_3.setAutoExclusive(False)
        self.cargar_datos()
        self.btnInico.clicked.connect(self.volver_inicio)
        self.btnMiPractica.clicked.connect(self.cargar_datos)
        self.btnMisPostulaciones.clicked.connect(self.ver_postulaciones)
        self.btnOfertaLaboral.clicked.connect(self.ver_ofertas)
        self.btnMisFormularios.clicked.connect(self.ver_formularios)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnBuscar.clicked.connect(self.buscar_actividades)
        self.txtBuscar.returnPressed.connect(self.buscar_actividades)
        self.txtBuscar.textChanged.connect(self.buscar_actividades)
        self.rbtAprobadas.toggled.connect(self.buscar_actividades)
        self.rbtAprobadas_2.toggled.connect(self.buscar_actividades)
        self.rbtAprobadas_3.toggled.connect(self.buscar_actividades)

    def configurar_tabla(self):
        columnas = ["ID", "Descripcion", "Horas", "Fecha", "Aprobada", "Completada", "Estado"]
        self.tblListaActividades.setColumnCount(len(columnas))
        self.tblListaActividades.setHorizontalHeaderLabels(columnas)
        self.tblListaActividades.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblListaActividades.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblListaActividades.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblListaActividades.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblListaActividades.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        progreso = self.practicas.obtener_progreso_estudiante(self.usuario.id_usuario)
        practica = progreso["practica"]
        if practica is None:
            self.lblEmpresaEditar.setText("Sin practica asignada")
            self.lblTAEditar.setText("Sin tutor asignado")
            self.lblTEEditar.setText("Sin tutor asignado")
            self.lblNumHorasEditar.setText(f"0/{HORAS_MAXIMAS_PRACTICA}")
            self.lblActCompletadasEditar.setText("0")
            self.tblListaActividades.setRowCount(0)
            return

        empresa = Empresa.buscar_por_id(practica.id_empresa)
        tutor_academico = Usuario.buscar_por_id(practica.id_tutor_academico)
        tutor_empresarial = Usuario.buscar_por_id(practica.tutor_empresarial)
        self.lblEmpresaEditar.setText(empresa.nombre_empresa if empresa else practica.id_empresa)
        self.lblTAEditar.setText(tutor_academico.nombre if tutor_academico else practica.id_tutor_academico)
        self.lblTEEditar.setText(tutor_empresarial.nombre if tutor_empresarial else practica.tutor_empresarial)
        self.lblNumHorasEditar.setText(f"{practica.horas_cumplidas}/{HORAS_MAXIMAS_PRACTICA}")
        self.lblActCompletadasEditar.setText(str(progreso["actividades_completadas"]))
        self._llenar_tabla(progreso["actividades"])

    def buscar_actividades(self):
        progreso = self.practicas.obtener_progreso_estudiante(self.usuario.id_usuario)
        actividades = list(progreso["actividades"])
        texto = self.txtBuscar.text().strip().lower()
        if texto:
            actividades = [
                actividad for actividad in actividades
                if texto in actividad.id_actividad.lower()
                or texto in actividad.descripcion.lower()
                or texto in actividad.obtener_estado().lower()
            ]
        if self.rbtAprobadas.isChecked():
            actividades = [a for a in actividades if a.aprobada_por_tutor_academico and not a.completada_por_tutor_empresarial]
        if self.rbtAprobadas_2.isChecked():
            actividades = [a for a in actividades if not a.aprobada_por_tutor_academico]
        if self.rbtAprobadas_3.isChecked():
            actividades = [a for a in actividades if a.completada_por_tutor_empresarial]
        self._llenar_tabla(actividades)

    def ver_formularios(self):
        from controlador.ControlVentanaEstudianteFormularios import ControlVentanaEstudianteFormularios
        self._abrir_ventana(ControlVentanaEstudianteFormularios(self.usuario, self.ventana_estudiante, self.login))

    def ver_postulaciones(self):
        from controlador.ControlVentanaEstudiantePostulaciones import ControlVentanaEstudiantePostulaciones
        self._abrir_ventana(ControlVentanaEstudiantePostulaciones(self.usuario, self.ventana_estudiante, self.login))

    def ver_ofertas(self):
        from controlador.ControlVentanaEstudianteOfertasLaborales import ControlVentanaEstudianteOfertasLaborales
        self._abrir_ventana(ControlVentanaEstudianteOfertasLaborales(self.usuario, self.ventana_estudiante, self.login))

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_estudiante is not None:
            self.ventana_estudiante.salir()

    def closeEvent(self, event):
        if self.cerrando_sesion:
            super().closeEvent(event)
            return
        self._mostrar_principal()
        self.hide()
        event.ignore()

    def _llenar_tabla(self, actividades: list[Actividad]):
        self.tblListaActividades.setRowCount(len(actividades))
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
                self.tblListaActividades.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _abrir_ventana(self, ventana):
        self.subventana = ventana
        self.subventana.show()
        self.hide()

    def _mostrar_principal(self):
        if self.ventana_estudiante is not None:
            self.ventana_estudiante.cargar_datos()
            self.ventana_estudiante.show()
            self.ventana_estudiante.raise_()
            self.ventana_estudiante.activateWindow()
