# Sistema de Gestion de Practicas Preprofesionales

Aplicacion de escritorio en Python y PyQt6 para gestionar practicas preprofesionales. El sistema mantiene una arquitectura por capas con controladores, modelos persistentes y vistas generadas desde Qt Designer.

## Paquetes necesarios

Instalar las dependencias desde la raiz del proyecto:

```bash
pip install -r requirements.txt
```

Paquetes principales:

- `PyQt6`: interfaz grafica.
- `PyQt6-Charts`: graficos de reportes y paneles informativos.

## Ejecucion

Desde la carpeta del proyecto:

```bash
python main.py
```

Al iniciar, el sistema prepara las carpetas de recursos `iconos/` e `imagenes/` y crea los archivos de datos necesarios si no existen.

## Usuario semilla

El sistema solo siembra un usuario administrador inicial cuando `datos/usuarios.dat` esta vacio.

Credenciales de ingreso:

- Usuario: `admin`
- Contrasenia: `admin`

El usuario se guarda con:

- ID: `admin`
- Email interno: `admin@local`
- Cedula valida de prueba: `1300000005`
- Rol: administrador

Los demas usuarios, empresas, ofertas, tutores, estudiantes y coordinadores deben crearse desde el panel del administrador.

## Archivos de datos

La persistencia local se guarda en la carpeta `datos/` mediante archivos `.dat` con `pickle`.

Archivos preparados por el sistema:

- `usuarios.dat`
- `empresas.dat`
- `ofertas.dat`
- `postulaciones.dat`
- `practicas.dat`
- `actividades.dat`
- `formularios.dat`
- `documentos.dat`
- `solicitudes.dat`
- `convenios.dat`
- `notificaciones.dat`

Los documentos PDF adjuntos por estudiantes se almacenan en:

```text
datos/documentos_postulacion/
```

Si se desea reiniciar completamente la aplicacion para pruebas, se puede vaciar la carpeta `datos/`. Al volver a ejecutar `main.py`, se recreara solo el administrador semilla.

## Estructura del proyecto

```text
configuracion/
controlador/
datos/
iconos/
imagenes/
modelo/
utilidades/
vista/
main.py
requirements.txt
README.md
```

- `configuracion/`: constantes globales, roles, rutas y horas maximas.
- `modelo/`: entidades persistentes como usuarios, empresas, ofertas, postulaciones, practicas, actividades, documentos y notificaciones.
- `controlador/`: reglas de negocio y controladores de ventanas.
- `vista/`: archivos `ui_*.py` generados por PyQt6.
- `utilidades/`: persistencia, excepciones, generacion de IDs, semilla y validaciones.
- `datos/`: almacenamiento local de la aplicacion.

## Roles del sistema

- Administrador
- Coordinador
- Estudiante
- Tutor academico
- Tutor empresarial

Todos los usuarios tienen nombres, apellidos, cedula, email, contrasenia, rol y estado activo.

## Validacion de cedula

La cedula se valida bajo directrices de Ecuador:

- Debe tener 10 digitos.
- La provincia debe estar entre `01` y `24`.
- El tercer digito debe corresponder a persona natural.
- El ultimo digito se verifica con el algoritmo oficial de coeficientes `2,1,2,1,2,1,2,1,2`.

La implementacion esta en `utilidades/ValidacionCedula.py` y usa programacion funcional con `filter`, `map`, `zip`, lambdas y `sum` para limpiar, transformar y calcular el digito verificador.

## Flujo principal

1. El administrador ingresa con `admin/admin`.
2. El administrador crea coordinadores, estudiantes, tutores academicos, tutores empresariales y empresas.
3. El coordinador crea ofertas de practicas.
4. El estudiante revisa ofertas y postula adjuntando su avance de malla en PDF.
5. El coordinador revisa la postulacion, visualiza el documento, aprueba o niega.
6. Al aprobar, el coordinador asigna tutor academico, tutor empresarial y fechas para crear la practica.
7. Si la empresa no tiene convenio, el sistema genera carta compromiso para el estudiante.
8. El tutor empresarial registra actividades sin superar las 240 horas.
9. El tutor academico aprueba o rechaza actividades.
10. El tutor empresarial marca actividades aprobadas como completadas.
11. Al completar 240 horas, la practica se finaliza y se notifica a estudiante, tutores y coordinador.
12. El tutor academico califica la practica sobre 100.
13. El estudiante puede consultar formularios y progreso aun si la practica ya finalizo.

## Reglas implementadas

- La cedula y el email deben ser unicos.
- Solo estudiantes matriculados desde sexto ciclo pueden postular.
- Una oferta debe estar abierta, vigente y con cupos disponibles.
- Al aceptar una postulacion se descuenta un cupo.
- Al eliminar un estudiante se eliminan sus postulaciones, practicas, actividades, documentos y notificaciones asociadas.
- Al eliminar un tutor con relaciones historicas se solicita un tutor reemplazo.
- No se puede eliminar el ultimo administrador activo ni el ultimo coordinador activo.
- Las actividades no pueden superar 240 horas por practica.
- Una actividad completada no puede editarse.
- Una actividad completada no puede perder su aprobacion academica.
- La practica se finaliza automaticamente al llegar a 240 horas.

## Reportes y graficos

Los paneles de coordinador usan `PyQt6-Charts` para mostrar:

- Estado de estudiantes frente a practicas: en practica, aprobado, postulando y sin iniciar.
- Estudiantes por ciclo academico.
- Practicas por estado.

Si `PyQt6-Charts` no esta instalado, las ventanas muestran un mensaje informativo en lugar de cerrar el programa.

## Nota sobre persistencia

Los archivos `.dat` usan `pickle`, por lo que deben considerarse archivos internos de la aplicacion. No se recomienda abrir ni cargar archivos `.dat` de origen desconocido.
