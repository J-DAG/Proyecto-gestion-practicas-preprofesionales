from PyQt6 import QtCore, QtGui, QtWidgets

try:
    from PyQt6.QtCharts import (
        QBarCategoryAxis,
        QBarSeries,
        QBarSet,
        QChart,
        QChartView,
        QPieSeries,
        QValueAxis,
    )
except ImportError:
    QBarCategoryAxis = None
    QBarSeries = None
    QBarSet = None
    QChart = None
    QChartView = None
    QPieSeries = None
    QValueAxis = None

from modelo.configuracion.ajustes import ROLES
from modelo.Empresa import Empresa
from modelo.Postulacion import Postulacion
from modelo.Practica import Practica
from modelo.Usuario import Coordinador, Usuario
from vista.estilos import EstilosClase
from vista.ui_coordinador_informacion_reportes import Ui_frmReportes


class ControlVentanaCoordinadorReportes(QtWidgets.QWidget, Ui_frmReportes):
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
        self.cargar_resumen()
        self.btnInicio.clicked.connect(self.volver_inicio)
        self.btnReportes.clicked.connect(self.cargar_resumen)
        self.btnEstudiantes.clicked.connect(self.abrir_estudiantes)
        self.btnTutores.clicked.connect(self.abrir_tutores)
        self.btnOfertas.clicked.connect(self.abrir_ofertas)
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnPracticas.clicked.connect(self.abrir_practicas)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def cargar_resumen(self):
        usuarios = Usuario.cargar_todos()
        practicas = Practica.cargar_todos()
        empresas = Empresa.cargar_todos()
        postulaciones = Postulacion.cargar_todos()
        resumen = self._generar_resumen(usuarios, practicas, empresas, postulaciones)

        self.lblNumEstudiantes.setText(str(resumen["estudiantes"]))
        self.lblNumTA.setText(str(resumen["tutores_academicos"]))
        self.lblTE.setText(str(resumen["tutores_empresariales"]))
        self.lblNumEmpresas.setText(str(resumen["empresas"]))
        self.lblNumPostulaciones.setText(str(resumen["postulaciones"]))
        self.lblNumPracActiva.setText(str(resumen["practicas_activas"]))
        self.lblNumPracFinalizada.setText(str(resumen["practicas_finalizadas"]))
        self.cargar_graficos(usuarios, practicas, postulaciones)

    def _generar_resumen(
        self,
        usuarios: list[Usuario],
        practicas: list[Practica],
        empresas: list[Empresa],
        postulaciones: list[Postulacion],
    ) -> dict[str, int]:
        contar_rol = lambda rol: sum(map(lambda usuario: usuario.rol == rol, usuarios))
        contar_practicas = lambda estado: sum(map(lambda practica: practica.estado == estado, practicas))
        return {
            "estudiantes": contar_rol(ROLES["ESTUDIANTE"]),
            "tutores_academicos": contar_rol(ROLES["TUTOR_ACADEMICO"]),
            "tutores_empresariales": contar_rol(ROLES["TUTOR_EMPRESARIAL"]),
            "empresas": len(empresas),
            "postulaciones": len(postulaciones),
            "practicas_activas": contar_practicas("activa"),
            "practicas_finalizadas": contar_practicas("finalizada"),
        }

    def cargar_graficos(
        self,
        usuarios: list[Usuario],
        practicas: list[Practica],
        postulaciones: list[Postulacion],
    ):
        if QChart is None:
            self._mostrar_graficos_no_disponibles()
            return
        self._crear_grafico_estado_estudiantes(usuarios, practicas, postulaciones)
        self._crear_grafico_estudiantes_ciclo(usuarios, practicas, postulaciones)

    def _crear_grafico_estado_estudiantes(
        self,
        usuarios: list[Usuario],
        practicas: list[Practica],
        postulaciones: list[Postulacion],
    ):
        estudiantes = [usuario for usuario in usuarios if usuario.rol == ROLES["ESTUDIANTE"]]
        practicas_por_estudiante: dict[str, list[Practica]] = {}
        for practica in practicas:
            practicas_por_estudiante.setdefault(practica.id_estudiante, []).append(practica)

        postulaciones_por_estudiante: dict[str, list[Postulacion]] = {}
        for postulacion in postulaciones:
            postulaciones_por_estudiante.setdefault(postulacion.id_estudiante, []).append(postulacion)

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

    def _crear_grafico_estudiantes_ciclo(
        self,
        usuarios: list[Usuario],
        practicas: list[Practica],
        postulaciones: list[Postulacion],
    ):
        estudiantes = [usuario for usuario in usuarios if usuario.rol == ROLES["ESTUDIANTE"]]
        ciclos = sorted({int(getattr(estudiante, "ciclo_actual", 0) or 0) for estudiante in estudiantes})
        ciclos = [ciclo for ciclo in ciclos if ciclo > 0]

        datos = {
            ciclo: {
                "En practica": 0,
                "Aprobado": 0,
                "Postulando": 0,
                "Sin iniciar": 0,
            }
            for ciclo in ciclos
        }

        practicas_por_estudiante: dict[str, list[Practica]] = {}
        for practica in practicas:
            practicas_por_estudiante.setdefault(practica.id_estudiante, []).append(practica)

        postulaciones_abiertas = {"pendiente", "validada", "en_terna"}
        postulaciones_por_estudiante: dict[str, list[Postulacion]] = {}
        for postulacion in postulaciones:
            postulaciones_por_estudiante.setdefault(postulacion.id_estudiante, []).append(postulacion)

        for estudiante in estudiantes:
            ciclo = int(getattr(estudiante, "ciclo_actual", 0) or 0)
            if ciclo not in datos:
                continue
            estado = self._estado_estudiante_practica(
                estudiante.id_usuario,
                practicas_por_estudiante,
                postulaciones_por_estudiante,
                postulaciones_abiertas,
            )
            datos[ciclo][estado] += 1

        categorias = [str(ciclo) for ciclo in ciclos] or ["Sin datos"]
        colores = {
            "En practica": "#2f80ed",
            "Aprobado": "#27ae60",
            "Postulando": "#f2994a",
            "Sin iniciar": "#bdbdbd",
        }
        series = QBarSeries()
        maximo = 1
        for estado, color in colores.items():
            barra = QBarSet(estado)
            barra.setColor(QtGui.QColor(color))
            valores = [datos[ciclo][estado] for ciclo in ciclos] if ciclos else [0]
            for valor in valores:
                barra.append(valor)
                maximo = max(maximo, valor)
            series.append(barra)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Estudiantes por ciclo academico")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundVisible(False)

        eje_x = QBarCategoryAxis()
        eje_x.append(categorias)
        eje_y = QValueAxis()
        eje_y.setRange(0, maximo + 1)
        eje_y.setLabelFormat("%d")
        eje_y.setTitleText("Estudiantes")

        chart.addAxis(eje_x, QtCore.Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(eje_y, QtCore.Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(eje_x)
        series.attachAxis(eje_y)

        self._insertar_chart_view(self.widgetGraficoBarras, chart)

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

    def _mostrar_graficos_no_disponibles(self):
        mensaje = (
            "Instale PyQt6-Charts para visualizar este grafico.\n"
            "Comando: pip install PyQt6-Charts"
        )
        self._insertar_mensaje_widget(self.widgetGraficoPastel, mensaje)
        self._insertar_mensaje_widget(self.widgetGraficoBarras, mensaje)

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

    def abrir_estudiantes(self):
        from controlador.ControlVentanaCoordinadorEstudiantes import ControlVentanaCoordinadorEstudiantes
        self._abrir_ventana(ControlVentanaCoordinadorEstudiantes(self.usuario, self.ventana_coordinador, self.login))

    def abrir_ofertas(self):
        from controlador.ControlVentanaCoordinadorOferta import ControlVentanaCoordinadorOferta
        self._abrir_ventana(ControlVentanaCoordinadorOferta(self.usuario, self.ventana_coordinador, self.login))

    def abrir_postulaciones(self):
        from controlador.ControlVentanaCoordinadorPostulacion import ControlVentanaCoordinadorPostulacion
        self._abrir_ventana(ControlVentanaCoordinadorPostulacion(self.usuario, self.ventana_coordinador, self.login))

    def abrir_practicas(self):
        from controlador.ControlVentanaCoordinadorPractica import ControlVentanaCoordinadorPractica
        self._abrir_ventana(ControlVentanaCoordinadorPractica(self.usuario, self.ventana_coordinador, self.login))

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

