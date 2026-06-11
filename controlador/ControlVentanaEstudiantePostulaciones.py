from PyQt6 import QtWidgets

from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Usuario import Estudiante
from vista.estilos import EstilosClase
from vista.ui_EST_postulaciones import Ui_FormESTPostulaciones


class ControlVentanaEstudiantePostulaciones(QtWidgets.QWidget, Ui_FormESTPostulaciones):
    def __init__(self, usuario: Estudiante, ventana_estudiante=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_estudiante = ventana_estudiante
        self.login = login
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInico.clicked.connect(self.volver_inicio)
        self.btnMiPractica.clicked.connect(self.ver_progreso)
        self.btnMisPostulaciones.clicked.connect(self.cargar_datos)
        self.btnOfertaLaboral.clicked.connect(self.ver_ofertas)
        self.btnMisFormularios.clicked.connect(self.ver_formularios)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Oferta", "Titulo", "Fecha", "Estado", "Documento"]
        self.tblPostulaciones.setColumnCount(len(columnas))
        self.tblPostulaciones.setHorizontalHeaderLabels(columnas)
        self.tblPostulaciones.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblPostulaciones.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblPostulaciones.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblPostulaciones.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblPostulaciones.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        postulaciones = [p for p in Postulacion.cargar_todos() if p.id_estudiante == self.usuario.id_usuario]
        postulaciones.sort(key=lambda postulacion: str(postulacion.fecha_postulacion), reverse=True)
        self.tblPostulaciones.setRowCount(len(postulaciones))
        for fila, postulacion in enumerate(postulaciones):
            oferta = Oferta.buscar_por_id(postulacion.id_oferta)
            valores = [
                postulacion.id_postulacion,
                postulacion.id_oferta,
                oferta.titulo if oferta else "Oferta no encontrada",
                postulacion.fecha_postulacion,
                postulacion.estado,
                "Adjunto" if postulacion.tiene_documento_malla() else "Sin adjunto",
            ]
            for columna, valor in enumerate(valores):
                self.tblPostulaciones.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def ver_progreso(self):
        from controlador.ControlVentanaEstudiantePractica import ControlVentanaEstudiantePractica
        self._abrir_ventana(ControlVentanaEstudiantePractica(self.usuario, self.ventana_estudiante, self.login))

    def ver_formularios(self):
        from controlador.ControlVentanaEstudianteFormularios import ControlVentanaEstudianteFormularios
        self._abrir_ventana(ControlVentanaEstudianteFormularios(self.usuario, self.ventana_estudiante, self.login))

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
