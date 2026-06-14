"""Vista de consola para estudiantes."""

from __future__ import annotations

from controlador.ControlNotificacion import ControlNotificacion
from controlador.ControlOferta import ControlOferta
from controlador.ControlPostulacion import ControlPostulacion
from controlador.ControlPractica import ControlPractica
from modelo.Usuario import Estudiante
from modelo.utilidades.Excepciones import SistemaPracticasError
from vista.ValidacionDatos import imprimir_tabla, leer_texto, pausar


class VistaEstudiante:
    def __init__(self, usuario: Estudiante) -> None:
        self.usuario = usuario
        self.ofertas = ControlOferta()
        self.postulaciones = ControlPostulacion()
        self.practicas = ControlPractica()
        self.notificaciones = ControlNotificacion()

    def mostrar(self) -> None:
        while True:
            print("\n=== Panel Estudiante ===")
            print("1. Ver ofertas disponibles")
            print("2. Postular a oferta")
            print("3. Ver mis postulaciones")
            print("4. Ver mi practica activa")
            print("5. Ver progreso de mi practica")
            print("6. Ver formularios recibidos")
            print("7. Ver notificaciones")
            print("0. Cerrar sesion")
            opcion = leer_texto("Seleccione: ")

            if opcion == "1":
                imprimir_tabla(self.ofertas.listar_ofertas(solo_disponibles=True))
                pausar()
            elif opcion == "2":
                self._postular()
            elif opcion == "3":
                propias = [
                    p
                    for p in self.postulaciones.listar_postulaciones()
                    if p.id_estudiante == self.usuario.id_usuario
                ]
                imprimir_tabla(propias)
                pausar()
            elif opcion == "4":
                self._ver_practica_activa()
            elif opcion == "5":
                self._ver_progreso_practica()
            elif opcion == "6":
                self._ver_formularios()
            elif opcion == "7":
                self._ver_notificaciones()
            elif opcion == "0":
                return

    def _postular(self) -> None:
        ofertas = self.ofertas.listar_ofertas(solo_disponibles=True)
        print("\nOfertas disponibles:")
        if not ofertas:
            print("No hay ofertas disponibles para postular.")
        for oferta in ofertas:
            print(
                f"- {oferta.id_oferta} | {oferta.titulo} | "
                f"Area: {oferta.area} | Cupos: {oferta.cupos} | "
                f"Cierre: {oferta.fecha_cierre}"
            )
        id_oferta = leer_texto("ID de oferta: ")
        try:
            postulacion = self.postulaciones.crear_postulacion(
                self.usuario.id_usuario,
                id_oferta,
            )
            print(f"Postulacion creada: {postulacion.id_postulacion}")
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

    def _ver_formularios(self) -> None:
        try:
            formularios = self.practicas.listar_formularios_estudiante(
                self.usuario.id_usuario,
            )
            if not formularios:
                print("No tiene formularios recibidos.")
            for formulario in formularios:
                print("\n" + "=" * 50)
                print(f"{formulario.tipo} | {formulario.fecha_registro}")
                print(f"Practica: {formulario.id_practica}")
                if formulario.calificacion is not None:
                    print(f"Calificacion: {formulario.calificacion}/100")
                if formulario.observaciones:
                    print(f"Observaciones: {formulario.observaciones}")
                if formulario.contenido:
                    print("\nContenido para impresion:")
                    print(formulario.contenido)
            if formularios:
                print("\nSimulacion: estos formularios fueron enviados al correo del estudiante.")
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _ver_progreso_practica(self) -> None:
        try:
            progreso = self.practicas.obtener_progreso_estudiante(self.usuario.id_usuario)
            practica = progreso["practica"]
            if practica is None:
                print("No tiene practicas registradas.")
                pausar()
                return

            print(f"Practica: {practica.id_practica}")
            print(f"Estado: {practica.estado}")
            print(f"Horas cumplidas: {progreso['horas_cumplidas']}/{progreso['horas_requeridas']}")
            print(f"Actividades registradas: {progreso['actividades_registradas']}")
            print(f"Actividades aprobadas: {progreso['actividades_aprobadas']}")
            print(f"Actividades completadas: {progreso['actividades_completadas']}")
            print(f"Actividades pendientes: {progreso['actividades_pendientes']}")
            print("\nActividades:")

            actividades = progreso["actividades"]
            if not actividades:
                print("No hay actividades registradas.")
            for actividad in actividades:
                print(
                    f"- {actividad.fecha} | {actividad.descripcion} | "
                    f"{actividad.horas} horas | {actividad.obtener_estado()}"
                )
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

    def _ver_practica_activa(self) -> None:
        try:
            practica = self.practicas.obtener_practica_activa_estudiante(
                self.usuario.id_usuario,
            )
            if practica is None:
                print("No tiene una practica activa.")
            else:
                print(practica)
        except SistemaPracticasError as error:
            print(f"Error: {error}")
        pausar()

