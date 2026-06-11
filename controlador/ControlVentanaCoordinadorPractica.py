from PyQt6 import QtCore, QtGui, QtWidgets

try:
    from PyQt6.QtCharts import QChart, QChartView, QPieSeries
except ImportError:
    QChart = None
    QChartView = None
    QPieSeries = None

from controlador.ControlVentanaVerActividades import ControlVentanaVerActividades
from modelo.Empresa import Empresa
from modelo.Practica import Practica
from modelo.Usuario import Coordinador, Usuario
from vista.estilos import EstilosClase
from vista.ui_coordinador_practicas import Ui_frmAdministracionPracticas


class ControlVentanaCoordinadorPractica(QtWidgets.QWidget, Ui_frmAdministracionPracticas):
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
        self.btnEstudiantes.clicked.connect(self.abrir_estudiantes)
        self.btnTutores.clicked.connect(self.abrir_tutores)
        self.btnOfertas.clicked.connect(self.abrir_ofertas)
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnPracticas.clicked.connect(self.cargar_datos)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnBuscar.clicked.connect(self.buscar_practicas)
        self.txtBuscar.returnPressed.connect(self.buscar_practicas)
        self.txtBuscar.textChanged.connect(self.buscar_practicas)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnVerActividades.clicked.connect(self.ver_actividades)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Estudiante", "Empresa", "Inicio", "Fin", "Horas", "Estado"]
        self.tblPracticas.setColumnCount(len(columnas))
        self.tblPracticas.setHorizontalHeaderLabels(columnas)
        self.tblPracticas.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblPracticas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblPracticas.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblPracticas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblPracticas.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        practicas = Practica.cargar_todos()
        self._llenar_tabla(practicas)
        self._cargar_grafico_estado_practicas(practicas)

    def buscar_practicas(self):
        texto = self.txtBuscar.text().strip().lower()
        practicas = Practica.cargar_todos()
        if texto:
            practicas = [
                practica
                for practica in practicas
                if texto in practica.id_practica.lower()
                or texto in practica.id_estudiante.lower()
                or texto in practica.id_empresa.lower()
                or texto in self._nombre_estudiante(practica.id_estudiante).lower()
                or texto in self._nombre_empresa(practica.id_empresa).lower()
                or texto in practica.estado.lower()
            ]
        self._llenar_tabla(practicas)
        self._cargar_grafico_estado_practicas(practicas)

    def _llenar_tabla(self, practicas: list[Practica]):
        self.tblPracticas.setRowCount(len(practicas))
        for fila, practica in enumerate(practicas):
            valores = [
                practica.id_practica,
                self._nombre_estudiante(practica.id_estudiante),
                self._nombre_empresa(practica.id_empresa),
                practica.fecha_inicio,
                practica.fecha_fin,
                practica.horas_cumplidas,
                practica.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblPracticas.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _nombre_estudiante(self, id_estudiante: str) -> str:
        estudiante = Usuario.buscar_por_id(id_estudiante)
        return estudiante.nombre if estudiante else id_estudiante

    def _nombre_empresa(self, id_empresa: str) -> str:
        empresa = Empresa.buscar_por_id(id_empresa)
        return empresa.nombre_empresa if empresa else id_empresa

    def _cargar_grafico_estado_practicas(self, practicas: list[Practica]):
        if QChart is None:
            self._insertar_mensaje_widget(
                self.widgetGraficoPastel,
                "Instale PyQt6-Charts para visualizar este grafico.\n"
                "Comando: pip install PyQt6-Charts",
            )
            return

        datos: dict[str, int] = {}
        for practica in practicas:
            estado = practica.estado.strip().capitalize() if practica.estado else "Sin estado"
            datos[estado] = datos.get(estado, 0) + 1

        series = QPieSeries()
        if not practicas:
            series.append("Sin datos", 1)
        else:
            for estado, total in datos.items():
                series.append(f"{estado}: {total}", total)

        colores = [
            QtGui.QColor("#2f80ed"),
            QtGui.QColor("#27ae60"),
            QtGui.QColor("#f2994a"),
            QtGui.QColor("#9b51e0"),
            QtGui.QColor("#eb5757"),
        ]
        for indice, porcion in enumerate(series.slices()):
            porcion.setLabelVisible(True)
            porcion.setColor(colores[indice % len(colores)])

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Practicas por estado")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundVisible(False)

        self._insertar_chart_view(self.widgetGraficoPastel, chart)

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

    def ver_actividades(self):
        practica = self._practica_seleccionada()
        if practica is None:
            return
        self.subventana = ControlVentanaVerActividades(practica, self)
        self.subventana.show()
        self.hide()

    def _practica_seleccionada(self) -> Practica | None:
        fila = self.tblPracticas.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una practica de la tabla.")
            return None

        item = self.tblPracticas.item(fila, 0)
        if item is None:
            return None
        return Practica.buscar_por_id(item.text())

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def abrir_empresas(self):
        from controlador.ControlVentanaCoordinadorEmpresa import ControlVentanaCoordinadorEmpresa
        self._abrir_ventana(ControlVentanaCoordinadorEmpresa(self.usuario, self.ventana_coordinador, self.login))

    def abrir_estudiantes(self):
        from controlador.ControlVentanaCoordinadorEstudiantes import ControlVentanaCoordinadorEstudiantes
        self._abrir_ventana(ControlVentanaCoordinadorEstudiantes(self.usuario, self.ventana_coordinador, self.login))

    def abrir_ofertas(self):
        from controlador.ControlVentanaCoordinadorOferta import ControlVentanaCoordinadorOferta
        self._abrir_ventana(ControlVentanaCoordinadorOferta(self.usuario, self.ventana_coordinador, self.login))

    def abrir_postulaciones(self):
        from controlador.ControlVentanaCoordinadorPostulacion import ControlVentanaCoordinadorPostulacion
        self._abrir_ventana(ControlVentanaCoordinadorPostulacion(self.usuario, self.ventana_coordinador, self.login))

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
