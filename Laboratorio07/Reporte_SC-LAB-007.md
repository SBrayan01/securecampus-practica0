# Reporte de práctica: Exploración guiada de APIs REST y GraphQL

**Proyecto:** SecureCampus  
**Clave de práctica:** SC-LAB-007  
**Asignatura / tema:** Desarrollo seguro — Seguridad en aplicaciones web y APIs  
**Modalidad:** Demostración guiada  
**Estudiante:** ____________________________________  
**Grupo:** ____________________  
**Fecha:** ____________________

---

## 1. Descripción de la práctica

La práctica SC-LAB-007 tuvo como propósito explorar el funcionamiento de dos estilos de API: REST y GraphQL, mediante la aplicación educativa SecureCampus. La actividad permitió enviar solicitudes desde una interfaz web, consultar y modificar calificaciones ficticias, interpretar respuestas JSON y reconocer el significado de distintos códigos de estado HTTP.

También se revisó la diferencia entre autenticación y autorización. Mediante pruebas con cuentas de profesor y estudiante, se observó que iniciar sesión no concede acceso automático a todos los recursos: el servidor debe comprobar que la cuenta tenga permisos sobre el estudiante, grupo y operación solicitados.

La práctica se realizó en un entorno local con Python, Flask, SQLite y una interfaz accesible desde el navegador. No fue necesario desarrollar una API desde cero; se utilizó el proyecto proporcionado y se ejecutaron pruebas automatizadas con `pytest`.

## 2. Objetivo

Iniciar y utilizar una API REST y una API GraphQL en SecureCampus para consultar y modificar calificaciones ficticias, interpretar las respuestas HTTP y JSON, y comprobar la importancia de aplicar controles de autorización en el servidor.

## 3. Entorno y herramientas utilizadas

| Elemento | Descripción |
|---|---|
| Sistema operativo | Windows |
| Lenguaje / entorno | Python 3 |
| Editor | Visual Studio Code |
| Framework web | Flask |
| Base de datos | SQLite con información ficticia |
| API | REST y GraphQL |
| Procesamiento GraphQL | `graphql-core` |
| Pruebas automatizadas | `pytest` |
| Navegador | Para acceder a la interfaz local |
| Dirección local | `http://127.0.0.1:5000` |

La conexión a Internet se requiere únicamente para instalar los paquetes la primera vez. La demostración se ejecuta en `localhost`; no requiere Docker ni una cuenta de GitHub.

## 4. Preparación y ejecución del proyecto

Se descomprimió el proyecto proporcionado y se abrió la carpeta desde Visual Studio Code. Después, se creó y activó un entorno virtual para mantener aisladas las dependencias de la práctica.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Con el entorno virtual activo, se instalaron las dependencias:

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Finalmente, se inició la aplicación:

```powershell
python run.py
```

Se accedió desde el navegador a `http://127.0.0.1:5000`. La terminal debe permanecer abierta mientras se utiliza la aplicación.

## 5. Conceptos principales

### 5.1 API

Una API (Application Programming Interface) permite que diferentes componentes de software se comuniquen mediante operaciones y estructuras definidas. En esta práctica, la interfaz web envía solicitudes a los servicios de SecureCampus y presenta sus respuestas.

### 5.2 REST

REST es un estilo arquitectónico para diseñar servicios que utilizan recursos identificados mediante rutas. En el laboratorio, la ruta `/grades/3/10` identifica la calificación del estudiante 3 perteneciente al grupo 10.

Las operaciones observadas fueron:

- **GET:** consulta información de un recurso.
- **PUT:** modifica un recurso existente.

El servidor debe validar la solicitud y comprobar los permisos antes de entregar o modificar la información.

### 5.3 GraphQL

GraphQL es una tecnología de consulta para APIs que permite al cliente indicar qué recurso y qué campos necesita. En SecureCampus se utilizó una consulta para solicitar `studentId`, `groupId` y `grade`.

A diferencia del ejemplo REST, donde la ruta identifica el recurso, en GraphQL la consulta especifica los datos requeridos. La respuesta puede contener la clave `data` cuando la operación se procesa correctamente o `errors` cuando se produce un error.

### 5.4 JSON

JSON (JavaScript Object Notation) es un formato de intercambio de datos estructurados. En esta práctica se utilizó para representar la información de las calificaciones y los resultados de las solicitudes.

### 5.5 Códigos de estado HTTP

| Código | Significado | Aplicación en la práctica |
|---|---|---|
| **200 OK** | La solicitud se procesó correctamente. | Se pudo consultar o modificar una calificación autorizada. |
| **400 Bad Request** | La solicitud contiene datos inválidos o no cumple el formato esperado. | Se intentó registrar una calificación fuera del rango permitido, como 150. |
| **401 Unauthorized** | La solicitud no cuenta con autenticación válida. | Se intenta acceder sin iniciar sesión o sin una sesión válida. |
| **403 Forbidden** | El servidor reconoce la solicitud, pero la cuenta no tiene permiso para realizar esa operación o acceder al recurso. | Ana intenta consultar o modificar información del grupo 20, al que no pertenece. |

**Diferencia importante:** 401 se relaciona con la falta de autenticación válida; 403 indica que el acceso está prohibido aunque la identidad de la cuenta pueda estar reconocida.

### 5.6 Autenticación

La autenticación es el proceso mediante el cual el sistema comprueba la identidad de una cuenta. En el laboratorio se realiza al iniciar sesión con una de las cuentas ficticias. La sesión se conserva mediante una cookie configurada como HTTP-only.

### 5.7 Autorización

La autorización determina qué acciones y recursos puede utilizar una cuenta autenticada. Por ejemplo, la profesora Ana puede consultar y modificar calificaciones dentro del grupo ISC401, pero no debe acceder a las del grupo ISC402.

La comprobación debe realizarse en el servidor. No es suficiente ocultar opciones en la interfaz, ya que una persona podría cambiar los identificadores enviados en una solicitud.

### 5.8 Cookie HTTP-only

Es una cookie configurada para que JavaScript ejecutado en el navegador no pueda leerla directamente. En la práctica se utiliza para conservar la sesión de la cuenta. Esta característica ayuda a reducir determinados riesgos de acceso a la cookie desde scripts, pero no sustituye otros controles de seguridad.

### 5.9 Token CSRF

CSRF (Cross-Site Request Forgery) es un tipo de ataque en el que se intenta provocar que el navegador de una persona autenticada envíe una solicitud no deseada. En el laboratorio, la operación PUT requiere un token CSRF que la interfaz obtiene al iniciar sesión y envía en la cabecera `X-CSRF-Token`.

### 5.10 Resolver de GraphQL

Un resolver es la función encargada de obtener el dato solicitado por un campo de GraphQL. Además de recuperar la información, debe aplicar las comprobaciones de autorización correspondientes. La seguridad no debe limitarse a las rutas REST.

### 5.11 Pruebas automatizadas

`pytest` es la herramienta utilizada para ejecutar pruebas automatizadas y comprobar que el comportamiento de la aplicación coincide con lo esperado. El material indica que el paquete entregado debe aprobar 18 pruebas: 15 del laboratorio previo y 3 nuevas.

## 6. Datos ficticios utilizados

| Cuenta | Rol | Grupo |
|---|---|---|
| `profe_ana` | Profesor | ISC401 (10) |
| `profe_luis` | Profesor | ISC402 (20) |
| `alumna_eli` | Estudiante | ISC401 (10) |
| `alumno_paz` | Estudiante | ISC402 (20) |

**Datos adicionales del laboratorio:** la contraseña de demostración indicada para las cuentas es `Laboratorio2026!`. Eli corresponde al ID 3 y Paz al ID 4. Estas credenciales son exclusivamente ficticias y no deben sustituirse por contraseñas personales.

## 7. Desarrollo de las experiencias guiadas

### 7.1 Experiencia A: consulta mediante REST GET

Se inició sesión con la cuenta `profe_ana` y se consultó al estudiante 3 del grupo 10. La solicitud debía responder con HTTP 200 y mostrar la calificación en formato JSON.

Después, se cambió la consulta al estudiante 4 del grupo 20. La respuesta esperada fue HTTP 403, porque Ana no pertenece a ese grupo.

**Pregunta: ¿Qué cambia entre ambas solicitudes?**

Cambia el identificador del estudiante y el grupo consultado. En la primera solicitud, Ana intenta acceder a una calificación de su grupo autorizado (3/10), por lo que el servidor permite la consulta. En la segunda, intenta acceder a un recurso del grupo 20, al que no pertenece, por lo que el servidor deniega el acceso con HTTP 403.

**Pregunta: ¿Por qué la autenticación por sí sola no basta?**

Porque la autenticación únicamente confirma quién es la persona que inició sesión. No determina si esa cuenta tiene permiso para consultar un recurso específico. Después de autenticarla, el sistema debe comprobar su autorización para cada operación y recurso solicitado.

### 7.2 Experiencia B: modificación mediante REST PUT

Con Ana autenticada, se indicó el estudiante 3, el grupo 10 y la calificación 88.50. La modificación debía responder con HTTP 200. Posteriormente, se consultó nuevamente el registro para verificar el valor actualizado.

Al intentar modificar la calificación del estudiante 4 del grupo 20, la respuesta esperada fue HTTP 403. Finalmente, se envió el valor 150 para el registro 3/10; el servidor debía responder HTTP 400 porque el dato está fuera del rango válido.

El PUT requiere un token CSRF, enviado en la cabecera `X-CSRF-Token`.

**Interpretación:** la operación PUT requiere más que una sesión activa. El servidor debe verificar el token CSRF, comprobar que la cuenta tenga autorización sobre el recurso y validar que la calificación recibida sea válida antes de realizar el cambio.

### 7.3 Experiencia C: estudiante y control de acceso

Se cerró la sesión de Ana y se inició sesión como `alumna_eli`.

- La consulta GET del estudiante 3, grupo 10, debía responder HTTP 200.
- La consulta del estudiante 4, grupo 20, debía responder HTTP 403.
- El intento de modificar la calificación 3/10 mediante PUT debía responder HTTP 403.

**Pregunta: ¿Por qué ser dueño de una calificación no autoriza a cambiarla?**

Porque ser el estudiante al que pertenece una calificación permite consultar la información propia, pero no concede privilegios de modificación. La actualización de calificaciones es una operación restringida a los roles autorizados, como el profesor responsable del grupo. El sistema debe aplicar permisos diferentes según el rol y la acción solicitada.

### 7.4 Experiencia D: consulta mediante GraphQL

Con Eli autenticada, se utilizó la siguiente consulta:

```graphql
query {
  grade(studentId: 3, groupId: 10) {
    studentId
    groupId
    grade
  }
}
```

La consulta del estudiante 3 del grupo 10 debía responder HTTP 200 y devolver la información bajo `data.grade`.

Al cambiar los identificadores al estudiante 4 y grupo 20, la respuesta esperada fue HTTP 403 con un error de acceso denegado. Esto demuestra que GraphQL también debe aplicar controles de autorización.

Como prueba adicional, se indicó solicitar únicamente el campo `grade`. GraphQL devuelve solo los campos seleccionados por el cliente.

## 8. Conocer la interfaz visual

La interfaz de SecureCampus se divide en cuatro zonas principales:

| Zona | Función |
|---|---|
| **Inicio de sesión** | Autentica una cuenta ficticia y conserva la sesión mediante una cookie HTTP-only. |
| **REST** | Permite enviar solicitudes GET para consultar y PUT para modificar una calificación. |
| **GraphQL** | Permite enviar una consulta con los campos seleccionados y visualizar la respuesta del servicio. |
| **Resultados** | Muestra el código de estado HTTP y el cuerpo de la respuesta en formato JSON. |

**Descripción de la interfaz:** el inicio de sesión establece la identidad con la que se realizarán las solicitudes. La sección REST permite probar operaciones sobre las calificaciones mediante los métodos GET y PUT. La sección GraphQL permite definir los campos que se desean recuperar. Finalmente, el área de resultados permite comprobar si la solicitud fue aceptada o denegada, mediante el código HTTP y la respuesta JSON.

**Interpretación de seguridad:** la interfaz facilita la interacción, pero no es la responsable final de proteger los datos. La autorización debe comprobarse en el servidor para evitar que una persona obtenga información o modifique registros cambiando los identificadores de la solicitud.

## 9. Comparación entre REST y GraphQL

| REST | GraphQL |
|---|---|
| La ruta identifica el recurso, por ejemplo: `/grades/3/10`. | La consulta indica el recurso y los campos que se desean obtener. |
| En esta práctica, GET consulta y PUT modifica. | En este laboratorio solo se implementan consultas. |
| La respuesta utiliza JSON. | La respuesta utiliza JSON bajo la clave `data` o `errors`. |
| El servidor debe verificar los permisos de acceso. | El resolver también debe verificar los permisos de acceso. |

**Análisis:** REST y GraphQL ofrecen formas diferentes de solicitar información, pero ambos requieren controles de seguridad en el servidor. REST utiliza rutas y métodos HTTP para identificar la operación; GraphQL permite seleccionar los campos mediante una consulta. Ninguno debe confiar en que los identificadores enviados por el cliente sean legítimos ni omitir la autorización.

## 10. Ejecución de pruebas automatizadas

Para ejecutar las pruebas, se debe detener el servidor con `Ctrl+C` y ejecutar en la terminal del proyecto:

```powershell
python -m pytest -q
```

De acuerdo con la guía, el paquete entregado debe mostrar 18 pruebas aprobadas: 15 correspondientes al laboratorio previo y 3 nuevas.

**Resultado obtenido:** ______________________________________________

**Interpretación:** las pruebas automatizadas permiten verificar que las funciones de la aplicación respondan de acuerdo con los comportamientos esperados. Si se presenta algún fallo, la guía indica compartir la salida completa con la profesora antes de modificar el código.

## 11. Preguntas de reflexión

### 11.1 ¿Qué significa 200, 400, 401 y 403?

- **200 OK:** la solicitud se procesó correctamente.
- **400 Bad Request:** los datos enviados son inválidos o la solicitud tiene un formato incorrecto.
- **401 Unauthorized:** falta una autenticación válida para acceder al servicio.
- **403 Forbidden:** la cuenta no tiene autorización para acceder al recurso o realizar la operación solicitada.

### 11.2 ¿Qué diferencia existe entre iniciar sesión y tener autorización?

Iniciar sesión corresponde a la autenticación y permite comprobar la identidad de la cuenta. Tener autorización significa que esa cuenta cuenta con los permisos necesarios para realizar una acción sobre un recurso. Por ello, una persona puede estar autenticada y aun así recibir una respuesta 403 cuando intenta acceder a información que no le corresponde.

### 11.3 ¿Por qué una persona no debe poder consultar calificaciones de otros estudiantes cambiando los identificadores?

Porque los identificadores enviados por el cliente no deben considerarse una prueba de permiso. Si el servidor aceptara cualquier ID sin verificar la relación entre la cuenta, el estudiante y el grupo, una persona podría consultar información académica ajena. Para evitarlo, el servidor debe validar la autorización en cada solicitud.

### 11.4 ¿Qué cambia al consultar una calificación por REST o por GraphQL?

En REST se utiliza una ruta que identifica el recurso y un método HTTP, como GET, para consultar la información. En GraphQL se envía una consulta donde se especifican el recurso y los campos requeridos. Aunque cambia la forma de solicitar los datos, ambos mecanismos deben aplicar las mismas reglas de autorización.

### 11.5 ¿Qué pasaría si GraphQL omitiera la comprobación de permisos?

Una persona autenticada podría consultar información de estudiantes o grupos a los que no tiene acceso, modificando los identificadores incluidos en la consulta. Esto expondría información académica y permitiría el acceso no autorizado a recursos. Por eso, los resolvers deben comprobar los permisos en el servidor, igual que los endpoints REST.

## 12. Tabla de problemas frecuentes y soluciones

| Situación | Qué revisar / solución |
|---|---|
| No se reconoce `python` | Verificar que Python esté instalado y agregado a la variable de entorno `PATH`. |
| No aparece `(.venv)` | Activar el entorno virtual desde la terminal ubicada en la carpeta del proyecto. |
| `ModuleNotFoundError` | Instalar `requirements.txt` y `requirements-dev.txt` dentro del entorno virtual. |
| No abre la página | Confirmar que `python run.py` siga ejecutándose y acceder a `http://127.0.0.1:5000`. |
| Puerto 5000 ocupado | Cerrar otra aplicación que utilice el puerto y consultar a la profesora si el problema continúa. |
| Respuesta 401 | Iniciar sesión y verificar que la sesión siga siendo válida. |
| Respuesta 403 | Comprobar si la cuenta tiene permiso para acceder al estudiante y grupo indicados o realizar la operación. |
| Respuesta 400 | Revisar los datos enviados y, en GraphQL, la sintaxis de la consulta. |

## 13. Evidencias de la práctica

En este apartado se dejan espacios para incorporar las capturas solicitadas en la guía. Las imágenes deben mostrar la interfaz y el resultado correspondiente de forma legible.

### Evidencia 1. REST GET — respuesta HTTP 200

**Descripción:** consulta autorizada de una calificación mediante REST. Debe observarse el código HTTP 200 y el cuerpo JSON de la respuesta.

**Insertar captura aquí:**

> [Espacio reservado para la captura REST 200]

---

### Evidencia 2. REST GET — respuesta HTTP 403

**Descripción:** consulta denegada al intentar acceder a un estudiante de un grupo al que la cuenta autenticada no pertenece. Debe observarse el código HTTP 403.

**Insertar captura aquí:**

> [Espacio reservado para la captura REST 403]

---

### Evidencia 3. GraphQL — respuestas HTTP 200 y 403

**Descripción:** incluir la consulta GraphQL autorizada con respuesta HTTP 200 y la consulta con identificadores de otro grupo que produce HTTP 403. Se debe distinguir el resultado permitido del acceso denegado.

**Insertar capturas aquí:**

> [Espacio reservado para la captura GraphQL 200]

> [Espacio reservado para la captura GraphQL 403]

---

### Evidencia 4. Resultado de pruebas con pytest

**Descripción:** captura de la terminal después de ejecutar `python -m pytest -q`. La evidencia debe permitir identificar el número de pruebas aprobadas y, si existieran, los fallos.

**Insertar captura aquí:**

> [Espacio reservado para la captura del resultado pytest]

## 14. Conclusión

La práctica permitió reconocer las diferencias entre REST y GraphQL a partir de solicitudes reales realizadas en SecureCampus. REST utiliza rutas y métodos HTTP para consultar o modificar recursos, mientras que GraphQL permite especificar mediante una consulta los campos que se desean recuperar.

El aspecto de seguridad más importante observado fue la separación entre autenticación y autorización. Iniciar sesión permite identificar una cuenta, pero el servidor todavía debe comprobar si tiene permiso para consultar o modificar el recurso solicitado. Las respuestas HTTP 200 y 403 permitieron distinguir entre operaciones permitidas y accesos denegados; por su parte, el código 400 mostró la importancia de validar los datos recibidos.

También se identificó que los controles de autorización deben aplicarse tanto en los endpoints REST como en los resolvers de GraphQL. Si alguno de estos mecanismos omitiera la verificación, los usuarios podrían acceder a información de otros grupos mediante el cambio de identificadores. Finalmente, las pruebas automatizadas con `pytest` sirven para comprobar el comportamiento esperado de la aplicación.

## 15. Alcance y consideraciones de seguridad

SecureCampus es un proyecto educativo que utiliza cuentas y calificaciones ficticias. La demostración debe ejecutarse únicamente en la computadora local y no representa un sistema institucional de producción.

El laboratorio implementa consultas GraphQL, pero no incorpora un cliente móvil ni un despliegue público. No se deben publicar la base de datos ni contraseñas reales en repositorios. Las conclusiones de este reporte se limitan a los componentes y comportamientos descritos en la guía de la práctica.
