# Reporte de análisis de seguridad — SecureCampus

## 1. Datos generales

- **Proyecto:** SecureCampus
- **Práctica:** Corrección y verificación de controles de seguridad
- **Integrante(s):** [Nombre(s)]
- **Grupo:** [Grupo]
- **Fecha:** [DD/MM/AAAA]
- **Entorno:** Windows, PowerShell y entorno virtual de Python
- **Proyecto analizado:** `securecampus-practica0\Branji`

## 2. Objetivo

Documentar los errores encontrados en la ejecución inicial de las pruebas de seguridad de SecureCampus, describir las correcciones aplicadas y registrar la evidencia de la ejecución final.

## 3. Alcance y metodología

El trabajo se centró en los controles de validación de calificaciones y permisos de acceso. La verificación se realizó con la suite de pruebas automatizadas `pytest`.

**Nota sobre las herramientas:** No se ejecutaron herramientas especializadas de análisis estático (SAST) ni de análisis dinámico (DAST). Por tanto, este reporte documenta los resultados de las pruebas automatizadas disponibles y no presenta estos resultados como un análisis SAST/DAST.

## 4. Resultados iniciales

### 4.1 Evidencia de la terminal

Primera ejecución de las pruebas:

```text
(.venv) PS C:\Users\jesus\Downloads\securecampus-practica0\Branji> python -m pytest -q
FFFFFFFF.FFF...                                                                                                         [100%]

11 failed, 4 passed in 13.32s
```

### 4.2 Pruebas que fallaron

```text
FAILED tests/test_security.py::test_grade_invalid[150]
FAILED tests/test_security.py::test_grade_invalid[-1]
FAILED tests/test_security.py::test_grade_invalid[hola]
FAILED tests/test_security.py::test_grade_invalid[]
FAILED tests/test_security.py::test_grade_invalid[NaN]
FAILED tests/test_security.py::test_grade_invalid[Infinity]
FAILED tests/test_security.py::test_grade_invalid[None]
FAILED tests/test_security.py::test_grade_invalid[99.999]
FAILED tests/test_security.py::test_professor_other_group_forbidden
FAILED tests/test_security.py::test_student_cannot_modify
FAILED tests/test_security.py::test_student_cannot_read_other_student
```

### 4.3 Análisis de los errores iniciales

Se identificaron dos grupos principales de fallos:

- **Validación de calificaciones:** algunas entradas inválidas eran aceptadas con respuesta HTTP `200` en lugar de `400`. En otros casos, el procesamiento dejaba escapar la excepción `decimal.InvalidOperation`.
- **Control de permisos:** las solicitudes que debían denegarse por las reglas de acceso devolvían HTTP `200` en lugar de `403`.

### 4.4 Código original

**Archivo(s) revisado(s):** src/validators.py

```python

```

```python
# Errores iniciales y soluciones

## Evidencia inicial de la terminal

La primera ejecución de las pruebas mostró los siguientes resultados:

```text
(.venv) PS C:\Users\jesus\Downloads\securecampus-practica0\Branji> python -m pytest -q
FFFFFFFF.FFF...                                                                                                         [100%]

11 failed, 4 passed in 13.32s
```

Los 11 fallos reportados fueron:

```text
FAILED tests/test_security.py::test_grade_invalid[150]
FAILED tests/test_security.py::test_grade_invalid[-1]
FAILED tests/test_security.py::test_grade_invalid[hola]
FAILED tests/test_security.py::test_grade_invalid[]
FAILED tests/test_security.py::test_grade_invalid[NaN]
FAILED tests/test_security.py::test_grade_invalid[Infinity]
FAILED tests/test_security.py::test_grade_invalid[None]
FAILED tests/test_security.py::test_grade_invalid[99.999]
FAILED tests/test_security.py::test_professor_other_group_forbidden
FAILED tests/test_security.py::test_student_cannot_modify
FAILED tests/test_security.py::test_student_cannot_read_other_student
```

Los errores de validación devolvían `200` cuando debían devolver `400` o
dejaban escapar `decimal.InvalidOperation`. Los errores de permisos devolvían
`200` cuando debían devolver `403`.

## Resumen

La ejecución inicial de las pruebas produjo:
@@ -164,15 +195,9 @@ La corrección se verificó ejecutando la suite desde el entorno virtual del
proyecto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado:

```text
15 passed in 13.81s
(.venv) PS C:\Users\jesus\Downloads\securecampus-practica0\Branji> python -m pytest -q
...............                                                                                                         [100%]
15 passed in 12.86s
```

La primera ejecución desde la carpeta padre utilizó otro entorno virtual sin
Flask y produjo `ModuleNotFoundError`. La ejecución válida fue la realizada
desde la carpeta `Branji`, usando `Branji\.venv`.
Esta ejecución confirma que los 15 casos de prueba pasan correctamente.
```

## 5. Correcciones realizadas

### 5.1 Solución aplicada a la validación

Se aplicó la Logica necesaria que verifica si el numero ingresado es nulo o booleano, posteriormente se trata de convertir a decimal con un manejo de excepciones, si es un String se quitan los espacios en blanco al inicio y al final, para posteriormente filtrar si es un valor NaN o infinity, valdamos el rango para que este dentro de [0-100],posteriormente se verifica que no tenga mas de 2 dígitos.
Finalmente retornamos el valor procesado.

### 5.2 Solución aplicada a los permisos

[Describir el cambio realizado para que un profesor no modifique calificaciones de estudiantes de otros grupos y para impedir que un estudiante modifique calificaciones o consulte las de otro estudiante.]

### 5.3 Código corregido

**Archivo(s) modificado(s):** [Indicar rutas de los archivos]

```python

from decimal import Decimal
from decimal import Decimal, InvalidOperation

def validar_calificacion(valor):
    # TODO: rechazar valores nulos, booleanos, texto no numérico, NaN, Infinity, fuera de 0..100 y >2 decimales.
    # No redondear entradas incorrectas.
    return Decimal(str(valor))
    # 1. Rechazar nulos y booleanos (en Python bool es subclase de int, por lo que True/False pasan isinstance numérico si no se filtran)
    if valor is None or isinstance(valor, bool):
        raise ValueError("Calificación inválida: valor nulo o booleano.")

    # 2. Intentar convertir a Decimal (maneja texto no numérico, cadenas vacías, etc.)
    try:
        # Si es un string, quitamos espacios en blanco al inicio/final
        val_str = str(valor).strip()
        if not val_str:
            raise ValueError("Calificación vacía.")
            
        d = Decimal(val_str)
    except (InvalidOperation, TypeError):
        raise ValueError("Calificación inválida: texto no numérico.")

    # 3. Rechazar NaN e Infinity
    if d.is_nan() or d.is_infinite():
        raise ValueError("Calificación inválida: valor no finito (NaN o Infinity).")

    # 4. Verificar rango [0, 100]
    if d < Decimal('0') or d > Decimal('100'):
        raise ValueError("Calificación fuera de rango (debe estar entre 0 y 100).")

    # 5. Verificar que no tenga más de 2 decimales (sin redondear silenciosamente)
    # as_tuple().exponent nos indica el número de decimales (si es negativo)
    if d.as_tuple().exponent < -2:
        raise ValueError("Calificación inválida: más de 2 decimales.")

    return d
```

```python
[Pegar aquí el fragmento del código corregido de permisos]
```

## 6. Verificación posterior

### 6.1 Comando ejecutado

La suite se ejecutó desde la carpeta `Branji`, utilizando el intérprete del entorno virtual del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### 6.2 Evidencia de la terminal

```text
15 passed in 13.81s
(.venv) PS C:\Users\jesus\Downloads\securecampus-practica0\Branji> python -m pytest -q
...............                                                                                                         [100%]
15 passed in 12.86s
```

### 6.3 Incidencia del entorno

Una ejecución realizada desde la carpeta padre utilizó otro entorno virtual que no tenía Flask instalado y produjo `ModuleNotFoundError`. La ejecución válida se realizó desde la carpeta `Branji`, usando `Branji\.venv`.

### 6.4 Interpretación del resultado

La ejecución final reportó **15 pruebas aprobadas y ningún fallo**. Esto confirma que los casos incluidos en la suite automatizada pasan después de las correcciones. No demuestra por sí solo que la aplicación esté libre de todas las vulnerabilidades ni sustituye un análisis SAST o DAST.

## 7. Comparación de resultados

| Métrica | Ejecución inicial | Ejecución final |
|---|---:|---:|
| Pruebas aprobadas | 4 | 15 |
| Pruebas fallidas | 11 | 0 |
| Total de pruebas | 15 | 15 |

## 8. Reportes de herramientas SAST y DAST

No se generaron reportes SAST ni DAST porque no se utilizaron herramientas especializadas para esos análisis.

- **Reporte SAST:** No disponible; no ejecutado.
- **Reporte DAST:** No disponible; no ejecutado.
- **Evidencia disponible:** Salidas de `pytest` antes y después de las correcciones.

## 9. Conclusión

Las pruebas iniciales identificaron fallos en la validación de calificaciones y en el control de permisos. Después de realizar las correcciones, la suite pasó de 11 pruebas fallidas y 4 aprobadas a 15 pruebas aprobadas. También se identificó que las pruebas deben ejecutarse desde el entorno virtual correcto para evitar errores relacionados con dependencias.

Los resultados demuestran que los casos de prueba disponibles se cumplen en la ejecución final. Como no se ejecutaron herramientas SAST ni DAST, no es posible afirmar que se haya completado una auditoría estática y dinámica de la aplicación. Esos análisis quedan pendientes si forman parte de los requisitos de la práctica.
