# SC-LAB-004 — Análisis de Seguridad Estático y Dinámico

## 1. Objetivo

Realizar un análisis de seguridad sobre la aplicación SecureCampus utilizando técnicas **SAST (Static Application Security Testing)** y **DAST (Dynamic Application Security Testing)**.

El objetivo fue identificar vulnerabilidades en el código fuente y en la aplicación en ejecución, corregir las vulnerabilidades encontradas y realizar un nuevo análisis para comprobar las correcciones.

---

## 2. Entorno

| Componente        | Descripción              |
| ----------------- | ------------------------ |
| Sistema operativo | Windows                  |
| Editor            | Visual Studio Code       |
| Lenguaje          | Python 3.14.x            |
| Framework         | Flask 3.x                |
| SAST              | Semgrep Community        |
| DAST              | OWASP ZAP                |
| Contenedores      | Docker Desktop           |
| Repositorio       | SecureCampus-SecurityLab |

Los análisis activos se realizaron únicamente sobre la aplicación local del laboratorio.

---

# 3. Análisis humano previo

Antes de ejecutar Semgrep se realizó una revisión manual del archivo `src/app.py`.

### Entrada controlada por el usuario

El usuario controla el valor correspondiente al **nombre del estudiante** mediante la entrada del formulario.

### Flujo del dato

El dato proporcionado por el usuario llega hasta una consulta SQL.

### Operación sensible

La operación sensible corresponde a la ejecución de una consulta mediante:

```python
cursor.execute(consulta)
```

### Riesgo identificado

En la versión vulnerable se utilizaba concatenación para incorporar el valor del nombre dentro de la consulta SQL. Debido a que la entrada no se encontraba adecuadamente protegida, un usuario podía proporcionar fragmentos de SQL que podrían ser interpretados por la consulta.

### Control propuesto

Se propuso utilizar **consultas parametrizadas** en lugar de concatenar directamente los valores proporcionados por el usuario.

---

# 4. Análisis SAST con Semgrep

## 4.1 Comando utilizado

```bash
docker run --rm -v "${PWD}:/src" semgrep/semgrep semgrep scan --config auto /src/
```

## 4.2 Hallazgos

Semgrep identificó principalmente una construcción relacionada con la concatenación de una entrada no confiable dentro de una consulta SQL.

El hallazgo indicó que la entrada no confiable concatenada con SQL crudo puede provocar una **inyección SQL**, recomendando utilizar sentencias preparadas y parámetros.

También se identificaron construcciones relacionadas con el uso de formato de cadenas en plantillas, susceptibles a problemas de **SSTI y XSS**.

### Líneas señaladas

```text
15  cursor.execute(consulta)

31  return render_template_string(HTML)

86  return render_template_string(HTML)

106 return render_template_string(resultado_html, nombre=nombre)
```

## 4.3 Comparación con el análisis humano

El resultado de Semgrep coincidió parcialmente con el análisis realizado manualmente.

El análisis humano permitió identificar el riesgo relacionado con la **inyección SQL**, mientras que el análisis automatizado también señaló construcciones relacionadas con la generación de plantillas y posibles problemas de SSTI/XSS.

---

# 5. Corrección de la vulnerabilidad SQL

La concatenación de datos dentro de la consulta SQL fue sustituida por una consulta parametrizada.

### Consulta corregida

```python
consulta = (
    "SELECT id, nombre, correo "
    "FROM estudiantes "
    "WHERE nombre = ?"
)

cursor.execute(consulta, (nombre,))
```

De esta forma, el valor proporcionado por el usuario se envía como parámetro y no se incorpora directamente a la estructura de la consulta SQL.

---

# 6. Reanálisis SAST

Después de realizar la corrección se ejecutó nuevamente Semgrep:

```bash
docker run --rm -v "${PWD}:/src" semgrep/semgrep semgrep scan --config auto /src/
```

### Resultado

```text
Scan completed successfully.

Findings: 0 (0 blocking)
Rules run: 47
Targets scanned: 1

Ran 47 rules on 1 file: 0 findings.
```

El resultado de **0 findings** indica que las reglas ejecutadas no reportaron hallazgos en ese momento. Esto no significa que la aplicación sea completamente segura, ya que pueden existir problemas que las reglas utilizadas no detecten.

---

# 7. Análisis DAST con OWASP ZAP

## 7.1 Inicio de la aplicación

La aplicación Flask fue ejecutada localmente mediante:

```bash
python src\webapp.py
```

Posteriormente se comprobó que el contenedor Docker pudiera comunicarse con la aplicación:

```bash
docker run --rm curlimages/curl http://host.docker.internal:5000
```

---

# 8. Baseline Scan

Se ejecutó OWASP ZAP mediante:

```bash
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://host.docker.internal:5000
```

## Hallazgos principales

| Hallazgo                              | Tipo                  | Requiere análisis |
| ------------------------------------- | --------------------- | ----------------- |
| Missing Anti-clickjacking Header      | Cabecera HTTP         | Sí                |
| X-Content-Type-Options Header Missing | Cabecera HTTP         | Sí                |
| CSP Header Not Set                    | Política de contenido | Sí                |

Estos resultados corresponden principalmente a configuraciones y cabeceras de seguridad HTTP que deben analizarse de acuerdo con el contexto de la aplicación.

---

# 9. Active Scan

Posteriormente se ejecutó el análisis activo:

```bash
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py -t http://host.docker.internal:5000
```

Durante este análisis se revisó específicamente el posible:

**Cross Site Scripting (Reflected) [40012]**

El endpoint involucrado fue:

```text
/buscar?nombre=...
```

El análisis permitió observar el comportamiento de la aplicación ante entradas controladas por el usuario.

---

# 10. Validación manual del XSS

Para validar manualmente el comportamiento se introdujo como nombre:

```html
<script>alert(1)</script>
```

Si la aplicación muestra la ventana `alert(1)`, se confirma que la entrada proporcionada por el usuario está siendo interpretada como código HTML/JavaScript en lugar de tratarse únicamente como texto.

Esta prueba permite complementar la evidencia proporcionada por OWASP ZAP.

---

# 11. Corrección del XSS

Para corregir el problema se evitó insertar directamente la entrada del usuario mediante un `f-string`.

La salida se modificó para utilizar una variable de plantilla:

```python
resultado_html = """
...
<p>Estudiante buscado: {{ nombre }}</p>
...
"""

return render_template_string(resultado_html, nombre=nombre)
```

De esta manera, el valor proporcionado por el usuario puede ser procesado mediante el mecanismo de escaping de la plantilla.

---

# 12. Retesting

Después de modificar el código fue necesario **reiniciar Flask** para garantizar que la instancia en ejecución utilizara la versión corregida.

Se realizaron nuevamente las pruebas:

### Búsqueda normal

Se comprobó que una búsqueda normal, como:

```text
María
```

continuara funcionando.

### Prueba de XSS

Se volvió a introducir:

```html
<script>alert(1)</script>
```

Después de la corrección, el contenido debe mostrarse como texto y no ejecutarse como JavaScript.

### Nuevo análisis

Se ejecutó nuevamente:

```bash
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py -t http://host.docker.internal:5000
```

El objetivo del retesting fue comprobar que el hallazgo:

```text
Cross Site Scripting (Reflected) [40012]
```

pasara de **WARN a PASS**.

Las advertencias relacionadas con otras cabeceras de seguridad pueden permanecer debido a que no forman parte de la corrección específica realizada para el XSS.

---

# 13. Comparación SAST vs DAST

| Criterio                          | SAST                                  | DAST                                         |
| --------------------------------- | ------------------------------------- | -------------------------------------------- |
| Objeto de análisis                | Código fuente                         | Aplicación en ejecución                      |
| ¿Necesita ejecutar la aplicación? | No                                    | Sí                                           |
| Perspectiva                       | Interna/estática                      | Externa/dinámica                             |
| Evidencia obtenida                | Construcción SQL insegura             | XSS y configuración HTTP                     |
| Fortaleza                         | Detecta patrones y rutas en el código | Observa el comportamiento real expuesto      |
| Limitación                        | No garantiza la lógica de negocio     | No observa todo el código ni todas las rutas |

## Conclusión de la comparación

SAST y DAST proporcionan evidencias diferentes y complementarias. SAST permitió identificar problemas directamente relacionados con la construcción del código, mientras que DAST permitió observar el comportamiento de la aplicación en ejecución y detectar problemas como el XSS reflejado.

---

# 14. Evidencia Git

Para registrar los cambios se utilizaron los siguientes comandos:

```bash
git status
git diff
git add src/webapp.py docs/security/SC-LAB-004-sast-dast.md
git diff --staged
```

Posteriormente se registró el cambio mediante:

```bash
git commit -m "fix: aplicar escape de salida para prevenir XSS reflejado"
```

Finalmente se enviaron los cambios al repositorio:

```bash
git push
```

Y se comprobó nuevamente el estado:

```bash
git status
```

---

# 15. Conclusión

La práctica permitió comprobar que SAST y DAST tienen objetivos y alcances diferentes.

El análisis SAST permitió identificar una construcción SQL insegura y posteriormente comprobar que, después de utilizar una consulta parametrizada, Semgrep no reportó nuevos hallazgos con las reglas ejecutadas.

Por otra parte, el análisis DAST permitió identificar problemas relacionados con la configuración HTTP y analizar el comportamiento de la aplicación ante una entrada potencialmente maliciosa. La validación manual permitió comprobar el comportamiento del XSS y posteriormente se aplicó output escaping para corregirlo.

Finalmente, se comprobó la importancia de realizar un **retesting** después de aplicar una corrección y de mantener evidencia de los cambios mediante Git. Ninguna de las dos técnicas sustituye completamente la revisión humana, las pruebas negativas, la validación de autorización o el análisis de la lógica de negocio.
