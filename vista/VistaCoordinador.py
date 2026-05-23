from configuracion.Ajustes import ROLES
from controlador.ControlOferta import ControlOferta
from controlador.ControlPostulacion import ControlPostulacion
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Usuario import Coordinador, Usuario, Estudiante
from utilidades.Excepciones import SistemaPracticasError, ValidacionError, ReglaNegocioError
from vista.Validaciones import leer_texto, leer_bool, pausar, leer_entero, leer_fecha, imprimir_tabla


class VistaCoordinador:
    def __init__(self, usuario: Coordinador) -> None:
        self.usuario = usuario
        self.ofertas = ControlOferta()
        self.postulaciones = ControlPostulacion()
        self.practicas = ControlPractica()

    def mostrar(self) -> None:
        while True:
            print("\n=== Panel Coordinador ===")
            print("1. Registrar empresa")
            print("2. Crear oferta")
            print("3. Listar ofertas")
            print("4. Ver postulantes por oferta")
            print("5. Gestionar postulacion")
            print("6. Generar terna")
            print("7. Crear practica manualmente")
            print("8. Ver practicas")
            print("9. Ver progreso de estudiantes")
            print("0. Cerrar sesion")
            opcion = leer_texto("Seleccione: ")

            acciones = {
                "1": self._registrar_empresa,
                "2": self._crear_oferta,
                "3": self._listar_ofertas,
                "4": self._ver_postulantes_por_oferta,
                "5": self._gestionar_postulacion,
                "6": self._generar_terna,
                "7": self._crear_practica,
                "8": self._listar_practicas,
                "9": self._ver_progreso_estudiantes,
            }
            if opcion == "0":
                return
            accion = acciones.get(opcion)
            if accion:
                accion()

    def _registrar_empresa(self) -> None:
        try:
            empresa = self.ofertas.registrar_empresa(
                leer_texto("Nombre comercial: "),
                leer_texto("Email: "),
                leer_texto("Razon social: "),
                leer_texto("RUC: "),
                leer_texto("Sector: "),
                leer_texto("Ubicacion: "),
                leer_texto("Mision: "),
                leer_texto("Vision: "),
                leer_bool("Convenio vigente"),
            )
            print(f"Empresa registrada: {empresa.id_empresa}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _crear_oferta(self) -> None:
        try:
            self._mostrar_empresas()
            oferta = self.ofertas.crear_oferta(
                leer_texto("ID empresa: "),
                leer_texto("Titulo: "),
                leer_texto("Descripcion: "),
                leer_texto("Requisitos: "),
                leer_texto("Area: "),
                leer_entero("Cupos: "),
                leer_fecha("Fecha cierre"),
            )
            print(f"Oferta creada: {oferta.id_oferta}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _listar_ofertas(self) -> None:
        imprimir_tabla(self.ofertas.listar_ofertas())
        pausar()

    def _ver_postulantes_por_oferta(self) -> None:
        try:
            self._mostrar_ofertas()
            id_oferta = leer_texto("ID oferta: ")
            oferta = Oferta.obtener_por_id(id_oferta)
            empresa = Empresa.buscar_por_id(oferta.id_empresa)
            postulaciones = [
                postulacion
                for postulacion in self.postulaciones.listar_postulaciones()
                if postulacion.id_oferta == id_oferta
            ]

            print(f"\nOferta: {oferta.titulo}")
            print(f"Empresa: {empresa.nombre_empresa if empresa else oferta.id_empresa}")
            print(f"Cupos disponibles: {oferta.cupos}")
            if not postulaciones:
                print("No hay postulantes para esta oferta.")
            for postulacion in postulaciones:
                estudiante = Usuario.buscar_por_id(postulacion.id_estudiante)
                self._imprimir_postulacion(postulacion, estudiante)
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _gestionar_postulacion(self) -> None:
        print("\n=== Gestionar postulacion ===")
        print("1. Aprobar/validar postulacion")
        print("2. Aprobar definitivamente y crear practica")
        print("3. Rechazar postulacion")
        opcion = leer_texto("Seleccione: ")
        if opcion == "1":
            self._validar_postulacion()
        elif opcion == "2":
            self._aceptar_postulacion()
        elif opcion == "3":
            self._rechazar_postulacion()

    def _validar_postulacion(self) -> None:
        try:
            self._mostrar_postulaciones()
            postulacion = self.postulaciones.validar_postulacion(
                leer_texto("ID postulacion: "),
                self.usuario,
            )
            print(f"Postulacion aprobada/validada: {postulacion.id_postulacion}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _generar_terna(self) -> None:
        try:
            self._mostrar_ofertas()
            terna = self.postulaciones.generar_terna(leer_texto("ID oferta: "))
            imprimir_tabla(terna)
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _aceptar_postulacion(self) -> None:
        try:
            self._mostrar_postulaciones(estados={"validada", "en_terna"})
            id_postulacion = leer_texto("ID postulacion: ")
            self._mostrar_tutores()
            fecha_inicio = leer_fecha("Fecha inicio")
            fecha_fin = leer_fecha("Fecha fin")
            id_tutor_academico = leer_texto("ID tutor academico: ")
            id_tutor_empresarial = leer_texto("ID tutor empresarial: ")
            self._validar_datos_practica(fecha_inicio, fecha_fin, id_tutor_academico, id_tutor_empresarial)

            postulacion = self.postulaciones.aceptar_postulacion(id_postulacion)
            practica = self.practicas.crear_practica(
                postulacion.id_postulacion,
                fecha_inicio,
                fecha_fin,
                id_tutor_academico,
                id_tutor_empresarial,
            )
            print(
                f"Postulacion aceptada y practica creada: "
                f"{practica.id_practica}"
            )
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _validar_datos_practica(
            self,
            fecha_inicio,
            fecha_fin,
            id_tutor_academico: str,
            id_tutor_empresarial: str,
    ) -> None:
        if fecha_fin < fecha_inicio:
            raise ValidacionError("La fecha de fin no puede ser anterior a la fecha de inicio.")

        tutor_academico = Usuario.obtener_por_id(id_tutor_academico)
        if tutor_academico.rol != ROLES["TUTOR_ACADEMICO"]:
            raise ReglaNegocioError("El tutor academico seleccionado no tiene ese rol.")

        tutor_empresarial = Usuario.obtener_por_id(id_tutor_empresarial)
        if tutor_empresarial.rol != ROLES["TUTOR_EMPRESARIAL"]:
            raise ReglaNegocioError("El tutor empresarial seleccionado no tiene ese rol.")

    def _rechazar_postulacion(self) -> None:
        try:
            self._mostrar_postulaciones(estados={"pendiente", "validada", "en_terna"})
            postulacion = self.postulaciones.rechazar_postulacion(leer_texto("ID postulacion: "))
            print(f"Postulacion rechazada: {postulacion.id_postulacion}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _crear_practica(self) -> None:
        try:
            self._mostrar_postulaciones(estados={"aceptada"})
            self._mostrar_tutores()
            practica = self.practicas.crear_practica(
                leer_texto("ID postulacion aceptada: "),
                leer_fecha("Fecha inicio"),
                leer_fecha("Fecha fin"),
                leer_texto("ID tutor academico: "),
                leer_texto("ID tutor empresarial: "),
            )
            print(f"Practica creada: {practica.id_practica}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _mostrar_empresas(self) -> None:
        empresas = self.ofertas.listar_empresas()
        print("\nEmpresas disponibles:")
        if not empresas:
            print("No hay empresas registradas.")
        for empresa in empresas:
            convenio = "con convenio" if empresa.convenio_vigente else "sin convenio"
            print(
                f"- {empresa.id_empresa} | {empresa.nombre_empresa} | "
                f"RUC: {empresa.ruc} | {convenio}"
            )

    def _mostrar_ofertas(self) -> None:
        ofertas = self.ofertas.listar_ofertas()
        print("\nOfertas registradas:")
        if not ofertas:
            print("No hay ofertas registradas.")
        for oferta in ofertas:
            empresa = Empresa.buscar_por_id(oferta.id_empresa)
            nombre_empresa = empresa.nombre_empresa if empresa else oferta.id_empresa
            print(
                f"- {oferta.id_oferta} | {oferta.titulo} | {nombre_empresa} | "
                f"Cupos: {oferta.cupos} | Estado: {oferta.estado} | "
                f"Cierre: {oferta.fecha_cierre}"
            )

    def _mostrar_postulaciones(self, estados: set[str] | None = None) -> None:
        postulaciones = self.postulaciones.listar_postulaciones()
        if estados is not None:
            postulaciones = [
                postulacion
                for postulacion in postulaciones
                if postulacion.estado in estados
            ]

        print("\nPostulaciones disponibles:")
        if not postulaciones:
            print("No hay postulaciones para esta accion.")
        for postulacion in postulaciones:
            estudiante = Usuario.buscar_por_id(postulacion.id_estudiante)
            oferta = Oferta.buscar_por_id(postulacion.id_oferta)
            nombre_estudiante = estudiante.nombre if estudiante else postulacion.id_estudiante
            titulo_oferta = oferta.titulo if oferta else postulacion.id_oferta
            print(
                f"- {postulacion.id_postulacion} | {nombre_estudiante} | "
                f"Oferta: {titulo_oferta} | Estado: {postulacion.estado}"
            )

    def _mostrar_tutores(self) -> None:
        usuarios = Usuario.cargar_todo()
        print("\nTutores academicos:")
        academicos = [u for u in usuarios if u.rol == ROLES["TUTOR_ACADEMICO"]]
        if not academicos:
            print("No hay tutores academicos registrados.")
        for tutor in academicos:
            print(f"- {tutor.id_usuario} | {tutor.nombre} | {tutor.email}")

        print("\nTutores empresariales:")
        empresariales = [u for u in usuarios if u.rol == ROLES["TUTOR_EMPRESARIAL"]]
        if not empresariales:
            print("No hay tutores empresariales registrados.")
        for tutor in empresariales:
            empresa = Empresa.buscar_por_id(getattr(tutor, "id_empresa", ""))
            nombre_empresa = empresa.nombre_empresa if empresa else getattr(tutor, "id_empresa", "")
            print(f"- {tutor.id_usuario} | {tutor.nombre} | {nombre_empresa} | {tutor.email}")

    def _imprimir_postulacion(self, postulacion, estudiante: Usuario | None) -> None:
        if isinstance(estudiante, Estudiante):
            detalle_estudiante = (
                f"{estudiante.nombre} | Cedula: {estudiante.cedula} | "
                f"Carrera: {estudiante.carrera} | Ciclo: {estudiante.ciclo_actual} | "
                f"Practicas previas: {estudiante.practicas_previas}"
            )
        elif estudiante is not None:
            detalle_estudiante = f"{estudiante.nombre} | Rol: {estudiante.rol}"
        else:
            detalle_estudiante = "Estudiante no encontrado"

        print(
            f"- {postulacion.id_postulacion} | {detalle_estudiante} | "
            f"Fecha: {postulacion.fecha_postulacion} | Estado: {postulacion.estado}"
        )

    def _listar_practicas(self) -> None:
        imprimir_tabla(self.practicas.listar_practicas())
        pausar()

    def _ver_progreso_estudiantes(self) -> None:
        try:
            resumenes = self.practicas.listar_progreso_estudiantes()
            if not resumenes:
                print("No hay practicas registradas.")
            for resumen in resumenes:
                practica = resumen["practica"]
                estudiante = resumen["estudiante"]
                empresa = resumen["empresa"]
                nombre_estudiante = estudiante.nombre if estudiante else "Estudiante no encontrado"
                nombre_empresa = empresa.nombre_empresa if empresa else "Empresa no encontrada"
                print(
                    f"- {nombre_estudiante} | {nombre_empresa} | "
                    f"Practica: {practica.id_practica} | Estado: {practica.estado} | "
                    f"Horas: {practica.horas_cumplidas}/{resumen['horas_requeridas']} | "
                    f"Actividades: {resumen['actividades_completadas']}/{resumen['actividades']} completadas"
                )
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()
