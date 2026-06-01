from PyQt6 import QtWidgets

from modelo.Practica import Actividad, Practica
from modelo.Usuario import Usuario
from vista.ui_lista_actividades import Ui_frmListaActividades


class ControlVentanaVerActividades(QtWidgets.QWidget, Ui_frmListaActividades):
    def __init__(self, practica: Practica, parent=None):
        super().__init__()
        self.practica = practica
        self.ventana_practicas = parent
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnSalir.clicked.connect(self.salir)

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
        estudiante = Usuario.buscar_por_id(self.practica.id_estudiante)
        tutor_academico = Usuario.buscar_por_id(self.practica.id_tutor_academico)
        tutor_empresarial = Usuario.buscar_por_id(self.practica.tutor_empresarial)

        self.lblIDestudianteEditar.setText(self.practica.id_estudiante)
        self.lblIDpracticaEditar.setText(self.practica.id_practica)
        self.lblNombresEstudianteEditar.setText(estudiante.nombre if estudiante else "No encontrado")
        self.lblNombreTAEditar.setText(tutor_academico.nombre if tutor_academico else "No encontrado")
        self.lblNombreTEEditar.setText(tutor_empresarial.nombre if tutor_empresarial else "No encontrado")

        actividades = [
            actividad
            for actividad in Actividad.cargar_todos()
            if actividad.id_practica == self.practica.id_practica
        ]
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

    def salir(self):
        if self.ventana_practicas is not None:
            self.ventana_practicas.cargar_datos()
            self.ventana_practicas.show()
            self.ventana_practicas.raise_()
            self.ventana_practicas.activateWindow()
        self.close()
