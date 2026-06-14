from PyQt6 import QtWidgets

from modelo.configuracion.ajustes import HORAS_MAXIMAS_PRACTICA
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Practica import Practica
from modelo.Usuario import TutorAcademico, Usuario
from vista.estilos import EstilosClase
from vista.ui_TA_practicas_progreso import Ui_FormTAPracticasProgreso


class ControlVentanaTAPracticasProgreso(QtWidgets.QWidget, Ui_FormTAPracticasProgreso):
    def __init__(self, usuario: TutorAcademico, ventana_ta=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_ta = ventana_ta
        self.login = login
        self.practicas = ControlPractica()
        self.subventana = None
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInico.clicked.connect(self.volver_inicio)
        self.btnPracticasProgreso.clicked.connect(self.cargar_datos)
        self.btnPracticasCompletadas.clicked.connect(self.practicas_completas)
        self.btnNotificaciones.clicked.connect(self.ver_notificaciones)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnBuscar.clicked.connect(self.buscar_practicas)
        self.txtBuscar.returnPressed.connect(self.buscar_practicas)
        self.txtBuscar.textChanged.connect(self.buscar_practicas)
        self.btnActividades.clicked.connect(self.ver_actividades)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["Practica", "Estudiante", "Empresa", "Inicio", "Fin", "Horas", "Estado"]
        self.tblEstudiantesTA.setColumnCount(len(columnas))
        self.tblEstudiantesTA.setHorizontalHeaderLabels(columnas)
        self.tblEstudiantesTA.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblEstudiantesTA.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblEstudiantesTA.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblEstudiantesTA.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblEstudiantesTA.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        practicas = self._practicas_en_progreso()
        self._llenar_tabla(practicas)

    def buscar_practicas(self):
        texto = self.txtBuscar.text().strip().lower()
        practicas = self._practicas_en_progreso()
        if texto:
            practicas = [
                practica
                for practica in practicas
                if texto in practica.id_practica.lower()
                or texto in practica.id_estudiante.lower()
                or texto in practica.id_empresa.lower()
                or texto in self._nombre_estudiante(practica).lower()
                or texto in self._nombre_empresa(practica).lower()
            ]
        self._llenar_tabla(practicas)

    def ver_actividades(self):
        practica = self._practica_seleccionada()
        if practica is None:
            return
        from controlador.ControlVentanaTAActividades import ControlVentanaTAActividades

        self.subventana = ControlVentanaTAActividades(practica, self.usuario, self)
        self.subventana.show()
        self.hide()

    def practicas_completas(self):
        from controlador.ControlVentanaTAPracticasCompletas import ControlVentanaTAPracticasCompletas

        self._abrir_ventana(ControlVentanaTAPracticasCompletas(self.usuario, self.ventana_ta, self.login))

    def ver_notificaciones(self):
        from controlador.ControlVentanaNotificaciones import ControlVentanaNotificaciones

        self._abrir_ventana(ControlVentanaNotificaciones(self.usuario, self))

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_ta is not None:
            self.ventana_ta.salir()

    def closeEvent(self, event):
        if self.cerrando_sesion:
            super().closeEvent(event)
            return
        self._mostrar_principal()
        self.hide()
        event.ignore()

    def _llenar_tabla(self, practicas: list[Practica]):
        self.tblEstudiantesTA.setRowCount(len(practicas))
        for fila, practica in enumerate(practicas):
            valores = [
                practica.id_practica,
                self._nombre_estudiante(practica),
                self._nombre_empresa(practica),
                practica.fecha_inicio,
                practica.fecha_fin,
                f"{practica.horas_cumplidas}/{HORAS_MAXIMAS_PRACTICA}",
                practica.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblEstudiantesTA.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _practicas_en_progreso(self) -> list[Practica]:
        practicas = self.practicas.listar_practicas_por_tutor_academico(self.usuario.id_usuario)
        return [practica for practica in practicas if practica.estado == "activa"]

    def _practica_seleccionada(self) -> Practica | None:
        fila = self.tblEstudiantesTA.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una practica de la tabla.")
            return None
        item = self.tblEstudiantesTA.item(fila, 0)
        if item is None:
            return None
        return Practica.buscar_por_id(item.text())

    def _nombre_estudiante(self, practica: Practica) -> str:
        estudiante = Usuario.buscar_por_id(practica.id_estudiante)
        return estudiante.nombre if estudiante else practica.id_estudiante

    def _nombre_empresa(self, practica: Practica) -> str:
        empresa = Empresa.buscar_por_id(practica.id_empresa)
        return empresa.nombre_empresa if empresa else practica.id_empresa

    def _abrir_ventana(self, ventana):
        self.subventana = ventana
        self.subventana.show()
        self.hide()

    def _mostrar_principal(self):
        if self.ventana_ta is not None:
            self.ventana_ta.cargar_datos()
            self.ventana_ta.cargar_resumen()
            self.ventana_ta.show()
            self.ventana_ta.raise_()
            self.ventana_ta.activateWindow()

