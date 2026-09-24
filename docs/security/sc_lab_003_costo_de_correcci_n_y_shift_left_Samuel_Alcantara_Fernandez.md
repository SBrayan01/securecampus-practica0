# Integrantes

- Jesus Alberto Arroyo Lugo
- Samuel Alcantara Fernadez
- Brayan Antonio Segundo De Jesus

## Pregunta guía

¿Qué cambia cuando un problema de seguridad se descubre en Requisitos, Desarrollo, Pruebas o Producción?

## 1. Objetivo

Analizar el retrabajo y el impacto de detectar problemas de seguridad tarde, y proponer actividades Shift Left sin confundirlas con «hacer toda la seguridad al inicio».

## 2. Modelo conceptual

Mientras más tarde se descubre un problema, normalmente más artefactos, decisiones, pruebas, despliegues y personas pueden verse afectados. No se usarán multiplicadores universales de costo.

**Shift Left**
Mover determinadas actividades de seguridad hacia etapas más tempranas y mantener seguridad durante todo el ciclo.

## 3. Caso guiado: Recuperación de contraseña

**RF-010:** «SecureCampus deberá permitir al usuario recuperar su contraseña». El enlace generado dura 7 días y puede reutilizarse varias veces.

| Pregunta                                                                   | Respuesta del equipo                                                                                                                                                                                                   |
| :------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **¿Dónde se originó principalmente la omisión?**                 | En la fase de Requisitos / Diseño, ya que no se definieron políticas de seguridad sobre el ciclo de vida del token (casos de abuso o requisitos no funcionales de seguridad).                                        |
| **¿Dónde podría descubrirse?**                                    | En Pruebas (durante un pentesting que identifique la vulnerabilidad de reuso de token) o en Producción (si un atacante roba el enlace del historial del navegador y toma control de la cuenta).                       |
| **¿Qué artefactos habría que cambiar si se descubre en pruebas?** | El código del backend (para invalidar el token tras su uso), la base de datos (para registrar el estado del token), los scripts de pruebas unitarias/integración, y el documento de requisitos inicial.              |
| **¿Qué requisitos/criterios de seguridad faltaron?**               | 1) El token debe ser de un solo uso (One-Time).2) El tiempo de expiración debe ser corto (ej. 15-30 minutos máximo, no 7 días).                                                                                     |
| **¿Qué moverían a la izquierda?**                                 | La Definición de Casos de Abuso. Al documentar la historia de usuario en Requisitos, el equipo debe redactar criterios de aceptación de seguridad desde el día 1, evitando que el desarrollador adivine las reglas. |

## 4. Reto integral: tres situaciones

### Situaciones

| Caso                       | Situación                                                                                                                                        |
| :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| **A. Administrador** | El requisito permite consultar calificaciones sin definir condiciones. Al final se aclara que consultar y modificar requieren permisos distintos. |
| **B. Upload**        | Se aceptan archivos de usuarios autenticados sin definir tipo, tamaño, nombre ni almacenamiento seguro.                                          |
| **C. Dependencia**   | Una biblioteca sin vulnerabilidades conocidas al incorporarse publica una vulnerabilidad critica 8 meses después. Nadie la detecta por 2 meses.  |

### Análisis de Origen y Shift Left

| Origen / Caso                                                      | Descubrimiento                             | Retrabajo / impacto                                                                                                    | Actividad Shift Left                                                                                                             | Control posterior                                                                                   |
| :----------------------------------------------------------------- | :----------------------------------------- | :--------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| **Requisitos**(Omisión de RBAC)**A**                  | Pruebas (UAT) o Producción.               | **Alto:** Requiere alterar el modelo de base de datos, refactorizar controladores y actualizar vistas frontend.  | Modelado de Amenazas en la fase de Diseño para mapear quién puede leer vs. escribir.                                           | Monitoreo y auditoría de logs (identificar si alguien modificó calificaciones sin deber hacerlo). |
| **Diseño**(Falta de arquitectura segura)**B**         | Pruebas de seguridad (DAST) o Producción. | **Medio/Alto:** Obliga a reescribir la lógica de validación e integrar un almacenamiento externo (ej. AWS S3). | Estándares de codificación segura: Definir en Diseño que todo upload valida tipo MIME, restringe tamaño y renombra archivos. | Escaneo antivirus en el servidor de destino y un WAF para bloquear payloads maliciosos.             |
| **Operación**(Falta de gestión de dependencias)**C** | Operación (2 meses tarde).                | **Medio:** Requiere actualizar la librería, hacer pruebas de regresión y desplegar un parche de emergencia.    | Implementar herramientas SCA (Software Composition Analysis) en el pipeline CI/CD para detectar componentes vulnerables.         | Alertas automatizadas (ej. Dependabot o Snyk) y escaneo continuo del entorno de producción.        |

## 5. Escalera de costo cualitativa

Para uno de los casos, describan qué cambia si se detecta en cada momento.

| Momento               | ¿Qué habría que corregir/revisar?                                                                                       | Costo/retrabajo: Bajo/Medio/Alto + por qué                                                                                       |
| :-------------------- | :------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| **Requisitos**  | Añadir una línea al ticket: "El sistema solo aceptará PDFs menores a 2MB".                                              | **Bajo.** Solo cuesta unos minutos de análisis y edición de un documento de texto.                                        |
| **Diseño**     | Actualizar el diagrama de arquitectura para enviar archivos a un bucket de S3 en vez del servidor local.                   | **Bajo.** Modificar un diagrama es rápido y no hay código escrito aún.                                                   |
| **Desarrollo**  | Escribir la lógica de validación (MIME, tamaño, extensión) y cambiar la librería de almacenamiento.                   | **Medio.** Requiere horas de programación, revisión de código (PRs) y ajuste de pruebas locales.                         |
| **Pruebas**     | El QA rechaza el ticket. El desarrollador deja su tarea actual, recodifica, redespliega en QA y QA vuelve a probar.        | **Alto.** Rompe el flujo de trabajo (Context Switching), retrasa el sprint y duplica el esfuerzo del equipo.                |
| **Producción** | Se descubre porque el servidor se llenó de malware. Hay que apagar el sistema, limpiar el servidor, parchear y notificar. | **Muy Alto.** Genera tiempo de inactividad, posible daño a la reputación, estrés para el equipo (Hotfix) y riesgo legal. |

## 6. Pregunta con truco conceptual

**Dependencias**
*¿Puede Shift Left ayudar con una vulnerabilidad que todavía no existía públicamente cuando desarrollamos? Explique qué sí puede prepararse desde antes.*

Shift Left no puede predecir una vulnerabilidad que aún no ha sido descubierta (Zero-Day o una CVE futura). Sin embargo, sí ayuda enormemente a preparar la capacidad de respuesta. Al aplicar Shift Left, el equipo ya generó un Inventario de Software (SBOM) en tiempo de compilación y tiene escáneres SCA (Software Composition Analysis) integrados en el pipeline CI/CD. Así, cuando la vulnerabilidad se vuelve pública meses después, el equipo no pierde tiempo averiguando si usan la librería o dónde está: el sistema genera una alerta automatizada, se actualiza la versión y el pipeline vuelve a desplegar el sistema seguro de manera rápida y estructurada.

## 7. Reflexión

* **¿Shift Left elimina la necesidad de seguridad en operación?**No. Shift Left reduce la cantidad de defectos que llegan a producción, pero los sistemas operan en entornos hostiles en constante cambio. Ciertas amenazas, como ataques de Denegación de Servicio (DDoS), intentos de fuerza bruta, o la explotación de vulnerabilidades Zero-Day, solo pueden detectarse y mitigarse mediante controles de operación (WAF, SIEM, monitoreo de redes y alertas de incidentes).
* **¿Por qué una funcionalidad puede cumplir su requisito funcional y seguir siendo insegura?**Porque los requisitos funcionales suelen describir únicamente el "camino feliz" (Happy Path) -lo que debe hacer el sistema cuando el usuario interactúa de forma esperada y honesta-. Si no se definen requisitos de seguridad o Abuse Cases, el desarrollador no contempla cómo reaccionar ante entradas maliciosas, permitiendo que un atacante engañe al sistema mientras la funcionalidad sigue, técnicamente, "funcionando".
* **¿Qué decisión de su equipo habría sido más barata de corregir antes?**
  *(Puedes usar esta o ajustarla a la dinámica real de tu equipo):* No haber separado explícitamente los permisos de lectura y escritura en la función de calificaciones desde los Requisitos (Caso A). Agregar un modelo de roles complejos (RBAC) cuando el software ya está construido obliga a alterar la base de datos y refactorizar casi todos los controladores, lo que habría costado solo unos minutos de debate en la fase de diseño.
