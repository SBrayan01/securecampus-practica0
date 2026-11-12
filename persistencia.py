"""
Punto de Entrada Modular - Actividad 1
Materia: Adquisicion de Datos - Instituto Tecnologico de Toluca
"""

import sys
import os

# Permitir ejecucion directa como script o como modulo
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from actividad_1.auditor import ejecutar_auditoria_completa
    from actividad_1.extractor_world_bank import extraer_indicadores_mexico
    from actividad_1.persistencia import guardar_extraccion
else:
    from .auditor import ejecutar_auditoria_completa
    from .extractor_world_bank import extraer_indicadores_mexico
    from .persistencia import guardar_extraccion


def imprimir_tabla(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))
            
    header_str = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print(header_str)
    print(separator)
    for row in rows:
        print(" | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)))


def main():
    print("\n" + "#" * 85)
    print("  INSTITUTO TECNOLOGICO DE TOLUCA - INGENIERIA EN SISTEMAS COMPUTACIONALES")
    print("  MATERIA: ADQUISICION DE DATOS | ACTIVIDAD 1: AUDITORIA COMPARATIVA")
    print("#" * 85 + "\n")
    
    # 1. Auditoria Tecnica de los 5 Sitios
    res_auditoria = ejecutar_auditoria_completa()
    print("\n" + "=" * 85)
    print("   MATRIZ DE RESULTADOS EMPIRICOS DE AUDITORIA")
    print("=" * 85)
    headers = ["Sitio", "Clasificacion", "Status HTTP", "Latencia", "Robots HTTP", "Incidencias Tecnicas"]
    rows = [[r["Sitio"], r["Clasificacion"], r["Status"], r["Latencia"], r["Robots_HTTP"], r["Incidencias"]] for r in res_auditoria]
    imprimir_tabla(headers, rows)
    
    # 2. Extraccion Autorizada de API REST
    datos_banco_mundial = extraer_indicadores_mexico()
    
    if datos_banco_mundial:
        print("\n[+] CONJUNTO DE DATOS EXTRAIDO Y ESTRUCTURADO (MEXICO 2018 - 2023):")
        encabezados_tabla = ["Pais", "ISO3", "Anio", "Poblacion_Total", "PIB (Miles M USD)"]
        filas_tabla = [
            [
                f["Pais"],
                f["ISO3"],
                f["Anio"],
                f"{f['Poblacion_Total']:,}" if f["Poblacion_Total"] else "N/D",
                f"${f['PIB_Miles_Millones_USD']:,.2f} B" if f["PIB_Miles_Millones_USD"] else "N/D"
            ]
            for f in datos_banco_mundial
        ]
        imprimir_tabla(encabezados_tabla, filas_tabla)
        
        # 3. Persistencia
        guardar_extraccion(datos_banco_mundial)
        
    print("\n" + "=" * 85)
    print("   ACTIVIDAD 1 COMPLETADA DE FORMA EXITOSA Y ETICA")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    main()
