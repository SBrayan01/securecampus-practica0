# Actividad 1: Auditoría Comparativa de Sitios Externos

Reporte técnico completo y formal: [Actividad_1_Auditoria_Comparativa.md](../Actividad_1_Auditoria_Comparativa.md)

---

## 1. Arquitectura del Módulo y Diseño de Software

El paquete `actividad_1/` fue diseñado bajo el principio de **Responsabilidad Única (Single Responsibility Principle - SRP)** y una arquitectura en capas desacoplada. Esto asegura que la lógica de sondeo de red, el análisis de cumplimiento normativo (`robots.txt`), el consumo de APIs y la persistencia en disco operen de forma modular e independiente.

```
                         [ config.py ]
               (Constantes, URLs, Headers, Endpoints)
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
  [ auditor.py ]                          [ extractor_world_bank.py ]
(Sondeo HTTP, Latencia,                   (Consumo de API REST v2,
 RFC 9309 robots.txt, TLS)                 Paginación, Series PIB/Pob)
        |                                               |
        +-----------------------+-----------------------+
                                |
                                v
                           [ main.py ]
               (Orquestador CLI, Formateo de Tablas)
                                |
                                v
                       [ persistencia.py ]
                  (Serialización a JSON y CSV)
                                |
                                v
               [ datos_procesados / extracciones ]
```

---

## 2. Descripción de Componentes Arquitectónicos

### 2.1 Capa de Configuración: `config.py`
* **Propósito:** Centralizar parámetros inmutables, URLs objetivo de los 5 sitios institucionales (INEGI, Datos.gob.mx, World Bank, Data.gov, DOF), endpoints de la API del Banco Mundial y firmas de navegación (`User-Agent`).
* **Ventaja:** Permite modificar destinos o cabeceras sin alterar el código de los motores de auditoría o extracción.

### 2.2 Capa de Auditoría y Red: `auditor.py`
* **Propósito:** Ejecutar sondeos no invasivos mediante peticiones HTTP `HEAD` y `GET`.
* **Subprocesos:**
  1. **Métricas de Latencia:** Cronometraje preciso del *Time-To-First-Byte* (TTFB) y tiempo total de respuesta.
  2. **Inspección de `robots.txt`:** Descarga y verificación del archivo de exclusión bajo el estándar RFC 9309 para determinar directivas de acceso y sitemaps.
  3. **Manejo de Errores de Infraestructura:** Captura controlada de bloqueos WAF (`403 Forbidden` en peticiones bot a datos.gob.mx) y excepciones de certificados SSL (`verify=False` controlado para el DOF ante discrepancias de nombre de host).

### 2.3 Capa de Ingesta Oficial: `extractor_world_bank.py`
* **Propósito:** Implementar una extracción reproducible, autorizada y ética utilizando la **API REST v2 oficial del Banco Mundial**.
* **Lógica de Integración:**
  * Consulta de series temporales de México (`MEX`) para los indicadores `NY.GDP.MKTP.CD` (PIB) y `SP.POP.TOTL` (Población).
  * Control de paginación explícita (`per_page=100`) y desanidado de payloads JSON estructurados.

### 2.4 Capa de Persistencia: `persistencia.py`
* **Propósito:** Abstraer el almacenamiento en disco de los resultados generados.
* **Formatos de Salida:**
  * **JSON:** Mantiene la jerarquía completa de metadatos de auditoría y registros macroeconómicos.
  * **CSV:** Normaliza las series en un formato tabular delimitado por comas con codificación universal UTF-8.

### 2.5 Orquestador de Aplicación: `main.py`
* **Propósito:** Punto de entrada ejecutable por consola.
* **Responsabilidades:** Orquestar el flujo secuencial, coordinar la captura de excepciones, tabular los resultados de auditoría en tablas legibles de consola y presentar el resumen ejecutivo.

---

## 3. Instrucciones de Ejecución

Para ejecutar la auditoría de los 5 sitios externos y la extracción reproducible de la API:

```powershell
# Ejecución modular desde la raíz del proyecto
py -m actividad_1.main
```

### Salidas Generadas
Los archivos se depositan automáticamente en las carpetas `datos_procesados/` y `extracciones/`:
* `auditoria_sitios_externos.json`
* `banco_mundial_mexico.json`
* `extraccion_banco_mundial_mexico.csv`
