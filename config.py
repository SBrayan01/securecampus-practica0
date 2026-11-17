"""
Modulo de Auditoria Tecnica de Red y robots.txt - Actividad 1
"""

import time
import urllib3
import requests
from .config import SITES, USER_AGENT, DEFAULT_TIMEOUT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def auditar_portal(item):
    """Audita un portal institucional individual midiendo latencia y analizando robots.txt."""
    headers = {"User-Agent": USER_AGENT}
    registro = {
        "Sitio": item["nombre"],
        "Clasificacion": item["clasificacion"],
        "Status": "ERROR",
        "Latencia": "N/D",
        "Robots_HTTP": "ERROR",
        "Incidencias": "Ninguna",
        "Reglas_Robots": ""
    }
    
    # 1. Peticion al portal principal
    t0 = time.time()
    try:
        r = requests.get(item["url"], headers=headers, timeout=DEFAULT_TIMEOUT, verify=item["verify_ssl"])
        latencia = round((time.time() - t0) * 1000, 1)
        registro["Status"] = str(r.status_code)
        registro["Latencia"] = f"{latencia} ms"
        
        # Deteccion de WAF ante bloqueo a User-Agent personalizado
        if r.status_code == 403 and "datos.gob.mx" in item["url"]:
            headers_browser = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r_fallback = requests.get(item["url"], headers=headers_browser, timeout=DEFAULT_TIMEOUT)
            if r_fallback.status_code == 200:
                registro["Incidencias"] = "WAF activo: Bloquea User-Agent Bot (403), responde 200 a Navegadores"
                registro["Status"] = "403 Bot / 200 Browser"
    except requests.exceptions.SSLError:
        registro["Incidencias"] = "Fallo de verificacion SSL (Hostname Mismatch)"
    except requests.exceptions.RequestException as e:
        registro["Incidencias"] = f"Fallo de red: {type(e).__name__}"
        
    # 2. Descarga de robots.txt
    try:
        r_rob = requests.get(item["robots_url"], headers={"User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT, verify=item["verify_ssl"])
        registro["Robots_HTTP"] = str(r_rob.status_code)
        if r_rob.status_code == 200:
            lines = [line.strip() for line in r_rob.text.split("\n") if line.strip() and not line.startswith("#")]
            resumen_dir = "; ".join(lines[:3])
            if len(lines) > 3:
                resumen_dir += f" ... (+{len(lines)-3} reglas)"
            registro["Reglas_Robots"] = resumen_dir
        else:
            registro["Reglas_Robots"] = f"Codigo HTTP {r_rob.status_code}"
    except Exception as e:
        registro["Reglas_Robots"] = f"Error: {type(e).__name__}"
        
    return registro


def ejecutar_auditoria_completa():
    """Ejecuta la auditoria sobre los 5 sitios externos con pausas de cortesia."""
    print("=" * 85)
    print("   MODULO 1: AUDITORIA TECNICA Y ANALISIS EMPIRICO DE 5 SITIOS EXTERNOS")
    print("=" * 85)
    
    resultados = []
    for item in SITES:
        print(f"[*] Auditando: {item['nombre']}...")
        res = auditar_portal(item)
        print(f"    -> Status: {res['Status']} ({res['Latencia']}) | robots.txt: HTTP {res['Robots_HTTP']}")
        resultados.append(res)
        time.sleep(1.0) # Pausa de cortesia etica
        
    return resultados
