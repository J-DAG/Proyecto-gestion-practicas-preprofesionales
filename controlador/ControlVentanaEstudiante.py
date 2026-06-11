from PyQt6 import QtWidgets

from controlador.ControlOferta import ControlOferta
from modelo.Empresa import Empresa
from modelo.Usuario import Estudiante
from vista.estilos import EstilosClase
from vista.ui_main_window_estudiante import Ui_MainWindowEstudiante


class ControlVentanaEstudiante(QtWidgets.QMainWindow, Ui_MainWindowEstudiante):
    def __init__(self, usuario: Estudiante, login=None, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.login = login
        self.ofertas = ControlOferta()
        self.subventana = None
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnCerrarSesion_2.clicked.connect(self.salir)
        self.btnCerrarSesion.triggered.connect(self.salir)
        self.btnNotificaciones.triggered.connect(self.ver_notificaciones)
        self.btnVerNotificaciones.clicked.connect(self.ver_notificaciones)
        self.btnEnProgreso.triggered.connect(self.ver_progreso)
        self.btnFormularios.triggered.connect(self.ver_formularios)
        self.btnPostulaciones.triggered.connect(self.ver_postulaciones)
        self.btnOfertas.triggered.connect(self.ver_ofertas)
        if hasattr(self, "btnMisPracticas"):
            self.btnMisPracticas.clicked.connect(self.ver_progreso)
        if hasattr(self, "btnMisFormularios"):
            self.btnMisFormularios.clicked.connect(self.ver_formularios)
        if hasattr(self, "btnMisPostulaciones"):
            self.btnMisPostulaciones.clicked.connect(self.ver_postulaciones)
        if hasattr(self, "btnVerOfertaLaboral"):
            self.btnVerOfertaLaboral.clicked.connect(self.ver_ofertas)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Empresa", "Titulo", "Area", "Cupos", "Cierre", "Estado"]
        self.tblListaOfertasLaborales.setColumnCount(len(columnas))
        self.tblListaOfertasLaborales.setHorizontalHeaderLabels(columnas)
        self.tblListaOfertasLaborales.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblListaOfertasLaborales.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblListaOfertasLaborales.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblListaOfertasLaborales.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblListaOfertasLaborales.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        ofertas = self.ofertas.listar_ofertas(solo_disponibles=True)
        self.tblListaOfertasLaborales.setRowCount(len(ofertas))
        for fila, oferta in enumerate(ofertas):
            empresa = Empresa.buscar_por_id(oferta.id_empresa)
            valores = [
                oferta.id_oferta,
                empresa.nombre_empresa if empresa else oferta.id_empresa,
                oferta.titulo,
                oferta.area,
                oferta.cupos,
                oferta.fecha_cierre,
                oferta.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblListaOfertasLaborales.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def ver_progreso(self):
        from controlador.ControlVentanaEstudiantePractica import ControlVentanaEstudiantePractica

        self._abrir_ventana(ControlVentanaEstudiantePractica(self.usuario, self, self.login))

    def ver_formularios(self):
        from controlador.ControlVentanaEstudianteFormularios import ControlVentanaEstudianteFormularios

        self._abrir_ventana(ControlVentanaEstudianteFormularios(self.usuario, self, self.login))

    def ver_postulaciones(self):
        from controlador.ControlVentanaEstudiantePostulaciones import ControlVentanaEstudiantePostulaciones

        self._abrir_ventana(ControlVentanaEstudiantePostulaciones(self.usuario, self, self.login))

    def ver_ofertas(self):
        from controlador.ControlVentanaEstudianteOfertasLaborales import ControlVentanaEstudianteOfertasLaborales

        self._abrir_ventana(ControlVentanaEstudianteOfertasLaborales(self.usuario, self, self.login))

    def ver_notificaciones(self):
        from controlador.ControlVentanaNotificaciones import ControlVentanaNotificaciones

        self._abrir_ventana(ControlVentanaNotificaciones(self.usuario, self))

    def salir(self):
        self.close()
        if self.login is not None:
            self.login.volver_a_login()

    def _abrir_ventana(self, ventana):
        self.subventana = ventana
        self.subventana.show()
        self.hide()
