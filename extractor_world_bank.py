"""
Modulo de Configuracion - Actividad 1
Materia: Adquisicion de Datos - Instituto Tecnologico de Toluca
"""

import os

USER_AGENT = "ITToluca-DataAcquisitionBot/1.0 (Contacto: alumno@toluca.tecnm.mx; Proposito: Academico Educativo)"
DEFAULT_TIMEOUT = 12

SITES = [
    {
        "id": "INEGI",
        "nombre": "INEGI Datos Abiertos",
        "url": "https://www.inegi.org.mx/datosabiertos/",
        "robots_url": "https://www.inegi.org.mx/robots.txt",
        "clasificacion": "Avanzado",
        "verify_ssl": True
    },
    {
        "id": "DATOS_GOB_MX",
        "nombre": "Datos.gob.mx (Mexico)",
        "url": "https://www.datos.gob.mx/",
        "robots_url": "https://www.datos.gob.mx/robots.txt",
        "clasificacion": "Intermedio / Avanzado",
        "verify_ssl": True
    },
    {
        "id": "WORLD_BANK",
        "nombre": "World Bank Open Data",
        "url": "https://data.worldbank.org/",
        "robots_url": "https://data.worldbank.org/robots.txt",
        "clasificacion": "Avanzado",
        "verify_ssl": True
    },
    {
        "id": "DATA_GOV",
        "nombre": "Data.gov (Estados Unidos)",
        "url": "https://data.gov/",
        "robots_url": "https://data.gov/robots.txt",
        "clasificacion": "Avanzado",
        "verify_ssl": True
    },
    {
        "id": "DOF",
        "nombre": "Diario Oficial de la Federacion",
        "url": "https://www.dof.gob.mx/",
        "robots_url": "https://www.dof.gob.mx/robots.txt",
        "clasificacion": "Basico",
        "verify_ssl": False  # Certificado con Hostname Mismatch documentado
    }
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extracciones")
CSV_OUTPUT = os.path.join(OUTPUT_DIR, "extraccion_banco_mundial_mexico.csv")
JSON_OUTPUT = os.path.join(OUTPUT_DIR, "extraccion_banco_mundial_mexico.json")
