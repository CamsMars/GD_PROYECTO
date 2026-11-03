# Configuracion del lago de datos de Filadelfia

import os
from pathlib import Path
from urllib.parse import quote

# Carpetas
RAIZ = Path(__file__).resolve().parent
CRUDOS = RAIZ / "datos_crudos"      
LAGO = RAIZ / "lago"                
WEB_DATOS = RAIZ / "docs" / "datos"  
EVIDENCIA = RAIZ / "evidencia"      

for carpeta in (CRUDOS, LAGO, WEB_DATOS, EVIDENCIA):
    carpeta.mkdir(parents=True, exist_ok=True)

archivo_env = RAIZ / ".env"
if archivo_env.exists():
    for linea in archivo_env.read_text(encoding="utf-8").splitlines():
        if "=" in linea and not linea.strip().startswith("#"):
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"'))

ANIO_INICIO = 2020
ANIO_FIN = 2024
N_ANIOS = ANIO_FIN - ANIO_INICIO + 1


CRS_GEO = "EPSG:4326"
CRS_AREA = "EPSG:2272"  
PIES2_A_KM2 = 0.3048 ** 2 / 1_000_000

DISTRITOS = ["RW", "NDEL", "LFNE", "CTR", "USW", "UNW", "UNO", "STH", "NOR",
             "LS", "LNE", "CNE", "WST", "UFNE", "LSW", "WP", "LNO", "LNW"]

CATEGORIAS_VIALES = [
    "Street Defect", "Street Paving", "Cracked Street",
    "Traffic Signal Emergency", "SIGNAL REQUEST", "Stop Sign Repair",
    "Street Light Outage",
]

URL_F01 = ("https://hub.arcgis.com/api/v3/datasets/0960ea0f38f44146bb562f2b212075aa_0"
           "/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1")


def url_f02(anio):
    categorias = ",".join("'" + c + "'" for c in CATEGORIAS_VIALES)
    sql = ("SELECT service_request_id, requested_datetime, closed_datetime, status, "
           "service_name, lat, lon FROM public_cases_fc "
           f"WHERE requested_datetime >= '{anio}-01-01' "
           f"AND requested_datetime < '{anio + 1}-01-01' "
           f"AND service_name IN ({categorias})")
    return "https://phl.carto.com/api/v2/sql?format=csv&filename=public_cases_fc&q=" + quote(sql)


def url_f02_categorias(anio):
    sql = ("SELECT service_name, COUNT(*) AS n FROM public_cases_fc "
           f"WHERE requested_datetime >= '{anio}-01-01' "
           f"AND requested_datetime < '{anio + 1}-01-01' "
           "GROUP BY service_name ORDER BY n DESC")
    return "https://phl.carto.com/api/v2/sql?format=csv&q=" + quote(sql)


URL_F03 = ("https://hub.arcgis.com/api/v3/datasets/21154a8f1894449f839d2288726e9837_0"
           "/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1")

URL_F04 = "https://www3.septa.org/developer/gtfs_public.zip"

CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")
URL_F05 = ("https://api.census.gov/data/2024/acs/acs5"
           "?get=NAME,B01003_001E,B19013_001E&for=tract:*&in=state:42%20county:101")

URL_F06 = "https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_42_tract.zip"

# Ficha pública para la interfaz; el endpoint de ingesta sigue requiriendo clave.
URL_F05_FICHA = "https://api.census.gov/data/2024/acs/acs5.html"
