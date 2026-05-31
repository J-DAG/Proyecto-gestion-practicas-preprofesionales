# Sistema de Gestion de Practicas Preprofesionales

Aplicacion de consola en Python para gestionar practicas preprofesionales. Usa una arquitectura por capas similar a MVC, modelos orientados a objetos y persistencia local en archivos `.dat` mediante `pickle`.

## Ejecutar

```bash
python main.py
```

El archivo [main.py](main.py) inicializa los datos de prueba si `datos/usuarios.dat` esta vacio y luego abre el menu principal.

## Credenciales de prueba

- Administrador: `admin@uleam.edu.ec` / `admin123`
- Coordinador: `coord@uleam.edu.ec` / `coord123`
- Estudiante: `ana@uleam.edu.ec` / `ana123`
- Tutor academico: `tutor.academico@uleam.edu.ec` / `tutor123`
- Tutor empresarial: `tutor.empresarial@techandina.com` / `tutor123`

Los datos semilla solo se crean cuando `usuarios.dat` esta vacio. Si ya existen datos previos, los usuarios adicionales deben registrarse desde el panel administrador.

## Estructura

```text
configuracion/
controlador/
datos/
modelo/
utilidades/
vista/
main.py
README.md
```

- `configuracion/`: constantes centrales, rutas de datos, roles y horas maximas.
- `modelo/`: entidades persistentes como usuarios, empresas, ofertas, postulaciones, practicas, actividades, formularios y documentos.
- `controlador/`: reglas de negocio y casos de uso.
- `vista/`: menus de consola por rol.
- `utilidades/`: persistencia, excepciones, generacion de IDs y datos semilla.
- `datos/`: archivos `.dat` persistidos localmente.

## Roles

El sistema maneja cinco roles:

- Administrador
- Coordinador
- Estudiante
- Tutor academico
- Tutor empresarial

Los usuarios guardan nombres, apellidos y cedula como datos generales. La propiedad `nombre` se mantiene como nombre completo para mostrar datos en pantalla y conservar compatibilidad con registros anteriores.

## Flujo Principal

1. El administrador registra usuarios y puede activar o desactivar cuentas.
2. El coordinador registra empresas y crea ofertas de practica.
3. El estudiante ve ofertas disponibles y postula.
4. El coordinador revisa postulantes por oferta, valida postulaciones y aprueba definitivamente una postulacion.
5. Al aprobar definitivamente, el coordinador asigna fechas, tutor academico y tutor empresarial; el sistema crea la practica activa.
6. El tutor empresarial registra actividades sin superar las 240 horas totales.
7. El tutor academico aprueba actividades.
8. El tutor empresarial marca actividades aprobadas como completadas.
9. Al llegar a 240 horas, la practica se finaliza y se notifica a los actores.
10. El tutor academico califica la practica sobre 100.
11. El sistema genera formularios finales y simula su envio al correo del estudiante.

## Reglas Implementadas

- Solo estudiantes matriculados desde sexto ciclo pueden postular.
- La cedula y el email de usuario deben ser unicos.
- Un estudiante no puede postular si ya tiene practica activa.
- Una oferta debe tener cupos disponibles y fecha vigente.
- Al aceptar una postulacion se descuenta un cupo de la oferta.
- Si los cupos llegan a cero, la oferta se cierra.
- Una practica requiere tutor academico y tutor empresarial validos.
- El tutor empresarial solo gestiona practicas asignadas a su usuario.
- El tutor academico solo aprueba o califica practicas asignadas a su usuario.
- Si se desactiva un tutor con practicas activas, se debe reasignar un tutor activo del mismo rol.
- No se puede desactivar el ultimo coordinador activo del sistema.
- No se puede desactivar un estudiante con practica activa.
- Al desactivar un estudiante sin practica activa, sus postulaciones abiertas se rechazan automaticamente.
- Las actividades registradas no pueden superar 240 horas en total.
- Una actividad completada no puede editarse.
- Una actividad completada no puede perder su aprobacion academica.
- La practica se finaliza automaticamente al completar 240 horas.
- El estudiante puede ver el progreso de su practica aunque ya este finalizada.

## Formularios y Documentos

Al crear una practica, el sistema genera el `Formulario 1` con:

- fecha de inicio y fin,
- ID y nombre de empresa,
- tutor academico asignado,
- tutor empresarial asignado.

Si la empresa no tiene convenio vigente, se genera una carta compromiso y se notifica al estudiante.

Cuando la practica finaliza, el tutor academico debe registrar la calificacion sobre 100. Despues de calificar, el sistema genera:

- `Formulario 2`: evaluacion de practica, calificacion y actividades desarrolladas.
- `Formulario 3`: culminacion de practica, fecha fin, coordinador, tutores, empresa y calificacion.

El envio por correo se simula mediante notificaciones internas y la vista de formularios del estudiante.

## Persistencia

Cada entidad se persiste en su propio archivo `.dat` dentro de `datos/` usando `ManejoDatos`. Internamente cada archivo guarda un diccionario indexado por ID, por ejemplo:

```python
{id_usuario: Usuario}
{id_oferta: Oferta}
```

La persistencia con `pickle` es adecuada para pruebas locales y una aplicacion academica de consola. No debe usarse con archivos de origen desconocido.
