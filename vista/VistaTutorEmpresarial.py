from controlador.ControlNotificacion import ControlNotificacion
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Usuario import TutorEmpresarial, Usuario
from utilidades.Excepciones import SistemaPracticasError
from vista.Validaciones import leer_texto, pausar, leer_entero, leer_bool


class VistaTutorEmpresarial:
    def __init__(self, usuario: TutorEmpresarial) -> None:
        self.usuario = usuario
        self.practicas = ControlPractica()
        self.notificaciones = ControlNotificacion()

    def mostrar(self) -> None:
        while True:
            print("\n=== Panel Tutor Empresarial ===")
            print("1. Ver practicas asignadas")
            print("2. Registrar actividad")
            print("3. Editar actividad")
            print("4. Eliminar actividad")
            print("5. Marcar actividad completada o pendiente")
            print("6. Ver actividades de una practica")
            print("7. Ver notificaciones")
            print("0. Cerrar sesion")
            opcion = leer_texto("Seleccione: ")

            acciones = {
                "1": self._ver_practicas_asignadas,
                "2": self._registrar_actividad,
                "3": self._editar_actividad,
                "4": self._eliminar_actividad,
                "5": self._cambiar_completado,
                "6": self._ver_actividades,
                "7": self._ver_notificaciones,
            }
            if opcion == "0":
                return
            accion = acciones.get(opcion)
            if accion:
                accion()

    def _ver_practicas_asignadas(self) -> None:
        practicas = self.practicas.listar_practicas_por_tutor_empresarial(
            self.usuario.id_usuario,
        )
        if not practicas:
            print("No tiene practicas asignadas.")
        for practica in practicas:
            estudiante = Usuario.buscar_por_id(practica.id_estudiante)
            empresa = Empresa.buscar_por_id(practica.id_empresa)
            nombre_estudiante = estudiante.nombre if estudiante else "Estudiante no encontrado"
            nombre_empresa = empresa.nombre_empresa if empresa else "Empresa no encontrada"
            print(
                f"- {nombre_estudiante} | {nombre_empresa} | "
                f"Practica: {practica.id_practica} | Estado: {practica.estado} | "
                f"Horas: {practica.horas_cumplidas}/240"
            )
        pausar()

    def _registrar_actividad(self) -> None:
        try:
            self._mostrar_practicas_asignadas()
            id_practica = leer_texto("ID practica: ")
            self._obtener_practica_asignada(id_practica)
            disponibles = self.practicas.obtener_horas_disponibles_para_registro(
                id_practica,
            )
            print(f"Horas disponibles para registrar: {disponibles}/240")
            actividad = self.practicas.registrar_actividad(
                id_practica,
                leer_texto("Descripcion: "),
                leer_entero("Horas: "),
            )
            print(f"Actividad registrada: {actividad.id_actividad}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _editar_actividad(self) -> None:
        try:
            self._mostrar_actividades_asignadas()
            id_actividad = leer_texto("ID actividad: ")
            descripcion = leer_texto("Nueva descripcion (enter para conservar): ")
            horas_texto = leer_texto("Nuevas horas (enter para conservar): ")
            horas = int(horas_texto) if horas_texto else None
            actividad = self.practicas.editar_actividad(
                id_actividad,
                descripcion=descripcion or None,
                horas=horas,
                tutor_empresarial=self.usuario.id_usuario,
            )
            print(f"Actividad actualizada: {actividad.id_actividad}")
        except ValueError:
            print("Error: las horas deben ser un numero valido.")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _eliminar_actividad(self) -> None:
        try:
            self._mostrar_actividades_asignadas()
            self.practicas.eliminar_actividad(
                leer_texto("ID actividad: "),
                tutor_empresarial=self.usuario.id_usuario,
            )
            print("Actividad eliminada.")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _cambiar_completado(self) -> None:
        try:
            self._mostrar_actividades_asignadas()
            actividad = self.practicas.cambiar_completado_actividad(
                leer_texto("ID actividad: "),
                leer_bool("Completada"),
                tutor_empresarial=self.usuario.id_usuario,
            )
            print(f"Actividad actualizada: {actividad.id_actividad} | {actividad.obtener_estado()}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _ver_actividades(self) -> None:
        try:
            self._mostrar_practicas_asignadas()
            practica = self._obtener_practica_asignada(leer_texto("ID practica: "))
            actividades = self.practicas.listar_actividades(practica.id_practica)
            if not actividades:
                print("No hay actividades registradas.")
            for actividad in actividades:
                print(
                    f"- {actividad.id_actividad} | {actividad.fecha} | "
                    f"{actividad.descripcion} | {actividad.horas} horas | "
                    f"{actividad.obtener_estado()}"
                )
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _ver_notificaciones(self) -> None:
        try:
            notificaciones = self.notificaciones.listar_por_usuario(self.usuario.id_usuario)
            if not notificaciones:
                print("No tiene notificaciones.")
            for notificacion in notificaciones:
                estado = "Leida" if notificacion.leida else "Nueva"
                print(
                    f"- {notificacion.fecha_creacion:%Y-%m-%d %H:%M} | "
                    f"{estado} | {notificacion.titulo}: {notificacion.mensaje}"
                )
                if not notificacion.leida:
                    self.notificaciones.marcar_como_leida(notificacion.id_notificacion)
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _obtener_practica_asignada(self, id_practica: str):
        practicas = self.practicas.listar_practicas_por_tutor_empresarial(
            self.usuario.id_usuario,
        )
        for practica in practicas:
            if practica.id_practica == id_practica:
                return practica
        raise SistemaPracticasError("La practica no esta asignada a este tutor empresarial.")

    def _mostrar_practicas_asignadas(self) -> None:
        practicas = self.practicas.listar_practicas_por_tutor_empresarial(
            self.usuario.id_usuario,
        )
        print("\nPracticas asignadas:")
        if not practicas:
            print("No tiene practicas asignadas.")
        for practica in practicas:
            estudiante = Usuario.buscar_por_id(practica.id_estudiante)
            nombre_estudiante = estudiante.nombre if estudiante else practica.id_estudiante
            print(
                f"- {practica.id_practica} | {nombre_estudiante} | "
                f"Estado: {practica.estado} | "
                f"Horas completadas: {practica.horas_cumplidas}/240 | "
                f"Horas registradas: {self.practicas.obtener_horas_registradas(practica.id_practica)}/240"
            )

    def _mostrar_actividades_asignadas(self) -> None:
        practicas = self.practicas.listar_practicas_por_tutor_empresarial(
            self.usuario.id_usuario,
        )
        print("\nActividades de sus practicas:")
        hay_actividades = False
        for practica in practicas:
            estudiante = Usuario.buscar_por_id(practica.id_estudiante)
            nombre_estudiante = estudiante.nombre if estudiante else practica.id_estudiante
            for actividad in self.practicas.listar_actividades(practica.id_practica):
                hay_actividades = True
                print(
                    f"- {actividad.id_actividad} | Practica: {practica.id_practica} | "
                    f"{nombre_estudiante} | {actividad.descripcion} | "
                    f"{actividad.horas} horas | {actividad.obtener_estado()}"
                )
        if not hay_actividades:
            print("No hay actividades registradas en sus practicas.")
