"""
Modulo de Extraccion Autorizada de API REST - Actividad 1
Fuente: World Bank Open Data (World Development Indicators)
"""

import time
import requests
from .config import USER_AGENT, DEFAULT_TIMEOUT

METRICAS = [
    {"codigo": "SP.POP.TOTL", "columna": "Poblacion_Total"},
    {"codigo": "NY.GDP.MKTP.CD", "columna": "PIB_USD_Corrientes"}
]

def extraer_indicadores_mexico(anios="2018:2023"):
    """
    Consume la API REST v2 de World Bank de forma autorizada y reproducible.
    Extrae la Poblacion Total y el PIB de Mexico en el rango de anios especificado.
    """
    print("\n" + "=" * 85)
    print("   MODULO 2: EXTRACCION DE DATOS AUTORIZADA Y REPRODUCIBLE (BANCO MUNDIAL)")
    print("=" * 85)
    
    registros_por_anio = {}
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    
    for m in METRICAS:
        cod = m["codigo"]
        col = m["columna"]
        url_api = f"https://api.worldbank.org/v2/country/MEX/indicator/{cod}?date={anios}&format=json"
        
        print(f"[*] Consultando API Oficial: {cod} ({col})...")
        t0 = time.time()
        try:
            resp = requests.get(url_api, headers=headers, timeout=DEFAULT_TIMEOUT)
            duracion = round((time.time() - t0) * 1000, 1)
            
            if resp.status_code != 200:
                print(f"    [!] Error HTTP {resp.status_code}")
                continue
                
            data = resp.json()
            if len(data) < 2 or not data[1]:
                print(f"    [!] Respuesta sin registros.")
                continue
                
            observaciones = data[1]
            print(f"    -> HTTP 200 OK ({duracion} ms). Registros recuperados: {len(observaciones)}")
            
            for obs in observaciones:
                anio = obs.get("date")
                val = obs.get("value")
                pais = obs.get("country", {}).get("value", "Mexico")
                iso3 = obs.get("countryiso3code", "MEX")
                
                if anio not in registros_por_anio:
                    registros_por_anio[anio] = {
                        "Pais": pais,
                        "ISO3": iso3,
                        "Anio": int(anio),
                        "Poblacion_Total": None,
                        "PIB_USD_Corrientes": None,
                        "PIB_Miles_Millones_USD": None
                    }
                registros_por_anio[anio][col] = val
                if col == "PIB_USD_Corrientes" and val is not None:
                    registros_por_anio[anio]["PIB_Miles_Millones_USD"] = round(val / 1e9, 2)
                    
        except requests.exceptions.RequestException as e:
            print(f"    [!] Error al consumir el servicio: {e}")
            return []
            
        time.sleep(1.0)
        
    filas_ordenadas = sorted(registros_por_anio.values(), key=lambda x: x["Anio"])
    return filas_ordenadas
