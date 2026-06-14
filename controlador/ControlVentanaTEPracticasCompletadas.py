from PyQt6 import QtWidgets

from modelo.configuracion.ajustes import HORAS_MAXIMAS_PRACTICA
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Practica import Practica
from modelo.Usuario import TutorEmpresarial, Usuario
from vista.estilos import EstilosClase
from vista.ui_TE_practicas_completadas import Ui_FormTEPracticasCompletadas


class ControlVentanaTEPracticasCompletadas(QtWidgets.QWidget, Ui_FormTEPracticasCompletadas):
    def __init__(self, usuario: TutorEmpresarial, ventana_te=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_te = ventana_te
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
        self.btnPracticasProgreso.clicked.connect(self.practicas_en_progreso)
        self.btnPracticasCompletadas.clicked.connect(self.cargar_datos)
        self.btnNotificaciones.clicked.connect(self.ver_notificaciones)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnBuscar.clicked.connect(self.buscar_practicas)
        self.txtBuscar.returnPressed.connect(self.buscar_practicas)
        self.txtBuscar.textChanged.connect(self.buscar_practicas)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["Practica", "Estudiante", "Empresa", "Inicio", "Fin", "Horas", "Calificacion"]
        self.tblPracticasCompletadas.setColumnCount(len(columnas))
        self.tblPracticasCompletadas.setHorizontalHeaderLabels(columnas)
        self.tblPracticasCompletadas.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblPracticasCompletadas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblPracticasCompletadas.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblPracticasCompletadas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblPracticasCompletadas.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(self._practicas_completadas())

    def buscar_practicas(self):
        texto = self.txtBuscar.text().strip().lower()
        practicas = self._practicas_completadas()
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

    def practicas_en_progreso(self):
        from controlador.ControlVentanaTEPracticaEnProgreso import ControlVentanaTEPracticaEnProgreso

        self._abrir_ventana(ControlVentanaTEPracticaEnProgreso(self.usuario, self.ventana_te, self.login))

    def ver_notificaciones(self):
        from controlador.ControlVentanaNotificaciones import ControlVentanaNotificaciones

        self._abrir_ventana(ControlVentanaNotificaciones(self.usuario, self))

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_te is not None:
            self.ventana_te.salir()

    def closeEvent(self, event):
        if self.cerrando_sesion:
            super().closeEvent(event)
            return
        self._mostrar_principal()
        self.hide()
        event.ignore()

    def _llenar_tabla(self, practicas: list[Practica]):
        self.tblPracticasCompletadas.setRowCount(len(practicas))
        for fila, practica in enumerate(practicas):
            valores = [
                practica.id_practica,
                self._nombre_estudiante(practica),
                self._nombre_empresa(practica),
                practica.fecha_inicio,
                practica.fecha_fin,
                f"{practica.horas_cumplidas}/{HORAS_MAXIMAS_PRACTICA}",
                practica.calificacion if practica.calificacion is not None else "Pendiente",
            ]
            for columna, valor in enumerate(valores):
                self.tblPracticasCompletadas.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _practicas_completadas(self) -> list[Practica]:
        practicas = self.practicas.listar_practicas_por_tutor_empresarial(self.usuario.id_usuario)
        return [practica for practica in practicas if practica.estado == "finalizada"]

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
        if self.ventana_te is not None:
            self.ventana_te.cargar_datos()
            self.ventana_te.cargar_resumen()
            self.ventana_te.show()
            self.ventana_te.raise_()
            self.ventana_te.activateWindow()

