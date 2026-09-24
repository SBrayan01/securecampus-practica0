# Integrantes

- Jesus Alberto Arroyo Lugo
- Samuel Alcantara Fernadez
- Brayan Antonio Segundo De Jesus

## Pregunta guía

Ya identificamos qué puede salir mal en SecureCampus. Ahora debemos decidir: ¿en qué momento del ciclo de vida debemos actuar para prevenir, detectar o responder?

## 1. Objetivo

Relacionar riesgos y controles de SecureCampus con las fases del SDLC, distinguiendo Secure SDLC, Security by Design, Security by Default y Shift Left.

## 2. Resultados de aprendizaje

* Ubicar actividades de seguridad en Requisitos, Diseño, Desarrollo, Pruebas, Despliegue y Operación/Mantenimiento.
* Proponer controles preventivos, detectivos y correctivos para casos concretos.
* Explicar por qué seguridad no es una fase final.
* Generar evidencia técnica versionada en GitHub.

## 3. Conocimientos previos

* Activo, amenaza, vulnerabilidad, ataque, impacto, riesgo y control.
* Autenticación vs. autorización.
* Flujo básico Git/GitHub de Práctica 0 y SC-LAB-001.

## 4. Recordatorio: SDLC

`Requisitos` → `Diseño` → `Desarrollo` → `Pruebas` → `Despliegue` → `Operación/Mantenimiento`

> **Regla de trabajo:** No busques una única fase «correcta». Un mismo riesgo puede requerir controles diferentes a lo largo de varias fases.

## 5. Actividad guiada: Calificaciones

**Caso:** un estudiante autenticado puede cambiar `/calificaciones/125` por `/calificaciones/126` y consultar calificaciones ajenas.

| Fase                                 | ¿Qué debería hacerse?                                                                                                                                                                                                                                                                                                                                                                                                                                                | Control / evidencia                                                                                                                                                                                                                                           |
| :----------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Requisitos & Diseño**       | Definir reglas de control de acceso basadas en la propiedad del recurso, donde el estudiante solo tendrá acceso a sus propias calificaciones.Definir los roles de los usuarios para identificar su función dentro del sistema y establecer los permisos correspondientes.Definir autorización a nivel de objeto y uso de referencias indirectas.Diseñar la validación en el backend, estableciendo un uso de token de sesión evitando confiar en el ID de la URL. | **Requisito de seguridad documentado:** "El estudiante solo puede ver sus propias calificaciones".**DFD con límites de confianza**, documento de modelado de amenazas, especificación de funciones de autorización, revisión de arquitectura. |
| **Desarrollo**                 | Implementar verificación de autorización en el servidor para cada acceso a objeto. Filtrar consultas por propietario. Usar UUIDS.                                                                                                                                                                                                                                                                                                                                     | Código con función de autorización centralizada, PR con revisión de seguridad, SAST ejecutado, uso de UUIDS.                                                                                                                                              |
| **Pruebas**                    | Ejecutar pruebas negativas donde un usuario trate de acceder a la URL con el ID del usuario B y verificar la respuesta devuelta.                                                                                                                                                                                                                                                                                                                                        | Informe de pentest con intento de acceso cruzado denegado, resultados de DAST multi-usuario, casos de prueba automatizados en CI.                                                                                                                             |
| **Despliegue**                 | Verificar que las reglas de autorización y autenticación estén activas dentro del entorno del despiegue.Asegurarse que la configuración del servidor no almacene respuestas que contengan PII (Información Personal Identificable) en las calificaciones con base en URLS publicas.                                                                                                                                                                                | Checklist de despliegue firmado, pipeline que falla ante regresiones de autorización, logs de decisiones de autorización, configuración sin bypass.                                                                                                        |
| **Operación / Mantenimiento** | Monitorear patrones anormales, registros y atender intentos de acceso no autorizado.                                                                                                                                                                                                                                                                                                                                                                                    | Dashboard de monitoreo, alertas de picos de peticiones a IDs, registro de incidentes, revisión periódica de logs, plan de respuesta.                                                                                                                        |

## 6. Reto por equipo

Analicen los cuatro escenarios. Para cada uno, propongan al menos un control temprano y un control posterior.

### Escenarios

| Escenario               | Situación                                                                                 |
| :---------------------- | :----------------------------------------------------------------------------------------- |
| **A. Documentos** | Un estudiante intenta descargar el documento de otro usuario modificando un identificador. |
| **B. Token**      | Un desarrollador intenta incluir un token dentro de un commit.                             |
| **C. Profesor**   | Un profesor intenta modificar calificaciones de un grupo no asignado.                      |
| **D. Login**      | Una cuenta registra 100 intentos fallidos de autenticación en 10 minutos.                 |

### Controles a lo largo del SDLC

| Esc         | Requisitos                                                                                                                                                                                              | Diseño                                                                                                                                                                    | Desarrollo                                                                                                                                                                      | Pruebas                                                                                                                                                                                       | Despliegue                                                                                                                                                             | Operación / Mantenimiento                                                                                                                                              |
| :---------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A** | **Definir política:** "Solo el propietario puede acceder a su archivo".                                                                                                                          | **Arquitectura:** Usar UUIDS aleatorios en lugar de IDs secuenciales.                                                                                                | **Lógica:** Backend valida `if (usuario.id != doc.propietario) return 403;`                                                                                            | **Test automatizado:** Script prueba descargar con usuario incorrecto y espera error 403.                                                                                               | **Infraestructura:** Guardar en un bucket privado (ej. AWS S3) usando URLs firmadas de corta duración.                                                          | **Monitoreo:** Generar alerta si un usuario tiene demasiados errores 403 intentando bajar múltiples archivos.                                                    |
| **B** | **Definir política:** "Prohibido hardcodear secretos/tokens en código fuente". Usar variables de entorno o gestor de secretos. *Evidencia: política de seguridad y checklist de requisitos.* | **Diseñar integración** con gestor de secretos (Vault, AWS Secrets Manager) y flujo de inyección en runtime. *Evidencia: diagrama de arquitectura de secretos.* | **Configurar pre-commit hooks** (git-secrets, detect-secrets) y revisiones de código que bloqueen secretos. *Evidencia: hook en repo y PR con revisión de seguridad.* | **Ejecutar escaneo de secretos en CI** (SAST/secret scanning) sobre commits y PRs; verificar que no haya secretos en artefactos. *Evidencia: pipeline que falla si detecta un token.* | **Inyectar secretos** como variables de entorno o montajes efímeros; rotación automática. *Evidencia: configuración de despliegue sin secretos embebidos.* | **Monitorear accesos a secretos**, auditar repositorios periódicamente y alertar sobre exposiciones. *Evidencia: alertas SIEM y reportes de escaneo continuo.* |
| **C** | **Definir política:** "Un profesor solo puede modificar calificaciones de los alumnos inscritos en sus grupos asignados".                                                                        | **Arquitectura:** Diseñar un modelo de control de acceso basado en roles (RBAC). Mapear la relación profesor-grupo-alumno en la base de datos.                     | **Lógica:** El backend debe validar la asignación antes de procesar la solicitud: `if (profesor.grupo != alumno.grupo) return 403;`                                   | **Test automatizado:** Crear pruebas de integración donde un "Profesor A" intente modificar notas del "Grupo B" esperando un error 403.                                                | **Infraestructura:** Asegurar que las políticas de autorización estén activas y que no existan endpoints de depuración expuestos.                            | **Monitoreo:** Auditar todos los cambios de calificaciones. Generar alertas si un profesor recibe múltiples errores de acceso denegado (403).                    |
| **D** | **Definir política:** "Implementar bloqueo temporal de cuenta tras 5 intentos fallidos y establecer límite de peticiones (Rate Limiting)".                                                      | **Arquitectura:** Diseñar la integración de un middleware de Rate Limiting y mecanismo de bloqueo temporal o CAPTCHA.                                              | **Lógica:** Implementar contadores de intentos fallidos en caché (ej. Redis) y respuestas genéricas de error ("Usuario o contraseña incorrectos").                    | **Test automatizado:** Ejecutar un script de automatización que intente iniciar sesión repetidamente y verificar que al intento 6 se bloquee o limite.                                | **Infraestructura:** Configurar un Web Application Firewall (WAF) para bloquear direcciones IP con comportamiento anómalo.                                      | **Monitoreo:** Monitorear picos de peticiones de login. Alertar al equipo de respuesta a incidentes ante ataques de fuerza bruta sostenidos.                      |

## 7. Clasificación conceptual

Elijan dos decisiones de su mapa y expliquen cuál concepto representa mejor cada una.

| Decisión   | Secure SDLC / By Design / By Default / Shift Left | Justificación                                                                                                                                                                                                                                           |
| :---------- | :------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **Shift Left** (Escenario B)                | Implementar pre-commit hooks y escanear secretos desde el entorno del desarrollador traslada la detección de vulnerabilidades a las fases más tempranas del desarrollo, en lugar de esperar a descubrir el error durante las pruebas o la producción. |
| **2** | **Security By Default** (Escenario D)       | Implementar un bloqueo de cuenta automático tras varios intentos fallidos protege al usuario desde el primer momento, sin necesidad de que este configure o active funciones de seguridad adicionales en su perfil.                                     |

## 8. Reflexión

**¿Qué riesgo de SC-LAB-001 necesitó controles en más fases?**

* **Requisitos y Diseño:** Se debe definir desde la arquitectura la obligatoriedad de MFA (Doble Factor de Autenticación) para cuentas críticas, como las de Profesores y Administradores.
* **Desarrollo:** A nivel de código, es necesario sanitizar cualquier texto ingresado por el usuario y configurar las cookies de sesión con las banderas estrictas de seguridad (HttpOnly, Secure y SameSite) para prevenir XSS.
* **Despliegue y Operación:** A nivel de infraestructura, se requiere implementar Rate Limiting (ej. bloquear IP tras 5 intentos fallidos), integrar un CAPTCHA y configurar un WAF (Web Application Firewall) para mitigar el tráfico de botnets y ataques DoS.

**¿Qué habría ocurrido si el equipo hubiera esperado hasta pruebas?**
Si la seguridad se relega a la fase de pruebas, corregir vulnerabilidades arquitectónicas (como la falta de un modelo RBAC para los profesores) resulta mucho más costoso y demorado. Además, existe un alto riesgo de que vulnerabilidades críticas lleguen a producción si las pruebas no son exhaustivas.

**¿Qué control depende de una regla de negocio y cuál puede automatizarse?**
El **Escenario C** (Profesor modificando calificaciones) depende enteramente de una regla de negocio, ya que requiere contexto específico de la organización para definir quién tiene autorización sobre qué recursos. Por otro lado, el **Escenario B** (Token en commit) puede automatizarse completamente utilizando herramientas de análisis estático (SAST) y escáneres de secretos, ya que la regla es universal (nunca exponer credenciales).
