# Reporte de análisis de seguridad — SecureCampus

## 1. Datos generales

- **Proyecto:** SecureCampus
- **Práctica:** Corrección y verificación de controles de seguridad
- **Integrantes:**
  - Samuel Alcántara Fernández
  - Brayan Antonio Segundo de Jesús
  - Jesús Alberto Arroyo Lugo
- **Entorno:** Windows, PowerShell y entorno virtual de Python

---

## 2. Objetivo

Documentar los errores encontrados en la ejecución inicial de las pruebas de seguridad de SecureCampus, describir las correcciones aplicadas y registrar la evidencia de la ejecución final.

---

## 3. Alcance y metodología

El trabajo se centró en los controles de validación de calificaciones y permisos de acceso. La verificación se realizó con la suite de pruebas automatizadas `pytest`.

> **Nota sobre las herramientas:** No se ejecutaron herramientas especializadas de análisis estático (SAST) ni de análisis dinámico (DAST). Por tanto, este reporte documenta los resultados de las pruebas automatizadas disponibles y no presenta estos resultados como un análisis SAST/DAST.

---

## 4. Resultados iniciales

### 4.1 Evidencia de la terminal

Primera ejecución de las pruebas:

```text
(.venv) PS C:\Users\jesus\Downloads\securecampus-practica0\Branji> python -m pytest -q
FFFFFFFF.FFF...                                                                                         [100%]

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

1. **Validación de calificaciones:** Algunas entradas inválidas eran aceptadas con respuesta HTTP `200` en lugar de `400`. En otros casos, el procesamiento dejaba escapar la excepción `decimal.InvalidOperation`.
2. **Control de permisos:** Las solicitudes que debían denegarse por las reglas de acceso devolvían HTTP `200` en lugar de `403`.

### 4.4 Código original inicial

**Archivo:** `src/validators.py` (Inicial)
```python
from decimal import Decimal

def validar_calificacion(valor):
    # TODO: rechazar valores nulos, booleanos, texto no numérico, NaN, Infinity, fuera de 0..100 y >2 decimales.
    # No redondear entradas incorrectas.
    return Decimal(str(valor))
```

**Archivo:** `src/permissions.py` (Inicial)
```python
def puede_modificar(user, student_id, group_id, con):
    # TODO: solo profesor asignado al grupo Y estudiante inscrito en él.
    return True

def puede_consultar(user, student_id, group_id, con):
    # TODO: estudiante propio e inscrito, o profesor asignado al grupo con estudiante inscrito.
    return True
```

---

## 5. Correcciones realizadas

### 5.1 Solución aplicada a la validación

Se aplicó la lógica necesaria para verificar si el número ingresado es nulo o booleano. Posteriormente, se realiza la conversión a decimal con manejo de excepciones. En caso de recibir un string, se eliminan los espacios en blanco al inicio y al final para filtrar valores `NaN` o `Infinity`. Finalmente, se valida que el rango esté dentro de `[0, 100]` y que la cantidad de dígitos decimales no sea superior a 2 antes de retornar el valor procesado.

### 5.2 Solución aplicada a los permisos

Se modificaron las funciones del módulo de permisos:
- `puede_modificar`: Aplica la lógica necesaria para validar que solo el profesor asignado al grupo y con el estudiante inscrito en él pueda realizar modificaciones.
- `puede_consultar`: Permite el acceso únicamente si se trata del estudiante propio inscrito o del profesor asignado al grupo correspondiente.

### 5.3 Código corregido

**Archivo:** `src/validators.py`
```python
from decimal import Decimal, InvalidOperation

def validar_calificacion(valor):
    # 1. Rechazar nulos y booleanos
    if valor is None or isinstance(valor, bool):
        raise ValueError("Calificación inválida: valor nulo o booleano.")

    # 2. Intentar convertir a Decimal
    try:
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
    if d.as_tuple().exponent < -2:
        raise ValueError("Calificación inválida: más de 2 decimales.")

    return d
```

**Archivo:** `src/permissions.py`
```python
def puede_modificar(user, student_id, group_id, con):
    """
    Verifica que el usuario sea profesor, que esté asignado al grupo especificado
    y que el estudiante pertenezca a dicho grupo.
    """
    if user.get("role") != "professor":
        return False

    cursor = con.cursor()
    
    # Verificar asignación del profesor al grupo
    prof_check = cursor.execute(
        "SELECT 1 FROM group_professors WHERE group_id = ? AND professor_id = ?",
        (group_id, user.get("id"))
    ).fetchone()

    # Verificar inscripción del estudiante en el grupo
    student_check = cursor.execute(
        "SELECT 1 FROM group_students WHERE group_id = ? AND student_id = ?",
        (group_id, student_id)
    ).fetchone()

    return bool(prof_check and student_check)


def puede_consultar(user, student_id, group_id, con):
    """
    Verifica que la consulta la realice el propio estudiante inscrito
    o el profesor asignado al grupo.
    """
    role = user.get("role")
    cursor = con.cursor()

    if role == "student":
        # El estudiante solo puede consultar su propia información
        if user.get("id") != student_id:
            return False
        
        enrollment = cursor.execute(
            "SELECT 1 FROM group_students WHERE group_id = ? AND student_id = ?",
            (group_id, student_id)
        ).fetchone()
        return bool(enrollment)

    elif role == "professor":
        return puede_modificar(user, student_id, group_id, con)

    return False
```

---

## 6. Verificación posterior

### 6.1 Comando ejecutado

La suite de pruebas se ejecutó utilizando el entorno virtual activo del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### 6.2 Evidencia de la terminal

```text
...............                                                                                         [100%]
15 passed in 12.86s
```

### 6.3 Incidencia del entorno

Una ejecución realizada desde la carpeta raíz utilizó un entorno virtual que no contaba con Flask instalado, lo que produjo un error de tipo `ModuleNotFoundError`. La ejecución válida se realizó asegurando el uso del entorno virtual local (`.venv`).

### 6.4 Interpretación del resultado

La ejecución final reportó **15 pruebas aprobadas y 0 fallos**. Esto confirma que los casos de prueba incluidos en la suite automatizada pasan correctamente tras la aplicación de las correcciones.

---

## 7. Comparación de resultados

| Métrica | Ejecución inicial | Ejecución final |
| :--- | :---: | :---: |
| **Pruebas aprobadas** | 4 | 15 |
| **Pruebas fallidas** | 11 | 0 |
| **Total de pruebas** | 15 | 15 |

---

## 8. Reportes de herramientas SAST y DAST

No se generaron reportes SAST ni DAST debido a que no se emplearon herramientas especializadas para dichos análisis durante esta práctica.

- **Reporte SAST:** No disponible (no ejecutado).
- **Reporte DAST:** No disponible (no ejecutado).
- **Evidencia disponible:** Salidas de ejecuciones de `pytest` antes y después de los cambios.

---

## 9. Conclusión

Las pruebas iniciales permitieron identificar vulnerabilidades en la validación de entradas de calificaciones y fallos de lógica en las restricciones de acceso por rol/recurso. Con las modificaciones implementadas, la suite pasó exitosamente de 11 pruebas fallidas a 15 pruebas aprobadas. 

Asimismo, se enfatiza la importancia de utilizar el entorno virtual correspondiente para evitar problemas de resolución de dependencias durante las pruebas de integración.