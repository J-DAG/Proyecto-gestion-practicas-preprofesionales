from PyQt6 import QtCore, QtWidgets

from controlador.ControlPractica import ControlPractica
from modelo.Documentos import Formulario
from modelo.Practica import Practica
from modelo.Usuario import Estudiante
from vista.estilos import EstilosClase
from vista.ui_EST_formularios import Ui_FormEST


class ControlVentanaEstudianteFormularios(QtWidgets.QWidget, Ui_FormEST):
    def __init__(self, usuario: Estudiante, ventana_estudiante=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_estudiante = ventana_estudiante
        self.login = login
        self.practicas = ControlPractica()
        self.cerrando_sesion = False
        self.setupUi(self)
        self._crear_tabla_formularios()
        self.iniciar_controlador()

    def _crear_tabla_formularios(self):
        self.tblFormularios = QtWidgets.QTableWidget(parent=self)
        self.tblFormularios.setGeometry(QtCore.QRect(80, 220, 1041, 461))
        self.tblFormularios.setObjectName("tblFormularios")

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInico.clicked.connect(self.volver_inicio)
        self.btnMiPractica.clicked.connect(self.ver_progreso)
        self.btnMisPostulaciones.clicked.connect(self.ver_postulaciones)
        self.btnOfertaLaboral.clicked.connect(self.ver_ofertas)
        self.btnMisFormularios.clicked.connect(self.cargar_datos)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())
    """"
    Configurar lo de no tiene convenio para enviar carta compromiso
    vista de formularios 1 y 2
    """
    def configurar_tabla(self):
        columnas = ["ID", "Practica", "Tipo", "Fecha", "Calificacion", "Observaciones"]
        self.tblFormularios.setColumnCount(len(columnas))
        self.tblFormularios.setHorizontalHeaderLabels(columnas)
        self.tblFormularios.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblFormularios.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblFormularios.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblFormularios.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblFormularios.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        formularios = self.practicas.listar_formularios_estudiante(self.usuario.id_usuario)
        self.tblFormularios.setRowCount(len(formularios))
        for fila, formulario in enumerate(formularios):
            valores = [
                formulario.id_formulario,
                formulario.id_practica,
                formulario.tipo,
                formulario.fecha_registro,
                formulario.calificacion if formulario.calificacion is not None else "",
                formulario.observaciones,
            ]
            for columna, valor in enumerate(valores):
                self.tblFormularios.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

        tipos = {formulario.tipo for formulario in formularios}
        self.lblTitulo_2.setText("Formulario 1: enviado" if "Formulario 1" in tipos else "Formulario 1: pendiente")
        finales = {"Formulario 2", "Formulario 3"} & tipos
        self.lblTitulo_3.setText("Formularios finales: enviados" if finales else "Formularios finales: pendientes")

    def ver_progreso(self):
        from controlador.ControlVentanaEstudiantePractica import ControlVentanaEstudiantePractica
        self._abrir_ventana(ControlVentanaEstudiantePractica(self.usuario, self.ventana_estudiante, self.login))

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
