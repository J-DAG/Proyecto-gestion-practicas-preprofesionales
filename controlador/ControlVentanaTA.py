from PyQt6 import QtWidgets

from modelo.configuracion.ajustes import HORAS_MAXIMAS_PRACTICA
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Usuario import TutorAcademico, Usuario
from vista.estilos import EstilosClase
from vista.ui_main_window_TA import Ui_MainWindowTA


class ControlVentanaTA(QtWidgets.QMainWindow, Ui_MainWindowTA):
    def __init__(self, usuario: TutorAcademico, login=None, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.login = login
        self.practicas = ControlPractica()
        self.ventana_progreso = None
        self.ventana_completas = None
        self.ventana_notificaciones = None
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.cargar_resumen()
        self.btnCerrarSesion_2.clicked.connect(self.salir)
        self.btnCerrarSesion.triggered.connect(self.salir)
        self.btnEnProgreso.triggered.connect(self.practicas_en_progreso)
        self.btnVerNotificaciones.clicked.connect(self.ver_notificaciones)
        self.btnNotificaciones.triggered.connect(self.ver_notificaciones)
        self.btnCompletadas.triggered.connect(self.practicas_completas)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["Practica", "Estudiante", "Empresa", "Inicio", "Horas", "Estado"]
        self.tblEstudiantes.setColumnCount(len(columnas))
        self.tblEstudiantes.setHorizontalHeaderLabels(columnas)
        self.tblEstudiantes.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblEstudiantes.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblEstudiantes.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblEstudiantes.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblEstudiantes.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        practicas = self.practicas.listar_practicas_por_tutor_academico(self.usuario.id_usuario)
        practicas.sort(key=lambda practica: str(practica.fecha_inicio), reverse=True)
        self.tblEstudiantes.setRowCount(len(practicas))
        for fila, practica in enumerate(practicas):
            estudiante = Usuario.buscar_por_id(practica.id_estudiante)
            empresa = Empresa.buscar_por_id(practica.id_empresa)
            valores = [
                practica.id_practica,
                estudiante.nombre if estudiante else practica.id_estudiante,
                empresa.nombre_empresa if empresa else practica.id_empresa,
                practica.fecha_inicio,
                f"{practica.horas_cumplidas}/{HORAS_MAXIMAS_PRACTICA}",
                practica.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblEstudiantes.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def cargar_resumen(self):
        practicas = self.practicas.listar_practicas_por_tutor_academico(self.usuario.id_usuario)
        resumen = self._generar_resumen(practicas)
        self.lblNumEstudiantesEditar.setText(str(resumen["estudiantes"]).zfill(2))
        self.lblNumPracticasProgresoEditar.setText(str(resumen["practicas_activas"]).zfill(2))
        self.lblNumPracComprelatasEditar.setText(str(resumen["practicas_finalizadas"]).zfill(2))

    def _generar_resumen(self, practicas: list[object]) -> dict[str, int]:
        estudiantes = set(map(lambda practica: practica.id_estudiante, practicas))
        contar_practicas = lambda estado: sum(map(lambda practica: practica.estado == estado, practicas))
        return {
            "estudiantes": len(estudiantes),
            "practicas_activas": contar_practicas("activa"),
            "practicas_finalizadas": contar_practicas("finalizada"),
        }

    def practicas_en_progreso(self):
        from controlador.ControlVentanaTAPracticasProgreso import ControlVentanaTAPracticasProgreso

        self.ventana_progreso = ControlVentanaTAPracticasProgreso(self.usuario, self, self.login)
        self.ventana_progreso.show()
        self.hide()

    def practicas_completas(self):
        from controlador.ControlVentanaTAPracticasCompletas import ControlVentanaTAPracticasCompletas

        self.ventana_completas = ControlVentanaTAPracticasCompletas(self.usuario, self, self.login)
        self.ventana_completas.show()
        self.hide()

    def ver_notificaciones(self):
        from controlador.ControlVentanaNotificaciones import ControlVentanaNotificaciones

        self.ventana_notificaciones = ControlVentanaNotificaciones(self.usuario, self)
        self.ventana_notificaciones.show()
        self.hide()

    def salir(self):
        self.close()
        if self.login is not None:
            self.login.volver_a_login()

