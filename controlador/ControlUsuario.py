from pathlib import Path

from modelo.Estudiante import Estudiante
from utilidades.ManejoDatos import ManejoDatos
from utilidades.Seguridad import Seguridad
from utilidades.Validaciones import Validaciones


class ControlUsuario:
    Archivo_estudiantes = Path('datos/usuarios_estudiantes.dat')
    Archivo_empresas = Path('datos/usuarios_empresas.dat')

    def registrar_estudiante(self,datos):
        if not Validaciones.validar_email(datos['email']):
            raise ValueError('Email invalido')
        if not Validaciones.validar_cedula(datos['cedula']):
            raise ValueError('Cedula Invalida')
        clave_hash = Seguridad.cifrar_clave(datos['clave'])
        estudiante = Estudiante(
            nombre=datos['nombre'],
            email=datos['email'],
            clave= clave_hash,
            cedula=datos['cedula'],
            carrera=datos['carrera'],
            ciclo_actual=datos['ciclo_actual']
        )
        registros = ManejoDatos.cargar_datos(self.Archivo_estudiantes)
        registros.append(estudiante)
        ManejoDatos.guardar_datos(self.Archivo_estudiantes,registros)
        return estudiante

