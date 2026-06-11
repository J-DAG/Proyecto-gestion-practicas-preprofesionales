from PyQt6 import QtCore, QtGui, QtWidgets

try:
    from PyQt6.QtCharts import QChart, QChartView, QPieSeries
except ImportError:
    QChart = None
    QChartView = None
    QPieSeries = None

from configuracion.ajustes import ROLES
from modelo.Postulacion import Postulacion
from modelo.Practica import Practica
from modelo.Usuario import Coordinador, Usuario
from vista.estilos import EstilosClase
from vista.ui_coordinador_estudiante import Ui_frmEstudiantes


class ControlVentanaCoordinadorEstudiantes(QtWidgets.QWidget, Ui_frmEstudiantes):
    def __init__(self, usuario: Coordinador, ventana_coordinador=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_coordinador = ventana_coordinador
        self.login = login
        self.subventana = None
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInicio.clicked.connect(self.volver_inicio)
        self.btnReportes.clicked.connect(self.abrir_reportes)
        self.btnEstudiantes.clicked.connect(self.cargar_datos)
        self.btnTutores.clicked.connect(self.abrir_tutores)
        self.btnOfertas.clicked.connect(self.abrir_ofertas)
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnPracticas.clicked.connect(self.abrir_practicas)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnBuscar.clicked.connect(self.buscar_estudiantes)
        self.txtBuscar.returnPressed.connect(self.buscar_estudiantes)
        self.txtBuscar.textChanged.connect(self.buscar_estudiantes)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Nombres", "Apellidos", "Cedula", "Email", "Carrera", "Ciclo"]
        self.tblEstudiantes.setColumnCount(len(columnas))
        self.tblEstudiantes.setHorizontalHeaderLabels(columnas)
        self.tblEstudiantes.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblEstudiantes.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblEstudiantes.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblEstudiantes.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblEstudiantes.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        estudiantes = self._estudiantes()
        self._llenar_tabla(estudiantes)
        self._cargar_grafico_estado(estudiantes)

    def buscar_estudiantes(self):
        texto = self.txtBuscar.text().strip().lower()
        estudiantes = self._estudiantes()
        if texto:
            estudiantes = [
                estudiante
                for estudiante in estudiantes
                if texto in estudiante.id_usuario.lower()
                or texto in estudiante.nombres.lower()
                or texto in estudiante.apellidos.lower()
                or texto in estudiante.cedula.lower()
                or texto in estudiante.email.lower()
                or texto in estudiante.carrera.lower()
            ]
        self._llenar_tabla(estudiantes)
        self._cargar_grafico_estado(estudiantes)

    def _estudiantes(self):
        return [usuario for usuario in Usuario.cargar_todos() if usuario.rol == ROLES["ESTUDIANTE"]]

    def _llenar_tabla(self, estudiantes: list[Usuario]):
        self.tblEstudiantes.setRowCount(len(estudiantes))
        for fila, estudiante in enumerate(estudiantes):
            valores = [
                estudiante.id_usuario,
                estudiante.nombres,
                estudiante.apellidos,
                estudiante.cedula,
                estudiante.email,
                getattr(estudiante, "carrera", ""),
                getattr(estudiante, "ciclo_actual", ""),
            ]
            for columna, valor in enumerate(valores):
                self.tblEstudiantes.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _cargar_grafico_estado(self, estudiantes: list[Usuario]):
        if QChart is None:
            self._insertar_mensaje_widget(
                self.widgetGraficoPastel,
                "Instale PyQt6-Charts para visualizar este grafico.\n"
                "Comando: pip install PyQt6-Charts",
            )
            return

        practicas_por_estudiante = self._practicas_por_estudiante()
        postulaciones_por_estudiante = self._postulaciones_por_estudiante()
        postulaciones_abiertas = {"pendiente", "validada", "en_terna"}
        datos = {
            "En practica": 0,
            "Aprobado": 0,
            "Postulando": 0,
            "Sin iniciar": 0,
        }

        for estudiante in estudiantes:
            estado = self._estado_estudiante_practica(
                estudiante.id_usuario,
                practicas_por_estudiante,
                postulaciones_por_estudiante,
                postulaciones_abiertas,
            )
            datos[estado] += 1

        series = QPieSeries()
        if not estudiantes:
            series.append("Sin datos", 1)
        else:
            for estado, total in datos.items():
                if total > 0:
                    series.append(f"{estado}: {total}", total)

        colores = [
            QtGui.QColor("#2f80ed"),
            QtGui.QColor("#27ae60"),
            QtGui.QColor("#f2994a"),
            QtGui.QColor("#bdbdbd"),
        ]
        for indice, porcion in enumerate(series.slices()):
            porcion.setLabelVisible(True)
            porcion.setColor(colores[indice % len(colores)])

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Estado de aplicacion a practicas")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundVisible(False)

        self._insertar_chart_view(self.widgetGraficoPastel, chart)

    def _practicas_por_estudiante(self) -> dict[str, list[Practica]]:
        practicas_por_estudiante: dict[str, list[Practica]] = {}
        for practica in Practica.cargar_todos():
            practicas_por_estudiante.setdefault(practica.id_estudiante, []).append(practica)
        return practicas_por_estudiante

    def _postulaciones_por_estudiante(self) -> dict[str, list[Postulacion]]:
        postulaciones_por_estudiante: dict[str, list[Postulacion]] = {}
        for postulacion in Postulacion.cargar_todos():
            postulaciones_por_estudiante.setdefault(postulacion.id_estudiante, []).append(postulacion)
        return postulaciones_por_estudiante

    def _estado_estudiante_practica(
        self,
        id_estudiante: str,
        practicas_por_estudiante: dict[str, list[Practica]],
        postulaciones_por_estudiante: dict[str, list[Postulacion]],
        postulaciones_abiertas: set[str],
    ) -> str:
        practicas = practicas_por_estudiante.get(id_estudiante, [])
        if any(practica.estado == "activa" for practica in practicas):
            return "En practica"
        if any(practica.estado == "finalizada" for practica in practicas):
            return "Aprobado"
        postulaciones = postulaciones_por_estudiante.get(id_estudiante, [])
        if any(postulacion.estado in postulaciones_abiertas for postulacion in postulaciones):
            return "Postulando"
        return "Sin iniciar"

    def _insertar_chart_view(self, contenedor: QtWidgets.QWidget, chart: QChart):
        self._limpiar_contenedor(contenedor)
        layout = contenedor.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(contenedor)
            layout.setContentsMargins(0, 0, 0, 0)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        layout.addWidget(chart_view)

    def _insertar_mensaje_widget(self, contenedor: QtWidgets.QWidget, mensaje: str):
        self._limpiar_contenedor(contenedor)
        layout = contenedor.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(contenedor)
            layout.setContentsMargins(12, 12, 12, 12)
        label = QtWidgets.QLabel(mensaje)
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

    def _limpiar_contenedor(self, contenedor: QtWidgets.QWidget):
        layout = contenedor.layout()
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def abrir_empresas(self):
        from controlador.ControlVentanaCoordinadorEmpresa import ControlVentanaCoordinadorEmpresa
        self._abrir_ventana(ControlVentanaCoordinadorEmpresa(self.usuario, self.ventana_coordinador, self.login))

    def abrir_ofertas(self):
        from controlador.ControlVentanaCoordinadorOferta import ControlVentanaCoordinadorOferta
        self._abrir_ventana(ControlVentanaCoordinadorOferta(self.usuario, self.ventana_coordinador, self.login))

    def abrir_postulaciones(self):
        from controlador.ControlVentanaCoordinadorPostulacion import ControlVentanaCoordinadorPostulacion
        self._abrir_ventana(ControlVentanaCoordinadorPostulacion(self.usuario, self.ventana_coordinador, self.login))

    def abrir_practicas(self):
        from controlador.ControlVentanaCoordinadorPractica import ControlVentanaCoordinadorPractica
        self._abrir_ventana(ControlVentanaCoordinadorPractica(self.usuario, self.ventana_coordinador, self.login))

    def abrir_reportes(self):
        from controlador.ControlVentanaCoordinadorReportes import ControlVentanaCoordinadorReportes
        self._abrir_ventana(ControlVentanaCoordinadorReportes(self.usuario, self.ventana_coordinador, self.login))

    def abrir_tutores(self):
        from controlador.ControlVentanaCoordinadorTutores import ControlVentanaCoordinadorTutores
        self._abrir_ventana(ControlVentanaCoordinadorTutores(self.usuario, self.ventana_coordinador, self.login))

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_coordinador is not None:
            self.ventana_coordinador.salir()

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
        if self.ventana_coordinador is not None:
            self.ventana_coordinador.cargar_datos()
            self.ventana_coordinador.cargar_resumen()
            self.ventana_coordinador.show()
            self.ventana_coordinador.raise_()
            self.ventana_coordinador.activateWindow()
