# Errores iniciales y soluciones

## Resumen

La ejecución inicial de las pruebas produjo:

```text
11 failed, 4 passed
```

Los 11 fallos tenían dos causas principales:

1. `validar_calificacion()` aceptaba calificaciones inválidas o dejaba escapar
   excepciones de `Decimal`.
2. Las funciones de permisos devolvían siempre `True`, por lo que cualquier
   usuario podía consultar o modificar calificaciones.

Después de implementar las validaciones y los permisos, la suite terminó con:

```text
15 passed
```

## 1. Errores de validación de calificaciones

Archivo relacionado: [src/validators.py](src/validators.py)

La API recibe la calificación en `PUT /grades/<student_id>/<group_id>`.
El endpoint llama a `validar_calificacion()` y devuelve `400` cuando la
calificación no es válida.

### Error 1: valor `150`

- **Resultado inicial:** `200 OK`, aunque una calificación de 150 está fuera
  del rango permitido.
- **Causa:** el validador original solo convertía el valor a `Decimal`, sin
  comprobar el límite superior.
- **Solución:** se agregó la comprobación `0 <= calificación <= 100`.
- **Resultado esperado:** `400 Bad Request`.

### Error 2: valor `-1`

- **Resultado inicial:** `200 OK`, aunque una calificación negativa no es
  válida.
- **Causa:** no se verificaba el límite inferior.
- **Solución:** se rechazaron los valores menores que `0`.
- **Resultado esperado:** `400 Bad Request`.

### Error 3: texto `hola`

- **Resultado inicial:** `decimal.InvalidOperation` sin convertirse en una
  respuesta HTTP controlada.
- **Causa:** `Decimal('hola')` genera `InvalidOperation`, pero el validador
  original no capturaba esa excepción.
- **Solución:** se capturó `InvalidOperation` y se transformó en
  `ValueError`, que el endpoint maneja como `400`.
- **Resultado esperado:** `400 Bad Request`, sin traceback.

### Error 4: cadena vacía

- **Resultado inicial:** `decimal.InvalidOperation`.
- **Causa:** una cadena vacía se enviaba directamente a `Decimal`.
- **Solución:** se eliminan espacios y se rechaza la cadena si queda vacía.
- **Resultado esperado:** `400 Bad Request`.

### Error 5: valor `NaN`

- **Resultado inicial:** `200 OK`.
- **Causa:** `Decimal('NaN')` es una conversión válida para `Decimal`, pero no
  representa una calificación real.
- **Solución:** se agregó una comprobación con `is_nan()`.
- **Resultado esperado:** `400 Bad Request`.

### Error 6: valor `Infinity`

- **Resultado inicial:** `200 OK`.
- **Causa:** `Decimal('Infinity')` también puede convertirse sin error, pero
  no es una calificación válida.
- **Solución:** se agregó una comprobación con `is_infinite()`.
- **Resultado esperado:** `400 Bad Request`.

### Error 7: valor `None`

- **Resultado inicial:** `decimal.InvalidOperation`.
- **Causa:** el valor nulo se transformaba en el texto `"None"` y se enviaba a
  `Decimal`.
- **Solución:** se rechazan explícitamente los valores `None` antes de
  convertirlos.
- **Resultado esperado:** `400 Bad Request`.

### Error 8: valor `99.999`

- **Resultado inicial:** `200 OK`.
- **Causa:** no se controlaba la cantidad máxima de decimales.
- **Solución:** se inspecciona el exponente de `Decimal` y se rechazan valores
  con más de dos decimales, sin redondear silenciosamente.
- **Resultado esperado:** `400 Bad Request`.

### Reglas finales del validador

La implementación corregida acepta únicamente valores que:

- no sean `None`;
- no sean booleanos;
- sean numéricos;
- sean finitos;
- estén entre `0` y `100`;
- tengan como máximo dos decimales.

La función devuelve un `Decimal` validado para que el endpoint pueda
almacenarlo de forma consistente.

## 2. Errores de autorización

Archivo relacionado: [src/permissions.py](src/permissions.py)

El esquema real de la base de datos está definido en
[src/db.py](src/db.py). Sus roles son:

- `profesor`;
- `estudiante`;
- `administrador`.

Las relaciones de la aplicación son:

- `groups.professor_id`, para saber qué profesor imparte un grupo;
- `enrollments`, para saber qué estudiante está inscrito.

### Error 9: profesor modifica otro grupo

- **Prueba:** `test_professor_other_group_forbidden`.
- **Resultado inicial:** `200 OK`, aunque `profe_ana` no imparte el grupo `20`.
- **Causa:** `puede_modificar()` estaba implementada como `return True`.
- **Solución:** se verifica que el usuario tenga rol `profesor`, que su
  `id` coincida con `groups.professor_id` y que el estudiante esté inscrito
  en ese grupo mediante `enrollments`.
- **Resultado esperado:** `403 Forbidden`.

### Error 10: estudiante modifica su propia calificación

- **Prueba:** `test_student_cannot_modify`.
- **Resultado inicial:** `200 OK`.
- **Causa:** no se comprobaba el rol del usuario antes de permitir la
  modificación.
- **Solución:** `puede_modificar()` solo permite el rol `profesor`; los
  estudiantes no pueden modificar calificaciones aunque sean propias.
- **Resultado esperado:** `403 Forbidden`.

### Error 11: estudiante consulta la calificación de otro estudiante

- **Prueba:** `test_student_cannot_read_other_student`.
- **Resultado inicial:** `200 OK`.
- **Causa:** `puede_consultar()` también devolvía `True` sin revisar la
  identidad del estudiante.
- **Solución:** para el rol `estudiante` se compara el `id` de la sesión con
  el `student_id` solicitado. Para profesores se comprueba la asignación al
  grupo y para administradores se permite la consulta.
- **Resultado esperado:** `403 Forbidden` al consultar la calificación de
  otra persona y `200 OK` al consultar la propia.

## Resultado final

La corrección se verificó ejecutando la suite desde el entorno virtual del
proyecto:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado:

```text
15 passed in 13.81s
```

La primera ejecución desde la carpeta padre utilizó otro entorno virtual sin
Flask y produjo `ModuleNotFoundError`. La ejecución válida fue la realizada
desde la carpeta `Branji`, usando `Branji\.venv`.
