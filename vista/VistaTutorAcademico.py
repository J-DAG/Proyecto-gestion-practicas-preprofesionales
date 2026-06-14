"""Vista de consola para tutores academicos."""

from __future__ import annotations

from controlador.ControlNotificacion import ControlNotificacion
from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Usuario import Estudiante, TutorAcademico, Usuario
from modelo.utilidades.Excepciones import SistemaPracticasError
from vista.ValidacionDatos import leer_bool, leer_entero, leer_texto, pausar


class VistaTutorAcademico:
    def __init__(self, usuario: TutorAcademico) -> None:
        self.usuario = usuario
        self.practicas = ControlPractica()
        self.notificaciones = ControlNotificacion()

    def mostrar(self) -> None:
        while True:
            print("\n=== Panel Tutor Academico ===")
            print("1. Ver estudiantes asignados")
            print("2. Ver progreso de una practica")
            print("3. Aprobar o quitar aprobacion de actividad")
            print("4. Calificar practica finalizada")
            print("5. Ver notificaciones")
            print("0. Cerrar sesion")
            opcion = leer_texto("Seleccione: ")

            acciones = {
                "1": self._ver_estudiantes_asignados,
                "2": self._ver_progreso_practica,
                "3": self._cambiar_aprobacion,
                "4": self._calificar_practica,
                "5": self._ver_notificaciones,
            }
            if opcion == "0":
                return
            accion = acciones.get(opcion)
            if accion:
                accion()

    def _ver_estudiantes_asignados(self) -> None:
        practicas = self.practicas.listar_practicas_por_tutor_academico(
            self.usuario.id_usuario,
        )
        if not practicas:
            print("No tiene estudiantes asignados.")
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

    def _ver_progreso_practica(self) -> None:
        self._mostrar_practicas_asignadas()
        id_practica = leer_texto("ID practica: ")
        try:
            practica = self._obtener_practica_asignada(id_practica)
            estudiante = Usuario.buscar_por_id(practica.id_estudiante)
            print(f"Practica: {practica.id_practica}")
            print(f"Estudiante: {estudiante.nombre if estudiante else practica.id_estudiante}")
            print(f"Estado: {practica.estado}")
            print(f"Horas cumplidas: {practica.horas_cumplidas}/240")
            print("\nActividades:")
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

    def _cambiar_aprobacion(self) -> None:
        try:
            self._mostrar_actividades_asignadas()
            id_actividad = leer_texto("ID actividad: ")
            actividad = self.practicas.cambiar_aprobacion_actividad(
                id_actividad,
                leer_bool("Aprobada"),
                id_tutor_academico=self.usuario.id_usuario,
            )
            print(f"Actividad actualizada: {actividad.id_actividad} | {actividad.obtener_estado()}")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _calificar_practica(self) -> None:
        try:
            self._mostrar_practicas_finalizadas_pendientes()
            practica = self.practicas.calificar_practica(
                leer_texto("ID practica finalizada: "),
                leer_entero("Calificacion sobre 100: "),
                self.usuario.id_usuario,
            )
            print(
                f"Practica calificada: {practica.id_practica} | "
                f"Calificacion: {practica.calificacion}/100"
            )
            print("Formularios 2 y 3 enviados al correo del estudiante.")
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
        practicas = self.practicas.listar_practicas_por_tutor_academico(
            self.usuario.id_usuario,
        )
        for practica in practicas:
            if practica.id_practica == id_practica:
                return practica
        raise SistemaPracticasError("La practica no esta asignada a este tutor academico.")

    def _mostrar_practicas_asignadas(self) -> None:
        practicas = self.practicas.listar_practicas_por_tutor_academico(
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
                f"Estado: {practica.estado} | Horas: {practica.horas_cumplidas}/240"
            )

    def _mostrar_actividades_asignadas(self) -> None:
        practicas = self.practicas.listar_practicas_por_tutor_academico(
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

    def _mostrar_practicas_finalizadas_pendientes(self) -> None:
        practicas = [
            practica
            for practica in self.practicas.listar_practicas_por_tutor_academico(
                self.usuario.id_usuario,
            )
            if practica.estado == "finalizada" and practica.calificacion is None
        ]
        print("\nPracticas finalizadas pendientes de calificacion:")
        if not practicas:
            print("No hay practicas pendientes de calificacion.")
        for practica in practicas:
            estudiante = Usuario.buscar_por_id(practica.id_estudiante)
            nombre_estudiante = estudiante.nombre if estudiante else practica.id_estudiante
            print(
                f"- {practica.id_practica} | {nombre_estudiante} | "
                f"Horas: {practica.horas_cumplidas}/240 | Fin: {practica.fecha_fin}"
            )

